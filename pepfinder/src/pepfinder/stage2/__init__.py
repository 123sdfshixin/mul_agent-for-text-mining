"""Stage II: structure analysis and chunk generation."""

from pepfinder.stage2.fine_grained import FineGrainedChunkingAgent
from pepfinder.stage2.global_structure import GlobalStructureAgent

__all__ = ["GlobalStructureAgent", "FineGrainedChunkingAgent"]
