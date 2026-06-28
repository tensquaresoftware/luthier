"""Compilation section: C++ standard, preprocessor definitions, header paths."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QVBoxLayout, QWidget

from app.widgets.combo_field import ComboField
from app.widgets.text_area_field import TextAreaField
from core.display import display_str

_CXX_CHOICES = ["C++17", "C++20", "C++23"]
_DEFAULT_CXX = "C++17"


class CompilationSection(QWidget):
    """Per-project compilation options fed to the CMake target."""

    changed = Signal()

    def __init__(self):
        super().__init__()
        self._last_changed = None
        self._cxx = ComboField("C++ standard", _CXX_CHOICES, _DEFAULT_CXX)
        self._defs = TextAreaField("Preprocessor defs", "one per line, e.g. MY_FLAG=1")
        self._headers = TextAreaField("Header search paths", "one per line, relative to the project")
        self._build_ui()
        self._cxx._combo.currentTextChanged.connect(
            lambda _t: self._emit_changed(self._cxx)
        )
        self._defs._edit.textChanged.connect(lambda: self._emit_changed(self._defs))
        self._headers._edit.textChanged.connect(lambda: self._emit_changed(self._headers))

    def _emit_changed(self, field) -> None:
        self._last_changed = field
        self.changed.emit()

    def values(self) -> dict:
        return {
            "cxxStandard": self._cxx.value(),
            "preprocessorDefinitions": self._defs.value(),
            "headerSearchPaths": self._headers.value(),
        }

    def load(self, values: dict) -> None:
        cxx = values.get("cxxStandard", _DEFAULT_CXX)
        self._cxx.set_value(display_str(cxx) or _DEFAULT_CXX)
        self._defs.set_value(display_str(values.get("preprocessorDefinitions")))
        self._headers.set_value(display_str(values.get("headerSearchPaths")))

    def flash_saved(self, sender) -> None:
        if sender is self and self._last_changed is not None:
            self._last_changed.flash_saved()
            return
        for field in (self._cxx, self._defs, self._headers):
            if field.is_saved_sender(sender):
                field.flash_saved()
                return

    def is_saved_sender(self, sender) -> bool:
        if sender is self:
            return True
        return any(field.is_saved_sender(sender) for field in (self._cxx, self._defs, self._headers))

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        layout.addWidget(self._cxx)
        layout.addWidget(self._defs)
        layout.addWidget(self._headers)
