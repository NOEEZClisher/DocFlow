from __future__ import annotations

from pathlib import Path

from docflow.core.document_model import Document

from .registry import ConverterRegistry, default_registry


def load_document(path: Path) -> Document:
    """Load a supported file through its converter."""
    return default_registry.load_document(path)


def supported_extensions() -> frozenset[str]:
    return default_registry.supported_extensions()


__all__ = ["ConverterRegistry", "default_registry", "load_document", "supported_extensions"]
