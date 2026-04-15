"""Result aggregation for Stage III."""

from __future__ import annotations

from pepfinder.schemas.extraction import ExtractionDataset, PeptideRecord


class ResultAggregator:
    """Merge and deduplicate Stage III extraction records."""

    def aggregate(
        self,
        document_id: str,
        source_chunk_file: str,
        selected_chunk_ids: list[str],
        records: list[PeptideRecord],
    ) -> ExtractionDataset:
        """Build the final dataset artifact with light deduplication."""
        deduped = self._deduplicate(records)
        return ExtractionDataset(
            document_id=document_id,
            source_chunk_file=source_chunk_file,
            selected_chunk_ids=selected_chunk_ids,
            records=deduped,
            metadata={
                "record_count": len(deduped),
                "selected_chunk_count": len(selected_chunk_ids),
            },
        )

    def _deduplicate(self, records: list[PeptideRecord]) -> list[PeptideRecord]:
        """Deduplicate records conservatively while preserving traceability."""
        seen: set[tuple[str, str, str, str]] = set()
        deduped: list[PeptideRecord] = []
        for record in records:
            key = (
                (record.name or "").lower(),
                record.sequence or "",
                record.source_chunk_id,
                record.evidence_text.strip(),
            )
            if key in seen:
                continue
            seen.add(key)
            deduped.append(record)
        return deduped
