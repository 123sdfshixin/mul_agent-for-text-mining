"""Chunk-level schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class SourceSpan(BaseModel):
    """Character span in the source material."""

    start: int
    end: int


class ChunkPosition(BaseModel):
    """Traceable document position metadata for a chunk."""

    section_order: int
    paragraph_start: int
    paragraph_end: int
    char_span: SourceSpan


class Chunk(BaseModel):
    """A semantically meaningful unit created during Stage II."""

    chunk_id: str
    text: str
    section_name: str
    chunk_type: str = "paragraph"
    source_span: SourceSpan
    position: ChunkPosition
    score: float
    rationale: str
    metadata: dict[str, Any] = Field(default_factory=dict)
