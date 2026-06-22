"""Templates page: view, edit, replace or reset the C++ source templates."""

from pathlib import Path

from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListView,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.widgets.cpp_highlighter import CppHighlighter
from core import templates_store

_EDITOR_POINT_SIZE = 12


def _make_editor() -> QPlainTextEdit:
    editor = QPlainTextEdit()
    editor.setLineWrapMode(QPlainTextEdit.NoWrap)
    font = QFont("Menlo")
    font.setStyleHint(QFont.Monospace)
    font.setPointSize(_EDITOR_POINT_SIZE)
    editor.setFont(font)
    CppHighlighter(editor.document())
    return editor


class TemplatesPage(QWidget):
    """Edit the source templates used for new projects; overrides persist on disk."""

    def __init__(self):
        super().__init__()
        self._selector = QComboBox()
        view = QListView()
        view.setFrameShape(QListView.Shape.NoFrame)
        self._selector.setView(view)
        self._selector.addItems(templates_store.SOURCE_FILES)
        self._editor = _make_editor()
        self._status = QLabel("")
        self._status.setObjectName("FieldHint")
        self._build_ui()
        self._selector.currentTextChanged.connect(self._load_selected)
        self._load_selected(self._selector.currentText())

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(10)
        title = QLabel("Templates")
        title.setObjectName("PageTitle")
        selector_row = QHBoxLayout()
        selector_row.setContentsMargins(0, 0, 0, 0)
        selector_row.addWidget(self._selector, 1)
        selector_row.addStretch(1)
        layout.addWidget(title)
        layout.addLayout(selector_row)
        layout.addWidget(self._editor, 1)
        layout.addLayout(self._build_buttons())

    def _build_buttons(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.addWidget(self._status, 1)
        row.addWidget(self._make_button("Load from file…", self._on_load_file))
        row.addWidget(self._make_button("Reset to default", self._on_reset))
        row.addWidget(self._make_button("Save override", self._on_save))
        return row

    def _make_button(self, label: str, slot) -> QPushButton:
        button = QPushButton(label)
        button.setObjectName("ActionButton")
        button.clicked.connect(slot)
        return button

    def _load_selected(self, name: str) -> None:
        self._editor.setPlainText(templates_store.read_effective(name))
        self._update_status(name)

    def _on_save(self) -> None:
        name = self._selector.currentText()
        templates_store.save_override(name, self._editor.toPlainText())
        self._update_status(name)

    def _on_reset(self) -> None:
        name = self._selector.currentText()
        templates_store.reset(name)
        self._load_selected(name)

    def _on_load_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Load template file", "", "C++ source (*.h *.cpp);;All files (*)"
        )
        if path:
            self._editor.setPlainText(Path(path).read_text(encoding="utf-8"))

    def _update_status(self, name: str) -> None:
        if templates_store.has_override(name):
            self._status.setText("Override active — used for new projects.")
            return
        self._status.setText("Showing the built-in default.")
