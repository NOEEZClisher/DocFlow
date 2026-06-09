from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from docflow.core.document_model import Document, UnsupportedFileTypeError

from .base import DocumentConverter
from .docx_converter import DocxConverter
from .md_converter import MarkdownConverter
from .pptx_converter import PptxConverter
from .txt_converter import TxtConverter
from .xlsx_converter import XlsxConverter


class ConverterRegistry:
    """Registry that maps file extensions to document converters."""

    def __init__(self, converters: Iterable[DocumentConverter] | None = None) -> None:
        self._converters: dict[str, DocumentConverter] = {}
        for converter in converters or ():
            self.register(converter)

    def register(self, converter: DocumentConverter) -> None:
        for extension in converter.supported_extensions:
            self._converters[extension.lower()] = converter

    def get_converter(self, path: Path) -> DocumentConverter:
        suffix = path.suffix.lower()
        try:
            return self._converters[suffix]
        except KeyError as exc:
            raise UnsupportedFileTypeError(f"지원하지 않는 파일 형식입니다: {path.suffix or path.name}") from exc

    def load_document(self, path: Path) -> Document:
        return self.get_converter(path).convert(path)

    def supported_extensions(self) -> frozenset[str]:
        return frozenset(self._converters)


default_registry = ConverterRegistry(
    (
        TxtConverter(),
        MarkdownConverter(),
        DocxConverter(),
        XlsxConverter(),
        PptxConverter(),
    )
)
