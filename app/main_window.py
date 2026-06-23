"""Main window: top tab bar, page stack, and the Generate action bar."""

from pathlib import Path

from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QTabBar,
    QVBoxLayout,
    QWidget,
)

from app.pages.about import AboutPage
from app.pages.preferences import PreferencesPage
from app.pages.project import ProjectPage
from app.pages.templates import TemplatesPage
from core import plugin_settings, templates_store
from core.preferences import Preferences
from core.project_generator import ProjectGenerator
from core.project_reader import read_project
from core.project_spec import ProjectSpec

_TABS = ["Project", "Preferences", "Templates", "About"]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Luthier")
        self.resize(780, 680)
        self.setMinimumSize(720, 640)
        self._prefs = Preferences(Preferences.default_path())
        self._prefs.load()
        self._generator = ProjectGenerator(overrides=templates_store.overrides_dir())
        self._defaults = self._form_defaults()
        self._build_ui()
        self._show_load_error_if_any()
        self._refresh_generate_enabled()

    def _form_defaults(self) -> dict:
        keys = (
            "manufacturer", "manufacturerCode", "pluginCode", "destination",
            "companyCopyright", "companyWebsite", "companyEmail",
        )
        return {key: self._prefs.get(key) for key in keys}

    def _build_ui(self) -> None:
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._build_tab_bar())
        layout.addWidget(self._build_stack(), 1)
        layout.addWidget(self._build_bottom_bar())
        self.setCentralWidget(central)

    def _build_tab_bar(self) -> QWidget:
        container = QWidget()
        container.setObjectName("TabBarContainer")
        row = QHBoxLayout(container)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)
        self._tab_bar = QTabBar()
        self._tab_bar.setObjectName("TopTabBar")
        for name in _TABS:
            self._tab_bar.addTab(name)
        self._tab_bar.currentChanged.connect(self._on_section_changed)
        row.addWidget(self._tab_bar)
        row.addStretch(1)
        return container

    def _on_section_changed(self, index: int) -> None:
        self._stack.setCurrentIndex(index)

    def _build_stack(self) -> QStackedWidget:
        stack = QStackedWidget()
        self._project_page = ProjectPage(self._defaults, plugin_settings.bundle_id, self._prefs)
        self._prefs_page = PreferencesPage(self._prefs)
        self._templates_page = TemplatesPage()
        self._about_page = AboutPage()
        stack.addWidget(self._project_page)
        stack.addWidget(self._prefs_page)
        stack.addWidget(self._templates_page)
        stack.addWidget(self._about_page)
        self._project_page.validityChanged.connect(self._refresh_generate_enabled)
        self._stack = stack
        return stack

    def _build_bottom_bar(self) -> QWidget:
        bar = QWidget()
        bar.setObjectName("BottomBar")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(12)
        self._open = QPushButton("Open Project…")
        self._open.setObjectName("OpenButton")
        self._open.clicked.connect(self._on_open)
        self._status = QLabel("")
        self._generate = QPushButton("Generate Project")
        self._generate.setObjectName("GenerateButton")
        self._generate.clicked.connect(self._on_generate)
        layout.addWidget(self._open)
        layout.addWidget(self._status, 1)
        layout.addWidget(self._generate)
        return bar

    def _show_load_error_if_any(self) -> None:
        if self._generator.error:
            self._set_status(self._generator.error, ok=False)

    def _refresh_generate_enabled(self, _valid: bool = False) -> None:
        ready = self._generator.error is None and self._project_page.is_valid()
        self._generate.setEnabled(ready)

    def _on_generate(self) -> None:
        spec = self._project_page.spec()
        if not self._confirm_overwrite(spec):
            return
        self._run_generation(spec)

    def _on_open(self) -> None:
        start = self._prefs.get("destination") or ""
        directory = QFileDialog.getExistingDirectory(self, "Open JUCE plugin project", start)
        if directory:
            self._load_project(Path(directory))

    def _load_project(self, project_dir: Path) -> None:
        spec = read_project(project_dir)
        if spec is None:
            self._set_status(f"Not a JUCE plugin project: {project_dir}", ok=False)
            return
        if not spec.plugin_formats:
            self._set_status(f"No plugin formats detected in: {project_dir}", ok=False)
            return
        self._project_page.load(spec)
        self._prefs.update(spec)
        try:
            self._prefs.save()
        except OSError as error:
            self._set_status(f"Loaded {spec.project_name} — preferences not saved: {error}", ok=False)
            return
        self._set_status(f"Loaded {spec.project_name} from {project_dir}", ok=True)

    def _confirm_overwrite(self, spec: ProjectSpec) -> bool:
        if not self._generator.project_exists(spec.destination_dir, spec.project_name):
            return True
        answer = QMessageBox.question(
            self,
            "Overwrite project",
            f"A folder named '{spec.project_name}' already exists. Overwrite it?",
        )
        return answer == QMessageBox.Yes

    def _run_generation(self, spec: ProjectSpec) -> None:
        try:
            project_dir = self._generator.generate(spec)
        except Exception as error:
            self._set_status(f"Generation failed: {error}", ok=False)
            return
        self._prefs.update(spec)
        try:
            self._prefs.save()
        except OSError as error:
            self._set_status(f"Project generated at {project_dir} — preferences not saved: {error}", ok=False)
            return
        self._set_status(f"Project generated at {project_dir}", ok=True)

    def _set_status(self, text: str, ok: bool) -> None:
        self._status.setText(text)
        self._status.setObjectName("StatusOk" if ok else "StatusErr")
        self._status.style().unpolish(self._status)
        self._status.style().polish(self._status)
