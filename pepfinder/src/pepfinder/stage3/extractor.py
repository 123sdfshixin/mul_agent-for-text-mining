"""Backward-compatible exports for Stage III extraction."""

from pepfinder.stage3.extraction_agent import (
    BaseExtractor,
    FineTunedLLMExtractor,
    KnowledgeExtractionAgent,
    MockFineTunedLLMBackend,
)

__all__ = [
    "BaseExtractor",
    "KnowledgeExtractionAgent",
    "MockFineTunedLLMBackend",
    "FineTunedLLMExtractor",
]
