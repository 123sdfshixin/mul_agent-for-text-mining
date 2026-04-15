You are now a senior Python architect and research engineering assistant. Please help me implement an undergraduate graduation project from scratch in VS Code. The project title is:

PepFinder: A Multi-Agent System for Mining Peptide Data from Massive Scientific Literature

Project goal:
Build a three-stage multi-agent system for scientific literature that can automatically extract structured peptide information from PDF/LaTeX research papers. The overall workflow is:
Stage I: Document format normalization
Stage II: Collaborative agent-driven hierarchical semantic chunking
Stage III: Targeted knowledge extraction from information-dense segments

Please implement this strictly according to the requirements of being runnable, extensible, and suitable for an undergraduate thesis project. Do not build an overly complex industrial-scale system at the beginning. Instead, first create an MVP version with a clear structure, reasonable modularization, and convenient extensibility toward real LLMs and fine-tuned models in the future.

====================
I. Project Background and Design Requirements
====================

1. Core project idea
PepFinder does not let a single model process the entire paper directly. Instead, it adopts a three-stage architecture:
- Stage I: Convert documents such as PDF and LaTeX into unified Markdown-structured text, preserving section headings, tables, figure captions, formulas, and citation relations as much as possible.
- Stage II: Two collaborative agents perform hierarchical semantic chunking:
  - GlobalStructureAgent: performs coarse-grained full-document structural analysis
  - FineGrainedChunkingAgent: generates semantically complete, self-contained, high-value chunks
- Stage III: Perform knowledge extraction on the selected information-dense chunks and output structured peptide information.

2. Target information to extract
The system should ultimately support extraction of the following fields. First build the schema and interfaces; the first version does not need to recognize everything perfectly:
- peptide_name
- peptide_sequence
- modification
- source_organism_or_origin
- assay_or_experiment
- target
- activity_value
- activity_unit
- condition
- evidence_text
- source_section
- source_document

3. Development principles
- Use Python
- Adopt a clear src-layout
- Each module should have a single responsibility
- All key modules should be replaceable and extensible
- By default, the system should not depend on real commercial APIs in order to run
- If LLMs are involved, design an adapter/interface first, and provide a mock or rule-based fallback implementation
- The code must be runnable; do not provide pseudocode only
- Prefer writing complete files rather than scattered code snippets
- After each stage is completed, provide run commands and test methods

====================
II. Project Structure Requirements
====================

Please initialize the project according to the following structure. Minor adjustments are allowed if needed for implementation, but the project must remain clean and organized:

pepfinder/
  README.md
  requirements.txt
  requirements-dev.txt
  .gitignore
  pyproject.toml
  .env.example
  data/
    samples/
  docs/
  scripts/
  src/
    pepfinder/
      __init__.py
      config.py
      schemas/
      utils/
      agents/
      stage1/
      stage2/
      stage3/
      pipeline/
      cli.py
  tests/

Suggested directory responsibilities:
- schemas/: pydantic data structures
- agents/: abstract base agent classes and concrete agents
- stage1/: document conversion, normalization, intermediate representation
- stage2/: global structure analysis, chunking, chunk selection
- stage3/: extractors, LLM adapter, structured output
- pipeline/: overall workflow orchestration
- cli.py: command-line entry point
- scripts/: demo and experiment scripts
- tests/: pytest tests

====================
III. Functional Implementation Requirements
====================

Please implement in the following order. Do not skip steps:

### Step 1: Initialize the project skeleton
Please generate first:
- complete directory structure
- README.md
- requirements.txt
- requirements-dev.txt
- pyproject.toml
- basic .gitignore
- a minimal runnable CLI

The CLI must support at least these commands:
- pepfinder normalize <input_file>
- pepfinder chunk <normalized_file>
- pepfinder extract <chunk_file>
- pepfinder run <input_file>

### Step 2: Implement Stage I
Implement DocumentConversionAndNormalizationAgent with the following requirements:
- Input: pdf / tex / md / txt
- Output: unified intermediate representation UnifiedDocument
- The first version does not need fully sophisticated PDF parsing, but the interface design must be preserved
- Fully support txt / md first
- PDF / tex may initially use placeholder implementations or basic text extraction implementations
- UnifiedDocument must include at least:
  - document_id
  - source_path
  - raw_text
  - normalized_text
  - sections
  - tables
  - figures
  - metadata

Also implement:
- section splitter
- markdown-like normalized output
- save to json file

