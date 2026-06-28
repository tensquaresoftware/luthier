"""Main window: top tab bar, page stack, and dynamic action bar."""

from PySide6.QtCore import QByteArray, QEvent, QTimer, QRect, Qt
from PySide6.QtGui import QGuiApplication
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
from app.confirm import confirm_discard_unsaved
from app.widgets.status_capsule import (
    BAR_MIN_HEIGHT,
    STATUS_BAR_MARGIN_LEFT,
    STATUS_BAR_MARGIN_RIGHT,
    STATUS_BAR_V_PAD,
    ROW_SPACING,
    StatusCapsule,
    StatusMessageHeading,
    status_capsule_max_width,
)
from app.theme import apply_accent_theme
from core import plugin_settings, templates_store
from core.app_state import AppState
from core.preferences import Preferences
from core.project_generator import ProjectGenerator
from core.project_reader import read_project_result
from core.project_spec import ProjectSpec

_TABS = ["Project", "Preferences", "Templates", "About"]
_PROJECT_TAB_INDEX = _TABS.index("Project")
_PREFS_TAB_INDEX = _TABS.index("Preferences")
_ABOUT_TAB_INDEX = _TABS.index("About")
_MIN_WINDOW_WIDTH = 750
_MIN_WINDOW_HEIGHT = 720


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
    def __init__(self, prefs: Preferences | None = None):
        super().__init__()
        self.setWindowTitle("Luthier")
        self._prefs = prefs or Preferences(Preferences.default_path())
        self._prefs.ensure_initialized()
        app = QGuiApplication.instance()
        if app is not None:
            apply_accent_theme(app, self._prefs.accent_color)
        self._app_state = AppState(AppState.default_path())
        self._app_state.load()
        self._folder_start = lambda value: self._app_state.dialog_start_dir(value)
        self._generator = ProjectGenerator(overrides=templates_store.overrides_dir())
        self._defaults = self._prefs.seed_dict()
        self._geom_timer = QTimer(self)
        self._geom_timer.setSingleShot(True)
        self._geom_timer.timeout.connect(self._persist_geometry_to_disk)
        self._status_text = ""
        self._status_ok = True
        self._build_ui()
        self.setMinimumSize(_MIN_WINDOW_WIDTH, _MIN_WINDOW_HEIGHT)
        self._restore_window_geometry()
        if self._generator.error:
            self._set_status(self._generator.error, ok=False)
        elif self._prefs.accent_color_warning:
            self._set_status(self._prefs.accent_color_warning, ok=False)
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
        layout.addWidget(self._build_status_bar())
        self._bottom_bar = self._build_bottom_bar()
        layout.addWidget(self._bottom_bar)
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

    def _on_project_accent_changed(self, color: str) -> None:
        if self._tab_bar.currentIndex() == _PROJECT_TAB_INDEX:
            self._apply_accent_theme(color)

    def _on_prefs_accent_changed(self, color: str) -> None:
        if self._tab_bar.currentIndex() == _PREFS_TAB_INDEX:
            self._apply_accent_theme(color)

    def _apply_accent_theme(self, color: str) -> None:
        app = QGuiApplication.instance()
        if app is not None:
            apply_accent_theme(app, color)
        if self._status_text and self._status_ok:
            self._status._dismiss.set_tone(True)

    def _accent_color_for_tab(self, index: int) -> str:
        if index == _PROJECT_TAB_INDEX:
            return self._project_page.accent_section().color()
        if index == _PREFS_TAB_INDEX:
            return self._prefs_page.accent_section().color()
        return self._project_page.accent_section().color()

    def _on_section_changed(self, index: int) -> None:
        self._stack.setCurrentIndex(index)
        self._btn_stack.setCurrentIndex(index)
        self._bottom_bar.setVisible(index != _ABOUT_TAB_INDEX)
        if index in (_PROJECT_TAB_INDEX, _PREFS_TAB_INDEX):
            self._apply_accent_theme(self._accent_color_for_tab(index))

    def _build_stack(self) -> QStackedWidget:
        stack = QStackedWidget()
        self._project_page = ProjectPage(
            self._defaults, plugin_settings.bundle_id, self._prefs, self._folder_start
        )
        self._prefs_page = PreferencesPage(self._prefs, self._folder_start)
        self._templates_page = TemplatesPage()
        self._about_page = AboutPage()
        stack.addWidget(self._project_page)
        stack.addWidget(self._prefs_page)
        stack.addWidget(self._templates_page)
        stack.addWidget(self._about_page)
        self._project_page.validityChanged.connect(self._refresh_generate_enabled)
        self._project_page.accent_section().colorChanged.connect(self._on_project_accent_changed)
        self._prefs_page.accent_section().colorChanged.connect(self._on_prefs_accent_changed)
        self._stack = stack
        return stack

    def _build_status_bar(self) -> QWidget:
        bar = QWidget()
        bar.setObjectName("StatusBar")
        self._status_bar = bar
        bar.setFixedHeight(0)
        bar.setMaximumHeight(0)
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(
            STATUS_BAR_MARGIN_LEFT,
            STATUS_BAR_V_PAD,
            STATUS_BAR_MARGIN_RIGHT,
            STATUS_BAR_V_PAD,
        )
        layout.setSpacing(ROW_SPACING)
        self._status_heading = StatusMessageHeading()
        self._status = StatusCapsule()
        self._status.dismissed.connect(self._clear_status_message)
        layout.addWidget(self._status_heading, 0, Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self._status, 0, Qt.AlignmentFlag.AlignVCenter)
        layout.addStretch(1)
        return bar

    def _set_status_bar_open(self, open_: bool) -> None:
        height = BAR_MIN_HEIGHT if open_ else 0
        self._status_bar.setFixedHeight(height)
        self._status_bar.setMaximumHeight(height)
        if open_:
            self._status_heading.restart_pulse()
        else:
            self._status_heading.stop_pulse()

    def _clear_status_message(self) -> None:
        self._status_text = ""
        self._status.clear()
        self._set_status_bar_open(False)

    def _build_bottom_bar(self) -> QWidget:
        bar = QWidget()
        bar.setObjectName("BottomBar")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(16, 8, 16, 8)
        self._btn_stack = self._build_button_stack()
        layout.addWidget(self._btn_stack)
        return bar

    def _build_button_stack(self) -> QStackedWidget:
        stack = QStackedWidget()
        stack.addWidget(self._project_buttons())
        stack.addWidget(self._prefs_buttons())
        stack.addWidget(self._templates_buttons())
        stack.addWidget(QWidget())
        return stack

    def _project_buttons(self) -> QWidget:
        self._new_btn = _make_btn("Create New Project", "ActionButton", self._on_create_new_project)
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

    def _schedule_geometry_save(self) -> None:
        self._geom_timer.start(300)

    def _persist_window_geometry(self) -> None:
        if self.isMinimized():
            return
        self._app_state.set_window_maximized(self.isMaximized())
        if self.isMaximized() or self.isFullScreen():
            return
        geo = self.geometry()
        self._app_state.set_window_rect(geo.x(), geo.y(), geo.width(), geo.height())

    def _persist_geometry_to_disk(self) -> None:
        self._persist_window_geometry()
        try:
            self._app_state.save()
        except OSError:
            pass

    def _restore_window_geometry(self) -> None:
        if self._app_state.window_maximized():
            self.showMaximized()
            return
        rect = self._app_state.window_rect()
        if rect and self._rect_is_usable(rect):
            self.setGeometry(rect["x"], rect["y"], rect["width"], rect["height"])
            return
        encoded = self._app_state.window_geometry_b64()
        if encoded and self.restoreGeometry(QByteArray.fromBase64(encoded.encode("ascii"))):
            return
        self.resize(self.minimumWidth(), self.minimumHeight())
        self._center_on_screen()

    def _rect_is_usable(self, rect: dict) -> bool:
        if rect["width"] < self.minimumWidth() or rect["height"] < self.minimumHeight():
            return False
        target = QRect(rect["x"], rect["y"], rect["width"], rect["height"])
        for screen in QGuiApplication.screens():
            if screen.availableGeometry().intersects(target):
                return True
        return False

    def _center_on_screen(self) -> None:
        screen = QGuiApplication.primaryScreen()
        if screen is None:
            return
        frame = self.frameGeometry()
        frame.moveCenter(screen.availableGeometry().center())
        self.move(frame.topLeft())

    def changeEvent(self, event) -> None:
        super().changeEvent(event)
        if event.type() == QEvent.Type.WindowStateChange:
            self._schedule_geometry_save()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._refresh_status_display()
        self._schedule_geometry_save()

    def moveEvent(self, event) -> None:
        super().moveEvent(event)
        self._schedule_geometry_save()

    def closeEvent(self, event) -> None:
        self._geom_timer.stop()
        self._persist_window_geometry()
        try:
            self._app_state.save()
        except OSError:
            pass
        super().closeEvent(event)

    def _remember_prefs_profile_dir(self, path: str) -> None:
        self._app_state.remember_prefs_profile_dir(path)
        try:
            self._app_state.save()
        except OSError:
            pass

    def _on_prefs_import(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Preferences",
            self._app_state.prefs_profile_dir(),
            "JSON (*.json);;All files (*)",
        )
        if not path:
            return
        self._remember_prefs_profile_dir(path)
        ok, message = self._prefs_page.import_from_file(path)
        if ok:
            self._defaults = self._prefs.seed_dict()
            if self._tab_bar.currentIndex() == _PREFS_TAB_INDEX:
                self._apply_accent_theme(self._prefs.accent_color)
            self._set_status(f"Preferences imported from {Path(path).name}.", ok=True)
        else:
            QMessageBox.warning(self, "Import Preferences", message)
            self._set_status("Preferences import failed.", ok=False)

    def _on_prefs_export(self) -> None:
        start_dir = self._app_state.prefs_profile_dir()
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Preferences",
            str(Path(start_dir) / "preferences.json"),
            "JSON (*.json);;All files (*)",
        )
        if not path:
            return
        self._remember_prefs_profile_dir(path)
        ok, message = self._prefs_page.export_to_file(path)
        if ok:
            self._set_status(f"Preferences exported to {Path(path).name}.", ok=True)
        else:
            QMessageBox.warning(self, "Export Preferences", message)
            self._set_status("Preferences export failed.", ok=False)

    def _on_generate(self) -> None:
        spec = self._project_page.spec()
        dest = spec.destination_dir.strip()
        if not dest or not Path(dest).is_dir():
            chosen = QFileDialog.getExistingDirectory(
                self,
                "Choose destination folder",
                self._app_state.dialog_start_dir(dest),
            )
            if not chosen:
                return
            self._project_page.set_destination(chosen)
            spec = self._project_page.spec()
            if not self._project_page.is_valid():
                return
        if not self._confirm_overwrite(spec):
            return
        self._run_generation(spec)

    def _on_create_new_project(self) -> None:
        if self._project_page.is_dirty():
            if not confirm_discard_unsaved(
                self,
                "Create New Project",
                "The project form has unsaved changes. Discard them and start a new project?",
            ):
                return
        self._project_page.reset(self._form_defaults())
        self._project_page.accent_section().set_color(self._prefs.accent_color)
        if self._tab_bar.currentIndex() == _PROJECT_TAB_INDEX:
            self._apply_accent_theme(self._prefs.accent_color)
        self._set_status("New project — defaults from Preferences.", ok=True)

    def _on_open(self) -> None:
        start = self._app_state.dialog_start_dir()
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
        self._app_state.remember_parent(spec.destination_dir)
        try:
            self._app_state.save()
        except OSError as error:
            self._set_status(
                f"Project generated at {project_dir} — could not remember folder: {error}",
                ok=False,
            )
            return
        self._set_status(f"Project generated at {project_dir}", ok=True)

    def _set_status(self, text: str, ok: bool) -> None:
        self._status_text = text
        self._status_ok = ok
        if not text:
            self._clear_status_message()
            return
        self._set_status_bar_open(True)
        self._status.set_message(text, ok)
        self._refresh_status_display()

    def _refresh_status_display(self) -> None:
        if not self._status_text or self._status_bar.height() == 0:
            return
        bar_width = self._status_bar.width()
        max_width = status_capsule_max_width(bar_width)
        if max_width > 0:
            self._status.set_max_width(max_width)
        elif self._status_text:
            self._status.set_message(self._status_text, self._status_ok)
