"""Schemas for Stage II global guidance and chunking artifacts."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from pepfinder.schemas.chunk import Chunk, SourceSpan


class SectionNode(BaseModel):
    """Hierarchical section summary used by the GS Agent."""

    section_name: str
    level: int
    order: int
    summary: str
    paragraph_count: int
    score: float
    is_information_dense: bool


class RegionLink(BaseModel):
    """A semantic relation between a special block and nearby explanation text."""

    source_id: str
    source_type: str
    target_region_id: str
    relation: str
    confidence: float


class ImportantRegion(BaseModel):
    """A document region likely to contain extraction-worthy scientific content."""

    region_id: str
    region_type: str
    section_name: str
    section_order: int
    source_span: SourceSpan
    paragraph_start: int
    paragraph_end: int
    score: float
    signals: list[str] = Field(default_factory=list)
    related_table_ids: list[str] = Field(default_factory=list)
    related_figure_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class GlobalStructureGuidance(BaseModel):
    """Structured GS Agent output used to guide fine-grained chunking."""

    document_id: str
    section_nodes: list[SectionNode] = Field(default_factory=list)
    important_regions: list[ImportantRegion] = Field(default_factory=list)
    figure_links: list[RegionLink] = Field(default_factory=list)
    table_links: list[RegionLink] = Field(default_factory=list)
    coarse_boundaries: list[SourceSpan] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ChunkArtifact(BaseModel):
    """Saved Stage II artifact with guidance plus final chunks."""

    document_id: str
    guidance: GlobalStructureGuidance
    chunks: list[Chunk] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
