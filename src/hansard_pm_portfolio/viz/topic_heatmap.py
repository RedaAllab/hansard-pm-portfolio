"""Plotting functions for project 02 (THEMATIC_HEATMAP.md): the topic
heatmap and its two secondary visuals. See viz/style_duel.py's module
docstring and ARCHITECTURE.md for why viz functions are split per project.
"""

import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.figure import Figure

from hansard_pm_portfolio import data_access as da
from hansard_pm_portfolio import style
from hansard_pm_portfolio.viz.common import FIGURE_KW, fit_text_to_width, hide_spines, plot_footer


def _month_edges(monthly: pd.DataFrame) -> tuple[float, float]:
    """Numeric x-extent for imshow: first month's start to one month past
    the last, so each column represents one calendar month's mean weight.
    """
    start = mdates.date2num(monthly.index[0])
    end = mdates.date2num(monthly.index[-1] + pd.DateOffset(months=1))
    return start, end


def _draw_crisis_windows(ax, y_top: float, x_start: float, x_end: float) -> None:
    """Grey overlay bands + a short label above each (THEMATIC_HEATMAP.md
    section 3/6). `y_top` is the y-coordinate of the plot's top edge (0 for
    the main heatmap's row-index axis) - labels sit just above it.

    Labels are wider than their own window (narrow windows like mini_budget
    span barely a month), so two fixes keep them from colliding: alternating
    height by index (mini_budget and ukraine_invasion are 4 months apart -
    close enough that same-height labels overlap) and edge-aware horizontal
    alignment (labour_leadership_crisis sits at the chart's own right edge,
    so centering its label would run it off the canvas).
    """
    span = x_end - x_start
    for i, (key, (start, end)) in enumerate(da.CRISIS_WINDOWS.items()):
        start_ts, end_ts = pd.Timestamp(start), pd.Timestamp(end)
        ax.axvspan(start_ts, end_ts, color=style.SURFACE, alpha=0.4, zorder=2, lw=0)
        mid = start_ts + (end_ts - start_ts) / 2
        mid_frac = (mdates.date2num(mid) - x_start) / span
        ha = "left" if mid_frac < 0.08 else "right" if mid_frac > 0.92 else "center"
        y = y_top - (0.35 if i % 2 == 0 else 0.85)
        ax.text(
            mid, y, da.CRISIS_LABELS[key], ha=ha, va="bottom",
            fontsize=style.CRISIS_LABEL_SIZE, color=style.TEXT_SECONDARY,
            fontfamily=style.BODY_FONT, clip_on=False,
        )


def _draw_pm_transitions(
    ax, tenures: pd.DataFrame, chart_end: pd.Timestamp, y_bottom: float
) -> None:
    """Dotted vertical line at each PM transition (skipping the first PM's
    start - that's the chart's own left edge, same convention as app.py's
    `pm_transitions.iloc[1:]`) plus a name label centered in each PM's
    segment, below the x-axis. Truss's 49-day segment is too narrow for her
    full name - THEMATIC_HEATMAP.md's own ASCII mockup abbreviates her to
    "T", followed here.
    """
    starts = tenures["tenure_start"].tolist()
    names = tenures["pm_name"].tolist()

    for start in starts[1:]:
        ax.axvline(pd.Timestamp(start), color=style.SECONDARY, linestyle=":",
                   linewidth=1, zorder=4)

    boundaries = [pd.Timestamp(s) for s in starts] + [chart_end]
    for i, name in enumerate(names):
        mid = boundaries[i] + (boundaries[i + 1] - boundaries[i]) / 2
        # style.pm_abbreviation() centralizes this rule (D.5/E/I.8) - was
        # previously its own copy identical to annual_recap.py's.
        label = style.pm_abbreviation(name, boundaries[i], boundaries[i + 1])
        ax.text(
            mid, y_bottom, label, ha="center", va="top", fontsize=style.TOPIC_LABEL_SIZE,
            color=style.TEXT_SECONDARY, fontfamily=style.BODY_FONT, clip_on=False,
        )


