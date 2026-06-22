"""Compilation section: C++ standard, preprocessor definitions, header paths."""

from PySide6.QtWidgets import QVBoxLayout, QWidget

from app.widgets.combo_field import ComboField
from app.widgets.text_area_field import TextAreaField

_CXX_CHOICES = ["C++17", "C++20", "C++23"]
_DEFAULT_CXX = "C++17"


class CompilationSection(QWidget):
    """Per-project compilation options fed to the CMake target."""

    def __init__(self):
        super().__init__()
        self._cxx = ComboField("C++ standard", _CXX_CHOICES, _DEFAULT_CXX)
        self._defs = TextAreaField("Preprocessor defs", "one per line, e.g. MY_FLAG=1")
        self._headers = TextAreaField("Header search paths", "one per line, relative to the project")
        self._build_ui()

    def values(self) -> dict:
        return {
            "cxxStandard": self._cxx.value(),
            "preprocessorDefinitions": self._defs.value(),
            "headerSearchPaths": self._headers.value(),
        }

    def load(self, values: dict) -> None:
        self._cxx.set_value(values.get("cxxStandard", _DEFAULT_CXX))
        self._defs.set_value(values.get("preprocessorDefinitions", ""))
        self._headers.set_value(values.get("headerSearchPaths", ""))

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        layout.addWidget(self._cxx)
        layout.addWidget(self._defs)
        layout.addWidget(self._headers)
