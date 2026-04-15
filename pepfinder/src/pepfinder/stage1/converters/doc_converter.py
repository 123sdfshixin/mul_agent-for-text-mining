"""Basic DOC and DOCX conversion helpers."""

from __future__ import annotations

from pathlib import Path
from xml.etree import ElementTree as ET
import zipfile

from pepfinder.stage1.base import BaseDocumentConverter, ConversionResult


class DocLikeConverter(BaseDocumentConverter):
    """Convert DOCX files when possible and provide placeholders for DOC."""

    WORD_NAMESPACE = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

    def convert(self, input_path: Path) -> ConversionResult:
        """Convert DOCX or return a readable placeholder for legacy DOC."""
        suffix = input_path.suffix.lower()
        if suffix == ".docx":
            return self._convert_docx(input_path)
        if suffix == ".doc":
            placeholder = (
                f"# {input_path.stem}\n\n"
                "Legacy .doc conversion is not implemented in the MVP. "
                "Please convert this file to .docx, .pdf, .md, or .txt first."
            )
            return ConversionResult(
                raw_text=placeholder,
                markdown_text=placeholder,
                metadata={"conversion_backend": "doc_placeholder", "todo": "add legacy .doc parser"},
            )
        raise ValueError(f"Unsupported Word format: {suffix}")

    def _convert_docx(self, input_path: Path) -> ConversionResult:
        """Extract paragraph text and heading styles from a DOCX file."""
        with zipfile.ZipFile(input_path) as archive:
            xml_bytes = archive.read("word/document.xml")

        root = ET.fromstring(xml_bytes)
        markdown_lines: list[str] = []
        raw_parts: list[str] = []

        for paragraph in root.findall(".//w:p", self.WORD_NAMESPACE):
            texts = [
                node.text or ""
                for node in paragraph.findall(".//w:t", self.WORD_NAMESPACE)
                if node.text
            ]
            content = "".join(texts).strip()
            if not content:
                continue

            style_value = None
            style_node = paragraph.find(".//w:pStyle", self.WORD_NAMESPACE)
            if style_node is not None:
                style_value = style_node.attrib.get(f"{{{self.WORD_NAMESPACE['w']}}}val", "")

            if style_value and style_value.lower().startswith("heading"):
                heading_level = "".join(ch for ch in style_value if ch.isdigit()) or "1"
                markdown_lines.append(f"{'#' * int(heading_level)} {content}")
            else:
                markdown_lines.append(content)

            raw_parts.append(content)

        markdown_text = "\n\n".join(markdown_lines) if markdown_lines else f"# {input_path.stem}\n"
        return ConversionResult(
            raw_text="\n".join(raw_parts),
            markdown_text=markdown_text,
            metadata={"conversion_backend": "basic_docx"},
        )
