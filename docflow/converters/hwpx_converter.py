from __future__ import annotations

from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import Any
from xml.etree import ElementTree
from zipfile import BadZipFile, ZipFile

from docflow.core.document_model import Document, DocumentLoadError
from docflow.core.markdown_renderer import render_markdown

from .base import DocumentConverter


class HwpxConverter(DocumentConverter):
    """Convert HWPX section XML paragraphs and tables into Markdown."""

    supported_extensions = frozenset({".hwpx"})

    def convert(self, path: Path) -> Document:
        try:
            with ZipFile(path) as archive:
                section_names = _section_xml_names(archive.namelist())
                if not section_names:
                    raise DocumentLoadError(f"HWPX 본문 XML을 찾을 수 없습니다: {path}")

                blocks: list[str] = []
                for section_name in section_names:
                    blocks.extend(_section_blocks(archive.read(section_name)))
        except DocumentLoadError:
            raise
        except BadZipFile as exc:
            raise DocumentLoadError(f"HWPX ZIP 파일을 열 수 없습니다: {path}") from exc
        except OSError as exc:
            raise DocumentLoadError(f"HWPX 파일을 읽을 수 없습니다: {path}") from exc
        except ElementTree.ParseError as exc:
            raise DocumentLoadError(f"HWPX XML을 해석할 수 없습니다: {path}") from exc

        raw_text = "\n\n".join(blocks).strip()
        if not raw_text:
            raise DocumentLoadError(f"HWPX 본문 텍스트를 찾을 수 없습니다: {path}")

        return Document(
            path=path,
            kind="hwpx",
            raw_text=raw_text,
            rendered_html=render_markdown(raw_text),
        )


def _section_xml_names(names: Iterable[str]) -> list[str]:
    section_names = [
        name
        for name in names
        if name.lower().endswith(".xml") and _looks_like_section_xml(name)
    ]
    return sorted(section_names, key=_section_sort_key)


def _looks_like_section_xml(name: str) -> bool:
    parts = [part.casefold() for part in Path(name).parts]
    filename = parts[-1] if parts else ""
    return filename.startswith("section") or ("contents" in parts and "section" in filename)


def _section_sort_key(name: str) -> tuple[str, int, str]:
    filename = Path(name).name
    digits = "".join(char for char in filename if char.isdigit())
    return (str(Path(name).parent), int(digits) if digits else -1, filename.casefold())


def _section_blocks(xml_bytes: bytes) -> list[str]:
    root = ElementTree.fromstring(xml_bytes)
    return list(_iter_blocks(root))


def _iter_blocks(element: ElementTree.Element) -> Iterator[str]:
    for child in element:
        name = _local_name(child.tag)
        if name == "tbl":
            table = _table_to_markdown(child)
            if table:
                yield table
            continue

        if name == "p":
            paragraph = _paragraph_to_markdown(child)
            if paragraph:
                yield paragraph
            yield from _iter_tables(child)
            continue

        yield from _iter_blocks(child)


def _iter_tables(element: ElementTree.Element) -> Iterator[str]:
    for child in element:
        if _local_name(child.tag) == "tbl":
            table = _table_to_markdown(child)
            if table:
                yield table
        else:
            yield from _iter_tables(child)


def _paragraph_to_markdown(paragraph: ElementTree.Element) -> str:
    text = _text_from_element(paragraph, excluded_ancestors={"tbl"})
    return _normalize_text(text)


def _table_to_markdown(table: ElementTree.Element) -> str:
    rows = [_table_row(row) for row in _descendants_by_name(table, "tr")]
    rows = [row for row in rows if any(cell for cell in row)]
    if not rows:
        return ""

    column_count = max(len(row) for row in rows)
    normalized_rows = [_normalize_row(row, column_count) for row in rows]
    separator = ["---"] * column_count
    lines = [
        _format_table_row(normalized_rows[0]),
        _format_table_row(separator),
    ]
    lines.extend(_format_table_row(row) for row in normalized_rows[1:])
    return "\n".join(lines)


def _table_row(row: ElementTree.Element) -> list[str]:
    cells = list(_descendants_by_name(row, "tc"))
    return [_escape_table_cell(_normalize_text(_text_from_element(cell))) for cell in cells]


def _descendants_by_name(element: ElementTree.Element, name: str) -> Iterator[ElementTree.Element]:
    for descendant in element.iter():
        if descendant is not element and _local_name(descendant.tag) == name:
            yield descendant


def _text_from_element(
    element: ElementTree.Element,
    excluded_ancestors: set[str] | None = None,
) -> str:
    excluded_ancestors = excluded_ancestors or set()
    pieces: list[str] = []

    def visit(node: ElementTree.Element, excluded: bool = False) -> None:
        node_name = _local_name(node.tag)
        is_excluded = excluded or node_name in excluded_ancestors
        if not is_excluded and node.text:
            pieces.append(node.text)

        for child in node:
            visit(child, is_excluded)
            if not is_excluded and child.tail:
                pieces.append(child.tail)

    visit(element)
    return "".join(pieces)


def _normalize_text(text: str) -> str:
    return " ".join(text.replace("\r\n", "\n").replace("\r", "\n").split()).strip()


def _normalize_row(row: list[str], column_count: int) -> list[str]:
    return row + [""] * (column_count - len(row))


def _escape_table_cell(text: str) -> str:
    return (
        text.replace("\\", "\\\\")
        .replace("|", "\\|")
        .replace("\r\n", " ")
        .replace("\n", " ")
        .replace("\r", " ")
    )


def _format_table_row(row: list[str]) -> str:
    return "| " + " | ".join(row) + " |"


def _local_name(tag: Any) -> str:
    tag_text = str(tag)
    if "}" in tag_text:
        return tag_text.rsplit("}", 1)[1]
    if ":" in tag_text:
        return tag_text.rsplit(":", 1)[1]
    return tag_text
