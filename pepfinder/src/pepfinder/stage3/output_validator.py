"""Validation helpers for Stage III extraction output."""

from __future__ import annotations

import json
import re
from typing import Any

from pepfinder.schemas.chunk import Chunk
from pepfinder.schemas.extraction import PeptideRecord


VALID_SEQUENCE_PATTERN = re.compile(r"^[ACDEFGHIKLMNPQRSTVWY]+$")


class OutputValidator:
    """Validate model output and convert it into PeptideRecord objects."""

    def validate(
        self,
        raw_output: str | list[dict[str, Any]] | dict[str, Any],
        chunk: Chunk,
        source_document: str,
    ) -> list[PeptideRecord]:
        """Validate JSON structure, enforce traceability, and normalize records."""
        payload = self._coerce_to_python(raw_output)
        if isinstance(payload, dict):
            payload = [payload]
        if not isinstance(payload, list):
            raise ValueError("Extraction output must be a list or object.")

        records: list[PeptideRecord] = []
        for index, item in enumerate(payload, start=1):
            if not isinstance(item, dict):
                continue

            sequence = _normalize_sequence(item.get("sequence"))
            length = item.get("length")
            if sequence and length is None:
                length = len(sequence)
            if sequence and length not in {None, len(sequence)}:
                length = len(sequence)

            evidence_text = (item.get("evidence_text") or "").strip() or chunk.text
            record = PeptideRecord(
                id=item.get("id") or f"{chunk.chunk_id}-record-{index}",
                name=_empty_to_none(item.get("name")),
                sequence=sequence,
                length=length,
                source=_empty_to_none(item.get("source")),
                modification=_empty_to_none(item.get("modification")),
                activity=_empty_to_none(item.get("activity")),
                target=_empty_to_none(item.get("target")),
                assay=_empty_to_none(item.get("assay")),
                condition=_empty_to_none(item.get("condition")),
                measurement_values=_normalize_measurements(item.get("measurement_values")),
                evidence_text=evidence_text,
                source_chunk_id=chunk.chunk_id,
                source_section=chunk.section_name,
                source_document=source_document,
                metadata=item.get("metadata", {}) or {},
            )
            if not record.name and not record.sequence and not record.measurement_values:
                continue
            records.append(record)
        return records

    def _coerce_to_python(self, raw_output: str | list[dict[str, Any]] | dict[str, Any]) -> Any:
        """Convert backend output into Python objects."""
        if isinstance(raw_output, str):
            raw_output = raw_output.strip()
            if not raw_output:
                return []
            return json.loads(raw_output)
        return raw_output


def _normalize_sequence(sequence: Any) -> str | None:
    """Normalize a peptide sequence if it looks valid."""
    if not sequence:
        return None
    normalized = str(sequence).strip().upper().replace(" ", "")
    if not VALID_SEQUENCE_PATTERN.match(normalized):
        return None
    return normalized


def _normalize_measurements(values: Any) -> list[str]:
    """Normalize measurement values into a string list."""
    if values is None:
        return []
    if isinstance(values, str):
        return [values.strip()] if values.strip() else []
    if isinstance(values, list):
        return [str(item).strip() for item in values if str(item).strip()]
    return [str(values).strip()]


def _empty_to_none(value: Any) -> str | None:
    """Convert blank-like values to None."""
    if value is None:
        return None
    text = str(value).strip()
    return text or None
