"""Knowledge extraction agent and backend abstractions for Stage III."""

from __future__ import annotations

from abc import ABC, abstractmethod
import json
import re

from pepfinder.schemas.chunk import Chunk
from pepfinder.schemas.extraction import PeptideRecord
from pepfinder.stage3.output_validator import OutputValidator
from pepfinder.stage3.prompt_builder import PromptBuilder


NAME_PATTERN = re.compile(r"\b(?:peptide\s+)?([A-Z]{1,4}[-]?\d{1,3}|[A-Z]{2,6}-\d+)\b")
SEQUENCE_PATTERN = re.compile(r"\b([ACDEFGHIKLMNPQRSTVWY]{6,})\b")
MEASUREMENT_PATTERN = re.compile(
    r"\b(?:(MIC|IC50|EC50)\s*(?:of\s*)?)?(\d+(?:\.\d+)?)\s?(uM|µM|ug/mL|mg/L|nM|mM)\b",
    re.IGNORECASE,
)
CONDITION_PATTERN = re.compile(r"\b(pH\s*\d+(?:\.\d+)?|[A-Za-z]+\s+buffer|saline buffer)\b", re.IGNORECASE)
SOURCE_PATTERN = re.compile(r"\b(?:from|isolated from|derived from)\s+([A-Za-z][A-Za-z0-9 ._-]{2,60})", re.IGNORECASE)
ASSAY_PATTERN = re.compile(r"\b(broth microdilution|microdilution|antimicrobial assay|binding assay)\b", re.IGNORECASE)
MODIFICATION_PATTERN = re.compile(r"\b(amidated|acetylated|phosphorylated|methylated|cyclized)\b", re.IGNORECASE)


class BaseExtractor(ABC):
    """Abstract extractor interface."""

    @abstractmethod
    def extract(self, chunk: Chunk, source_document: str) -> list[PeptideRecord]:
        """Extract structured records from a chunk."""


class BaseLLMBackend(ABC):
    """Abstract backend for real or mock fine-tuned extraction models."""

    @abstractmethod
    def generate(self, prompt: str, chunk: Chunk, source_document: str) -> str:
        """Generate JSON output for a chunk."""


class MockFineTunedLLMBackend(BaseLLMBackend):
    """Rule-based backend that mimics a constrained fine-tuned LLM response."""

    def generate(self, prompt: str, chunk: Chunk, source_document: str) -> str:
        """Return a JSON string with extracted peptide records."""
        _ = prompt
        text = chunk.text
        names = _extract_names(text)
        sequences = SEQUENCE_PATTERN.findall(text)
        measurements = _extract_measurements(text)
        target = _extract_target(text)
        source = _extract_first(SOURCE_PATTERN, text)
        assay = _extract_first(ASSAY_PATTERN, text)
        modification = _extract_first(MODIFICATION_PATTERN, text)
        condition = _extract_first(CONDITION_PATTERN, text)
        activity = _infer_activity(text, target, measurements)

        candidates = max(len(names), len(sequences), 1)
        payload: list[dict] = []
        for index in range(candidates):
            name = names[index] if index < len(names) else (names[0] if names else None)
            sequence = sequences[index] if index < len(sequences) else (sequences[0] if sequences else None)
            if not name and not sequence and not measurements:
                continue
            evidence_text = _select_evidence_sentence(text, sequence or name or (measurements[0] if measurements else ""))
            payload.append(
                {
                    "id": f"{chunk.chunk_id}-record-{index + 1}",
                    "name": name,
                    "sequence": sequence,
                    "length": len(sequence) if sequence else None,
                    "source": source,
                    "modification": modification,
                    "activity": activity,
                    "target": target,
                    "assay": assay,
                    "condition": condition,
                    "measurement_values": measurements,
                    "evidence_text": evidence_text,
                    "source_chunk_id": chunk.chunk_id,
                    "source_section": chunk.section_name,
                    "source_document": source_document,
                    "metadata": {"backend": "mock_fine_tuned_llm"},
                }
            )
        return json.dumps(payload, ensure_ascii=False)


