"""Plotting function for project 04 (ROADMAP_ANNUAL_RECAP.md /
ANNUAL_RECAP.md): the whole corpus, one card per calendar year. See
ANNUAL_RECAP.md for the composition decisions this module follows.
"""

import textwrap

import matplotlib.dates as mdates
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle

from hansard_pm_portfolio import style
from hansard_pm_portfolio.viz.common import FIGURE_KW, hide_spines

_CARD_WIDTH_FLOOR = 0.5


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
        span_months = (seg_end - seg_start).days / 30
        mid = seg_start + (seg_end - seg_start) / 2
        # Truss's 49-day segment is too narrow for her full name - same "T"
        # abbreviation convention as viz/topic_heatmap.py's own PM frieze.
        label = row["pm_name"].split()[-1] if span_months >= 3 else "T"
        fontsize = 10 if span_months >= 3 else 8
        ax.text(mid, 0.5, label, ha="center", va="center", fontsize=fontsize, fontweight="bold",
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

    theme_lines = textwrap.wrap(row.dominant_theme, width=16)[:3]
    ax.text(0.5, 0.62, "\n".join(theme_lines), ha="center", va="top", fontsize=style.CARD_BODY_SIZE,
            color=style.TEXT_PRIMARY, fontfamily=style.BODY_FONT, linespacing=1.35)

    bar_y, bar_h = 0.40, 0.05
    ax.plot([0.1, 0.9], [bar_y + bar_h / 2, bar_y + bar_h / 2], color=style.GRID, linewidth=1,
            zorder=1)
    bar_width = 0.8 * (row.word_count / max_word_count)
    ax.add_patch(Rectangle((0.1, bar_y), bar_width, bar_h, facecolor=style.SECONDARY, zorder=2))

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
    """
    style.register_fonts()
    fig = plt.figure(figsize=(12, 5), **FIGURE_KW)
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
             fontsize=7, color=style.TEXT_SECONDARY, fontfamily=style.BODY_FONT)
    fig.text(0.97, 0.035, "Source: Hansard API · hansard-pm-nlp", ha="right",
              fontsize=style.SOURCE_SIZE, color=style.SECONDARY, fontfamily=style.BODY_FONT)
    return fig
