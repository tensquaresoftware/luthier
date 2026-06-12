"""Qt stylesheet helpers."""

from PySide6.QtWidgets import QWidget


def repolish(widget: QWidget) -> None:
    """Re-apply the stylesheet after an object name or dynamic property change."""
    widget.style().unpolish(widget)
    widget.style().polish(widget)
