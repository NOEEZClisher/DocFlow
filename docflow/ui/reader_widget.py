from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from docflow.core.document_model import Document


class ReaderWidget(QWidget):
    """Document reader with rendered/raw view switching."""

    def __init__(self) -> None:
        super().__init__()
        self._document: Document | None = None

        self._title = QLabel("문서 리더")
        self._title.setObjectName("readerTitle")
        self._title.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self._title.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self._view_mode = QComboBox()
        self._view_mode.addItem("렌더링 보기", "rendered")
        self._view_mode.addItem("원문 보기", "raw")
        self._view_mode.currentIndexChanged.connect(self._refresh_view)

        header = QHBoxLayout()
        header.addWidget(self._title, stretch=1)
        header.addWidget(QLabel("보기"))
        header.addWidget(self._view_mode)

        self._viewer = QTextBrowser()
        self._viewer.setOpenExternalLinks(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(header)
        layout.addWidget(self._viewer, stretch=1)

        self.show_message("문서를 선택하면 이곳에 내용이 표시됩니다.")

    def set_document(self, document: Document) -> None:
        self._document = document
        self._title.setText(document.display_name)

        rendered_index = self._view_mode.findData("rendered")
        raw_index = self._view_mode.findData("raw")
        self._view_mode.setItemData(
            rendered_index,
            None if document.has_rendered_view else "TXT 파일은 원문 보기만 지원합니다.",
            Qt.ItemDataRole.ToolTipRole,
        )
        self._view_mode.model().item(rendered_index).setEnabled(document.has_rendered_view)

        if document.has_rendered_view:
            self._view_mode.setCurrentIndex(rendered_index)
        else:
            self._view_mode.setCurrentIndex(raw_index)
        self._refresh_view()

    def show_message(self, message: str) -> None:
        self._document = None
        self._title.setText("문서 리더")
        self._viewer.setPlainText(message)

    def _refresh_view(self) -> None:
        if self._document is None:
            return

        mode = self._view_mode.currentData()
        if mode == "rendered" and self._document.rendered_html:
            self._viewer.setHtml(self._document.rendered_html)
            return

        self._viewer.setPlainText(self._document.raw_text)
