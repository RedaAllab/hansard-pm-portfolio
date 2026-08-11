"""Plotting function for project 04 (ROADMAP_ANNUAL_RECAP.md /
ANNUAL_RECAP.md): the whole corpus, one card per calendar year. See
ANNUAL_RECAP.md for the composition decisions this module follows.

UX/dataviz audit B4.1-B4.5 (CRITICAL, priority 1): the previous
`_draw_year_card()` wrapped `dominant_theme` at a fixed character width
independent of the card's actual (variable, per `_card_width_ratios()`)
physical width, and positioned it at a fixed y with no relationship to the
word-volume bar's own fixed y - the two silently overlapped for any theme
long enough to fill 3 wrapped lines. Fixed per C.1/J.2: `fit_text_to_width()`
measures the real card width; the bar's position stays fixed (so bars stay
horizontally comparable across cards, ANNUAL_RECAP.md's own point), and the
theme text's start position is what now varies per card, computed from the
real rendered text-block height so its bottom edge keeps a fixed minimum
gap above the bar - never the reverse.
"""

import matplotlib.dates as mdates
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle

from hansard_pm_portfolio import style
from hansard_pm_portfolio.viz import common
from hansard_pm_portfolio.viz.common import FIGURE_KW, hide_spines

_CARD_WIDTH_FLOOR = 0.5

# Year-card internal layout constants (audit C.1/D.1: named and derived
# from each other rather than left as independent magic numbers that can
# silently drift apart, which is exactly what caused B4.1-B4.4).
_CARD_BAR_Y, _CARD_BAR_H = 0.40, 0.05
_CARD_THEME_TOP = 0.78  # never starts higher than this (PM band bottom is 0.80)
_CARD_THEME_MAX_WIDTH_FRAC = 0.86
_CARD_TEXT_BAR_GAP = 0.05  # min axes-fraction gap kept between theme text and bar


def _card_width_ratios(recap: pd.DataFrame) -> list[float]:
    """1.0 for a fully-covered year; `coverage_fraction` (floored at
    `_CARD_WIDTH_FLOOR` so a sparse year stays readable) for a partial one -
    ANNUAL_RECAP.md section 4: card width itself carries the "partial year"
    signal, not only the caption inside it.
    """
    return [
        1.0 if not row.is_partial_year else max(row.coverage_fraction, _CARD_WIDTH_FLOOR)
        for row in recap.itertuples()
    ]


def _draw_pm_band(ax, segments: list[tuple[str, float]], y0: float, height: float) -> None:
    """Stacked PM-tenure segments, left to right. A PM whose tenure only
    partly overlaps the period drawn (a year-card's year, or the header's
    full 2019-2026 span) leaves the rest of the band unfilled rather than
    stretched, matching `yearly_pm_segments()`'s own docstring.
    """
    ax.add_patch(
        Rectangle((0, y0), 1, height, fill=False, edgecolor=style.GRID, linewidth=0.6,
                  linestyle=":", zorder=1)
    )
    cursor = 0.0
    for pm, share in segments:
        ax.add_patch(
            Rectangle((cursor, y0), share, height, facecolor=style.PM_COLORS[pm],
                      edgecolor=style.BACKGROUND, linewidth=0.5, zorder=2)
        )
        cursor += share


