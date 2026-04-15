"""Parse normalized Markdown into PepFinder document structures."""

from __future__ import annotations

import re

from pepfinder.schemas.document import FigureContent, Section, TableContent


HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.*)$")
FIGURE_PATTERN = re.compile(r"^(figure|fig\.?)\s*(\d+)?[:. -]\s*(.+)$", re.IGNORECASE)
TABLE_CAPTION_PATTERN = re.compile(r"^table\s*(\d+)?[:. -]\s*(.+)$", re.IGNORECASE)


def infer_title(markdown_text: str) -> str | None:
    """Infer a document title from the first heading or first non-empty line."""
    for line in markdown_text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        heading_match = HEADING_PATTERN.match(stripped)
        if heading_match and len(heading_match.group(1)) == 1:
            return heading_match.group(2).strip()
        return stripped.lstrip("#").strip()
    return None


def parse_sections(markdown_text: str) -> list[Section]:
    """Split normalized Markdown into ordered sections."""
    sections: list[Section] = []
    current_heading: str | None = None
    current_level = 1
    current_lines: list[str] = []

    def flush_section() -> None:
        heading = current_heading or "Document"
        if current_lines or (heading and not sections):
            sections.append(
                Section(
                    heading=heading,
                    content="\n".join(current_lines).strip(),
                    level=current_level,
                    order=len(sections) + 1,
                )
            )

    for line in markdown_text.splitlines():
        heading_match = HEADING_PATTERN.match(line.strip())
        if heading_match:
            if current_lines:
                flush_section()
            current_heading = heading_match.group(2).strip() or "Untitled Section"
            current_level = len(heading_match.group(1))
            current_lines = []
            continue
        current_lines.append(line)

    flush_section()
    return [section for section in sections if section.content or section.heading]


def parse_tables(markdown_text: str, default_section: str | None = None) -> list[TableContent]:
    """Extract simple Markdown tables and nearby captions."""
    lines = markdown_text.splitlines()
    tables: list[TableContent] = []
    buffer: list[str] = []
    caption = ""

    def flush_table() -> None:
        nonlocal buffer, caption
        if not buffer:
            return
        table_index = len(tables) + 1
        markdown = "\n".join(buffer).strip()
        tables.append(
            TableContent(
                table_id=f"table-{table_index}",
                caption=caption,
                content=_table_text_from_markdown(markdown),
                markdown=markdown,
                section_name=default_section,
            )
        )
        buffer = []
        caption = ""

    for index, line in enumerate(lines):
        stripped = line.strip()
        if _is_markdown_table_line(stripped):
            if not buffer and index > 0:
                previous = lines[index - 1].strip()
                caption_match = TABLE_CAPTION_PATTERN.match(previous)
                if caption_match:
                    caption = previous
            buffer.append(line)
        else:
            flush_table()

    flush_table()
    return tables


def parse_figures(markdown_text: str, default_section: str | None = None) -> list[FigureContent]:
    """Extract figure captions from Markdown text."""
    figures: list[FigureContent] = []
    for line in markdown_text.splitlines():
        stripped = line.strip()
        match = FIGURE_PATTERN.match(stripped)
        if not match:
            continue
        figure_number = match.group(2) or str(len(figures) + 1)
        figures.append(
            FigureContent(
                figure_id=f"figure-{figure_number}",
                caption=stripped,
                reference=f"Figure {figure_number}",
                section_name=default_section,
            )
        )
    return figures


def _is_markdown_table_line(line: str) -> bool:
    """Detect whether a line belongs to a Markdown table."""
    return "|" in line and len([part for part in line.split("|") if part.strip()]) >= 2


def _table_text_from_markdown(markdown: str) -> str:
    """Convert a Markdown table block into a plain-text summary."""
    rows = []
    for line in markdown.splitlines():
        stripped = line.strip().strip("|")
        if not stripped:
            continue
        line_without_table_chars = stripped.replace("|", "").replace("-", "").replace(":", "").strip()
        if not line_without_table_chars:
            continue
        cells = [cell.strip() for cell in stripped.split("|")]
        rows.append("\t".join(cells))
    return "\n".join(rows)
