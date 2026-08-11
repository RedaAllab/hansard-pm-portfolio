"""Shared design-system constants for every portfolio visual (colors, fonts,
sizes), lifted verbatim from STYLE_DUEL.md section 3-4. THEMATIC_HEATMAP.md
(project 02, not yet built) reuses the same PM palette and typography by
importing from this module too - see ARCHITECTURE.md.

Do not hardcode a hex value or font name in a plotting function; import it
from here instead, so the two portfolio projects can't silently drift apart.
"""

from pathlib import Path

import matplotlib.font_manager as fm
import pandas as pd

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

# --- PM abbreviation convention (audit D.5/E, I.5/I.8) -----------------------
# `"T" if span_months < 3 else name.split()[-1]` used to exist identically in
# topic_heatmap.py, pm_handover.py and annual_recap.py (3 independently
# maintained copies of the same rule - I.8 checks there is now exactly one).
# Only Liz Truss's 49-day tenure is short enough to trigger it anywhere in
# the current PM scope, but the mapping is keyed by name rather than
# hardcoded to her specifically, so a future short tenure doesn't silently
# fall through with no abbreviation.
PM_SHORT_LABEL = {"Liz Truss": "T"}
_ABBREVIATE_BELOW_MONTHS = 3.0


def pm_abbreviation(pm_name: str, segment_start, segment_end) -> str:
    """Surname, or a short abbreviation (see PM_SHORT_LABEL) if the segment
    this label is drawn inside (`segment_start` to `segment_end` - a PM
    frieze band, a year-card's PM band) is under `_ABBREVIATE_BELOW_MONTHS`
    wide, too narrow for the full surname to read cleanly.

    Takes the segment boundaries (not a pre-computed `span_months` float)
    so the "how many months is this segment" computation lives in exactly
    one place (I.8) - it used to be copy-pasted independently into
    topic_heatmap.py, pm_handover.py and annual_recap.py (3 near-identical
    `span_months = (end - start).days / 30` lines feeding 3 near-identical
    `"T" if span_months < 3 else ...` decisions).

    Centralizes the label decision so every image that abbreviates a PM
    also has a caption for it, via `pm_abbreviation_note()` - never
    abbreviate without one (D.5/I.5).
    """
    span_months = (pd.Timestamp(segment_end) - pd.Timestamp(segment_start)).days / 30
    if span_months < _ABBREVIATE_BELOW_MONTHS:
        return PM_SHORT_LABEL.get(pm_name, pm_name.split()[-1][:1])
    return pm_name.split()[-1]


def pm_abbreviation_note(pm_name: str, tenure_days: int | None = None) -> str:
    """On-image legend text for an abbreviated PM label (D.5) - e.g.
    "T = Liz Truss (49 days)". Always pair a `pm_abbreviation()` call that
    can actually produce a non-surname short label with this note rendered
    somewhere on the same figure (a footer/caption), not only in the
    README prose beside it.
    """
    short = PM_SHORT_LABEL.get(pm_name, pm_name.split()[-1][:1])
    if tenure_days is not None:
        return f"{short} = {pm_name} ({tenure_days} days)"
    return f"{short} = {pm_name}"

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
# UX/dataviz audit D.3/I.3: every *_SIZE constant here must be >=9pt, no
# silent exceptions - an exception would need to be whitelisted here with a
# comment referencing STYLE_DUEL.md section 7's stated 9pt floor. None is
# currently whitelisted: TICK_SIZE (8->9) and CARD_BODY_SIZE/
# CARD_CAPTION_SIZE (7.5/6.5->9, audit B4/J.2) were the 3 violations found
# and are fixed below rather than exempted.
TITLE_SIZE = 20
SUBTITLE_SIZE = 12
AXIS_LABEL_SIZE = 11
TICK_SIZE = 9
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
# Audit J.2: raised from 7.5/6.5 to the 9pt floor. On their own this makes
# each card's wrapped theme text taller (fewer characters fit per line at
# the same card width), which is why J.2 pairs this with (a) a taller
# annual_recap_main.png canvas (viz/annual_recap.py's figsize) and (b)
# viz/common.py's fit_text_to_width() computing an explicit ellipsis
# fallback instead of assuming this size still fits any theme in 3 lines.
CARD_BODY_SIZE = 9
CARD_CAPTION_SIZE = 9
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
