from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path

from docflow.converters import load_document
from docflow.core.document_model import Document


DocumentLoader = Callable[[Path], Document]


@dataclass(frozen=True)
class ExportFailure:
    source_path: Path
    message: str


@dataclass(frozen=True)
class ExportSummary:
    saved_paths: tuple[Path, ...]
    failures: tuple[ExportFailure, ...]

    @property
    def success_count(self) -> int:
        return len(self.saved_paths)

    @property
    def failure_count(self) -> int:
        return len(self.failures)


def markdown_filename(source_path: Path) -> str:
    return f"{source_path.stem}.md"


def markdown_output_path(source_path: Path, output_folder: Path) -> Path:
    return output_folder / markdown_filename(source_path)


def unique_markdown_output_path(
    source_path: Path,
    output_folder: Path,
    reserved_paths: set[Path] | None = None,
) -> Path:
    reserved_paths = reserved_paths if reserved_paths is not None else set()
    base_path = markdown_output_path(source_path, output_folder)
    if not base_path.exists() and base_path not in reserved_paths:
        return base_path

    counter = 1
    while True:
        candidate = output_folder / f"{base_path.stem}-{counter}.md"
        if not candidate.exists() and candidate not in reserved_paths:
            return candidate
        counter += 1


def save_document_as_markdown(
    document: Document,
    output_folder: Path,
    reserved_paths: set[Path] | None = None,
) -> Path:
    output_folder.mkdir(parents=True, exist_ok=True)
    output_path = unique_markdown_output_path(document.path, output_folder, reserved_paths)
    output_path.write_text(document.raw_text, encoding="utf-8")
    if reserved_paths is not None:
        reserved_paths.add(output_path)
    return output_path


def export_documents(
    source_paths: Iterable[Path],
    output_folder: Path,
    loader: DocumentLoader = load_document,
) -> ExportSummary:
    saved_paths: list[Path] = []
    failures: list[ExportFailure] = []
    reserved_paths: set[Path] = set()

    for source_path in source_paths:
        try:
            document = loader(source_path)
            saved_paths.append(save_document_as_markdown(document, output_folder, reserved_paths))
        except Exception as exc:
            failures.append(ExportFailure(source_path=source_path, message=str(exc)))

    return ExportSummary(saved_paths=tuple(saved_paths), failures=tuple(failures))