def plot_topic_heatmap(monthly: pd.DataFrame, tenures: pd.DataFrame) -> Figure:
    """THEMATIC_HEATMAP.md section 6, visuel principal: 13 topics x month,
    Cividis, crisis windows + PM transitions overlaid.

    Audit B2.1: `subplots_adjust(bottom=0.26)` plus the horizontal
    colorbar's own `pad=0.22` left roughly 35-40% of the figure as dead
    vertical space below the heatmap. Figure height cut from 6 to 5.3in
    and the colorbar's pad reduced from 0.22 to 0.14 - `bottom` stays the
    same fraction, so the heatmap itself and the PM-transition labels
    beneath it keep the same relative layout, just without the empty
    margin under the colorbar.
    """
    style.register_fonts()
    n_topics = monthly.shape[1]

    fig, ax = plt.subplots(figsize=(12, 5.3), **FIGURE_KW)
    ax.set_facecolor(style.BACKGROUND)

    x_start, x_end = _month_edges(monthly)
    im = ax.imshow(
        monthly.T.values, cmap=style.SEQUENTIAL_CMAP, aspect="auto",
        extent=[x_start, x_end, n_topics, 0], vmin=0, vmax=monthly.values.max(),
    )
    # Subtle 0.3pt cell borders in the background color (section 6) - drawn
    # as a light grid over the image rather than per-cell patches, since
    # imshow doesn't expose per-cell edges.
    for i in range(n_topics + 1):
        ax.axhline(i, color=style.BACKGROUND, linewidth=0.3, zorder=3)

    ax.set_yticks(np.arange(n_topics) + 0.5)
    ax.set_yticklabels(monthly.columns, fontsize=style.TOPIC_LABEL_SIZE, color=style.TEXT_PRIMARY,
                        fontfamily=style.BODY_FONT, ha="right")
    ax.tick_params(axis="y", length=0, pad=8)

    ax.xaxis_date()
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.tick_params(axis="x", colors=style.TEXT_SECONDARY, labelsize=style.TOPIC_LABEL_SIZE, pad=6)
    ax.set_xlim(x_start, x_end)

    hide_spines(ax)

    chart_end = monthly.index[-1] + pd.DateOffset(months=1)
    _draw_crisis_windows(ax, y_top=0, x_start=x_start, x_end=x_end)
    # Well below the year ticks (n_topics + ~1) rather than right against
    # them, which otherwise reads as one crowded line of text.
    _draw_pm_transitions(ax, tenures, chart_end, y_bottom=n_topics + 1.9)

    fig.text(style.TITLE_X, 0.95, "THE THEMATIC HEATMAP", ha=style.TITLE_HA,
              fontsize=style.TITLE_SIZE, fontweight="bold", color=style.TEXT_PRIMARY,
              fontfamily=style.TITLE_FONT)
    fig.text(style.TITLE_X, 0.91, "7 years of British politics, month by month",
              ha=style.TITLE_HA, fontsize=style.SUBTITLE_SIZE, color=style.TEXT_SECONDARY,
              fontfamily=style.SUBTITLE_FONT)

    fig.subplots_adjust(top=0.84, bottom=0.26, left=0.30, right=0.95)

    cbar = fig.colorbar(im, ax=ax, orientation="horizontal", fraction=0.04, pad=0.20,
                         aspect=40)
    cbar.set_ticks([0, monthly.values.max()])
    cbar.set_ticklabels(["low", "high"])
    cbar.ax.tick_params(colors=style.TEXT_SECONDARY, labelsize=style.CRISIS_LABEL_SIZE)
    cbar.outline.set_visible(False)

    # D.5/I.5: the PM-transition labels below the heatmap may abbreviate a
    # PM to "T" (style.pm_abbreviation(), only Liz Truss's 49-day tenure
    # currently triggers it) - legend it on-image whenever that happens,
    # via plot_footer(), not only in the surrounding README prose.
    truss = tenures[tenures["pm_name"] == "Liz Truss"]
    note = None
    if not truss.empty:
        tenure_days = (pd.Timestamp(truss.iloc[0]["tenure_end"])
                        - pd.Timestamp(truss.iloc[0]["tenure_start"])).days
        note = style.pm_abbreviation_note("Liz Truss", tenure_days=tenure_days)
    plot_footer(fig, x=0.95, y=0.02, ha="right", note=note)
    return fig


