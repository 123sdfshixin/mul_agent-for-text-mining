"""File-format detection for Stage I."""

from __future__ import annotations

from pathlib import Path


SUPPORTED_FORMATS = {".md", ".txt", ".pdf", ".tex", ".doc", ".docx"}


def detect_source_format(path: Path) -> str:
    """Return the normalized source format for an input path."""
    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported file type: {suffix}")
    return suffix.lstrip(".")
