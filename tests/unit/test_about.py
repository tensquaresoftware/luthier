"""Application release metadata for About."""

from app.version import REVISION_DATE, VERSION


def test_release_metadata():
    assert VERSION == "1.0.0"
    assert REVISION_DATE == "2026-07-01"
