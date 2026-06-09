from __future__ import annotations

from pathlib import Path

from docflow.core.document_model import Document, DocumentLoadError
from docflow.core.exporter import export_documents, markdown_filename, save_document_as_markdown


def test_markdown_filename_replaces_extension_with_md() -> None:
    assert markdown_filename(Path("sample.docx")) == "sample.md"
    assert markdown_filename(Path("notes.markdown")) == "notes.md"
    assert markdown_filename(Path("plain.txt")) == "plain.md"


def test_save_document_as_markdown_writes_raw_text_as_utf8(tmp_path: Path) -> None:
    document = Document(path=Path("sample.docx"), kind="docx", raw_text="# 제목\n\n학생 제출물")

    output_path = save_document_as_markdown(document, tmp_path)

    assert output_path == tmp_path / "sample.md"
    assert output_path.read_text(encoding="utf-8") == "# 제목\n\n학생 제출물"


def test_save_document_as_markdown_avoids_overwriting_duplicate_names(tmp_path: Path) -> None:
    (tmp_path / "sample.md").write_text("기존 파일", encoding="utf-8")
    document = Document(path=Path("sample.docx"), kind="docx", raw_text="새 파일")

    output_path = save_document_as_markdown(document, tmp_path)

    assert output_path == tmp_path / "sample-1.md"
    assert (tmp_path / "sample.md").read_text(encoding="utf-8") == "기존 파일"
    assert output_path.read_text(encoding="utf-8") == "새 파일"


def test_export_documents_continues_after_failure(tmp_path: Path) -> None:
    good_a = tmp_path / "good-a.txt"
    bad = tmp_path / "bad.docx"
    good_b = tmp_path / "good-b.md"

    def load_for_test(path: Path) -> Document:
        if path == bad:
            raise DocumentLoadError("읽기 실패")
        return Document(path=path, kind="test", raw_text=f"saved: {path.name}")

    output_folder = tmp_path / "out"
    summary = export_documents((good_a, bad, good_b), output_folder, loader=load_for_test)

    assert summary.success_count == 2
    assert summary.failure_count == 1
    assert [path.name for path in summary.saved_paths] == ["good-a.md", "good-b.md"]
    assert summary.failures[0].source_path == bad
    assert (output_folder / "good-a.md").read_text(encoding="utf-8") == "saved: good-a.txt"
    assert (output_folder / "good-b.md").read_text(encoding="utf-8") == "saved: good-b.md"
