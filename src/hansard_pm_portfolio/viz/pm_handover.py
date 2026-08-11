"""Plotting functions for project 03 (ROADMAP_PM_HANDOVER.md): what happens
to style and sentiment right around each PM transition. See
viz/topic_heatmap.py's module docstring and ARCHITECTURE.md for why viz
functions are split per project.

UX/dataviz audit B3.1-B3.3, resolved per J.1/J.3: `plot_transition_panels()`
used to show 6 independent numeric y-scales (3 panels x 2 metrics), each
with raw matplotlib-chosen numeric tick labels - inconsistent with project
01's "no raw scale" convention and project 02's heatmap colorbar, which
already only ever shows "low"/"high". Fixed here by (J.3) computing one
shared y-range per metric across all 3 panels (Option A: `sharey`, done
manually since the metric's 2nd axis is a per-panel `twinx()`, not part of
`plt.subplots(sharey=...)`'s own bookkeeping) and (J.1) never rendering a
raw numeric tick anywhere - only a single "low"/"high" pair, shown once, on
the leftmost/rightmost panel. D.4 also drops the marker-shape channel
(circle/square) that used to double up with linestyle to encode the same
"which metric" distinction - linestyle plus each metric's own axis (left
vs right) is enough on its own, bringing the chart down to 2 simultaneous
encodings needing a legend (linestyle for metric, ring for crisis overlap)
instead of 3.
"""

import matplotlib.dates as mdates
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.figure import Figure

from hansard_pm_portfolio import data_access as da
from hansard_pm_portfolio import style
from hansard_pm_portfolio.viz.common import FIGURE_KW, hide_spines, plot_footer

_SIDE_COLOR = {"before": style.SECONDARY, "after": style.ACCENT}


def _plot_side(ax, side_df: pd.DataFrame, y: str, side: str, linestyle: str) -> None:
    """One before/after segment. Never interpolate across the gap: the gap
    is the finding. No marker shape here (D.4): linestyle alone (doubled
    by which axis/panel the series is drawn on) is enough to distinguish
    the 2 metrics without a 3rd simultaneous redundant channel.
    """
    if side_df.empty:
        return
    side_df = side_df.sort_values("days_from_transition")
    ax.plot(
        side_df["days_from_transition"], side_df[y], color=_SIDE_COLOR[side],
        linestyle=linestyle, linewidth=1.6, zorder=3,
    )


def _padded_range(series: pd.Series, pad_frac: float = 0.08) -> tuple[float, float]:
    """[min, max] of `series` padded by `pad_frac` of its span on each
    side, so a point at the series' true extreme doesn't sit right on the
    plotted low/high boundary (J.3: this padded range becomes the one
    shared y-scale for all 3 panels of that metric).
    """
    lo, hi = series.min(), series.max()
    span = (hi - lo) or 1.0
    return lo - span * pad_frac, hi + span * pad_frac


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
        ha="center", va="center", fontsize=style.SOURCE_SIZE, color=style.TEXT_SECONDARY,
        fontfamily=style.BODY_FONT, style="italic",
    )


