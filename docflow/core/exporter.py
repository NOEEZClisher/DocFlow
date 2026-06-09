from __future__ import annotations

import csv
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path

from docflow.converters import load_document
from docflow.core.document_model import Document


DocumentLoader = Callable[[Path], Document]
REPORT_FILENAME = "export_report.csv"
REPORT_COLUMNS = (
    "source_name",
    "source_path",
    "output_name",
    "output_path",
    "success",
    "error_message",
)


@dataclass(frozen=True)
class ExportFailure:
    source_path: Path
    message: str


@dataclass(frozen=True)
class ExportRecord:
    source_path: Path
    output_path: Path | None = None
    error_message: str = ""

    @property
    def success(self) -> bool:
        return self.output_path is not None


@dataclass(frozen=True)
class ExportSummary:
    records: tuple[ExportRecord, ...]

    @property
    def saved_paths(self) -> tuple[Path, ...]:
        return tuple(record.output_path for record in self.records if record.output_path is not None)

    @property
    def failures(self) -> tuple[ExportFailure, ...]:
        return tuple(
            ExportFailure(source_path=record.source_path, message=record.error_message)
            for record in self.records
            if not record.success
        )

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
    records: list[ExportRecord] = []
    reserved_paths: set[Path] = set()

    for source_path in source_paths:
        try:
            document = loader(source_path)
            output_path = save_document_as_markdown(document, output_folder, reserved_paths)
            records.append(ExportRecord(source_path=source_path, output_path=output_path))
        except Exception as exc:
            records.append(ExportRecord(source_path=source_path, error_message=str(exc)))

    return ExportSummary(records=tuple(records))


def write_export_report(summary: ExportSummary, output_folder: Path) -> Path:
    output_folder.mkdir(parents=True, exist_ok=True)
    report_path = output_folder / REPORT_FILENAME

    with report_path.open("w", newline="", encoding="utf-8-sig") as report_file:
        writer = csv.DictWriter(report_file, fieldnames=REPORT_COLUMNS)
        writer.writeheader()
        for record in summary.records:
            writer.writerow(_report_row(record))

    return report_path


def _report_row(record: ExportRecord) -> dict[str, str]:
    output_path = record.output_path
    return {
        "source_name": record.source_path.name,
        "source_path": str(record.source_path),
        "output_name": output_path.name if output_path is not None else "",
        "output_path": str(output_path) if output_path is not None else "",
        "success": "true" if record.success else "false",
        "error_message": "" if record.success else record.error_message,
    }
