"""Fine-grained semantic chunking agent for Stage II."""

from __future__ import annotations

from pepfinder.agents.base import BaseAgent
from pepfinder.schemas.chunk import Chunk, ChunkPosition, SourceSpan
from pepfinder.schemas.document import UnifiedDocument
from pepfinder.schemas.stage2 import GlobalStructureGuidance, ImportantRegion
from pepfinder.stage2.base import build_paragraph_units


class FineGrainedChunkingAgent(BaseAgent):
    """Create semantic chunks guided by GS Agent output."""

    def run(self, document: UnifiedDocument, guidance: GlobalStructureGuidance) -> list[Chunk]:
        """Generate traceable semantically complete chunks from important regions."""
        paragraph_units = build_paragraph_units(document)
        chunks: list[Chunk] = []
        for region in guidance.important_regions:
            chunk = self._chunk_from_region(document, region, guidance, paragraph_units, len(chunks) + 1)
            if chunk is not None:
                chunks.append(chunk)
        return chunks

    def _chunk_from_region(
        self,
        document: UnifiedDocument,
        region: ImportantRegion,
        guidance: GlobalStructureGuidance,
        paragraph_units: list,
        chunk_index: int,
    ) -> Chunk | None:
        """Assemble a single chunk from a guided semantic region."""
        region_unit_ids = set(region.metadata.get("unit_ids", []))
        region_units = [unit for unit in paragraph_units if unit.unit_id in region_unit_ids]
        if not region_units:
            return None

        text_parts = [f"## {region.section_name}"]
        rationale_parts = [f"GS-selected {region.region_type} region", f"signals={', '.join(region.signals) or 'none'}"]
        metadata = {
            "region_id": region.region_id,
            "related_table_ids": region.related_table_ids,
            "related_figure_ids": region.related_figure_ids,
        }

        region_text = "\n\n".join(unit.text for unit in region_units)
        text_parts.append(region_text)

        for link in guidance.table_links:
            if link.target_region_id == region.region_id:
                metadata.setdefault("linked_tables", []).append(link.source_id)
        for link in guidance.figure_links:
            if link.target_region_id == region.region_id:
                metadata.setdefault("linked_figures", []).append(link.source_id)

        if metadata.get("linked_tables"):
            table_texts = []
            for table in document.tables:
                if table.table_id in metadata["linked_tables"]:
                    table_block = table.markdown or table.content
                    if table.caption:
                        table_block = f"{table.caption}\n{table_block}".strip()
                    table_texts.append(table_block)
            if table_texts:
                text_parts.append("\n\n".join(table_texts))
                rationale_parts.append("merged linked table context")

        if metadata.get("linked_figures"):
            figure_texts = []
            for figure in document.figures:
                if figure.figure_id in metadata["linked_figures"]:
                    figure_texts.append(figure.caption or figure.reference)
            if figure_texts:
                text_parts.append("\n\n".join(figure_texts))
                rationale_parts.append("merged linked figure caption")

        chunk_text = "\n\n".join(part for part in text_parts if part.strip())
        return Chunk(
            chunk_id=f"{document.document_id}-chunk-{chunk_index}",
            text=chunk_text,
            section_name=region.section_name,
            chunk_type=region.region_type,
            source_span=region.source_span,
            position=ChunkPosition(
                section_order=region.section_order,
                paragraph_start=region.paragraph_start,
                paragraph_end=region.paragraph_end,
                char_span=SourceSpan(start=region.source_span.start, end=region.source_span.end),
            ),
            score=region.score,
            rationale="; ".join(rationale_parts),
            metadata=metadata,
        )
