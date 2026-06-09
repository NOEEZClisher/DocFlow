from __future__ import annotations

from pathlib import Path
from zipfile import ZipFile

import pytest

from docflow.converters.hwpx_converter import HwpxConverter
from docflow.converters.registry import default_registry
from docflow.core.document_model import DocumentLoadError


def write_hwpx(path: Path, section_xml: str, section_name: str = "Contents/section0.xml") -> Path:
    with ZipFile(path, "w") as archive:
        archive.writestr("mimetype", "application/hwp+zip")
        archive.writestr(section_name, section_xml)
    return path


def write_hwpx_sections(path: Path, sections: dict[str, str]) -> Path:
    with ZipFile(path, "w") as archive:
        archive.writestr("mimetype", "application/hwp+zip")
        for name, xml in sections.items():
            archive.writestr(name, xml)
    return path


def test_hwpx_converter_extracts_paragraphs_from_section_xml(tmp_path: Path) -> None:
    path = write_hwpx(
        tmp_path / "paragraphs.hwpx",
        """
        <hp:sec xmlns:hp="http://www.hancom.co.kr/hwpml/2011/paragraph">
          <hp:p><hp:run><hp:t>첫 번째 문단</hp:t></hp:run></hp:p>
          <hp:p><hp:run><hp:t>두 번째 문단</hp:t></hp:run></hp:p>
        </hp:sec>
        """,
    )

    document = HwpxConverter().convert(path)

    assert document.kind == "hwpx"
    assert document.raw_text == "첫 번째 문단\n\n두 번째 문단"
    assert document.rendered_html is not None
    assert "<p>첫 번째 문단</p>" in document.rendered_html


def test_hwpx_converter_extracts_tables_with_namespaces(tmp_path: Path) -> None:
    path = write_hwpx(
        tmp_path / "table.hwpx",
        """
        <hp:sec xmlns:hp="http://www.hancom.co.kr/hwpml/2011/paragraph">
          <hp:p><hp:run><hp:t>표 안내</hp:t></hp:run></hp:p>
          <hp:tbl>
            <hp:tr>
              <hp:tc><hp:subList><hp:p><hp:run><hp:t>항목</hp:t></hp:run></hp:p></hp:subList></hp:tc>
              <hp:tc><hp:subList><hp:p><hp:run><hp:t>상태</hp:t></hp:run></hp:p></hp:subList></hp:tc>
            </hp:tr>
            <hp:tr>
              <hp:tc><hp:subList><hp:p><hp:run><hp:t>초안</hp:t></hp:run></hp:p></hp:subList></hp:tc>
              <hp:tc><hp:subList><hp:p><hp:run><hp:t>완료 | 확인</hp:t></hp:run></hp:p></hp:subList></hp:tc>
            </hp:tr>
          </hp:tbl>
        </hp:sec>
        """,
    )

    document = HwpxConverter().convert(path)

    assert document.raw_text == "\n\n".join(
        [
            "표 안내",
            "\n".join(
                [
                    "| 항목 | 상태 |",
                    "| --- | --- |",
                    "| 초안 | 완료 \\| 확인 |",
                ]
            ),
        ]
    )
    assert "<table>" in document.rendered_html


def test_hwpx_converter_merges_multiple_sections_in_sorted_order(tmp_path: Path) -> None:
    path = write_hwpx_sections(
        tmp_path / "sections.hwpx",
        {
            "Contents/section2.xml": """
            <hp:sec xmlns:hp="http://www.hancom.co.kr/hwpml/2011/paragraph">
              <hp:p><hp:run><hp:t>세 번째 section</hp:t></hp:run></hp:p>
            </hp:sec>
            """,
            "Contents/section1.xml": """
            <hp:sec xmlns:hp="http://www.hancom.co.kr/hwpml/2011/paragraph">
              <hp:p><hp:run><hp:t>두 번째 section</hp:t></hp:run></hp:p>
            </hp:sec>
            """,
        },
    )

    document = HwpxConverter().convert(path)

    assert document.raw_text == "두 번째 section\n\n세 번째 section"


def test_hwpx_converter_ignores_empty_paragraphs(tmp_path: Path) -> None:
    path = write_hwpx(
        tmp_path / "empty-paragraph.hwpx",
        """
        <hp:sec xmlns:hp="http://www.hancom.co.kr/hwpml/2011/paragraph">
          <hp:p />
          <hp:p><hp:run><hp:t>내용 있는 문단</hp:t></hp:run></hp:p>
          <hp:p><hp:run><hp:t>   </hp:t></hp:run></hp:p>
        </hp:sec>
        """,
    )

    document = HwpxConverter().convert(path)

    assert document.raw_text == "내용 있는 문단"


def test_hwpx_converter_raises_for_invalid_hwpx_file(tmp_path: Path) -> None:
    path = tmp_path / "invalid.hwpx"
    path.write_text("not a zip", encoding="utf-8")

    with pytest.raises(DocumentLoadError):
        HwpxConverter().convert(path)


def test_hwpx_converter_raises_when_section_xml_is_missing(tmp_path: Path) -> None:
    path = tmp_path / "missing-section.hwpx"
    with ZipFile(path, "w") as archive:
        archive.writestr("Contents/header.xml", "<root />")

    with pytest.raises(DocumentLoadError):
        HwpxConverter().convert(path)


def test_registry_selects_hwpx_converter_for_hwpx_files() -> None:
    converter = default_registry.get_converter(Path("submission.hwpx"))

    assert isinstance(converter, HwpxConverter)
