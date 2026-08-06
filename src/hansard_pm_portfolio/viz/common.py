"""Plotting helpers shared by every project's viz module - the banner
generator and small figure-styling utilities. Split out once a second
project (topic_heatmap.py) needed the same banner/dark-axes/save logic
project 01 already had - see ARCHITECTURE.md.
"""

from matplotlib import pyplot as plt
from matplotlib.figure import Figure

from hansard_pm_portfolio import style

FIGURE_KW = {"facecolor": style.BACKGROUND}


def hide_spines(*axes) -> None:
    """Hide all 4 spines on each given axes."""
    for ax in axes:
        for spine in ax.spines.values():
            spine.set_visible(False)


def dark_axes(ax) -> None:
    """Standard dark-theme axes styling: background, no spines, secondary-
    colored ticks. Most plots then override specific spines/ticks further.
    """
    ax.set_facecolor(style.BACKGROUND)
    hide_spines(ax)
    ax.tick_params(colors=style.TEXT_SECONDARY)


def save(fig: Figure, path) -> None:
    """Save at the figure's native size x 200 dpi - no bbox_inches='tight',
    so the exported PNG matches each spec's stated pixel dimensions exactly
    (e.g. 8x8in -> 1600x1600px) rather than whatever a tight crop produces.
    """
    fig.savefig(path, dpi=200, facecolor=fig.get_facecolor())


def plot_banner(title: str, subtitle: str) -> Figure:
    """README banner, shared format across projects: 1600x400px, title +
    subtitle only, no data - a simple typographic header, not a chart.
    """
    style.register_fonts()
    fig = plt.figure(figsize=(8, 2), **FIGURE_KW)
    fig.text(0.06, 0.62, title.upper(), fontsize=28, fontweight="bold",
              color=style.TEXT_PRIMARY, fontfamily=style.TITLE_FONT, va="center")
    fig.text(0.06, 0.28, subtitle, fontsize=13, color=style.TEXT_SECONDARY,
              fontfamily=style.SUBTITLE_FONT, va="center")
    fig.text(0.94, 0.28, "hansard-pm-nlp", fontsize=11, color=style.ACCENT,
              fontfamily=style.BODY_FONT, va="center", ha="right")
    return fig
