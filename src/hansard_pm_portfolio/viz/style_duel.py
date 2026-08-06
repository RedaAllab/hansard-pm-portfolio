"""Plotting functions for project 01 (STYLE_DUEL.md): the style-duel radar
and its two secondary visuals. One file per portfolio project under viz/ -
see ARCHITECTURE.md for why this differs from STYLE_DUEL.md's single
portfolio_viz.py suggestion.
"""

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.figure import Figure

from hansard_pm_portfolio import style
from hansard_pm_portfolio.data_access import IN_SCOPE_PMS, RADAR_AXES, normalize_radar
from hansard_pm_portfolio.viz.common import FIGURE_KW, dark_axes, plot_banner, save

__all__ = [
    "plot_banner",
    "save",
    "plot_style_radar",
    "plot_feature_importance_bar",
    "plot_confusion_matrix",
]


def plot_style_radar(
    profile: pd.DataFrame, selected_pms: list[str] = IN_SCOPE_PMS
) -> Figure:
    """STYLE_DUEL.md section 6, visuel principal: 6-axis radar, one line per
    PM, values min-max normalized across `selected_pms`.
    """
    style.register_fonts()
    cols = [c for c, _ in RADAR_AXES]
    labels = [label for _, label in RADAR_AXES]
    n_by_pm = profile.set_index("pm_name")["n_contributions"]
    normalized = normalize_radar(profile, cols, selected_pms)

    n_axes = len(cols)
    angles = np.linspace(0, 2 * np.pi, n_axes, endpoint=False).tolist()
    angles += angles[:1]

    fig = plt.figure(figsize=(8, 8), **FIGURE_KW)
    fig.subplots_adjust(top=0.82, bottom=0.16)
    ax = fig.add_subplot(111, polar=True)
    ax.set_facecolor(style.BACKGROUND)

    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=style.AXIS_LABEL_SIZE, color=style.TEXT_PRIMARY,
                        fontfamily=style.BODY_FONT)

    # Headroom past 1.0 so a PM maxing out an axis (value=1.0, right at the
    # outer ring) doesn't collide with that axis's label - without it, the
    # data point and the label text sit at the same radius.
    ax.set_ylim(0, 1.18)
    ax.set_yticks([0.33, 0.66, 1.0])
    ax.set_yticklabels(["", "", ""])  # 3 radial gridlines, no numeric scale (section 6)
    ax.tick_params(axis="y", labelsize=style.TICK_SIZE, colors=style.TEXT_SECONDARY)
    ax.tick_params(axis="x", pad=18)
    ax.grid(color=style.GRID, linewidth=0.5)
    ax.spines["polar"].set_color(style.GRID)

    for pm in selected_pms:
        values = normalized.loc[pm, cols].tolist()
        values += values[:1]
        color = style.PM_COLORS[pm]
        linestyle = style.PM_LINESTYLES[pm]
        # n= counts only called out for Truss, inline with her caveat - the
        # other 3 PMs' counts aren't decision-relevant and made the legend
        # overflow the figure width at ncol=4.
        label = f"{pm} (n={n_by_pm[pm]})*" if pm == "Liz Truss" else pm
        ax.plot(angles, values, color=color, linestyle=linestyle, linewidth=2, label=label)
        ax.fill(angles, values, color=color, alpha=0.15)

    fig.text(
        0.5, 0.94, "LE DUEL DE STYLE", ha="center", fontsize=style.TITLE_SIZE,
        fontweight="bold", color=style.TEXT_PRIMARY, fontfamily=style.TITLE_FONT,
    )
    fig.text(
        0.5, 0.90, "Ce que 6 traits stylométriques révèlent", ha="center",
        fontsize=style.SUBTITLE_SIZE, color=style.TEXT_SECONDARY, fontfamily=style.SUBTITLE_FONT,
    )

    legend = ax.legend(
        loc="upper center", bbox_to_anchor=(0.5, -0.08), ncol=4, frameon=False,
        fontsize=style.LEGEND_SIZE, columnspacing=1.2, handletextpad=0.5,
    )
    for text in legend.get_texts():
        text.set_color(style.TEXT_PRIMARY)
        text.set_fontfamily(style.BODY_FONT)

    fig.text(
        0.5, 0.065, style.TRUSS_CAVEAT, ha="center", fontsize=style.SOURCE_SIZE,
        color=style.TEXT_SECONDARY, fontfamily=style.BODY_FONT,
    )
    fig.text(
        0.5, 0.02, "Source : Hansard API · hansard-pm-nlp", ha="center",
        fontsize=style.SOURCE_SIZE, color=style.SECONDARY, fontfamily=style.BODY_FONT,
    )
    return fig


