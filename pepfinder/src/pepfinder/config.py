"""Project configuration models."""

from pathlib import Path

from pydantic import BaseModel, Field


class Settings(BaseModel):
    """Runtime settings for the PepFinder MVP."""

    output_dir: Path = Field(default=Path("output"))
    normalized_dirname: str = Field(default="normalized")
    chunks_dirname: str = Field(default="chunks")
    extraction_dirname: str = Field(default="extractions")

    @property
    def normalized_dir(self) -> Path:
        """Return the directory used for normalized documents."""
        return self.output_dir / self.normalized_dirname

    @property
    def chunks_dir(self) -> Path:
        """Return the directory used for chunk artifacts."""
        return self.output_dir / self.chunks_dirname

    @property
    def extraction_dir(self) -> Path:
        """Return the directory used for extraction artifacts."""
        return self.output_dir / self.extraction_dirname


DEFAULT_SETTINGS = Settings()
