"""Preset accent colours for the Luthier UI theme."""

DEFAULT_ACCENT_COLOR = "#A45C94"

ACCENT_PRESETS: tuple[tuple[str, str], ...] = (
    ("Magenta", "#A45C94"),
    ("Orange", "#B85818"),
    ("Jaune", "#807010"),
    ("Vert clair", "#368036"),
    ("Vert foncé", "#287848"),
    ("Turquoise", "#147C74"),
    ("Cyan", "#168098"),
    ("Bleu pétrole", "#1A6478"),
    ("Bleu marine", "#2E5088"),
    ("Fuchsia", "#C83098"),
    ("Violet", "#7040B0"),
    ("Marron", "#7A5538"),
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
