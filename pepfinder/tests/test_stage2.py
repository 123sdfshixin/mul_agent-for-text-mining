"""Tests for Stage II semantic chunking."""

import json
from pathlib import Path

from pepfinder.pipeline.orchestrator import PepFinderPipeline


def test_chunk_stage_generates_guidance_and_semantic_chunks(tmp_path: Path) -> None:
    """Stage II should emit GS guidance plus structured chunk artifacts."""
    sample_path = tmp_path / "semantic.md"
    sample_path.write_text(
        "\n".join(
            [
                "# Study",
                "",
                "## Results",
                "",
                "Peptide PF-2 showed activity against E. coli with MIC 4 ug/mL.",
                "",
                "Figure 1: Structural overview of PF-2.",
                "",
                "As shown in Figure 1, the peptide sequence was KWKLFKKIGAVL.",
                "",
                "Table 1: Activity summary",
                "| Target | Value |",
                "| --- | --- |",
                "| E. coli | 4 ug/mL |",
                "",
                "Table 1 summarizes the antimicrobial assay results.",
            ]
        ),
        encoding="utf-8",
    )

    pipeline = PepFinderPipeline()
    pipeline.settings.output_dir = tmp_path / "output"

    normalize_outputs = pipeline.normalize(sample_path)
    chunk_outputs = pipeline.chunk(normalize_outputs["json_path"])

    guidance_payload = json.loads(Path(chunk_outputs["guidance_path"]).read_text(encoding="utf-8"))
    chunk_payload = json.loads(Path(chunk_outputs["chunk_path"]).read_text(encoding="utf-8"))

    assert guidance_payload["important_regions"]
    assert chunk_payload["chunks"]
    assert any(chunk["chunk_type"] in {"mixed", "paragraph", "figure_caption", "table"} for chunk in chunk_payload["chunks"])
    assert "guidance" in chunk_payload
