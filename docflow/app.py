from __future__ import annotations

import sys
from collections.abc import Sequence

from PySide6.QtWidgets import QApplication

from docflow.ui.main_window import MainWindow


def run_app(argv: Sequence[str] | None = None) -> int:
    """Create and run the DocFlow Qt application."""
    app = QApplication(list(argv) if argv is not None else sys.argv)
    app.setApplicationName("DocFlow")
    app.setOrganizationName("DocFlow")

    window = MainWindow()
    window.show()

    return app.exec()