def plot_transition_panels(windows: pd.DataFrame, transitions: pd.DataFrame) -> Figure:
    """ROADMAP_PM_HANDOVER.md Phase 2/3, visuel principal: 3 panels, one per
    transition, `net_certainty` (left axis, solid line) and `vader_compound`
    (right axis, dashed line) both colored by side (grey-blue before, cyan
    after - never the chart's positive/negative pair, which this
    descriptive project does not use to avoid implying a value judgment).
    A dotted line at day 0 marks the transition itself.

    J.1/J.3: both metrics share ONE y-scale across all 3 panels (computed
    once from `windows`, not per panel), and neither scale ever shows a
    raw numeric tick - only a single qualitative "low"/"high" pair, shown
    once (panel 1's left axis for net certainty, panel 3's right axis for
    VADER), consistent with topic_heatmap.py's colorbar convention.
    """
    style.register_fonts()
    weeks = da.TRANSITION_WINDOW_WEEKS
    metric_a, label_a = da.HANDOVER_METRICS[0]
    metric_b, label_b = da.HANDOVER_METRICS[1]
    range_a = _padded_range(windows[metric_a])
    range_b = _padded_range(windows[metric_b])

    fig, axes = plt.subplots(1, 3, figsize=(8, 4.5), **FIGURE_KW)

    for i, (ax, (_, t)) in enumerate(zip(axes, transitions.iterrows(), strict=True)):
        ax.set_facecolor(style.BACKGROUND)
        ax2 = ax.twinx()
        ax2.set_facecolor("none")

        label = f"{t['before_pm'].split()[-1]} to {t['after_pm'].split()[-1]}"
        panel = windows[windows["transition_label"] == label]
        before = panel[panel["side"] == "before"]
        after = panel[panel["side"] == "after"]

        _plot_side(ax, before, metric_a, "before", "-")
        _plot_side(ax, after, metric_a, "after", "-")
        _plot_side(ax2, before, metric_b, "before", "--")
        _plot_side(ax2, after, metric_b, "after", "--")
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

        # J.3: identical y-limits on every panel's pair of axes (Option A,
        # a manual `sharey` since ax2 is a per-panel twinx(), not something
        # plt.subplots(sharey=...) reaches). J.1: only 2 ticks (the range's
        # own extremes) ever drawn, labeled "low"/"high" - never a raw
        # number - and only on the outermost panel for each metric.
        ax.set_ylim(*range_a)
        ax2.set_ylim(*range_b)
        ax.set_yticks(list(range_a))
        ax2.set_yticks(list(range_b))
        # Explicit "" labels, not just tick_params(labelleft=False) - that
        # only hides matplotlib's auto-generated numeric label visually,
        # the raw number would still be the Text artist's actual content
        # (I.4 checks the real text, not just what's currently visible).
        ax.set_yticklabels(["low", "high"] if i == 0 else ["", ""])
        ax2.set_yticklabels(["low", "high"] if i == len(axes) - 1 else ["", ""])

        ax.tick_params(axis="x", colors=style.TEXT_SECONDARY, labelsize=style.SOURCE_SIZE,
                        length=0)
        ax.tick_params(axis="y", colors=style.SECONDARY, labelsize=style.SOURCE_SIZE, length=0)
        ax2.tick_params(axis="y", colors=style.ACCENT, labelsize=style.SOURCE_SIZE, length=0)
        hide_spines(ax, ax2)

    axes[0].set_ylabel(label_a, fontsize=style.AXIS_SIDE_LABEL_SIZE, color=style.SECONDARY,
                        fontfamily=style.BODY_FONT)
    fig.text(
        0.995, 0.62, label_b, rotation=90, va="center", ha="right",
        fontsize=style.AXIS_SIDE_LABEL_SIZE, color=style.ACCENT, fontfamily=style.BODY_FONT,
    )

    # A pre-existing overlap independent of the audit's own findings, found
    # while regenerating this image: `fig.suptitle()` positions itself
    # using matplotlib's own automatic y (a function of figure height/
    # fontsize), which the other 3 projects' identical-looking titles never
    # use - they all place the title via `fig.text()` at the same fixed
    # `style.TITLE_X`/y pair as everything else on the figure. Here,
    # suptitle's auto-y landed almost exactly on top of the subtitle's
    # hardcoded y=0.905, overlapping in every render regardless of the
    # numeric-scale/legend fixes above. Switched to the same fig.text()
    # convention the other 3 projects use, for the same reason D.1 exists:
    # two independently positioned elements can't be trusted not to
    # collide unless they're placed by the same, consistent mechanism.
    fig.text(
        style.TITLE_X, 0.95, "THE HANDOVER", ha=style.TITLE_HA, fontsize=style.TITLE_SIZE,
        fontweight="bold", color=style.TEXT_PRIMARY, fontfamily=style.TITLE_FONT,
    )
    fig.text(
        style.TITLE_X, 0.905,
        "Style and sentiment, six weeks either side of each new Prime Minister",
        ha=style.TITLE_HA, fontsize=style.SUBTITLE_SIZE, color=style.TEXT_SECONDARY,
        fontfamily=style.SUBTITLE_FONT,
    )
    # D.4: down to 2 simultaneous encodings needing a legend (linestyle for
    # which metric, ring for the crisis-window overlap) - the marker-shape
    # channel that used to double up with linestyle for the same
    # distinction is gone (see _plot_side).
    plot_footer(
        fig, x=0.06, y=0.015, ha="left",
        note="— net certainty (solid, left axis)    -- VADER sentiment (dashed, right axis)"
             "    ○ ring = inside the mini-budget crisis window",
    )
    fig.subplots_adjust(top=0.80, bottom=0.22, left=0.09, right=0.90, wspace=0.75)
    return fig


