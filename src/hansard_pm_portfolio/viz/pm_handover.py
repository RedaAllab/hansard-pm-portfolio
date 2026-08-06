"""Plotting functions for project 03 (ROADMAP_PM_HANDOVER.md): what happens
to style and sentiment right around each PM transition. See
viz/topic_heatmap.py's module docstring and ARCHITECTURE.md for why viz
functions are split per project.
"""

import matplotlib.dates as mdates
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator

from hansard_pm_portfolio import data_access as da
from hansard_pm_portfolio import style
from hansard_pm_portfolio.viz.common import FIGURE_KW, hide_spines

_SIDE_COLOR = {"before": style.SECONDARY, "after": style.ACCENT}


def _plot_side(ax, side_df: pd.DataFrame, y: str, side: str, linestyle: str, marker: str) -> None:
    """One before/after segment. Never interpolate across the gap: the gap is the finding."""
    if side_df.empty:
        return
    side_df = side_df.sort_values("days_from_transition")
    ax.plot(
        side_df["days_from_transition"], side_df[y], color=_SIDE_COLOR[side],
        linestyle=linestyle, marker=marker, markersize=4, linewidth=1.3, zorder=3,
    )


def _mark_crisis_overlap(ax, side_df: pd.DataFrame, y: str, crisis_key: str) -> None:
    """Ring any point that falls inside CRISIS_WINDOWS - PM effect and crisis
    effect aren't separable there. See ARCHITECTURE.md §16.
    """
    flagged = side_df[side_df["sitting_date"].apply(lambda d: da.in_crisis_window(d, crisis_key))]
    if flagged.empty:
        return
    ax.scatter(
        flagged["days_from_transition"], flagged[y], s=90, facecolors="none",
        edgecolors=style.TEXT_PRIMARY, linewidths=1.2, zorder=4,
    )


def _empty_side_note(ax, side: str, weeks: int) -> None:
    x = -weeks * 3.5 if side == "before" else weeks * 3.5
    ax.text(
        x, 0.5, "No sittings\n(recess / election)", transform=ax.get_xaxis_transform(),
        ha="center", va="center", fontsize=7, color=style.TEXT_SECONDARY,
        fontfamily=style.BODY_FONT, style="italic",
    )


def plot_transition_panels(windows: pd.DataFrame, transitions: pd.DataFrame) -> Figure:
    """ROADMAP_PM_HANDOVER.md Phase 2/3, visuel principal: 3 panels, one per
    transition, `net_certainty` (left axis, solid circles) and
    `vader_compound` (right axis, dashed squares) both colored by side
    (grey-blue before, cyan after - never the chart's positive/negative
    pair, which this descriptive project does not use to avoid implying a
    value judgment). A dotted line at day 0 marks the transition itself.
    """
    style.register_fonts()
    weeks = da.TRANSITION_WINDOW_WEEKS
    metric_a, label_a = da.HANDOVER_METRICS[0]
    metric_b, label_b = da.HANDOVER_METRICS[1]

    fig, axes = plt.subplots(1, 3, figsize=(8, 4.5), **FIGURE_KW)

    for ax, (_, t) in zip(axes, transitions.iterrows(), strict=True):
        ax.set_facecolor(style.BACKGROUND)
        ax2 = ax.twinx()
        ax2.set_facecolor("none")

        label = f"{t['before_pm'].split()[-1]} to {t['after_pm'].split()[-1]}"
        panel = windows[windows["transition_label"] == label]
        before = panel[panel["side"] == "before"]
        after = panel[panel["side"] == "after"]

        _plot_side(ax, before, metric_a, "before", "-", "o")
        _plot_side(ax, after, metric_a, "after", "-", "o")
        _plot_side(ax2, before, metric_b, "before", "--", "s")
        _plot_side(ax2, after, metric_b, "after", "--", "s")
        _mark_crisis_overlap(ax, before, metric_a, "mini_budget")
        _mark_crisis_overlap(ax2, before, metric_b, "mini_budget")

        if before.empty:
            _empty_side_note(ax, "before", weeks)

        ax.axvline(0, color=style.GRID, linestyle=":", linewidth=1, zorder=1)
        ax.set_xlim(-weeks * 7, weeks * 7)
        ax.set_title(
            f"{t['before_pm'].split()[-1]} → {t['after_pm'].split()[-1]}",
            fontsize=style.PANEL_TITLE_SIZE, color=style.TEXT_PRIMARY,
            fontfamily=style.SUBTITLE_FONT, fontweight="bold", pad=10,
        )
        ax.set_xticks([-weeks * 7, 0, weeks * 7])
        ax.set_xticklabels([f"-{weeks}w", "handover", f"+{weeks}w"])
        ax.yaxis.set_major_locator(MaxNLocator(nbins=4))
        ax2.yaxis.set_major_locator(MaxNLocator(nbins=4))
        ax.tick_params(axis="x", colors=style.TEXT_SECONDARY, labelsize=8, length=0)
        ax.tick_params(axis="y", colors=style.SECONDARY, labelsize=7, length=0)
        ax2.tick_params(axis="y", colors=style.ACCENT, labelsize=7, length=0)
        hide_spines(ax, ax2)

    axes[0].set_ylabel(label_a, fontsize=style.AXIS_SIDE_LABEL_SIZE, color=style.SECONDARY,
                        fontfamily=style.BODY_FONT)
    fig.text(
        0.995, 0.62, label_b, rotation=90, va="center", ha="right",
        fontsize=style.AXIS_SIDE_LABEL_SIZE, color=style.ACCENT, fontfamily=style.BODY_FONT,
    )

    fig.suptitle(
        "THE HANDOVER", x=style.TITLE_X, ha=style.TITLE_HA, fontsize=style.TITLE_SIZE,
        fontweight="bold", color=style.TEXT_PRIMARY, fontfamily=style.TITLE_FONT,
    )
    fig.text(
        style.TITLE_X, 0.905,
        "Style and sentiment, six weeks either side of each new Prime Minister",
        ha=style.TITLE_HA, fontsize=style.SUBTITLE_SIZE, color=style.TEXT_SECONDARY,
        fontfamily=style.SUBTITLE_FONT,
    )
    fig.text(
        0.06, 0.045,
        "● solid = net certainty (left)   ■ dashed = VADER sentiment (right)   "
        "○ ring = inside the mini-budget crisis window",
        fontsize=7, color=style.TEXT_SECONDARY, fontfamily=style.BODY_FONT,
    )
    fig.text(
        0.06, 0.015, "Source: Hansard API · hansard-pm-nlp", ha="left", fontsize=style.SOURCE_SIZE,
        color=style.SECONDARY, fontfamily=style.BODY_FONT,
    )
    fig.subplots_adjust(top=0.80, bottom=0.20, left=0.09, right=0.90, wspace=0.75)
    return fig


