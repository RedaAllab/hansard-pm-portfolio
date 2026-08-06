"""Shared design-system constants for every portfolio visual (colors, fonts,
sizes), lifted verbatim from STYLE_DUEL.md section 3-4. THEMATIC_HEATMAP.md
(project 02, not yet built) reuses the same PM palette and typography by
importing from this module too - see ARCHITECTURE.md.

Do not hardcode a hex value or font name in a plotting function; import it
from here instead, so the two portfolio projects can't silently drift apart.
"""

from pathlib import Path

import matplotlib.font_manager as fm

# --- Palette (STYLE_DUEL.md section 3) -------------------------------------

BACKGROUND = "#0E1117"
SURFACE = "#262730"
TEXT_PRIMARY = "#FAFAFA"
TEXT_SECONDARY = "#9CA3AF"
GRID = "#3A3D46"
ACCENT = "#22D3EE"
SECONDARY = "#7C89A6"
POSITIVE = "#4A90D9"  # reserved, unused by this project
NEGATIVE = "#D9764A"  # reserved, unused by this project

# Okabe-Ito subset, one color per PM. Truss is dashed (STYLE_DUEL.md section
# 3: line style always doubles the color coding, never color-only).
PM_COLORS = {
    "Boris Johnson": "#E69F00",
    "Liz Truss": "#56B4E9",
    "Rishi Sunak": "#009E73",
    "Keir Starmer": "#CC79A7",
}
PM_LINESTYLES = {
    "Boris Johnson": "-",
    "Liz Truss": "--",
    "Rishi Sunak": "-",
    "Keir Starmer": "-",
}
TRUSS_CAVEAT = "* 49 day tenure, read with caution"

# Sequential scale for the confusion-matrix heatmap (section 6, visuel 2):
# Cividis, colorblind-safe by design.
SEQUENTIAL_CMAP = "cividis"

# --- Typography (STYLE_DUEL.md section 4) -----------------------------------
# Static instances of the Google Fonts variable families, pinned to the exact
# weight the spec asks for (fontTools varLib.instancer - see
# assets/fonts/README.md) so matplotlib resolves a single, unambiguous
# family name per weight instead of guessing an instance out of a variable
# font, which it does not do reliably.

FONT_DIR = Path(__file__).resolve().parents[2] / "assets" / "fonts"

TITLE_FONT = "Lora"  # 700/Bold - Lora-Bold.ttf
SUBTITLE_FONT = "Inter SemiBold"  # 600 - Inter-SemiBold.ttf
BODY_FONT = "Inter"  # 400/Regular - Inter-Regular.ttf
NUMBER_FONT = "IBM Plex Mono Medium"  # 500 - IBMPlexMono-Medium.ttf

_FONT_FILES = (
    "Lora-Bold.ttf",
    "Inter-SemiBold.ttf",
    "Inter-Regular.ttf",
    "IBMPlexMono-Medium.ttf",
)

# Sizes in points, by usage (STYLE_DUEL.md section 5-6).
TITLE_SIZE = 20
SUBTITLE_SIZE = 12
AXIS_LABEL_SIZE = 11
TICK_SIZE = 8
LEGEND_SIZE = 11
SOURCE_SIZE = 9
NUMBER_SIZE = 10

# THEMATIC_HEATMAP.md section 6: topic-row labels and year ticks are 10pt,
# distinct from STYLE_DUEL.md's 11pt axis labels; crisis-window labels are
# 9pt like a source note.
TOPIC_LABEL_SIZE = 10
CRISIS_LABEL_SIZE = 9

# Projects 03-04's smaller compositions (panels, year-cards) - named rather
# than left as inline numbers, same rule as above.
SECONDARY_TITLE_SIZE = 14
PANEL_TITLE_SIZE = 11
AXIS_SIDE_LABEL_SIZE = 9
CARD_YEAR_SIZE = 13
CARD_BODY_SIZE = 7.5
CARD_CAPTION_SIZE = 6.5
CARD_NUMBER_SIZE = 12

# --- Layout ------------------------------------------------------------------
# Every flagship visual's title/subtitle sits at the same x, left-aligned -
# the house convention already used by most secondary visuals, now applied
# to the 4 main ones too so they read as one system when viewed in sequence.
TITLE_X = 0.06
TITLE_HA = "left"

_fonts_registered = False


def register_fonts() -> None:
    """Register the four static font files with matplotlib's font manager.

    Idempotent and safe to call at import time or per-figure - addfont() on
    an already-registered file just re-registers the same family, it does
    not duplicate or error.
    """
    global _fonts_registered
    for filename in _FONT_FILES:
        path = FONT_DIR / filename
        if not path.exists():
            raise FileNotFoundError(
                f"Missing font file {path}. Fonts are committed under "
                "assets/fonts/ - did you check out that directory?"
            )
        fm.fontManager.addfont(str(path))
    _fonts_registered = True


def contrast_ratio(hex_a: str, hex_b: str) -> float:
    """WCAG relative-luminance contrast ratio between two hex colors.

    Used by tests/test_style.py to hold the palette to STYLE_DUEL.md section
    7's stated thresholds (4.5:1 for body text, checked here rather than
    trusted by eye) rather than for runtime plotting.
    """

    def _linear(channel: float) -> float:
        c = channel / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    def _luminance(hex_color: str) -> float:
        h = hex_color.lstrip("#")
        r, g, b = (int(h[i : i + 2], 16) for i in (0, 2, 4))
        rl, gl, bl = _linear(r), _linear(g), _linear(b)
        return 0.2126 * rl + 0.7152 * gl + 0.0722 * bl

    l_a, l_b = _luminance(hex_a), _luminance(hex_b)
    lighter, darker = max(l_a, l_b), min(l_a, l_b)
    return (lighter + 0.05) / (darker + 0.05)
