"""Shared helpers for Stage II semantic chunking."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from pepfinder.schemas.document import UnifiedDocument


PEPTIDE_KEYWORDS = (
    "peptide",
    "sequence",
    "assay",
    "activity",
    "target",
    "mic",
    "ic50",
    "ec50",
    "inhibition",
    "antimicrobial",
    "toxicity",
    "binding",
    "organism",
)

SECTION_PRIORITY_TERMS = (
    "abstract",
    "result",
    "discussion",
    "experiment",
    "method",
    "activity",
    "supplementary",
)

SEQUENCE_PATTERN = re.compile(r"\b[A-Z]{6,}\b")
ACTIVITY_PATTERN = re.compile(r"\b\d+(?:\.\d+)?\s?(?:uM|µM|ug/mL|mg/L|nM|mM)\b", re.IGNORECASE)
FIGURE_REF_PATTERN = re.compile(r"\b(?:figure|fig\.?)\s*\d+\b", re.IGNORECASE)
TABLE_REF_PATTERN = re.compile(r"\btable\s*\d+\b", re.IGNORECASE)
EQUATION_PATTERN = re.compile(r"\$\$.*?\$\$", re.DOTALL)


@dataclass
class ParagraphUnit:
    """Paragraph-level unit used internally by Stage II."""

    unit_id: str
    section_name: str
    section_order: int
    section_level: int
    paragraph_index: int
    text: str
    start: int
    end: int
    paragraph_type: str = "paragraph"
    score: float = 0.0
    signals: list[str] = field(default_factory=list)
    related_table_ids: list[str] = field(default_factory=list)
    related_figure_ids: list[str] = field(default_factory=list)


def build_paragraph_units(document: UnifiedDocument) -> list[ParagraphUnit]:
    """Split sections into traceable paragraph units with source spans."""
    units: list[ParagraphUnit] = []
    search_start = 0
    for section in document.sections:
        paragraphs = [part.strip() for part in section.content.split("\n\n") if part.strip()]
        if not paragraphs and section.content.strip():
            paragraphs = [section.content.strip()]

        for paragraph_index, paragraph in enumerate(paragraphs, start=1):
            start = document.normalized_text.find(paragraph, search_start)
            if start == -1:
                start = document.normalized_text.find(paragraph)
            end = start + len(paragraph) if start >= 0 else len(paragraph)
            if start >= 0:
                search_start = end

            paragraph_type = classify_paragraph(paragraph)
            score, signals = score_text(paragraph, section.heading)
            units.append(
                ParagraphUnit(
                    unit_id=f"{document.document_id}-p-{len(units) + 1}",
                    section_name=section.heading,
                    section_order=section.order,
                    section_level=section.level,
                    paragraph_index=paragraph_index,
                    text=paragraph,
                    start=max(start, 0),
                    end=max(end, 0),
                    paragraph_type=paragraph_type,
                    score=score,
                    signals=signals,
                )
            )
    return units


def classify_paragraph(text: str) -> str:
    """Infer a coarse paragraph type from Markdown-like text."""
    stripped = text.strip()
    if "|" in stripped and "\n" in stripped:
        return "table"
    if stripped.lower().startswith(("figure", "fig.")):
        return "figure_caption"
    if EQUATION_PATTERN.search(stripped):
        return "equation"
    return "paragraph"


def score_text(text: str, section_name: str) -> tuple[float, list[str]]:
    """Score a text segment for peptide-information density."""
    lowered = text.lower()
    signals: list[str] = []
    score = 0.0

    for keyword in PEPTIDE_KEYWORDS:
        count = lowered.count(keyword)
        if count:
            score += 1.5 * count
            signals.append(f"keyword:{keyword}")

    if SEQUENCE_PATTERN.search(text):
        score += 2.5
        signals.append("sequence_pattern")
    if ACTIVITY_PATTERN.search(text):
        score += 2.0
        signals.append("activity_value")
    if FIGURE_REF_PATTERN.search(text):
        score += 1.0
        signals.append("figure_reference")
    if TABLE_REF_PATTERN.search(text):
        score += 1.0
        signals.append("table_reference")
    if EQUATION_PATTERN.search(text):
        score += 0.8
        signals.append("equation_block")

    if any(term in section_name.lower() for term in SECTION_PRIORITY_TERMS):
        score += 1.0
        signals.append("priority_section")

    score += min(len(text) / 400.0, 1.2)
    return round(score, 3), signals
