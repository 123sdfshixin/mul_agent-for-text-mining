"""Tests for Stage I document normalization."""

import json
from pathlib import Path

from pepfinder.pipeline.orchestrator import PepFinderPipeline
from pepfinder.stage1.normalizer import DocumentConversionAndNormalizationAgent


def test_markdown_normalization_parses_structure() -> None:
    """Normalize Markdown and preserve structural content."""
    agent = DocumentConversionAndNormalizationAgent()
    sample_path = Path("data/samples/sample_article_1.md")

    document = agent.run(sample_path)

    assert document.source_format == "md"
    assert document.title == "Title"
    assert len(document.sections) >= 2
    assert "PF-1" in document.normalized_text


def test_tex_conversion_creates_markdown_headings(tmp_path: Path) -> None:
    """Convert LaTeX section commands into Markdown headings."""
    tex_path = tmp_path / "paper.tex"
    tex_path.write_text(
        "\\title{Peptide Study}\n\\section{Methods}\nSequence was KWKLFKKI.\n",
        encoding="utf-8",
    )

    agent = DocumentConversionAndNormalizationAgent()
    document = agent.run(tex_path)

    assert document.source_format == "tex"
    assert document.title == "Peptide Study"
    assert any(section.heading == "Methods" for section in document.sections)


def test_normalize_command_writes_json_and_markdown(tmp_path: Path) -> None:
    """Stage I should emit both JSON and Markdown artifacts."""
    sample_path = tmp_path / "sample.txt"
    sample_path.write_text("Peptide Alpha has sequence KWKLFKKI.", encoding="utf-8")

    pipeline = PepFinderPipeline()
    original_output = pipeline.settings.output_dir
    pipeline.settings.output_dir = tmp_path / "output"

    outputs = pipeline.normalize(sample_path)
    json_path = Path(outputs["json_path"])
    markdown_path = Path(outputs["markdown_path"])

    assert json_path.exists()
    assert markdown_path.exists()

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["source_format"] == "txt"
    assert "normalized_text" in payload

    pipeline.settings.output_dir = original_output
