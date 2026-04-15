"""Artifact writing helpers for Stage I."""

from __future__ import annotations

from pathlib import Path

from pepfinder.schemas.document import UnifiedDocument
from pepfinder.utils.io import ensure_dir, write_json


def write_normalization_artifacts(
    output_dir: Path,
    document: UnifiedDocument,
) -> dict[str, str]:
    """Write normalized Markdown and JSON artifacts for a document."""
    ensure_dir(output_dir)
    markdown_path = output_dir / f"{document.document_id}.normalized.md"
    json_path = output_dir / f"{document.document_id}.normalized.json"
    markdown_path.write_text(document.normalized_text, encoding="utf-8")
    write_json(json_path, document.model_dump())
    return {
        "document_id": document.document_id,
        "markdown_path": str(markdown_path),
        "json_path": str(json_path),
    }
