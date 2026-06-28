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
    return editor


class TemplatesPage(QWidget):
    """Edit the source templates used for new projects; overrides persist on disk."""

    def __init__(self):
        super().__init__()
        self._selector = QComboBox()
        view = QListView()
        view.setFrameShape(QListView.Shape.NoFrame)
        self._selector.setView(view)
        self._selector.addItems(templates_store.EDITABLE_FILES)
        self._editor = _make_editor()
        self._highlighter: CppHighlighter | None = CppHighlighter(self._editor.document())
        self._status = QLabel("")
        self._status.setObjectName("FieldHint")
        self._build_ui()
        self._selector.currentTextChanged.connect(self._load_selected)
        self._load_selected(self._selector.currentText())

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(10)
        layout.addLayout(self._build_header())
        layout.addWidget(self._editor, 1)
        layout.addWidget(self._status)

    def _build_header(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)
        label = QLabel("Select file :")
        label.setObjectName("SectionTitle")
        row.addWidget(label)
        row.addWidget(self._selector, 1)
        return row

    def save_override(self) -> None:
        name = self._selector.currentText()
        templates_store.save_override(name, self._editor.toPlainText())
        self._update_status(name)

    def reset_to_default(self) -> None:
        name = self._selector.currentText()
        templates_store.reset(name)
        self._load_selected(name)

    def load_from_file(self) -> None:
        name = self._selector.currentText()
        path = self._pick_file_for_template(name)
        if not path:
            return
        if not self._is_valid_template_file(name, path):
            self._abort_load(name, "Invalid file type for the selected template.")
            return
        try:
            content = Path(path).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as error:
            self._abort_load(name, f"Could not read file: {error}")
            return
        self._editor.setPlainText(content)
        self._update_loaded_status(path)

    def _pick_file_for_template(self, name: str) -> str:
        if name == templates_store.GITIGNORE_FILE:
            return self._pick_gitignore_file()
        path, _ = QFileDialog.getOpenFileName(
            self, "Load template file", "", "C++ source (*.h *.cpp);;All files (*)"
        )
        return path

    def _is_valid_template_file(self, name: str, path: str) -> bool:
        file_path = Path(path)
        if name == templates_store.GITIGNORE_FILE:
            return (
                file_path.name == templates_store.GITIGNORE_FILE
                or file_path.suffix.lower() == ".gitignore"
            )
        return file_path.suffix.lower() in (".h", ".cpp")

    def _abort_load(self, name: str, message: str) -> None:
        self._editor.setPlainText(templates_store.read_effective(name))
        self._status.setText(message)

    def _update_loaded_status(self, path: str) -> None:
        self._status.setText(
            f"Loaded from {Path(path).name} — not saved until you click Save override."
        )

    def _load_selected(self, name: str) -> None:
        self._set_syntax_mode(name)
        self._editor.setPlainText(templates_store.read_effective(name))
        self._update_status(name)

    def _set_syntax_mode(self, name: str) -> None:
        if name == templates_store.GITIGNORE_FILE:
            if self._highlighter:
                self._highlighter.setDocument(None)
                self._highlighter = None
            return
        if not self._highlighter:
            self._highlighter = CppHighlighter(self._editor.document())

    def _pick_gitignore_file(self) -> str:
        dialog = QFileDialog(self, "Load template file", "")
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        dialog.setNameFilter("Git ignore (*.gitignore);;All files (*)")
        dialog.setOption(QFileDialog.Option.ShowHidden, True)
        dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
        if not dialog.exec():
            return ""
        selected = dialog.selectedFiles()
        return selected[0] if selected else ""

    def _update_status(self, name: str) -> None:
        if templates_store.has_override(name):
            self._status.setText("Override active — used for new projects.")
            return
        self._status.setText("Showing the built-in default.")
