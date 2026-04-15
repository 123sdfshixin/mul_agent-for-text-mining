# PepFinder

PepFinder is an MVP multi-agent system for mining peptide information from scientific literature. The current version includes a runnable Stage I normalization module and a GS-guided Stage II semantic chunking module, plus replaceable architectural layers for:

1. Stage I: document conversion and normalization
2. Stage II: collaborative hierarchical semantic chunking
3. Stage III: targeted peptide knowledge extraction

The project is intentionally thesis-friendly: modular, readable, runnable locally, and designed for later extension toward stronger document parsers and LLM-backed extraction.

## Project Structure

```text
pepfinder/
  data/
    samples/
  docs/
  scripts/
  src/
    pepfinder/
      agents/
      pipeline/
      schemas/
      stage1/
      stage2/
      stage3/
      utils/
      cli.py
      config.py
  tests/
```

## Installation

1. Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install runtime dependencies:

```bash
pip install -r requirements.txt
pip install -e .
```

3. Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

## CLI Usage

From the `pepfinder/` directory, run:

```bash
python -m pepfinder.cli normalize data/samples/sample_article_1.md
python -m pepfinder.cli chunk output/normalized/sample_article_1.normalized.json
python -m pepfinder.cli extract output/chunks/sample_article_1.chunks.json
python -m pepfinder.cli run data/samples/sample_article_1.md
```

If installed as a package, the console command is also available:

```bash
pepfinder normalize data/samples/sample_article_1.md
```

Without editable installation, you can also run with:

```bash
PYTHONPATH=src python -m pepfinder.cli run data/samples/sample_article_1.md
```

The repository also includes a lightweight compatibility package at [pepfinder/__init__.py](/home/xinyushi/multi_agent/pepfinder/pepfinder/__init__.py), so running `python -m pepfinder.cli ...` from the project root works even before `pip install -e .`.

## Stage I Support

Stage I currently supports:

- `md`: native Markdown preservation
- `txt`: paragraph-based Markdown normalization
- `tex`: basic LaTeX section-to-Markdown conversion
- `pdf`: local Marker adapter when Marker dependencies are available, otherwise readable fallback output
- `docx`: lightweight XML-based extraction
- `doc`: placeholder conversion with a clear TODO path

The `normalize` command writes two artifacts under `output/normalized/`:

- `<document_id>.normalized.md`
- `<document_id>.normalized.json`

The JSON artifact contains the `UnifiedDocument` representation with:

- `document_id`
- `source_path`
- `source_format`
- `title`
- `raw_text`
- `normalized_text`
- `sections`
- `tables`
- `figures`
- `metadata`

## Stage II Support

Stage II is implemented as a two-agent collaboration:

1. `GlobalStructureAgent`
2. `FineGrainedChunkingAgent`

The `chunk` command reads a Stage I normalized JSON file and writes:

- `output/chunks/<document_id>.guidance.json`
- `output/chunks/<document_id>.chunks.json`

The GS guidance artifact includes:

- section hierarchy summaries
- important regions
- coarse boundaries
- figure-to-region links
- table-to-region links

The chunk artifact includes:

- `chunk_id`
- `text`
- `section_name`
- `chunk_type`
- `position`
- `source_span`
- `score`
- `rationale`
- `metadata`

## Stage III Support

Stage III is implemented as a selective extraction pipeline:

1. `ExtractionController`
2. `KnowledgeExtractionAgent`
3. `PromptBuilder`
4. `OutputValidator`
5. `ResultAggregator`

The `extract` command reads a Stage II chunk artifact and writes:

- `output/extractions/<document_id>.extractions.json`

The extraction dataset includes:

- `document_id`
- `source_chunk_file`
- `selected_chunk_ids`
- `records`
- `metadata`

Each `PeptideRecord` includes:

- `id`
- `name`
- `sequence`
- `length`
- `source`
- `modification`
- `activity`
- `target`
- `assay`
- `condition`
- `measurement_values`
- `evidence_text`
- `source_chunk_id`
- `source_section`
- `source_document`

## Demo Script

Run the end-to-end demo:

```bash
python scripts/run_demo.py
```

## Test

Run the test suite:

```bash
pytest
```

## Current Assumptions

- `txt` and `md` are fully supported in the MVP.
- `tex` uses a basic but runnable converter.
- `pdf` uses Marker through an adapter layer and degrades gracefully if its runtime dependencies are missing.
- `docx` is lightweight and intended for thesis demos rather than full-fidelity office parsing.
- Stage III uses a mock fine-tuned backend by default because no real LLM API is required for the MVP.
- Advanced improvements such as few-shot prompting, retrieval augmentation, and cross-chunk reasoning are left as TODOs.

## Next Iteration

The next implementation round should focus on improving extraction quality:

- stronger multi-record extraction in a single chunk
- better source organism and modification parsing
- cross-chunk evidence merging
- integration with a real fine-tuned LLM backend