def plot_feature_importance_bar(
    importance: pd.DataFrame, title: str, subtitle: str
) -> Figure:
    """STYLE_DUEL.md section 6, visuel secondaire 1: horizontal permutation-
    importance bar chart, single accent color, values labeled in
    IBM Plex Mono.

    `importance` must have `feature` and `importance` columns, already
    limited to the rows to plot (top 6) and pre-sorted ascending, since
    matplotlib's barh draws top-to-bottom in the order given.
    """
    style.register_fonts()
    fig, ax = plt.subplots(figsize=(8, 5), **FIGURE_KW)
    dark_axes(ax)

    bars = ax.barh(importance["feature"], importance["importance"], color=style.ACCENT)
    ax.set_xlabel("")
    for label in ax.get_yticklabels():
        label.set_fontsize(style.AXIS_LABEL_SIZE)
        label.set_color(style.TEXT_PRIMARY)
        label.set_fontfamily(style.BODY_FONT)
    ax.grid(axis="x", color=style.GRID, linewidth=0.5)
    ax.set_axisbelow(True)

    for bar, value in zip(bars, importance["importance"], strict=True):
        ax.text(
            bar.get_width() + importance["importance"].max() * 0.02,
            bar.get_y() + bar.get_height() / 2,
            f"{value:.3f}", va="center", fontsize=style.NUMBER_SIZE,
            color=style.TEXT_PRIMARY, fontfamily=style.NUMBER_FONT,
        )

    fig.suptitle(title, x=0.05, ha="left", fontsize=16, color=style.TEXT_PRIMARY,
                 fontfamily=style.TITLE_FONT, fontweight="bold")
    fig.text(0.062, 0.90, subtitle, fontsize=style.SUBTITLE_SIZE, color=style.TEXT_SECONDARY,
              fontfamily=style.SUBTITLE_FONT)
    fig.subplots_adjust(top=0.82, left=0.28, right=0.95, bottom=0.1)
    return fig


def _plain_language_score(accuracy: float) -> str:
    """"9 cas sur 10" style phrasing (STYLE_DUEL.md section 6, visuel 2) -
    accuracy is a 0-1 fraction, rounded to the nearest /10 the way the spec's
    own example phrases it.
    """
    return f"{round(accuracy * 10)} cas sur 10"


def plot_confusion_matrix(matrix: pd.DataFrame, accuracy: float) -> Figure:
    """STYLE_DUEL.md section 6, visuel secondaire 2: 3x3 confusion matrix
    (Truss excluded, matching Phase 6's classifier scope), row-normalized to
    percentages, Cividis colormap, diagonal outlined.

    `matrix` is `data_access.build_confusion_matrix()`'s output: actual PMs
    as the index, predicted PMs as columns, both already ordered so the
    diagonal is Johnson/Sunak/Starmer top-left to bottom-right.
    """
    style.register_fonts()
    fig, ax = plt.subplots(figsize=(6, 6), **FIGURE_KW)
    ax.set_facecolor(style.BACKGROUND)

    im = ax.imshow(matrix.values, cmap=style.SEQUENTIAL_CMAP, vmin=0, vmax=100)

    n = len(matrix)
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    # Short display labels (surname only) so 3 columns fit at 6in width
    # without rotating tick text - full names are still in the y-axis and
    # the surrounding README/notebook prose.
    short_labels = [name.split()[-1] for name in matrix.columns]
    ax.set_xticklabels(short_labels, fontsize=style.AXIS_LABEL_SIZE, color=style.TEXT_PRIMARY,
                        fontfamily=style.BODY_FONT, ha="center")
    ax.set_yticklabels(matrix.index, fontsize=style.AXIS_LABEL_SIZE, color=style.TEXT_PRIMARY,
                        fontfamily=style.BODY_FONT)
    ax.set_xlabel("Prédit", fontsize=style.AXIS_LABEL_SIZE, color=style.TEXT_SECONDARY,
                  fontfamily=style.BODY_FONT, labelpad=10)
    ax.set_ylabel("Réel", fontsize=style.AXIS_LABEL_SIZE, color=style.TEXT_SECONDARY,
                  fontfamily=style.BODY_FONT)
    for spine in ax.spines.values():
        spine.set_visible(False)

    for i in range(n):
        for j in range(n):
            value = matrix.values[i, j]
            text_color = style.BACKGROUND if value > 55 else style.TEXT_PRIMARY
            ax.text(
                j, i, f"{value:.0f}%", ha="center", va="center",
                fontsize=14, color=text_color, fontfamily=style.NUMBER_FONT,
            )
            if i == j:
                ax.add_patch(
                    plt.Rectangle(
                        (j - 0.5, i - 0.5), 1, 1, fill=False,
                        edgecolor=style.ACCENT, linewidth=2,
                    )
                )

    fig.suptitle(
        "Le classifieur retrouve-t-il le bon Premier ministre ?", x=0.5,
        fontsize=14, color=style.TEXT_PRIMARY, fontfamily=style.TITLE_FONT, fontweight="bold",
    )
    caption = (
        f"Le modèle retrouve le bon Premier ministre dans {_plain_language_score(accuracy)}."
    )
    fig.text(
        0.5, 0.025, caption, ha="center", fontsize=style.SUBTITLE_SIZE,
        color=style.TEXT_SECONDARY, fontfamily=style.BODY_FONT,
    )
    fig.subplots_adjust(top=0.88, bottom=0.20, left=0.22, right=0.88)
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.ax.tick_params(colors=style.TEXT_SECONDARY, labelsize=style.TICK_SIZE)
    cbar.outline.set_visible(False)
    return fig