### Step 3: Implement Stage II
Implement two agents:
1. GlobalStructureAgent
- Input: UnifiedDocument
- Output: global structure analysis results
- Mark possible information-dense regions
- Provide section-level hints

2. FineGrainedChunkingAgent
- Generate chunks according to the full-document structure and hints
- Each chunk must include:
  - chunk_id
  - text
  - section_name
  - source_span
  - score
  - rationale

Requirements:
- The first version may use rules + heuristics
- Support paragraph-level chunking
- Support combination strategies such as “heading + paragraph” and “table + caption”
- Output structured chunk json

### Step 4: Implement Stage III
Implement the knowledge extraction module:
- Define BaseExtractor
- Define MockLLMExtractor or RuleBasedPeptideExtractor
- Reserve an interface for FineTunedLLMExtractor
- Input: chunk
- Output: list of PeptideRecord

The first version may use the following extraction strategy:
- regular expressions + keywords + simple pattern matching
- basic extraction of peptide sequences, activity values, units, and conditions
- return evidence_text and source_section

### Step 5: Implement the Pipeline Orchestrator
Implement PepFinderPipeline:
- Connect Stage I / II / III in sequence
- Support run(input_path)
- Save intermediate results and final extraction results
- Include logging output
- Include basic error handling

### Step 6: Tests and examples
Please also generate:
- at least 3 sample files
- pytest tests
- one demo script
- installation and usage instructions in README

====================
IV. Code Style Requirements
====================

- Use Python 3.11
- 4-space indentation
- Follow PEP 8
- Use snake_case for files, functions, and variables
- Use PascalCase for classes
- Prefer dataclass or pydantic where appropriate
- Add concise comments for key logic
- All public functions must have docstrings
- Do not put all logic into a single file
- Do not use too many fancy frameworks
- Prioritize readability, modularity, and testability

====================
V. Implementation Strategy Requirements
====================

Please respond in a step-by-step implementation style rather than giving only conceptual explanations at once.

In each round, work in the following format:
1. First explain what will be implemented in this round
2. Provide the file tree to be created/modified
3. Output the complete code
4. Explain how to run it
5. Suggest the next step

If there are uncertainties in implementation:
- Do not keep asking repeated clarification questions
- Make reasonable default assumptions first
- Explicitly state those assumptions

If some advanced capability cannot be realistically implemented for now:
- Design the interface first
- Then provide a mock implementation
- Do not omit the architectural layer

====================
VI. Special Requirements
====================

1. This is an undergraduate thesis project, so the coding style should reflect clear structure, ease of thesis description, and ease of demonstration.
2. Prioritize building the system first, then gradually improve its performance.
3. All module names should be as consistent as possible with the thesis architecture, for example:
- DocumentConversionAndNormalizationAgent
- GlobalStructureAgent
- FineGrainedChunkingAgent
- DomainExtractor
- PepFinderPipeline
4. Do not introduce a complex database for now; storing first-version results in json is sufficient.
5. Prioritize generating a truly runnable end-to-end demo.
6. Do not only provide ideas; directly start creating the project code.

Now begin:
First provide the implementation plan for the first iteration of the whole project, and generate the complete file contents required to initialize the project skeleton.




**Stage1版本的prompt**
Now we move to the next round.

In this round, we need to implement **Stage I** of the PepFinder project. The goal of this stage is to build an agent that can automatically convert scientific documents from heterogeneous formats into a unified **Markdown-based intermediate representation**.

## Main objective
Please implement a new module for **Document Conversion and Normalization**.

The core component should be:

- `DocumentConversionAndNormalizationAgent`

Its responsibility is to take input files in formats such as:

- PDF
- DOC / DOCX
- TXT
- LaTeX / TEX

and convert them into a normalized Markdown-style output that preserves as much useful document structure as possible.

## Important context
I have already placed the **Marker project** inside the project folder.  
Please inspect the Marker project, understand its pipeline, and reuse or adapt it where appropriate for our implementation.  
Do not copy blindly. Instead, integrate it into our PepFinder architecture in a clean and modular way.

## Requirements for Stage I
Please implement this stage with the following goals:

1. **Format conversion**
   - Support at least `.md` and `.txt` properly in the first version.
   - For `.pdf`, integrate the Marker-based pipeline if possible.
   - For `.doc/.docx` and `.tex`, provide either a working basic implementation or a clean placeholder interface if full support is not yet practical.

2. **Unified output**
   - Convert all supported input files into a unified Markdown-like text format.
   - Preserve document structure as much as possible, including:
     - title
     - section headings
     - subsection headings
     - paragraphs
     - tables
     - figure captions
     - formulas / equation blocks if available
     - references to figures/tables if recoverable