def _draw_header(ax, tenures: pd.DataFrame, year_bounds: tuple[pd.Timestamp, pd.Timestamp]) -> None:
    """The full 2019-2026 PM frieze: one continuous version of the same
    segmented-band encoding each year-card uses below it, so the header
    reads as a zoomed-out summary, not a different visual language
    (ANNUAL_RECAP.md section 4).
    """
    start, end = year_bounds
    for _, row in tenures.iterrows():
        seg_start = max(pd.Timestamp(row["tenure_start"]), start)
        seg_end = min(pd.Timestamp(row["tenure_end"]), end)
        if seg_end <= seg_start:
            continue
        ax.axvspan(seg_start, seg_end, color=style.PM_COLORS[row["pm_name"]], zorder=2)
        mid = seg_start + (seg_end - seg_start) / 2
        # style.pm_abbreviation() centralizes the abbreviation rule shared
        # with viz/topic_heatmap.py's and viz/pm_handover.py's own PM
        # friezes (audit D.5/E/I.8: was 3 independent copies of the same
        # "abbreviate to a single letter below a 3-month-wide segment"
        # calculation - I.8 checks that calculation now lives only in
        # style.py, not duplicated here).
        label = style.pm_abbreviation(row["pm_name"], seg_start, seg_end)
        ax.text(mid, 0.5, label, ha="center", va="center", fontsize=10, fontweight="bold",
                color=style.BACKGROUND, fontfamily=style.SUBTITLE_FONT, zorder=3)
    for _, row in tenures.iloc[1:].iterrows():
        ax.axvline(pd.Timestamp(row["tenure_start"]), color=style.BACKGROUND, linewidth=1.2,
                   zorder=4)

    ax.set_xlim(start, end)
    ax.set_ylim(0, 1)
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.tick_params(axis="x", colors=style.TEXT_SECONDARY, labelsize=8, length=0, pad=4)
    ax.set_yticks([])
    hide_spines(ax)


def _draw_year_card(ax, row, tone_range: tuple[float, float], max_word_count: int) -> None:
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_facecolor("none")
    hide_spines(ax)
    ax.set_xticks([])
    ax.set_yticks([])

    ax.text(0.5, 1.05, str(row.year), ha="center", va="bottom", fontsize=style.CARD_YEAR_SIZE,
            fontweight="bold", color=style.TEXT_PRIMARY, fontfamily=style.SUBTITLE_FONT,
            transform=ax.transAxes)
    if row.is_partial_year:
        ax.text(0.5, 0.955, "partial year", ha="center", va="bottom",
                fontsize=style.CARD_CAPTION_SIZE, color=style.TEXT_SECONDARY,
                fontfamily=style.BODY_FONT, style="italic")

    _draw_pm_band(ax, row.pm_segments, y0=0.80, height=0.10)

    # fit_text_to_width measures THIS card's real rendered width (which
    # varies with _card_width_ratios(), unlike the old fixed
    # textwrap.wrap(..., width=16)) and falls back to an explicit ellipsis
    # rather than a silent [:3] cutoff if the theme still doesn't fit.
    theme_lines = common.fit_text_to_width(
        ax, row.dominant_theme, max_width_frac=_CARD_THEME_MAX_WIDTH_FRAC,
        fontsize=style.CARD_BODY_SIZE, max_lines=3,
    )
    theme_artist = ax.text(
        0.5, _CARD_THEME_TOP, "\n".join(theme_lines), ha="center", va="top",
        fontsize=style.CARD_BODY_SIZE, color=style.TEXT_PRIMARY,
        fontfamily=style.BODY_FONT, linespacing=1.35, gid="theme_text",
    )
    # Measure the real rendered block height, then move the text (not the
    # bar) so the two never touch regardless of how many lines this card's
    # theme needed - the bar stays at the same fixed y across every card so
    # word-volume bars remain horizontally comparable (D.1, C.1).
    renderer = common._get_renderer(ax.figure)
    block_bbox = theme_artist.get_window_extent(renderer=renderer).transformed(
        ax.transData.inverted()
    )
    block_height = block_bbox.y1 - block_bbox.y0
    y_start = min(_CARD_THEME_TOP, _CARD_BAR_Y + _CARD_BAR_H + _CARD_TEXT_BAR_GAP + block_height)
    theme_artist.set_position((0.5, y_start))

    bar_y, bar_h = _CARD_BAR_Y, _CARD_BAR_H
    ax.plot([0.1, 0.9], [bar_y + bar_h / 2, bar_y + bar_h / 2], color=style.GRID, linewidth=1,
            zorder=1)
    bar_width = 0.8 * (row.word_count / max_word_count)
    bar_patch = Rectangle((0.1, bar_y), bar_width, bar_h, facecolor=style.SECONDARY, zorder=2)
    bar_patch.set_gid("word_bar")
    ax.add_patch(bar_patch)

    ax.text(0.5, 0.28, f"{row.word_count / 1000:.0f}k", ha="center", va="bottom",
            fontsize=style.CARD_NUMBER_SIZE, fontweight="bold", color=style.SECONDARY,
            fontfamily=style.NUMBER_FONT)
    ax.text(0.5, 0.235, "words", ha="center", va="top", fontsize=style.CARD_CAPTION_SIZE,
            color=style.TEXT_SECONDARY, fontfamily=style.BODY_FONT)

    tone_min, tone_max = tone_range
    span = tone_max - tone_min or 1.0
    frac = (row.net_certainty - tone_min) / span
    y_scale = 0.06
    ax.plot([0.1, 0.9], [y_scale, y_scale], color=style.GRID, linewidth=1, zorder=1)
    ax.plot(0.1 + frac * 0.8, y_scale, marker="o", markersize=5, color=style.ACCENT, zorder=2)


