"""Label + Choose… button + validated path field row."""

from collections.abc import Callable

from PySide6.QtCore import QStandardPaths, Signal
from PySide6.QtWidgets import QFileDialog, QHBoxLayout, QLineEdit, QLabel, QPushButton, QVBoxLayout, QWidget

from app.qss import repolish
from app.widgets.saved_badge import BadgedInputHost
from app.widgets.validated_field import FieldSpec, make_field_label

_LABEL_WIDTH = 150


class FolderField(QWidget):
    """Folder path row with native directory picker and inline validation."""

    validityChanged = Signal(bool)
    valueChanged = Signal(str)

    def __init__(
        self,
        spec: FieldSpec,
        dialog_title: str,
        parent: QWidget | None = None,
        start_dir_resolver: Callable[[str], str] | None = None,
    ):
        super().__init__(parent)
        self._spec = spec
        self._dialog_title = dialog_title
        self._start_dir_resolver = start_dir_resolver
        self._valid = False
        self._build_ui()
        self._edit.setText(spec.default)
        self._on_text_changed(spec.default)

    def value(self) -> str:
        return self._edit.text()

    def set_value(self, value: str) -> None:
        self._edit.setText(value)
        self._on_text_changed(value)

    def is_valid(self) -> bool:
        return self._valid

    def flash_saved(self) -> None:
        self._edit_host.flash_saved()

    def is_saved_sender(self, sender) -> bool:
        return sender in (self, self._edit)

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 4, 0, 4)
        outer.setSpacing(3)
        outer.addLayout(self._build_input_row())
        self._error = QLabel("")
        self._error.setObjectName("FieldError")
        self._error.setContentsMargins(_LABEL_WIDTH + 8, 0, 0, 0)
        self._error.setVisible(False)
        outer.addWidget(self._error)

    def _build_input_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(8)
        edit = QLineEdit()
        edit.setPlaceholderText(self._spec.placeholder)
        edit.textChanged.connect(self._on_text_changed)
        self._edit_host = BadgedInputHost(edit)
        self._edit = edit
        choose = QPushButton("Choose…")
        choose.setObjectName("ActionButton")
        choose.clicked.connect(self._choose_directory)
        self._mark = QLabel("")
        self._mark.setObjectName("FieldMark")
        self._mark.setFixedWidth(16)
        row.addWidget(make_field_label(self._spec.label))
        row.addWidget(choose)
        row.addWidget(self._edit_host, 1)
        row.addWidget(self._mark)
        return row

    def _choose_directory(self) -> None:
        if self._start_dir_resolver is not None:
            start = self._start_dir_resolver(self.value())
        else:
            start = self.value() or QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.DesktopLocation
            )
        path = QFileDialog.getExistingDirectory(self, self._dialog_title, start)
        if path:
            self.set_value(path)

    def _on_text_changed(self, text: str) -> None:
        ok, message = self._spec.validator(text)
        self._valid = ok
        self._mark.setText("" if text == "" else ("✓" if ok else "✗"))
        self._mark.setProperty("state", "" if text == "" else ("ok" if ok else "err"))
        repolish(self._mark)
        show = bool(message) and not ok and text != ""
        self._error.setText(message if show else "")
        self._error.setVisible(show)
        self.validityChanged.emit(ok)
        self.valueChanged.emit(text)
