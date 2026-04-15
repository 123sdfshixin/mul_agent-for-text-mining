"""Command-line interface for PepFinder."""

from __future__ import annotations

import argparse
import json

from pepfinder.pipeline.orchestrator import PepFinderPipeline


def build_parser() -> argparse.ArgumentParser:
    """Build the top-level CLI parser."""
    parser = argparse.ArgumentParser(prog="pepfinder", description="PepFinder MVP CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    normalize_parser = subparsers.add_parser("normalize", help="Normalize an input document")
    normalize_parser.add_argument("input_file")

    chunk_parser = subparsers.add_parser("chunk", help="Chunk a normalized document JSON")
    chunk_parser.add_argument("normalized_file")

    extract_parser = subparsers.add_parser("extract", help="Extract records from a chunk JSON")
    extract_parser.add_argument("chunk_file")

    run_parser = subparsers.add_parser("run", help="Run the full pipeline")
    run_parser.add_argument("input_file")

    return parser


def main() -> None:
    """Run the PepFinder command-line interface."""
    parser = build_parser()
    args = parser.parse_args()
    pipeline = PepFinderPipeline()

    if args.command == "normalize":
        result = pipeline.normalize(args.input_file)
    elif args.command == "chunk":
        result = pipeline.chunk(args.normalized_file)
    elif args.command == "extract":
        result = pipeline.extract(args.chunk_file)
    elif args.command == "run":
        result = pipeline.run(args.input_file)
    else:
        parser.error(f"Unknown command: {args.command}")
        return

    print(json.dumps(result if isinstance(result, dict) else {"output_path": str(result)}, indent=2))


if __name__ == "__main__":
    main()
