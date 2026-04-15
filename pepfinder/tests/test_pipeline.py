"""Basic pipeline tests."""

import json
from pathlib import Path

from pepfinder.pipeline.orchestrator import PepFinderPipeline


def test_pipeline_run_creates_expected_artifacts(tmp_path: Path) -> None:
    """Run the MVP pipeline end to end on a small markdown input."""
    sample_path = tmp_path / "sample.md"
    sample_path.write_text(
        "# Results\n\nPeptide P-1 had sequence KWKLFKKI and MIC 8 ug/mL.\n",
        encoding="utf-8",
    )

    pipeline = PepFinderPipeline()
    original_output = pipeline.settings.output_dir
    pipeline.settings.output_dir = tmp_path / "output"

    results = pipeline.run(sample_path)

    normalized_json_path = Path(results["normalized_json_path"])
    normalized_markdown_path = Path(results["normalized_markdown_path"])
    guidance_path = Path(results["guidance_path"])
    chunk_path = Path(results["chunk_path"])
    extraction_path = Path(results["extraction_path"])

    assert normalized_json_path.exists()
    assert normalized_markdown_path.exists()
    assert guidance_path.exists()
    assert chunk_path.exists()
    assert extraction_path.exists()

    payload = json.loads(extraction_path.read_text(encoding="utf-8"))
    assert payload["document_id"] == "sample"
    assert payload["records"]
    assert payload["selected_chunk_ids"]

    pipeline.settings.output_dir = original_output
