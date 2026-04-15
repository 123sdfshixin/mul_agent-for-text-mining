"""Converters for Markdown and plain text files."""

from __future__ import annotations

from pathlib import Path

from pepfinder.stage1.base import BaseDocumentConverter, ConversionResult


class MarkdownTextConverter(BaseDocumentConverter):
    """Load Markdown files while preserving existing structure."""

    def convert(self, input_path: Path) -> ConversionResult:
        """Return Markdown content with minimal transformation."""
        text = input_path.read_text(encoding="utf-8")
        return ConversionResult(
            raw_text=text,
            markdown_text=text,
            metadata={"conversion_backend": "native_markdown"},
        )


class PlainTextConverter(BaseDocumentConverter):
    """Convert plain text files to simple Markdown."""

    def convert(self, input_path: Path) -> ConversionResult:
        """Convert paragraphs from plain text into Markdown-like text."""
        text = input_path.read_text(encoding="utf-8")
        paragraphs = [part.strip() for part in text.split("\n\n") if part.strip()]
        if not paragraphs:
            markdown = f"# {input_path.stem}\n"
        else:
            markdown_lines = [f"# {input_path.stem.replace('_', ' ').title()}"]
            markdown_lines.extend(paragraphs)
            markdown = "\n\n".join(markdown_lines)

        return ConversionResult(
            raw_text=text,
            markdown_text=markdown,
            metadata={"conversion_backend": "plain_text"},
        )
