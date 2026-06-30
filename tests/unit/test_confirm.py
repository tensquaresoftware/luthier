"""Tests for themed confirmation dialogs."""

from app.confirm import confirm_discard_unsaved


def test_confirm_discard_unsaved_delegates_to_confirm_yes_no(monkeypatch):
    calls = []

    def fake_confirm_yes_no(parent, title, message, **kwargs):
        calls.append((title, message, kwargs))
        return True

    monkeypatch.setattr("app.confirm.confirm_yes_no", fake_confirm_yes_no)
    assert confirm_discard_unsaved(None, "Title", "Message") is True
    assert calls == [
        (
            "Title",
            "Message",
            {"yes_label": "Yes", "no_label": "No", "default_yes": False},
        )
    ]
