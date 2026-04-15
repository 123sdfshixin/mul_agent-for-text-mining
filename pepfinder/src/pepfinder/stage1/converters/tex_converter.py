"""Basic LaTeX to Markdown conversion for the PepFinder MVP."""

from __future__ import annotations

import re
from pathlib import Path

from pepfinder.stage1.base import BaseDocumentConverter, ConversionResult


class TexConverter(BaseDocumentConverter):
    """Convert common LaTeX section commands into Markdown headings."""

    SECTION_MAPPINGS = {
        r"\\section\{(.+?)\}": "# {title}",
        r"\\subsection\{(.+?)\}": "## {title}",
        r"\\subsubsection\{(.+?)\}": "### {title}",
        r"\\paragraph\{(.+?)\}": "#### {title}",
        r"\\title\{(.+?)\}": "# {title}",
    }

    def convert(self, input_path: Path) -> ConversionResult:
        """Convert a subset of LaTeX commands into Markdown text."""
        text = input_path.read_text(encoding="utf-8")
        markdown = text
        for pattern, replacement in self.SECTION_MAPPINGS.items():
            markdown = re.sub(
                pattern,
                lambda match: replacement.format(title=match.group(1).strip()),
                markdown,
            )

        markdown = re.sub(r"\\begin\{equation\}", "\n$$\n", markdown)
        markdown = re.sub(r"\\end\{equation\}", "\n$$\n", markdown)
        markdown = re.sub(r"\\caption\{(.+?)\}", r"Figure: \1", markdown)
        markdown = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?(?:\{[^{}]*\})?", "", markdown)
        markdown = re.sub(r"\n{3,}", "\n\n", markdown)

        return ConversionResult(
            raw_text=text,
            markdown_text=markdown.strip(),
            metadata={"conversion_backend": "basic_tex"},
        )
