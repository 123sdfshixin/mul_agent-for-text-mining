"""Artifact helpers for Stage II."""

from __future__ import annotations

from pathlib import Path

from pepfinder.schemas.stage2 import ChunkArtifact, GlobalStructureGuidance
from pepfinder.utils.io import ensure_dir, write_json


def write_stage2_artifacts(
    output_dir: Path,
    guidance: GlobalStructureGuidance,
    artifact: ChunkArtifact,
) -> dict[str, str]:
    """Write GS guidance and final chunk artifacts."""
    ensure_dir(output_dir)
    guidance_path = output_dir / f"{guidance.document_id}.guidance.json"
    chunk_path = output_dir / f"{guidance.document_id}.chunks.json"
    write_json(guidance_path, guidance.model_dump())
    write_json(chunk_path, artifact.model_dump())
    return {"guidance_path": str(guidance_path), "chunk_path": str(chunk_path)}
