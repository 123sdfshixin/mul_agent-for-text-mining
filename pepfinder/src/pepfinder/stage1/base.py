"""Base classes and shared models for Stage I conversion."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class ConversionResult(BaseModel):
    """Raw conversion output before structural parsing."""

    raw_text: str
    markdown_text: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class BaseDocumentConverter(ABC):
    """Interface for file-format-specific document converters."""

    @abstractmethod
    def convert(self, input_path: Path) -> ConversionResult:
        """Convert an input file into Markdown-like text plus metadata."""
