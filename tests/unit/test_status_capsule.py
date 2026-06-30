"""Regression tests for status capsule accessibility announcements."""

import pytest
from PySide6.QtWidgets import QApplication, QWidget

from app.widgets.status_capsule import StatusCapsule, _announce_status


@pytest.fixture(scope="session")
def qapp():
    application = QApplication.instance()
    if application is None:
        application = QApplication([])
    return application


def test_announce_error_status_does_not_raise(qapp):
    host = QWidget()
    capsule = StatusCapsule(host)
    _announce_status(capsule, "Preferences file was corrupt and has been reset to defaults.", ok=False)
