from __future__ import annotations

from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QSizePolicy,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from docflow.converters import load_document
from docflow.core.document_model import Document, DocumentError, UnsupportedFileTypeError
from docflow.core.exporter import export_documents, save_document_as_markdown, write_export_report
from docflow.core.file_scanner import FolderScanError, scan_documents
from docflow.ui.reader_widget import ReaderWidget


class MainWindow(QMainWindow):
    """Main DocFlow desktop window."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("DocFlow")
        self.resize(1100, 720)

        self._current_folder: Path | None = None
        self._output_folder: Path | None = None
        self._current_document: Document | None = None

        self._folder_button = QPushButton("입력 폴더 선택")
        self._folder_button.clicked.connect(self._choose_input_folder)

        self._folder_label = QLabel("선택된 폴더 없음")
        self._folder_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self._folder_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        toolbar = QHBoxLayout()
        toolbar.addWidget(self._folder_button)
        toolbar.addWidget(self._folder_label, stretch=1)

        self._output_button = QPushButton("출력 폴더 선택")
        self._output_button.clicked.connect(self._choose_output_folder)

        self._output_label = QLabel("출력 폴더 없음")
        self._output_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self._output_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self._save_selected_button = QPushButton("선택 문서 저장")
        self._save_selected_button.clicked.connect(self._save_selected_document)

        self._save_all_button = QPushButton("전체 Markdown 저장")
        self._save_all_button.clicked.connect(self._save_all_documents)

        export_toolbar = QHBoxLayout()
        export_toolbar.addWidget(self._output_button)
        export_toolbar.addWidget(self._output_label, stretch=1)
        export_toolbar.addWidget(self._save_selected_button)
        export_toolbar.addWidget(self._save_all_button)

        self._file_list = QListWidget()
        self._file_list.setAlternatingRowColors(True)
        self._file_list.currentItemChanged.connect(self._open_selected_file)

        list_panel = QWidget()
        list_layout = QVBoxLayout(list_panel)
        list_layout.setContentsMargins(0, 0, 0, 0)
        list_label = QLabel("파일 목록")
        list_label.setObjectName("panelTitle")
        list_layout.addWidget(list_label)
        list_layout.addWidget(self._file_list, stretch=1)

        self._reader = ReaderWidget()

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(list_panel)
        splitter.addWidget(self._reader)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 4)
        splitter.setSizes([280, 820])

        self._status_log = QPlainTextEdit()
        self._status_log.setReadOnly(True)
        self._status_log.setMaximumBlockCount(300)
        self._status_log.setFixedHeight(104)
        self._status_log.setPlaceholderText("상태 로그")

        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.addLayout(toolbar)
        root_layout.addLayout(export_toolbar)
        root_layout.addWidget(splitter, stretch=1)
        root_layout.addWidget(self._make_separator())
        root_layout.addWidget(self._status_log)
        self.setCentralWidget(root)

        self._apply_style()
        self._update_save_buttons()
        self._log("DocFlow가 시작되었습니다.")

    def _choose_input_folder(self) -> None:
        start_dir = str(self._current_folder) if self._current_folder else str(Path.home())
        selected = QFileDialog.getExistingDirectory(self, "입력 폴더 선택", start_dir)
        if not selected:
            self._log("폴더 선택이 취소되었습니다.")
            return

        self._load_folder(Path(selected))

    def _choose_output_folder(self) -> None:
        start_dir = str(self._output_folder or self._current_folder or Path.home())
        selected = QFileDialog.getExistingDirectory(self, "출력 폴더 선택", start_dir)
        if not selected:
            self._log("출력 폴더 선택이 취소되었습니다.")
            return

        self._output_folder = Path(selected)
        self._output_label.setText(str(self._output_folder))
        self._update_save_buttons()
        self._log(f"출력 폴더를 선택했습니다: {self._output_folder}")

    def _load_folder(self, folder: Path) -> None:
        self._current_folder = folder
        self._current_document = None
        self._folder_label.setText(str(folder))
        self._file_list.clear()
        self._reader.show_message("문서를 선택하면 이곳에 내용이 표시됩니다.")
        self._update_save_buttons()

        try:
            files = scan_documents(folder)
        except (FileNotFoundError, NotADirectoryError, FolderScanError) as exc:
            self._log(f"폴더를 읽지 못했습니다: {exc}")
            QMessageBox.warning(self, "폴더 읽기 실패", str(exc))
            return

        if not files:
            self._log("지원하는 파일이 없는 빈 폴더입니다.")
            self._reader.show_message("선택한 폴더에 지원 문서가 없습니다.")
            return

        for path in files:
            item = QListWidgetItem(self._display_path(path, folder))
            item.setToolTip(str(path))
            item.setData(Qt.ItemDataRole.UserRole, str(path))
            self._file_list.addItem(item)

        self._log(f"{len(files)}개 문서를 찾았습니다.")
        self._file_list.setCurrentRow(0)
        self._update_save_buttons()

    def _open_selected_file(self, current: QListWidgetItem | None, _previous: QListWidgetItem | None) -> None:
        if current is None:
            self._current_document = None
            self._update_save_buttons()
            return

        raw_path = current.data(Qt.ItemDataRole.UserRole)
        if not raw_path:
            return

        path = Path(str(raw_path))
        try:
            document = load_document(path)
        except UnsupportedFileTypeError as exc:
            self._current_document = None
            self._reader.show_message("지원하지 않는 파일 형식입니다.")
            self._log(f"지원하지 않는 파일 형식: {path.name}")
            self._update_save_buttons()
            QMessageBox.information(self, "지원하지 않는 파일", str(exc))
            return
        except DocumentError as exc:
            self._current_document = None
            self._reader.show_message("파일을 읽는 중 문제가 발생했습니다.")
            self._log(f"읽기 실패: {path.name} - {exc}")
            self._update_save_buttons()
            QMessageBox.warning(self, "파일 읽기 실패", str(exc))
            return

        self._current_document = document
        self._reader.set_document(document)
        self._update_save_buttons()
        self._log(f"문서를 열었습니다: {path.name}")

    def _save_selected_document(self) -> None:
        if self._current_document is None:
            self._log("저장할 문서가 선택되지 않았습니다.")
            return
        if self._output_folder is None:
            self._log("출력 폴더를 먼저 선택해야 합니다.")
            return

        try:
            saved_path = save_document_as_markdown(self._current_document, self._output_folder)
        except OSError as exc:
            self._log(f"선택 문서 저장 완료: 성공 0개, 실패 1개 - {exc}")
            QMessageBox.warning(self, "저장 실패", str(exc))
            return

        self._log(f"선택 문서 저장 완료: 성공 1개, 실패 0개 - {saved_path.name}")

    def _save_all_documents(self) -> None:
        if self._output_folder is None:
            self._log("출력 폴더를 먼저 선택해야 합니다.")
            return

        file_paths = self._listed_file_paths()
        if not file_paths:
            self._log("저장할 문서 목록이 없습니다.")
            return

        summary = export_documents(file_paths, self._output_folder)
        try:
            report_path = write_export_report(summary, self._output_folder)
            self._log(f"저장 결과 리포트 생성: {report_path.name}")
        except OSError as exc:
            self._log(f"저장 결과 리포트 생성 실패: {exc}")

        for failure in summary.failures:
            self._log(f"저장 실패: {failure.source_path.name} - {failure.message}")
        self._log(f"전체 Markdown 저장 완료: 성공 {summary.success_count}개, 실패 {summary.failure_count}개")

    def _display_path(self, path: Path, folder: Path) -> str:
        try:
            return str(path.relative_to(folder))
        except ValueError:
            return path.name

    def _listed_file_paths(self) -> list[Path]:
        paths: list[Path] = []
        for index in range(self._file_list.count()):
            raw_path = self._file_list.item(index).data(Qt.ItemDataRole.UserRole)
            if raw_path:
                paths.append(Path(str(raw_path)))
        return paths

    def _update_save_buttons(self) -> None:
        has_output_folder = self._output_folder is not None
        self._save_selected_button.setEnabled(has_output_folder and self._current_document is not None)
        self._save_all_button.setEnabled(has_output_folder and self._file_list.count() > 0)

    def _log(self, message: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        self._status_log.appendPlainText(f"[{timestamp}] {message}")

    def _make_separator(self) -> QFrame:
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        return separator

    def _apply_style(self) -> None:
        self.setStyleSheet(
            """
            QMainWindow {
                background: #f7f7f4;
            }
            QLabel#panelTitle {
                color: #27313a;
                font-size: 14px;
                font-weight: 700;
                padding: 4px 2px;
            }
            QPushButton {
                background: #235d7c;
                border: 1px solid #1f506b;
                border-radius: 6px;
                color: white;
                font-weight: 700;
                padding: 8px 14px;
            }
            QPushButton:hover {
                background: #2e7094;
            }
            QPushButton:pressed {
                background: #19465f;
            }
            QListWidget, QPlainTextEdit, QTextBrowser {
                background: #ffffff;
                border: 1px solid #d7d9d3;
                border-radius: 6px;
                color: #1f2529;
                selection-background-color: #d8edf6;
                selection-color: #1f2529;
            }
            QPlainTextEdit {
                font-family: Consolas, "Courier New", monospace;
                font-size: 12px;
            }
            """
        )
