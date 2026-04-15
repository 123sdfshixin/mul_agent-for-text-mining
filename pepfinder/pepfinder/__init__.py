"""Compatibility shim for running the src-layout package from the repo root.

This package extends its import path to include ``src/pepfinder`` so that
``python -m pepfinder.cli`` works before editable installation.
"""

from pathlib import Path


_PACKAGE_DIR = Path(__file__).resolve().parent
_SRC_PACKAGE_DIR = _PACKAGE_DIR.parent / "src" / "pepfinder"

if _SRC_PACKAGE_DIR.exists():
    __path__.append(str(_SRC_PACKAGE_DIR))