def plot_topic_small_multiples(monthly: pd.DataFrame, tenures: pd.DataFrame) -> Figure:
    """THEMATIC_HEATMAP.md section 6, visuel secondaire 1: one small panel
    per topic rather than a single overlapping streamgraph - app.py's own
    Topics tab already tried both and documented why small multiples won
    at 13 series ("past 8-10 categories a shared legend stops being
    readable, and a stacked area hides whether a topic is rising or
    falling") - that finding is reused here rather than re-litigated.
    """
    style.register_fonts()
    topics = list(monthly.columns)
    # B2.2: a 4x4 grid left 3 of 16 cells empty for 13 topics, a
    # disproportionate share of blank space in one corner. 5x3=15 slots
    # leaves only 2 empty - the smallest rectangular grid that still fits
    # 13 panels at a reasonable per-panel aspect ratio.
    n_cols = 5
    n_rows = -(-len(topics) // n_cols)
    x_start, x_end = _month_edges(monthly)
    y_max = monthly.values.max() * 1.15

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(12, 4.8), sharex=True, sharey=True,
                              **FIGURE_KW)
    axes_flat = axes.flatten()

    for i, topic in enumerate(topics):
        ax = axes_flat[i]
        ax.set_facecolor(style.BACKGROUND)
        ax.plot(monthly.index, monthly[topic], color=style.SECONDARY, linewidth=1)
        ax.fill_between(monthly.index, monthly[topic], color=style.SECONDARY, alpha=0.25)
        for _, (start, end) in da.CRISIS_WINDOWS.items():
            ax.axvspan(pd.Timestamp(start), pd.Timestamp(end), color=style.SURFACE,
                      alpha=0.4, zorder=0, lw=0)
        for start in tenures["tenure_start"].iloc[1:]:
            ax.axvline(pd.Timestamp(start), color=style.GRID, linestyle=":", linewidth=0.6)
        # D.3: 9pt floor - was 7pt previously. At 9pt a narrower (5-column,
        # B2.2) panel can't always hold a full topic name on one line
        # (e.g. "Ukraine, Russia and international security" running into
        # the next panel) - common.fit_text_to_width() wraps it to this
        # panel's real width instead (same component annual_recap.py's
        # theme text uses, exactly the reuse audit section E anticipated).
        title_lines = fit_text_to_width(
            ax, topic, max_width_frac=0.98, fontsize=style.SOURCE_SIZE, max_lines=2,
        )
        ax.set_title("\n".join(title_lines), fontsize=style.SOURCE_SIZE, color=style.TEXT_PRIMARY,
                     fontfamily=style.BODY_FONT, pad=3, linespacing=1.15)
        ax.set_ylim(0, y_max)
        ax.set_xlim(x_start, x_end)
        hide_spines(ax)
        ax.set_yticks([])
        ax.xaxis.set_major_locator(mdates.YearLocator(2))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        # sharex=True hides tick labels by grid row, not "last visible panel
        # per column" - with only 2 of 5 slots empty in the last row, that
        # would otherwise leave most panels with no time reference at all.
        # Every panel gets its own labels instead. D.3: 9pt floor - was
        # 6pt previously.
        ax.tick_params(axis="x", colors=style.TEXT_SECONDARY, labelsize=style.SOURCE_SIZE,
                       length=0, labelbottom=True)

    for ax in axes_flat[len(topics):]:
        ax.set_visible(False)

    # Same fig.text() convention as the other 3 projects' titles, not
    # fig.suptitle() (whose automatic y previously overlapped the subtitle
    # below it here too - the same class of bug found and fixed in
    # pm_handover.py's plot_transition_panels() while regenerating these
    # images, independent of the audit's own explicitly-named findings).
    fig.text(0.06, 0.965, "Each theme, month by month", ha=style.TITLE_HA,
              fontsize=style.SECONDARY_TITLE_SIZE, color=style.TEXT_PRIMARY,
              fontfamily=style.TITLE_FONT, fontweight="bold")
    fig.text(0.06, 0.925, "The 13 themes separately, one panel per theme rather than a "
             "13 color legend", fontsize=style.SOURCE_SIZE, color=style.TEXT_SECONDARY,
             fontfamily=style.SUBTITLE_FONT)
    # More top margin and hspace than before (0.85/0.55) - panel titles can
    # now wrap to 2 lines (fit_text_to_width, above), so each row needs
    # more headroom than a guaranteed-1-line 7pt title did.
    fig.subplots_adjust(top=0.80, bottom=0.08, left=0.04, right=0.98, hspace=0.9, wspace=0.15)
    return fig