def plot_transition_timeline(monthly: pd.DataFrame, tenures: pd.DataFrame) -> Figure:
    """ROADMAP_PM_HANDOVER.md Phase 2, visuel secondaire: the full 2019-2026
    timeline in one continuous view, both HANDOVER_METRICS monthly-averaged
    and pooled across all in-scope PMs, transition dates marked - for the
    reader who wants the whole-corpus context rather than 3 isolated zooms.

    J.1 applies here too, not only to the 3-panel main visual: both y-axes
    show a single qualitative "low"/"high" tick pair, never raw numbers.
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
    abbreviated = False
    for i, name in enumerate(tenures["pm_name"]):
        mid = boundaries[i] + (boundaries[i + 1] - boundaries[i]) / 2
        # style.pm_abbreviation() centralizes this - was previously its own
        # 3rd independent (and inconsistent: this copy alone always
        # resolved to the full "Truss", never actually abbreviating to
        # "T") copy of the same rule (D.5/E/I.8).
        label = style.pm_abbreviation(name, boundaries[i], boundaries[i + 1])
        abbreviated = abbreviated or label in style.PM_SHORT_LABEL.values()
        ax.text(mid, 1.0, label, transform=ax.get_xaxis_transform(), ha="center", va="bottom",
                fontsize=style.SOURCE_SIZE, color=style.TEXT_SECONDARY,
                fontfamily=style.BODY_FONT, clip_on=False)

    ax.set_ylabel(label_a, fontsize=style.AXIS_SIDE_LABEL_SIZE, color=style.SECONDARY,
                  fontfamily=style.BODY_FONT)
    ax2.set_ylabel(label_b, fontsize=style.AXIS_SIDE_LABEL_SIZE, color=style.ACCENT,
                   fontfamily=style.BODY_FONT)
    range_a, range_b = _padded_range(monthly[metric_a].dropna()), _padded_range(
        monthly[metric_b].dropna()
    )
    ax.set_ylim(*range_a)
    ax2.set_ylim(*range_b)
    ax.set_yticks(list(range_a))
    ax.set_yticklabels(["low", "high"])
    ax2.set_yticks(list(range_b))
    ax2.set_yticklabels(["low", "high"])
    ax.tick_params(axis="y", colors=style.SECONDARY, labelsize=style.SOURCE_SIZE, length=0)
    ax2.tick_params(axis="y", colors=style.ACCENT, labelsize=style.SOURCE_SIZE, length=0)
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.tick_params(axis="x", colors=style.TEXT_SECONDARY, labelsize=style.SOURCE_SIZE, pad=6)
    hide_spines(ax, ax2)

    fig.suptitle("The same story, without the zoom", x=style.TITLE_X, ha=style.TITLE_HA,
                 fontsize=style.SECONDARY_TITLE_SIZE, color=style.TEXT_PRIMARY,
                 fontfamily=style.TITLE_FONT, fontweight="bold")
    fig.text(0.06, 0.895, "Net certainty and sentiment, monthly average, all 4 PMs, "
             "dotted lines mark each handover", fontsize=style.SOURCE_SIZE,
             color=style.TEXT_SECONDARY, fontfamily=style.SUBTITLE_FONT)
    note = style.pm_abbreviation_note("Liz Truss") if abbreviated else None
    plot_footer(fig, x=0.92, y=0.03, ha="right", note=note)
    fig.subplots_adjust(top=0.80, bottom=0.17, left=0.08, right=0.92)
    return fig