def plot_transition_timeline(monthly: pd.DataFrame, tenures: pd.DataFrame) -> Figure:
    """ROADMAP_PM_HANDOVER.md Phase 2, visuel secondaire: the full 2019-2026
    timeline in one continuous view, both HANDOVER_METRICS monthly-averaged
    and pooled across all in-scope PMs, transition dates marked - for the
    reader who wants the whole-corpus context rather than 3 isolated zooms.
    """
    style.register_fonts()
    metric_a, label_a = da.HANDOVER_METRICS[0]
    metric_b, label_b = da.HANDOVER_METRICS[1]

    fig, ax = plt.subplots(figsize=(10, 4), **FIGURE_KW)
    ax.set_facecolor(style.BACKGROUND)
    ax2 = ax.twinx()
    ax2.set_facecolor("none")

    ax.plot(monthly.index, monthly[metric_a], color=style.SECONDARY, linewidth=1.5, label=label_a)
    ax2.plot(monthly.index, monthly[metric_b], color=style.ACCENT, linewidth=1.5, linestyle="--",
             label=label_b)

    for start in tenures["tenure_start"].iloc[1:]:
        ax.axvline(pd.Timestamp(start), color=style.GRID, linestyle=":", linewidth=1, zorder=1)

    chart_end = monthly.index[-1] + pd.DateOffset(months=1)
    boundaries = [pd.Timestamp(s) for s in tenures["tenure_start"]] + [chart_end]
    for i, name in enumerate(tenures["pm_name"]):
        mid = boundaries[i] + (boundaries[i + 1] - boundaries[i]) / 2
        span_months = (boundaries[i + 1] - boundaries[i]).days / 30
        label = "Truss" if span_months < 3 else name.split()[-1]
        ax.text(mid, 1.0, label, transform=ax.get_xaxis_transform(), ha="center", va="bottom",
                fontsize=9, color=style.TEXT_SECONDARY, fontfamily=style.BODY_FONT, clip_on=False)

    ax.set_ylabel(label_a, fontsize=style.AXIS_SIDE_LABEL_SIZE, color=style.SECONDARY,
                  fontfamily=style.BODY_FONT)
    ax2.set_ylabel(label_b, fontsize=style.AXIS_SIDE_LABEL_SIZE, color=style.ACCENT,
                   fontfamily=style.BODY_FONT)
    ax.tick_params(axis="y", colors=style.SECONDARY, labelsize=8, length=0)
    ax2.tick_params(axis="y", colors=style.ACCENT, labelsize=8, length=0)
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.tick_params(axis="x", colors=style.TEXT_SECONDARY, labelsize=9, pad=6)
    hide_spines(ax, ax2)

    fig.suptitle("The same story, without the zoom", x=style.TITLE_X, ha=style.TITLE_HA,
                 fontsize=style.SECONDARY_TITLE_SIZE, color=style.TEXT_PRIMARY,
                 fontfamily=style.TITLE_FONT, fontweight="bold")
    fig.text(0.06, 0.895, "Net certainty and sentiment, monthly average, all 4 PMs, "
             "dotted lines mark each handover", fontsize=9, color=style.TEXT_SECONDARY,
             fontfamily=style.SUBTITLE_FONT)
    fig.subplots_adjust(top=0.80, bottom=0.15, left=0.08, right=0.92)
    return fig
