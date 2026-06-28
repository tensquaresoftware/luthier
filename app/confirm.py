"""Themed confirmation dialogs."""

from PySide6.QtWidgets import QMessageBox, QWidget

from app.qss import repolish


def confirm_discard_unsaved(
    parent: QWidget,
    title: str,
    message: str,
) -> bool:
    """Return True if the user chooses to discard unsaved changes (Yes)."""
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Icon.Question)
    box.setWindowTitle(title)
    box.setText(message)
    keep_btn = box.addButton("No", QMessageBox.ButtonRole.NoRole)
    discard_btn = box.addButton("Yes", QMessageBox.ButtonRole.YesRole)
    box.setDefaultButton(keep_btn)
    keep_btn.setObjectName("ActionButton")
    repolish(keep_btn)
    box.exec()
    return box.clickedButton() is discard_btn
