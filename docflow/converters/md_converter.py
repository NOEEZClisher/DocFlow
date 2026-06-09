from __future__ import annotations

from pathlib import Path

from docflow.core.document_model import Document
from docflow.core.markdown_renderer import render_markdown

from .base import DocumentConverter, read_text_file


class MarkdownConverter(DocumentConverter):
    """Load Markdown files and prepare rendered HTML."""

    supported_extensions = frozenset({".md", ".markdown"})

    def convert(self, path: Path) -> Document:
        raw_text = read_text_file(path)
        return Document(
            path=path,
            kind="markdown",
            raw_text=raw_text,
            rendered_html=render_markdown(raw_text),
        )
