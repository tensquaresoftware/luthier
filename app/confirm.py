"""Themed confirmation dialogs."""

from PySide6.QtWidgets import QMessageBox, QWidget

from app.qss import repolish


def confirm_yes_no(
    parent: QWidget,
    title: str,
    message: str,
    *,
    yes_label: str = "Yes",
    no_label: str = "No",
    default_yes: bool = False,
) -> bool:
    """Return True when the user clicks the affirmative (Yes) button."""
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Icon.Question)
    box.setWindowTitle(title)
    box.setText(message)
    no_btn = box.addButton(no_label, QMessageBox.ButtonRole.NoRole)
    yes_btn = box.addButton(yes_label, QMessageBox.ButtonRole.YesRole)
    default_btn = yes_btn if default_yes else no_btn
    box.setDefaultButton(default_btn)
    no_btn.setObjectName("ActionButton" if not default_yes else "")
    yes_btn.setObjectName("ActionButton" if default_yes else "")
    repolish(no_btn)
    repolish(yes_btn)
    box.exec()
    return box.clickedButton() is yes_btn


def confirm_discard_unsaved(
    parent: QWidget,
    title: str,
    message: str,
) -> bool:
    """Return True if the user chooses to discard unsaved changes (Yes)."""
    return confirm_yes_no(
        parent,
        title,
        message,
        yes_label="Yes",
        no_label="No",
        default_yes=False,
    )
