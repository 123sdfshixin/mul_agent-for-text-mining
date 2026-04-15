"""Markdown normalization helpers."""

from __future__ import annotations

import re


def normalize_markdown(text: str) -> str:
    """Normalize line endings and excessive whitespace in Markdown-like text."""
    normalized = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    normalized = re.sub(r"[ \t]+\n", "\n", normalized)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    return normalized.strip() + "\n"
