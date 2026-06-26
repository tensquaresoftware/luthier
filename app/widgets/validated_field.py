"""Reusable form field with inline orange/red validation feedback."""

from dataclasses import dataclass
from typing import Callable

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from app.qss import repolish
from core.paths import is_path_validator, normalize_portable_path
from app.widgets.elided_line_edit import ElidedLineEdit
from app.widgets.saved_badge import BadgedInputHost

Validator = Callable[[str], tuple[bool, str]]

_LABEL_WIDTH = 150


def make_field_label(text: str, *, align_top: bool = False) -> QLabel:
    """Fixed-width label shared by form rows; top-aligned for multi-line fields."""
    label = QLabel(text)
    label.setObjectName("FieldLabel")
    label.setFixedWidth(_LABEL_WIDTH)
    if align_top:
        label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        label.setContentsMargins(0, 8, 0, 0)
    else:
        label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
    return label


@dataclass
class FieldSpec:
    key: str
    label: str
    validator: Validator
    default: str = ""
    placeholder: str = ""


class ValidatedField(QWidget):
    """Label + line edit + inline validity mark and error message."""

    validityChanged = Signal(bool)
    valueChanged = Signal(str)

    def __init__(self, spec: FieldSpec):
        super().__init__()
        self._spec = spec
        self._valid = False
        self._build_ui()
        self._edit.setText(spec.default)
        self._edit.textChanged.connect(self._on_text_changed)
        self._on_text_changed(spec.default)

    def value(self) -> str:
        return self._edit.text()

    def set_value(self, value: str) -> None:
        if is_path_validator(self._spec.validator):
            value = normalize_portable_path(value)
        self._edit.setText(value)

    def _normalize_path_text(self) -> None:
        normalized = normalize_portable_path(self._edit.text())
        if normalized != self._edit.text():
            self._edit.setText(normalized)

    def is_valid(self) -> bool:
        return self._valid

    def focus(self) -> None:
        self._edit.setFocus()

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
        edit = ElidedLineEdit()
        edit.setPlaceholderText(self._spec.placeholder)
        if is_path_validator(self._spec.validator):
            edit.editingFinished.connect(self._normalize_path_text)
        self._edit_host = BadgedInputHost(edit)
        self._edit = edit
        self._mark = QLabel("")
        self._mark.setObjectName("FieldMark")
        self._mark.setFixedWidth(16)
        row.addWidget(make_field_label(self._spec.label))
        row.addWidget(self._edit_host, 1)
        row.addWidget(self._mark)
        return row

    def _on_text_changed(self, text: str) -> None:
        ok, message = self._spec.validator(text)
        self._valid = ok
        self._update_mark(ok, text)
        self._update_error(ok, message, text)
        self.validityChanged.emit(ok)
        self.valueChanged.emit(text)

    def _update_mark(self, ok: bool, text: str) -> None:
        self._mark.setText("" if text == "" else ("✓" if ok else "✗"))
        self._mark.setProperty("state", "" if text == "" else ("ok" if ok else "err"))
        repolish(self._mark)

    def _update_error(self, ok: bool, message: str, text: str) -> None:
        show = bool(message) and not ok and text != ""
        self._error.setText(message if show else "")
        self._error.setVisible(show)
