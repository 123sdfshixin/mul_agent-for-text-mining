"""Run an end-to-end demo of the PepFinder MVP."""

from pathlib import Path

from pepfinder.pipeline.orchestrator import PepFinderPipeline


def main() -> None:
    """Execute the pipeline on a bundled sample article."""
    pipeline = PepFinderPipeline()
    sample = Path("data/samples/sample_article_1.md")
    results = pipeline.run(sample)
    print("PepFinder demo complete.")
    for key, value in results.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
