"""Label + multi-line text field for optional, one-entry-per-line values."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QWidget

from app.widgets.saved_badge import MultilineBadgedEditor
from app.widgets.validated_field import make_field_label


class TextAreaField(QWidget):
    """A labelled multi-line editor; the value is the raw text (one item per line)."""

    def __init__(self, label: str, placeholder: str = ""):
        super().__init__()
        self._editor = MultilineBadgedEditor(placeholder)
        self._edit = self._editor.edit
        self._build_ui(label)

    def value(self) -> str:
        return self._edit.toPlainText()

    def set_value(self, value: str) -> None:
        self._edit.setPlainText(value)

    def flash_saved(self) -> None:
        self._editor.flash_saved()

    def is_saved_sender(self, sender) -> bool:
        return sender in (self, self._edit, self._editor)

    def _build_ui(self, label: str) -> None:
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 4, 0, 4)
        row.setSpacing(8)
        row.setAlignment(Qt.AlignmentFlag.AlignTop)
        row.addWidget(make_field_label(label, align_top=True), 0, Qt.AlignmentFlag.AlignTop)
        row.addWidget(self._editor, 1)
        row.addSpacing(24)
