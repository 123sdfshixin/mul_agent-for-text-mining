"""Stage I orchestration: document conversion and normalization."""

from __future__ import annotations

from pathlib import Path

from pepfinder.agents.base import BaseAgent
from pepfinder.schemas.document import UnifiedDocument
from pepfinder.stage1.base import BaseDocumentConverter
from pepfinder.stage1.converters import (
    DocLikeConverter,
    MarkerPdfConverter,
    MarkdownTextConverter,
    PlainTextConverter,
    TexConverter,
)
from pepfinder.stage1.detector import detect_source_format
from pepfinder.stage1.markdown_normalizer import normalize_markdown
from pepfinder.stage1.structure_parser import infer_title, parse_figures, parse_sections, parse_tables


class DocumentConversionAndNormalizationAgent(BaseAgent):
    """Convert heterogeneous scientific documents into a unified Markdown IR."""

    def __init__(self) -> None:
        """Register format-specific converters for Stage I."""
        self._converters: dict[str, BaseDocumentConverter] = {
            "md": MarkdownTextConverter(),
            "txt": PlainTextConverter(),
            "tex": TexConverter(),
            "pdf": MarkerPdfConverter(),
            "doc": DocLikeConverter(),
            "docx": DocLikeConverter(),
        }

    def run(self, input_path: str | Path) -> UnifiedDocument:
        """Normalize a document and return a UnifiedDocument artifact."""
        path = Path(input_path)
        source_format = detect_source_format(path)
        converter = self._converters[source_format]
        conversion_result = converter.convert(path)
        normalized_text = normalize_markdown(conversion_result.markdown_text)
        title = infer_title(normalized_text)
        sections = parse_sections(normalized_text)
        default_section = sections[0].heading if sections else None
        tables = parse_tables(normalized_text, default_section=default_section)
        figures = parse_figures(normalized_text, default_section=default_section)

        return UnifiedDocument(
            document_id=path.stem,
            source_path=str(path),
            source_format=source_format,
            title=title,
            raw_text=conversion_result.raw_text,
            normalized_text=normalized_text,
            sections=sections,
            tables=tables,
            figures=figures,
            metadata=conversion_result.metadata,
        )
