"""Extraction schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class PeptideRecord(BaseModel):
    """Structured peptide information extracted from a chunk."""

    id: str
    name: str | None = None
    sequence: str | None = None
    length: int | None = None
    source: str | None = None
    modification: str | None = None
    activity: str | None = None
    target: str | None = None
    assay: str | None = None
    condition: str | None = None
    measurement_values: list[str] = Field(default_factory=list)
    evidence_text: str
    source_chunk_id: str
    source_section: str
    source_document: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class ExtractionDataset(BaseModel):
    """Final Stage III dataset artifact."""

    document_id: str
    source_chunk_file: str
    selected_chunk_ids: list[str] = Field(default_factory=list)
    records: list[PeptideRecord] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
