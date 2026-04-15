"""Optional Marker-backed PDF conversion adapter."""

from __future__ import annotations

from pathlib import Path
import sys

from pepfinder.stage1.base import BaseDocumentConverter, ConversionResult


class MarkerPdfConverter(BaseDocumentConverter):
    """Use the local Marker project when available, otherwise degrade gracefully."""

    def __init__(self) -> None:
        """Initialize the adapter with the expected local Marker path."""
        self.marker_root = Path(__file__).resolve().parents[5] / "marker"

    def convert(self, input_path: Path) -> ConversionResult:
        """Convert a PDF via Marker if dependencies are available."""
        try:
            rendered = self._render_with_marker(input_path)
        except Exception as exc:  # noqa: BLE001
            placeholder = (
                f"# {input_path.stem}\n\n"
                "PDF conversion fallback was used because Marker could not run in the current "
                f"environment.\n\nReason: {exc}"
            )
            return ConversionResult(
                raw_text=placeholder,
                markdown_text=placeholder,
                metadata={
                    "conversion_backend": "marker_fallback",
                    "marker_available": False,
                    "fallback_reason": str(exc),
                },
            )

        markdown_text = rendered["markdown_text"]
        metadata = rendered["metadata"]
        return ConversionResult(
            raw_text=markdown_text,
            markdown_text=markdown_text,
            metadata={
                "conversion_backend": "marker_pdf",
                "marker_available": True,
                "marker_metadata": metadata,
                "page_count": rendered.get("page_count"),
                "image_count": rendered.get("image_count", 0),
            },
        )

    def _render_with_marker(self, input_path: Path) -> dict:
        """Run the local Marker Python API and return rendered content."""
        if not self.marker_root.exists():
            raise FileNotFoundError(f"Marker project not found at {self.marker_root}")

        marker_root_str = str(self.marker_root)
        if marker_root_str not in sys.path:
            sys.path.insert(0, marker_root_str)

        from marker.converters.pdf import PdfConverter
        from marker.models import create_model_dict
        from marker.output import text_from_rendered

        converter = PdfConverter(artifact_dict=create_model_dict())
        rendered = converter(str(input_path))
        markdown_text, _, images = text_from_rendered(rendered)
        return {
            "markdown_text": markdown_text,
            "metadata": getattr(rendered, "metadata", {}),
            "page_count": getattr(converter, "page_count", None),
            "image_count": len(images),
        }