3. **Structured intermediate representation**
   - In addition to Markdown text, produce a structured Python object such as `UnifiedDocument`.
   - This object should contain at least:
     - `document_id`
     - `source_path`
     - `source_format`
     - `raw_text`
     - `normalized_text`
     - `sections`
     - `tables`
     - `figures`
     - `metadata`

4. **JSON artifact**
   - Save the normalized result as JSON so later stages can consume it.
   - Also save the Markdown output to disk.

5. **Integration with current project**
   - Implement this inside our existing `src/pepfinder/` project layout.
   - The Stage I code should live in something like:
     - `src/pepfinder/stage1/`
   - Keep interfaces stable and easy to extend later.

6. **CLI integration**
   - Make sure the command below works after implementation:
     - `python -m pepfinder.cli normalize <input_file>`
   - The command should generate normalized Markdown and structured JSON output.

## Design expectations
Please do **not** build this as a messy script.
I want a clean thesis-style implementation with:
- clear module boundaries
- reusable utility functions
- stable interfaces
- readable code
- room for future extension toward more advanced parsing

## Suggested implementation ideas
You may split Stage I into submodules such as:
- file loader / format detector
- marker adapter
- markdown normalizer
- section splitter
- unified document builder
- artifact writer

If Marker already has useful conversion steps, wrap them through an adapter layer rather than tightly coupling our pipeline to Marker internals.

## Output expectations
Please work in the same step-by-step style as before.

For this round, provide:
1. a short implementation plan
2. the files that need to be created or modified
3. the complete code for all relevant files
4. how to install/run/test Stage I
5. the expected output files
6. the suggested next step for Stage II

## Additional note
If some formats cannot yet be fully supported, that is acceptable for this round, but you must:
- design the interface properly
- provide fallback behavior
- clearly mark TODO points
- keep the pipeline runnable

Now begin with Stage I implementation."



Now we move to Stage II implementation.

In this stage, we need to build a **two-agent collaborative system for semantic-aware document chunking**. This stage should take the normalized output from Stage I and produce structured, semantically meaningful chunks for Stage III extraction.

## Overall Goal
Design and implement two cooperating agents:

1. Global Structure Agent (GS Agent)
2. Fine-grained Chunking Agent

These agents should not work independently — the Fine-grained agent must be guided by the GS Agent.

---

## 1. Global Structure Agent (GS Agent)

### Objective
The GS Agent performs **coarse-grained, document-level structural understanding**.

### Responsibilities
- Read the entire normalized document (Markdown or structured representation)
- Capture **global semantic context**
- Identify **information-dense regions**, especially those likely containing peptide-related data
- Detect and map:
  - sections and subsections
  - tables and nearby text
  - figure captions and their referenced paragraphs
- Build a **global semantic segmentation**

### Output
The GS Agent should output a structured object, e.g.:

- list of sections with hierarchy
- list of candidate "important regions"
- mapping between:
  - figure captions ↔ related paragraphs
  - tables ↔ surrounding explanations
- coarse segmentation boundaries

This output should serve as **guidance for the next agent**, not final chunks.

---

## 2. Fine-grained Chunking Agent

### Objective
Perform **semantic-aware fine-grained chunking** based on GS Agent guidance.

### Key idea
Do NOT split text using fixed token length or naive sliding windows.

Instead:
- produce **semantically complete chunks**
- preserve logical units of scientific meaning

### Responsibilities
- Take GS Agent output + normalized document
- Focus only on **information-dense regions**
- Split content into meaningful units such as:
  - single paragraphs
  - paragraph groups
  - table + explanation
  - equation + surrounding interpretation
  - figure caption + referenced text

### Output
Produce a list of structured chunks, each containing:
- chunk_id
- text
- source section
- chunk type (paragraph / table / figure / mixed)
- position in document
- optional metadata (e.g., related figure/table id)

---

## Design Requirements

- Place implementation under:
  - `src/pepfinder/stage2/`
- Keep GS Agent and Chunking Agent as **separate modules**
- Define clean interfaces between:
  - Stage I → GS Agent
  - GS Agent → Chunking Agent
- Ensure outputs are saved as JSON artifacts

---

## Important Constraints

- Peptide-related information is **not localized**
  → must consider cross-section relationships
- Avoid naive chunking
- Preserve **semantic completeness and traceability**
- Ensure chunks can be traced back to original document positions

---

## CLI Integration

Extend the CLI so the following command works:
