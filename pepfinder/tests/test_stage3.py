"""Tests for Stage III targeted extraction."""

import json
from pathlib import Path

from pepfinder.pipeline.orchestrator import PepFinderPipeline


def test_extract_stage_generates_traceable_dataset(tmp_path: Path) -> None:
    """Stage III should produce structured, traceable peptide records."""
    sample_path = tmp_path / "extractable.md"
    sample_path.write_text(
        "\n".join(
            [
                "# Study",
                "",
                "## Results",
                "",
                "Peptide PF-2 showed antimicrobial activity against E. coli with MIC 4 ug/mL under pH 7.4.",
                "",
                "The peptide sequence was KWKLFKKIGAVL and the assay was broth microdilution.",
                "",
                "PF-2 was isolated from marine bacteria.",
            ]
        ),
        encoding="utf-8",
    )

    pipeline = PepFinderPipeline()
    pipeline.settings.output_dir = tmp_path / "output"

    normalize_outputs = pipeline.normalize(sample_path)
    chunk_outputs = pipeline.chunk(normalize_outputs["json_path"])
    extraction_path = pipeline.extract(chunk_outputs["chunk_path"])

    payload = json.loads(Path(extraction_path).read_text(encoding="utf-8"))
    assert payload["document_id"] == "extractable"
    assert payload["records"]

    record = payload["records"][0]
    assert record["source_chunk_id"]
    assert record["evidence_text"]
    assert record["sequence"] == "KWKLFKKIGAVL"
    assert record["length"] == 12

