"""Document-level schemas."""

from typing import Any

from pydantic import BaseModel, Field


class Section(BaseModel):
    """A normalized document section."""

    heading: str
    content: str
    level: int = 1
    order: int = 0


class TableContent(BaseModel):
    """A normalized table representation."""

    table_id: str = ""
    caption: str = ""
    content: str = ""
    markdown: str = ""
    section_name: str | None = None


class FigureContent(BaseModel):
    """A normalized figure representation."""

    figure_id: str = ""
    caption: str = ""
    reference: str = ""
    section_name: str | None = None


class UnifiedDocument(BaseModel):
    """Unified intermediate representation for a scientific document."""

    document_id: str
    source_path: str
    source_format: str
    title: str | None = None
    raw_text: str
    normalized_text: str
    sections: list[Section] = Field(default_factory=list)
    tables: list[TableContent] = Field(default_factory=list)
    figures: list[FigureContent] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
