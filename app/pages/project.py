"""The single scrollable page gathering every per-project setting."""

from collections.abc import Callable

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLabel, QScrollArea, QVBoxLayout, QWidget

from app.pages.artefacts import ArtefactsSection
from app.pages.compilation import CompilationSection
from app.pages.formats import FormatsPage
from app.pages.plugin_type import PluginTypePage
from app.pages.project_info import ProjectInfoPage
from app.widgets.section import Section
from core.preferences import Preferences
from core.project_form_state import form_snapshots_equal, new_project_seed
from core.project_spec import ProjectSpec


class ProjectPage(QScrollArea):
    """Scrollable composition of all project sections with aggregate validity."""

    validityChanged = Signal(bool)

    def __init__(
        self,
        defaults: dict,
        bundle_id_fn: Callable[[str, str], str],
        prefs: Preferences,
        folder_start_resolver: Callable[[str], str] | None = None,
    ):
        super().__init__()
        self._info = ProjectInfoPage(
            defaults, bundle_id_fn, folder_start_resolver=folder_start_resolver
        )
        self._type = PluginTypePage()
        self._formats = FormatsPage()
        self._compilation = CompilationSection()
        self._artefacts = ArtefactsSection(prefs)
        self._build_ui()
        self._connect_signals()
        self._baseline: dict = {}
        self._seed_new_project(defaults)

    def _seed_new_project(self, defaults: dict) -> None:
        self.load(ProjectSpec.from_dict(new_project_seed(defaults)))

    def values(self) -> dict:
        values = dict(self._info.values())
        values["pluginType"] = self._type.selected_type()
        values["pluginFormats"] = self._formats.value()
        values.update(self._compilation.values())
        return values

    def config(self) -> dict:
        return self._artefacts.values()

    def spec(self) -> ProjectSpec:
        d = dict(self._info.values())
        d["pluginType"] = self._type.selected_type()
        d["pluginFormats"] = self._formats.value()
        d.update(self._compilation.values())
        d.update(self._artefacts.values())
        return ProjectSpec.from_dict(d)

    def is_valid(self) -> bool:
        return self._info.is_valid() and self._formats.is_valid() and self._artefacts.is_valid()

    def reset(self, defaults: dict) -> None:
        self.load(ProjectSpec.from_dict(new_project_seed(defaults)))

    def is_dirty(self) -> bool:
        return not form_snapshots_equal(self._baseline, self.spec().to_dict())

    def load(self, spec: ProjectSpec) -> None:
        d = spec.to_dict()
        self._info.load(d)
        self._type.set_type(spec.plugin_type)
        self._formats.set_formats(spec.plugin_formats)
        self._compilation.load(d)
        self._artefacts.load(d)
        self._capture_baseline()

    def _capture_baseline(self) -> None:
        self._baseline = self.spec().to_dict()

    def set_destination(self, value: str) -> None:
        self._info.set_destination(value)

    def _build_ui(self) -> None:
        body = QWidget()
        layout = QVBoxLayout(body)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(36)
        layout.addWidget(self._hint())
        for name, widget in self._sections():
            layout.addWidget(Section(name, widget))
        layout.addStretch(1)
        self.setWidget(body)
        self.setWidgetResizable(True)

    def _hint(self) -> QLabel:
        label = QLabel(
            "Configure your JUCE project by entering the information below. "
            "Fields marked with an asterisk (*) are mandatory. A new project is "
            "pre-configured based on the default settings entered in the Preferences tab."
        )
        label.setObjectName("FieldHint")
        label.setWordWrap(True)
        return label

    def _sections(self) -> list:
        return [
            ("Project Info", self._info),
            ("Plugin Type", self._type),
            ("Formats", self._formats),
            ("Compilation", self._compilation),
            ("Artefacts", self._artefacts),
        ]

    def _connect_signals(self) -> None:
        self._info.validityChanged.connect(self._emit_validity)
        self._formats.validityChanged.connect(self._emit_validity)
        self._artefacts.validityChanged.connect(self._emit_validity)

    def _emit_validity(self, _ok: bool = False) -> None:
        self.validityChanged.emit(self.is_valid())