class KnowledgeExtractionAgent(BaseExtractor):
    """Run prompt-controlled extraction for a single semantic chunk."""

    def __init__(
        self,
        backend: BaseLLMBackend | None = None,
        prompt_builder: PromptBuilder | None = None,
        validator: OutputValidator | None = None,
    ) -> None:
        """Initialize extraction dependencies."""
        self.backend = backend or MockFineTunedLLMBackend()
        self.prompt_builder = prompt_builder or PromptBuilder()
        self.validator = validator or OutputValidator()

    def extract(self, chunk: Chunk, source_document: str) -> list[PeptideRecord]:
        """Build a prompt, call the backend, and validate structured output."""
        prompt = self.prompt_builder.build(chunk)
        raw_output = self.backend.generate(prompt, chunk, source_document)
        return self.validator.validate(raw_output, chunk, source_document)


class FineTunedLLMExtractor(KnowledgeExtractionAgent):
    """Reserved interface for a future true fine-tuned LLM backend."""

    def __init__(self) -> None:
        """Raise until a real fine-tuned backend is integrated."""
        raise NotImplementedError("FineTunedLLMExtractor is reserved for future model integration.")


def _extract_names(text: str) -> list[str]:
    """Extract plausible peptide names from text."""
    names: list[str] = []
    for match in NAME_PATTERN.finditer(text):
        candidate = match.group(1)
        if candidate.upper() in {"MIC", "IC50", "EC50"}:
            continue
        names.append(candidate)
    return list(dict.fromkeys(names))


def _extract_measurements(text: str) -> list[str]:
    """Extract normalized measurement strings."""
    labeled: list[str] = []
    unlabeled: list[str] = []
    for label, value, unit in MEASUREMENT_PATTERN.findall(text):
        normalized = f"{value} {unit}".strip()
        if label:
            labeled.append(f"{label.upper()} {normalized}")
        else:
            unlabeled.append(normalized)
    labeled = list(dict.fromkeys(labeled))
    labeled_values = {item.split(" ", 1)[1] for item in labeled}
    unlabeled = [item for item in dict.fromkeys(unlabeled) if item not in labeled_values]
    return labeled + unlabeled


def _extract_first(pattern: re.Pattern[str], text: str) -> str | None:
    """Extract the first regex group match if present."""
    match = pattern.search(text)
    if not match:
        return None
    return match.group(1).strip()


def _extract_target(text: str) -> str | None:
    """Extract a likely biological target mentioned after 'against'."""
    match = re.search(r"\bagainst\s+(.{1,80})", text, re.IGNORECASE)
    if not match:
        return None
    candidate = match.group(1)
    stop_match = re.search(r"\bwith\b|\bunder\b|\bat\b|\bvia\b|\busing\b|[,;]", candidate, re.IGNORECASE)
    if stop_match:
        candidate = candidate[: stop_match.start()]
    candidate = candidate.strip().rstrip(".")
    candidate = " ".join(candidate.split()).strip()
    return candidate or None


def _infer_activity(text: str, target: str | None, measurements: list[str]) -> str | None:
    """Infer a concise activity description from chunk text."""
    lowered = text.lower()
    if "antimicrobial" in lowered and target:
        return f"antimicrobial activity against {target}"
    if "activity" in lowered and target:
        return f"activity against {target}"
    if measurements:
        return f"reported measurement: {measurements[0]}"
    return None


def _select_evidence_sentence(text: str, anchor: str) -> str:
    """Select a compact evidence sentence anchored to a key signal."""
    cleaned = "\n".join(line for line in text.splitlines() if not line.strip().startswith("#")).strip()
    sentences = re.split(r"(?<=[.!?])\s+", cleaned)
    for sentence in sentences:
        if anchor and anchor in sentence:
            return sentence.strip()
    return sentences[0].strip() if sentences else cleaned
