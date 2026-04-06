# Repository Guidelines

## Project Structure & Module Organization
This repository is currently a fresh workspace for `Text_mining` work. Keep the layout simple and consistent as code is added:

- `src/`: core application code, agent logic, and reusable utilities
- `tests/`: unit and integration tests mirroring `src/`
- `data/`: small local sample datasets only; keep raw or large datasets out of git
- `scripts/`: one-off development or preprocessing scripts
- `docs/`: notes, design decisions, and usage examples

Example structure:
```text
src/text_mining/
tests/test_pipeline.py
scripts/run_demo.py
```

## Build, Test, and Development Commands
Prefer a Python-based workflow unless the project is intentionally changed.

- `python -m venv .venv && source .venv/bin/activate`: create and activate a local environment
- `pip install -r requirements.txt`: install runtime dependencies
- `pip install -r requirements-dev.txt`: install linting and test tools
- `pytest`: run the full test suite
- `python -m src.text_mining`: run the main package entry point if provided

If a `Makefile` is added later, keep aliases like `make test` and `make lint` aligned with the commands above.

## Coding Style & Naming Conventions
Use 4-space indentation and follow PEP 8 for Python code. Prefer:

- `snake_case` for files, functions, and variables
- `PascalCase` for classes
- clear module names such as `entity_extractor.py` or `agent_router.py`

Format with `black` and lint with `ruff` if those tools are introduced. Keep functions focused and avoid mixing data loading, modeling, and evaluation in one file.

## Testing Guidelines
Use `pytest` for all new tests. Name test files `test_*.py` and test functions `test_<behavior>()`. Mirror source paths where possible, for example `src/text_mining/pipeline.py` -> `tests/test_pipeline.py`.

Add tests for parsing, preprocessing, and agent decision logic. New features should include at least one happy-path test and one failure or edge-case test.

## Commit & Pull Request Guidelines
This repository does not yet have git history, so use short imperative commit messages such as `Add document parser` or `Create agent routing scaffold`.

For pull requests, include:

- a brief summary of the change
- test evidence, for example `pytest`
- linked issue or task ID if one exists
- sample input/output when behavior changes materially

## Security & Configuration Tips
Do not commit API keys, private corpora, or large generated artifacts. Store secrets in `.env` and add local-only data paths to `.gitignore`.
