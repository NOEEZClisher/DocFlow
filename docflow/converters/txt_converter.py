from __future__ import annotations

from pathlib import Path

from docflow.core.document_model import Document

from .base import DocumentConverter, read_text_file


class TxtConverter(DocumentConverter):
    """Load plain text files."""

    supported_extensions = frozenset({".txt"})

    def convert(self, path: Path) -> Document:
        return Document(path=path, kind="text", raw_text=read_text_file(path))
