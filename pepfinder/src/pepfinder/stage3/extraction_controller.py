"""Controller for Stage III selective knowledge extraction."""

from __future__ import annotations

from pathlib import Path

from pepfinder.schemas.chunk import Chunk
from pepfinder.schemas.extraction import ExtractionDataset
from pepfinder.schemas.stage2 import ChunkArtifact
from pepfinder.stage3.aggregator import ResultAggregator
from pepfinder.stage3.extraction_agent import KnowledgeExtractionAgent
from pepfinder.utils.io import ensure_dir, read_json, write_json


class ExtractionController:
    """Load Stage II chunks, select candidates, extract records, and aggregate results."""

    def __init__(
        self,
        extraction_agent: KnowledgeExtractionAgent | None = None,
        aggregator: ResultAggregator | None = None,
        score_threshold: float = 1.5,
    ) -> None:
        """Initialize controller dependencies."""
        self.extraction_agent = extraction_agent or KnowledgeExtractionAgent()
        self.aggregator = aggregator or ResultAggregator()
        self.score_threshold = score_threshold

    def run(self, chunk_path: str | Path, output_dir: Path) -> Path:
        """Execute Stage III extraction and write the dataset artifact."""
        chunk_path = Path(chunk_path)
        artifact = ChunkArtifact.model_validate(read_json(chunk_path))
        selected_chunks = self.select_candidate_chunks(artifact.chunks)

        records = []
        for chunk in selected_chunks:
            records.extend(self.extraction_agent.extract(chunk, source_document=artifact.document_id))

        dataset = self.aggregator.aggregate(
            document_id=artifact.document_id,
            source_chunk_file=str(chunk_path),
            selected_chunk_ids=[chunk.chunk_id for chunk in selected_chunks],
            records=records,
        )
        return self._write_dataset(dataset, output_dir)

    def select_candidate_chunks(self, chunks: list[Chunk]) -> list[Chunk]:
        """Select high-value chunks for targeted extraction."""
        selected = [
            chunk
            for chunk in chunks
            if chunk.score >= self.score_threshold
            or chunk.chunk_type in {"table", "figure_caption", "mixed"}
        ]
        return selected or chunks

    def _write_dataset(self, dataset: ExtractionDataset, output_dir: Path) -> Path:
        """Persist the final Stage III dataset JSON artifact."""
        ensure_dir(output_dir)
        output_path = output_dir / f"{dataset.document_id}.extractions.json"
        write_json(output_path, dataset.model_dump())
        return output_path
