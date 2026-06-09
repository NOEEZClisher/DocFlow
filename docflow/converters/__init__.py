from __future__ import annotations

from pathlib import Path

from docflow.core.document_model import Document, UnsupportedFileTypeError


def load_document(path: Path) -> Document:
    """Load a supported file through its converter."""
    suffix = path.suffix.lower()
    if suffix == ".txt":
        from .txt_converter import TxtConverter

        return TxtConverter().convert(path)

    if suffix in {".md", ".markdown"}:
        from .md_converter import MarkdownConverter

        return MarkdownConverter().convert(path)

    raise UnsupportedFileTypeError(f"지원하지 않는 파일 형식입니다: {path.suffix or path.name}")


__all__ = ["load_document"]
