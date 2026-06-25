"""Pure helpers for project form seeding and dirty-state comparison (no Qt)."""

from core.project_spec import ProjectSpec

_IDENTITY_RESET = {
    "projectName": "",
    "projectDisplayName": "",
    "projectVersion": "1.0.0",
}


def new_project_seed(defaults: dict) -> dict:
    """Merge preferences profile snapshot with cleared identity fields."""
    return {**defaults, **_IDENTITY_RESET}


def _normalize_snapshot(snapshot: dict) -> dict:
    """Apply ProjectInfoPage display-name fallback for stable comparison."""
    normalized = dict(snapshot)
    display = str(normalized.get("projectDisplayName", "")).strip()
    name = str(normalized.get("projectName", "")).strip()
    if not display:
        normalized["projectDisplayName"] = name
    return normalized


def form_snapshots_equal(baseline: dict, current: dict) -> bool:
    """Return True when two ProjectSpec snapshots represent the same form state."""
    left = _normalize_snapshot(baseline)
    right = _normalize_snapshot(current)
    keys = ProjectSpec().to_dict().keys()
    return all(left.get(key) == right.get(key) for key in keys)
