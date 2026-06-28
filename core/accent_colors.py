"""Preset accent colours for the Luthier UI theme."""

DEFAULT_ACCENT_COLOR = "#A45C94"

# Slot 1 — Projucer default; do not change.
ACCENT_PRESETS: tuple[tuple[str, str], ...] = (
    ("Magenta", "#A45C94"),
    ("Yellow", "#D7A503"),
    ("Orange", "#F56637"),
    ("Brown", "#803E1D"),
    ("Turquoise", "#01BB8B"),
    ("Green", "#009933"),
    ("Dark green", "#006633"),
    ("Light blue", "#3399CC"),
    ("Medium blue", "#3366FF"),
    ("Dark blue", "#3232C3"),
    ("Pink", "#D959B9"),
    ("Violet", "#6113D7"),
)

_VALID_ACCENTS = frozenset(color.upper() for _, color in ACCENT_PRESETS)


def _canonical_hex(value: str) -> str:
    candidate = str(value).strip().upper()
    if not candidate.startswith("#"):
        candidate = f"#{candidate}"
    if len(candidate) == 4:
        candidate = "#" + "".join(ch * 2 for ch in candidate[1:])
    return candidate


def normalize_accent_color(value: str | None) -> str:
    """Return a valid preset hex colour, falling back to the default."""
    if not value:
        return DEFAULT_ACCENT_COLOR
    candidate = _canonical_hex(value)
    if candidate in _VALID_ACCENTS:
        return candidate
    return DEFAULT_ACCENT_COLOR


def is_valid_accent_color(value: str) -> bool:
    """Return True when `value` matches a preset accent colour."""
    return _canonical_hex(value) in _VALID_ACCENTS