def plot_annual_recap(recap: pd.DataFrame, tenures: pd.DataFrame) -> Figure:
    """ANNUAL_RECAP.md section 4: header frieze + 8 year-cards, one figure,
    one `GridSpec` composition rather than several figures assembled after
    the fact.

    Canvas height raised from 5 to 5.8in (audit J.2): `top`/`bottom` stay
    the same *fractions* of the figure, so a taller figure gives every
    fixed-point-size element (CARD_BODY_SIZE etc, now at the 9pt floor) a
    larger absolute pixel budget within the same axes-fraction share -
    mechanically easing the vertical pressure `_draw_year_card()` measures
    around, rather than relying on that measurement alone.
    """
    style.register_fonts()
    fig = plt.figure(figsize=(12, 5.8), **FIGURE_KW)
    outer = fig.add_gridspec(2, 1, height_ratios=[1, 4.2], hspace=0.65, top=0.80, bottom=0.14,
                              left=0.03, right=0.97)

    header_bounds = (pd.Timestamp(f"{recap['year'].min()}-01-01"),
                      pd.Timestamp(f"{recap['year'].max() + 1}-01-01"))
    ax_header = fig.add_subplot(outer[0])
    ax_header.set_facecolor(style.BACKGROUND)
    _draw_header(ax_header, tenures, header_bounds)

    width_ratios = _card_width_ratios(recap)
    inner = outer[1].subgridspec(1, len(recap), width_ratios=width_ratios, wspace=0.12)
    tone_range = (recap["net_certainty"].min(), recap["net_certainty"].max())
    max_word_count = recap["word_count"].max()
    for i, row in enumerate(recap.itertuples()):
        ax = fig.add_subplot(inner[i])
        ax.set_facecolor(style.BACKGROUND)
        _draw_year_card(ax, row, tone_range, max_word_count)

    fig.text(style.TITLE_X, 0.94, "THE RECAP", ha=style.TITLE_HA, fontsize=style.TITLE_SIZE,
              fontweight="bold", color=style.TEXT_PRIMARY, fontfamily=style.TITLE_FONT)
    fig.text(style.TITLE_X, 0.895, "7 years of British politics, one card per year",
              ha=style.TITLE_HA, fontsize=style.SUBTITLE_SIZE, color=style.TEXT_SECONDARY,
              fontfamily=style.SUBTITLE_FONT)
    fig.text(style.TITLE_X, 0.035,
             "● tone marker = mean net certainty for the year, scaled across all 8 years",
             fontsize=style.SOURCE_SIZE, color=style.TEXT_SECONDARY, fontfamily=style.BODY_FONT)

    # D.5/I.5: the header frieze and any transition-year card may abbreviate
    # a PM to a single letter (style.pm_abbreviation()) when a segment is
    # under 3 months wide - only Liz Truss's 49-day tenure currently
    # triggers it. Whenever that PM is present, the abbreviation gets an
    # on-image legend note via plot_footer(), never only the README prose.
    truss = tenures[tenures["pm_name"] == "Liz Truss"]
    note = None
    if not truss.empty:
        tenure_days = (pd.Timestamp(truss.iloc[0]["tenure_end"])
                        - pd.Timestamp(truss.iloc[0]["tenure_start"])).days
        note = style.pm_abbreviation_note("Liz Truss", tenure_days=tenure_days)
    common.plot_footer(fig, x=0.97, y=0.035, ha="right", note=note)
    return fig
