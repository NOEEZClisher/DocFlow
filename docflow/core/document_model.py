from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


class DocumentError(Exception):
    """Base exception for document loading and conversion problems."""


class DocumentLoadError(DocumentError):
    """Raised when a supported document cannot be read."""


class UnsupportedFileTypeError(DocumentError):
    """Raised when there is no converter for a file extension."""


@dataclass(frozen=True)
class Document:
    """A loaded document ready for display in the reader."""

    path: Path
    kind: str
    raw_text: str
    rendered_html: str | None = None

    @property
    def display_name(self) -> str:
        return self.path.name

    @property
    def has_rendered_view(self) -> bool:
        return self.rendered_html is not None
