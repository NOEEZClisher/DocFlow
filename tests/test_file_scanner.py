from __future__ import annotations

from pathlib import Path

from docflow.core.file_scanner import scan_documents


def touch(path: Path, content: str = "sample") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_scan_documents_finds_only_supported_extensions(tmp_path: Path) -> None:
    touch(tmp_path / "lesson.txt")
    touch(tmp_path / "rubric.md")
    touch(tmp_path / "notes.markdown")
    touch(tmp_path / "archive.docx")
    touch(tmp_path / "image.png")

    found = {path.name for path in scan_documents(tmp_path)}

    assert found == {"lesson.txt", "rubric.md", "notes.markdown"}


def test_scan_documents_searches_subfolders_recursively(tmp_path: Path) -> None:
    touch(tmp_path / "root.txt")
    touch(tmp_path / "class-a" / "submission.md")
    touch(tmp_path / "class-a" / "nested" / "reflection.markdown")

    found = {path.relative_to(tmp_path).as_posix() for path in scan_documents(tmp_path)}

    assert found == {
        "root.txt",
        "class-a/submission.md",
        "class-a/nested/reflection.markdown",
    }


def test_scan_documents_ignores_unsupported_extensions(tmp_path: Path) -> None:
    touch(tmp_path / "supported.TXT")
    touch(tmp_path / "ignore.docx")
    touch(tmp_path / "ignore.hwpx")
    touch(tmp_path / "ignore.pptx")
    touch(tmp_path / "ignore.xlsx")

    found = [path.name for path in scan_documents(tmp_path)]

    assert found == ["supported.TXT"]
