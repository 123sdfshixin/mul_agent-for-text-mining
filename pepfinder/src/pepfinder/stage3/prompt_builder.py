"""Prompt construction for controlled Stage III extraction."""

from __future__ import annotations

import json

from pepfinder.schemas.chunk import Chunk


class PromptBuilder:
    """Build structured prompts for a fine-tuned extraction model."""

    def build(self, chunk: Chunk) -> str:
        """Create a constrained JSON-only extraction prompt."""
        schema_example = [
            {
                "id": "record-1",
                "name": "PF-1",
                "sequence": "KWKLFKKIGAVLKVL",
                "length": 15,
                "source": "marine bacteria",
                "modification": None,
                "activity": "antimicrobial activity against E. coli",
                "target": "E. coli",
                "assay": "broth microdilution",
                "condition": "pH 7.4",
                "measurement_values": ["MIC 8 ug/mL"],
                "evidence_text": "PF-1 showed antimicrobial activity against E. coli with a MIC of 8 ug/mL under pH 7.4 conditions.",
                "source_chunk_id": chunk.chunk_id,
                "source_section": chunk.section_name,
                "source_document": "document_id",
                "metadata": {},
            }
        ]
        instructions = {
            "task": "Extract peptide knowledge from the scientific chunk.",
            "constraints": [
                "Return JSON only.",
                "Do not invent values that are not explicitly supported by the text.",
                "Return an empty list if no peptide evidence is present.",
                "Every record must preserve evidence_text and source_chunk_id.",
            ],
            "output_schema": {
                "type": "list[PeptideRecord]",
                "fields": list(schema_example[0].keys()),
            },
            "example": schema_example,
            "chunk_context": {
                "chunk_id": chunk.chunk_id,
                "section_name": chunk.section_name,
                "chunk_type": chunk.chunk_type,
                "score": chunk.score,
                "text": chunk.text,
            },
        }
        return json.dumps(instructions, ensure_ascii=False, indent=2)
