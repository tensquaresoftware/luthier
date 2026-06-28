"""Display helpers for UI-bound string values."""


def display_str(value) -> str:
    return "" if value is None else str(value)
