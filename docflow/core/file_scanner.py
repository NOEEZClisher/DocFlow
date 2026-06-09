from __future__ import annotations

from pathlib import Path

from docflow.converters import default_registry

SUPPORTED_EXTENSIONS = default_registry.supported_extensions()


class FolderScanError(Exception):
    """Raised when an input folder cannot be scanned."""


def scan_documents(folder: Path) -> list[Path]:
    """Return supported document files inside a folder, searched recursively."""
    folder = folder.expanduser().resolve()
    if not folder.exists():
        raise FileNotFoundError(f"폴더가 존재하지 않습니다: {folder}")
    if not folder.is_dir():
        raise NotADirectoryError(f"폴더가 아닙니다: {folder}")

    supported_extensions = default_registry.supported_extensions()
    try:
        files = [
            path
            for path in folder.rglob("*")
            if path.is_file() and path.suffix.lower() in supported_extensions
        ]
    except OSError as exc:
        raise FolderScanError(f"폴더를 탐색할 수 없습니다: {folder}") from exc

    return sorted(files, key=lambda path: str(path).casefold())
