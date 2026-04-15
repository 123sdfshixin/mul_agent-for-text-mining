"""Global Structure Agent for Stage II."""

from __future__ import annotations

import re

from pepfinder.agents.base import BaseAgent
from pepfinder.schemas.document import UnifiedDocument
from pepfinder.schemas.stage2 import (
    GlobalStructureGuidance,
    ImportantRegion,
    RegionLink,
    SectionNode,
)
from pepfinder.schemas.chunk import SourceSpan
from pepfinder.stage2.base import FIGURE_REF_PATTERN, TABLE_REF_PATTERN, build_paragraph_units


FIGURE_ID_PATTERN = re.compile(r"(\d+)")
TABLE_ID_PATTERN = re.compile(r"(\d+)")


class GlobalStructureAgent(BaseAgent):
    """Build document-level semantic guidance for fine-grained chunking."""

    def run(self, document: UnifiedDocument) -> GlobalStructureGuidance:
        """Analyze sections, identify important regions, and build relation maps."""
        paragraph_units = build_paragraph_units(document)
        section_nodes = self._build_section_nodes(document, paragraph_units)
        important_regions = self._build_important_regions(paragraph_units)
        figure_links = self._link_figures(document, important_regions, paragraph_units)
        table_links = self._link_tables(document, important_regions, paragraph_units)
        boundaries = [region.source_span for region in important_regions]

        return GlobalStructureGuidance(
            document_id=document.document_id,
            section_nodes=section_nodes,
            important_regions=important_regions,
            figure_links=figure_links,
            table_links=table_links,
            coarse_boundaries=boundaries,
            metadata={"paragraph_count": len(paragraph_units)},
        )

    def _build_section_nodes(self, document: UnifiedDocument, paragraph_units: list) -> list[SectionNode]:
        """Summarize section hierarchy and density."""
        nodes: list[SectionNode] = []
        for section in document.sections:
            units = [unit for unit in paragraph_units if unit.section_name == section.heading]
            avg_score = sum(unit.score for unit in units) / len(units) if units else 0.0
            nodes.append(
                SectionNode(
                    section_name=section.heading,
                    level=section.level,
                    order=section.order,
                    summary=section.content[:180].strip(),
                    paragraph_count=len(units),
                    score=round(avg_score, 3),
                    is_information_dense=avg_score >= 1.8 or any(unit.score >= 2.5 for unit in units),
                )
            )
        return nodes

    def _build_important_regions(self, paragraph_units: list) -> list[ImportantRegion]:
        """Construct coarse semantic regions from paragraph units."""
        regions: list[ImportantRegion] = []
        dense_threshold = 2.0
        index = 0
        while index < len(paragraph_units):
            current = paragraph_units[index]
            should_keep = current.score >= dense_threshold or current.paragraph_type != "paragraph"
            if not should_keep:
                index += 1
                continue

            region_units = [current]
            next_index = index + 1
            while next_index < len(paragraph_units):
                nxt = paragraph_units[next_index]
                same_section = nxt.section_name == current.section_name
                semantically_close = nxt.score >= 1.2 or nxt.paragraph_type != "paragraph"
                adjacent = nxt.paragraph_index == region_units[-1].paragraph_index + 1
                if same_section and adjacent and semantically_close:
                    region_units.append(nxt)
                    next_index += 1
                    continue
                break

            region_type = self._region_type(region_units)
            signals = sorted({signal for unit in region_units for signal in unit.signals})
            region_text = "\n\n".join(unit.text for unit in region_units)
            regions.append(
                ImportantRegion(
                    region_id=f"{current.unit_id}-region",
                    region_type=region_type,
                    section_name=current.section_name,
                    section_order=current.section_order,
                    source_span=SourceSpan(start=region_units[0].start, end=region_units[-1].end),
                    paragraph_start=region_units[0].paragraph_index,
                    paragraph_end=region_units[-1].paragraph_index,
                    score=round(sum(unit.score for unit in region_units) / len(region_units), 3),
                    signals=signals,
                    related_table_ids=_extract_ref_ids(TABLE_REF_PATTERN, region_text, prefix="table"),
                    related_figure_ids=_extract_ref_ids(FIGURE_REF_PATTERN, region_text, prefix="figure"),
                    metadata={"unit_ids": [unit.unit_id for unit in region_units]},
                )
            )
            index = next_index
        return regions

    def _link_figures(self, document: UnifiedDocument, regions: list[ImportantRegion], paragraph_units: list) -> list[RegionLink]:
        """Link figure captions to nearby regions mentioning the same figure."""
        links: list[RegionLink] = []
        for figure in document.figures:
            figure_number = _extract_numeric_id(figure.figure_id)
            if not figure_number:
                continue
            for region in regions:
                region_text = self._region_text(region, paragraph_units).lower()
                same_figure = f"figure-{figure_number}" in region.related_figure_ids
                text_match = f"figure {figure_number}" in region_text or f"fig. {figure_number}" in region_text
                same_section = not figure.section_name or region.section_name == figure.section_name
                if same_figure or (same_section and text_match):
                    links.append(
                        RegionLink(
                            source_id=figure.figure_id,
                            source_type="figure",
                            target_region_id=region.region_id,
                            relation="caption_explains_region",
                            confidence=0.8,
                        )
                    )
        return links

    def _link_tables(self, document: UnifiedDocument, regions: list[ImportantRegion], paragraph_units: list) -> list[RegionLink]:
        """Link tables to nearby explanatory regions."""
        links: list[RegionLink] = []
        for table in document.tables:
            table_number = _extract_numeric_id(table.table_id)
            for region in regions:
                region_text = self._region_text(region, paragraph_units).lower()
                same_table = table.table_id in region.related_table_ids if table.table_id else False
                mentions_table = (
                    f"table {table_number}" in region_text if table_number else bool(TABLE_REF_PATTERN.search(region_text))
                )
                same_section = not table.section_name or region.section_name == table.section_name
                if same_table or (same_section and (mentions_table or region.region_type in {"table", "mixed"})):
                    links.append(
                        RegionLink(
                            source_id=table.table_id or f"table-{len(links) + 1}",
                            source_type="table",
                            target_region_id=region.region_id,
                            relation="table_explained_by_region",
                            confidence=0.8,
                        )
                    )
        return links

    def _region_text(self, region: ImportantRegion, paragraph_units: list) -> str:
        """Rebuild text for a region from underlying paragraph units."""
        unit_ids = set(region.metadata.get("unit_ids", []))
        return "\n\n".join(unit.text for unit in paragraph_units if unit.unit_id in unit_ids)

    def _region_type(self, region_units: list) -> str:
        """Infer the dominant region type from grouped paragraph units."""
        unit_types = {unit.paragraph_type for unit in region_units}
        if len(unit_types) == 1:
            return next(iter(unit_types))
        return "mixed"


def _extract_numeric_id(identifier: str) -> str | None:
    """Extract a numeric identifier from a table or figure id."""
    match = FIGURE_ID_PATTERN.search(identifier or "")
    return match.group(1) if match else None


def _extract_ref_ids(pattern: re.Pattern[str], text: str, prefix: str) -> list[str]:
    """Extract referenced figure or table ids from region text."""
    ids: list[str] = []
    for match in pattern.finditer(text):
        numeric_match = re.search(r"(\d+)", match.group(0))
        if numeric_match:
            ids.append(f"{prefix}-{numeric_match.group(1)}")
    return sorted(set(ids))
