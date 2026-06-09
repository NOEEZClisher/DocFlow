from __future__ import annotations

from pathlib import Path

from docflow.converters.base import read_text_file


def test_read_text_file_reads_utf8(tmp_path: Path) -> None:
    path = tmp_path / "utf8.txt"
    expected = "DocFlow UTF-8 sample\n교사용 문서"
    path.write_text(expected, encoding="utf-8")

    assert read_text_file(path) == expected


def test_read_text_file_reads_cp949(tmp_path: Path) -> None:
    path = tmp_path / "cp949.txt"
    expected = "DocFlow CP949 sample\n학생 제출물"
    path.write_bytes(expected.encode("cp949"))

    assert read_text_file(path) == expected
