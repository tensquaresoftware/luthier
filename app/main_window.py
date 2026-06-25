"""Main window: top tab bar, page stack, and dynamic action bar."""

from PySide6.QtCore import QTimer
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
from core.project_reader import read_project_result
from core.project_spec import ProjectSpec

_TABS = ["Project", "Preferences", "Templates", "About"]


def _make_btn(label: str, object_name: str, slot) -> QPushButton:
    btn = QPushButton(label)
    btn.setObjectName(object_name)
    btn.clicked.connect(slot)
    return btn


def _make_button_bar(buttons: list[QPushButton]) -> QWidget:
    widget = QWidget()
    row = QHBoxLayout(widget)
    row.setContentsMargins(0, 0, 0, 0)
    row.setSpacing(8)
    row.addStretch(1)
    for btn in buttons:
        row.addWidget(btn)
    row.addStretch(1)
    return widget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Luthier")
        self.resize(780, 680)
        self.setMinimumSize(720, 640)
        self._prefs = Preferences(Preferences.default_path())
        self._prefs.ensure_initialized()
        self._generator = ProjectGenerator(overrides=templates_store.overrides_dir())
        self._defaults = self._prefs.seed_dict()
        self._build_ui()
        if self._generator.error:
            self._set_status(self._generator.error, ok=False)
        self._refresh_generate_enabled()

    def _form_defaults(self) -> dict:
        return self._prefs.seed_dict()

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
        self._saved_indicator = QLabel("Saved")
        self._saved_indicator.setObjectName("SavedIndicator")
        self._saved_indicator.hide()
        row.addWidget(self._saved_indicator)
        row.addStretch(1)
        return container

    def _on_section_changed(self, index: int) -> None:
        self._stack.setCurrentIndex(index)
        self._btn_stack.setCurrentIndex(index)

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
        self._prefs_page.saved.connect(self._on_prefs_saved)
        self._stack = stack
        return stack

    def _build_bottom_bar(self) -> QWidget:
        bar = QWidget()
        bar.setObjectName("BottomBar")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(16, 8, 16, 8)
        self._status = QLabel("")
        self._btn_stack = self._build_button_stack()
        layout.addWidget(self._status, 1)
        layout.addWidget(self._btn_stack)
        layout.addStretch(1)
        return bar

    def _build_button_stack(self) -> QStackedWidget:
        stack = QStackedWidget()
        stack.addWidget(self._project_buttons())
        stack.addWidget(self._prefs_buttons())
        stack.addWidget(self._templates_buttons())
        stack.addWidget(QWidget())
        return stack

    def _project_buttons(self) -> QWidget:
        self._new_btn = _make_btn("Create New Project", "ActionButton",
                                  lambda: self._project_page.reset(self._form_defaults()))
        self._open_btn = _make_btn("Open Project…", "OpenButton", self._on_open)
        self._generate_btn = _make_btn("Generate Project", "GenerateButton", self._on_generate)
        return _make_button_bar([self._new_btn, self._open_btn, self._generate_btn])

    def _prefs_buttons(self) -> QWidget:
        return _make_button_bar([
            _make_btn("Import Preferences…", "ActionButton", self._on_prefs_import),
            _make_btn("Export Preferences…", "ActionButton", self._on_prefs_export),
        ])

    def _templates_buttons(self) -> QWidget:
        tp = self._templates_page
        return _make_button_bar([
            _make_btn("Load from file…", "ActionButton", tp.load_from_file),
            _make_btn("Reset to default", "ActionButton", tp.reset_to_default),
            _make_btn("Save override", "SaveButton", tp.save_override),
        ])

    def _refresh_generate_enabled(self, _valid: bool = False) -> None:
        ready = self._generator.error is None and self._project_page.is_valid()
        self._generate_btn.setEnabled(ready)

    def _on_prefs_saved(self) -> None:
        self._flash_saved_indicator()

    def _flash_saved_indicator(self) -> None:
        self._saved_indicator.show()
        QTimer.singleShot(2000, self._saved_indicator.hide)

    def _on_prefs_import(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Import Preferences", "", "JSON (*.json);;All files (*)"
        )
        if not path:
            return
        ok, message = self._prefs_page.import_from_file(path)
        if ok:
            self._defaults = self._prefs.seed_dict()
            self._flash_saved_indicator()
            self._set_status(f"Preferences imported from {Path(path).name}.", ok=True)
        else:
            QMessageBox.warning(self, "Import Preferences", message)
            self._set_status("Preferences import failed.", ok=False)

    def _on_prefs_export(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Preferences", "preferences.json", "JSON (*.json);;All files (*)"
        )
        if not path:
            return
        ok, message = self._prefs_page.export_to_file(path)
        if ok:
            self._set_status(f"Preferences exported to {Path(path).name}.", ok=True)
        else:
            QMessageBox.warning(self, "Export Preferences", message)
            self._set_status("Preferences export failed.", ok=False)

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
        result = read_project_result(project_dir)
        spec = result.spec
        if spec is None:
            sidecar = project_dir / ".luthier.json"
            if sidecar.exists():
                message = "Could not read project configuration (.luthier.json is invalid or unreadable)."
                status = message
            elif result.missing_fields:
                bullets = "\n".join(f"• {name}" for name in result.missing_fields)
                message = (
                    "Could not parse project configuration from CMakeLists.txt.\n\n"
                    f"Missing or unreadable fields:\n{bullets}"
                )
                status = "Could not parse project configuration from CMakeLists.txt"
            else:
                message = f"Not a JUCE plugin project: {project_dir}"
                status = message
            QMessageBox.critical(self, "Open Project", message)
            self._set_status(status, ok=False)
            return
        if not spec.plugin_formats:
            message = f"No plugin formats detected in: {project_dir}"
            QMessageBox.critical(self, "Open Project", message)
            self._set_status(message, ok=False)
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
