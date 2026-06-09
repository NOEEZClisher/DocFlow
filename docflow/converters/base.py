from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import ClassVar

from docflow.core.document_model import Document, DocumentLoadError


class DocumentConverter(ABC):
    """Base class for simple document converters."""

    supported_extensions: ClassVar[frozenset[str]] = frozenset()

    @classmethod
    def can_convert(cls, path: Path) -> bool:
        return path.suffix.lower() in cls.supported_extensions

    @abstractmethod
    def convert(self, path: Path) -> Document:
        """Load a file and return a displayable document."""


def read_text_file(path: Path) -> str:
    """Read text files with common Korean/UTF encodings."""
    last_decode_error: UnicodeDecodeError | None = None
    for encoding in ("utf-8-sig", "utf-8", "cp949"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError as exc:
            last_decode_error = exc
        except OSError as exc:
            raise DocumentLoadError(f"파일을 읽을 수 없습니다: {path}") from exc

    raise DocumentLoadError(f"파일 인코딩을 확인할 수 없습니다: {path}") from last_decode_error
