"""Pipeline orchestration for the PepFinder MVP."""

from __future__ import annotations

from pathlib import Path

from pepfinder.config import DEFAULT_SETTINGS, Settings
from pepfinder.schemas.document import UnifiedDocument
from pepfinder.schemas.stage2 import ChunkArtifact
from pepfinder.stage1.artifacts import write_normalization_artifacts
from pepfinder.stage1.normalizer import DocumentConversionAndNormalizationAgent
from pepfinder.stage2.artifacts import write_stage2_artifacts
from pepfinder.stage2.chunker import FineGrainedChunkingAgent, GlobalStructureAgent
from pepfinder.stage3.extraction_agent import KnowledgeExtractionAgent
from pepfinder.stage3.extraction_controller import ExtractionController
from pepfinder.utils.io import read_json


class PepFinderPipeline:
    """Orchestrate the three-stage PepFinder workflow."""

    def __init__(self, settings: Settings | None = None, extractor: KnowledgeExtractionAgent | None = None):
        """Initialize pipeline dependencies."""
        self.settings = settings or DEFAULT_SETTINGS
        self.normalizer = DocumentConversionAndNormalizationAgent()
        self.structure_agent = GlobalStructureAgent()
        self.chunking_agent = FineGrainedChunkingAgent()
        self.extraction_controller = ExtractionController(extraction_agent=extractor or KnowledgeExtractionAgent())

    def normalize(self, input_path: str | Path) -> dict[str, str]:
        """Run Stage I and write normalized Markdown and JSON artifacts."""
        document = self.normalizer.run(input_path)
        return write_normalization_artifacts(self.settings.normalized_dir, document)

    def chunk(self, normalized_path: str | Path) -> dict[str, str]:
        """Run Stage II and write guidance plus chunk JSON outputs."""
        normalized_payload = read_json(Path(normalized_path))
        document = UnifiedDocument.model_validate(normalized_payload)
        guidance = self.structure_agent.run(document)
        chunks = self.chunking_agent.run(document, guidance)
        artifact = ChunkArtifact(
            document_id=document.document_id,
            guidance=guidance,
            chunks=chunks,
            metadata={"chunk_count": len(chunks)},
        )
        return write_stage2_artifacts(self.settings.chunks_dir, guidance, artifact)

    def extract(self, chunk_path: str | Path) -> Path:
        """Run Stage III and write extraction JSON output."""
        return self.extraction_controller.run(chunk_path, self.settings.extraction_dir)

    def run(self, input_path: str | Path) -> dict[str, str]:
        """Execute the full Stage I -> Stage II -> Stage III pipeline."""
        normalization_outputs = self.normalize(input_path)
        chunk_outputs = self.chunk(normalization_outputs["json_path"])
        extraction_path = self.extract(chunk_outputs["chunk_path"])
        return {
            "normalized_markdown_path": normalization_outputs["markdown_path"],
            "normalized_json_path": normalization_outputs["json_path"],
            "guidance_path": chunk_outputs["guidance_path"],
            "chunk_path": chunk_outputs["chunk_path"],
            "extraction_path": str(extraction_path),
        }