def plot_covid_zoom(monthly: pd.DataFrame) -> Figure:
    """THEMATIC_HEATMAP.md section 6, visuel secondaire 2: the 3 Covid
    sub-topics side by side, zoomed to the crisis window. Demonstrates why
    they were kept separate (unlike T0+T1) - see
    data_access.COVID_TOPIC_LABELS' docstring for where this rationale
    actually comes from (app.py's own Topics tab caption, not invented).
    """
    style.register_fonts()
    covid_start, covid_end = da.CRISIS_WINDOWS["covid19"]
    pad = pd.DateOffset(months=3)
    window_start = pd.Timestamp(covid_start) - pad
    window_end = pd.Timestamp(covid_end) + pad
    zoomed = monthly.loc[window_start:window_end]
    y_max = zoomed[da.COVID_TOPIC_LABELS].values.max() * 1.15

    fig, axes = plt.subplots(1, 3, figsize=(8, 5), sharey=True, **FIGURE_KW)

    for ax, topic in zip(axes, da.COVID_TOPIC_LABELS, strict=True):
        ax.set_facecolor(style.BACKGROUND)
        ax.plot(zoomed.index, zoomed[topic], color=style.ACCENT, linewidth=1.5)
        ax.fill_between(zoomed.index, zoomed[topic], color=style.ACCENT, alpha=0.2)
        ax.axvspan(pd.Timestamp(covid_start), pd.Timestamp(covid_end), color=style.SURFACE,
                  alpha=0.4, zorder=0, lw=0)
        ax.set_title(topic.replace("Covid-19: ", ""), fontsize=10, color=style.TEXT_PRIMARY,
                     fontfamily=style.SUBTITLE_FONT, fontweight="bold")
        ax.set_ylim(0, y_max)
        ax.xaxis.set_major_locator(mdates.YearLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        ax.tick_params(axis="x", colors=style.TEXT_SECONDARY, labelsize=8)
        ax.tick_params(axis="y", length=0)
        hide_spines(ax)

    axes[0].set_yticks([0, y_max])
    axes[0].set_yticklabels(["low", "high"], fontsize=style.CRISIS_LABEL_SIZE,
                            color=style.TEXT_SECONDARY, fontfamily=style.BODY_FONT)

    fig.suptitle("Covid-19: three themes, not one", x=style.TITLE_X, ha=style.TITLE_HA,
                 fontsize=style.SECONDARY_TITLE_SIZE, color=style.TEXT_PRIMARY,
                 fontfamily=style.TITLE_FONT, fontweight="bold")
    fig.text(0.06, 0.90, "Unlike Ukraine/Russia, never merged: three distinct "
             "sub-phases of the same crisis.",
             fontsize=9, color=style.TEXT_SECONDARY, fontfamily=style.SUBTITLE_FONT)
    fig.subplots_adjust(top=0.78, bottom=0.12, left=0.08, right=0.96, wspace=0.15)
    return fig
