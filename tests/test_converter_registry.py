from __future__ import annotations

from pathlib import Path

import pytest

from docflow.converters.base import DocumentConverter
from docflow.converters.md_converter import MarkdownConverter
from docflow.converters.registry import ConverterRegistry, default_registry
from docflow.converters.txt_converter import TxtConverter
from docflow.core import file_scanner
from docflow.core.document_model import Document, UnsupportedFileTypeError


class FakeConverter(DocumentConverter):
    supported_extensions = frozenset({".school"})

    def convert(self, path: Path) -> Document:
        return Document(path=path, kind="fake", raw_text="")


def touch(path: Path) -> None:
    path.write_text("sample", encoding="utf-8")


def test_registry_selects_txt_converter_for_txt_files() -> None:
    converter = default_registry.get_converter(Path("submission.txt"))

    assert isinstance(converter, TxtConverter)


def test_registry_selects_markdown_converter_for_markdown_files() -> None:
    md_converter = default_registry.get_converter(Path("submission.md"))
    markdown_converter = default_registry.get_converter(Path("submission.markdown"))

    assert isinstance(md_converter, MarkdownConverter)
    assert isinstance(markdown_converter, MarkdownConverter)


def test_registry_raises_for_unsupported_extension() -> None:
    with pytest.raises(UnsupportedFileTypeError):
        default_registry.get_converter(Path("submission.docx"))


def test_scanner_uses_registry_supported_extensions(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    touch(tmp_path / "keep.school")
    touch(tmp_path / "skip.txt")

    registry = ConverterRegistry((FakeConverter(),))
    monkeypatch.setattr(file_scanner, "default_registry", registry)

    found = [path.name for path in file_scanner.scan_documents(tmp_path)]

    assert found == ["keep.school"]


def test_file_scanner_supported_extensions_are_registry_based() -> None:
    assert file_scanner.SUPPORTED_EXTENSIONS == default_registry.supported_extensions()
