"""Plotting helpers shared by every project's viz module - the banner
generator and small figure-styling utilities. Split out once a second
project (topic_heatmap.py) needed the same banner/dark-axes/save logic
project 01 already had - see ARCHITECTURE.md.

UX/dataviz audit (AUDIT_UX_DATAVIZ_hansard-pm-portfolio.md) section E adds
3 more reusable components here, all built on one principle (D.1 "measure
before positioning, never the inverse"): `fit_text_to_width()`,
`stack_below()`, and `plot_footer()` all measure a real rendered
`get_window_extent()` bbox rather than trusting a hardcoded coordinate or
character count, which is what caused the pixel-level overlaps this audit
found (annual_recap.py's theme text/bar, style_duel.py's legend/caveat).
"""

from matplotlib import pyplot as plt
from matplotlib.figure import Figure

from hansard_pm_portfolio import style

FIGURE_KW = {"facecolor": style.BACKGROUND}


def _get_renderer(fig: Figure):
    """A real renderer for `fig`, regardless of which backend is active.

    `fig.canvas.get_renderer()` only exists on some backends (Agg's does;
    the interactive macosx/Qt backends used for local notebook work don't
    always expose it the same way) - falling back to a throwaway Agg
    canvas keeps `fit_text_to_width()`/`stack_below()` measurement-based
    (D.1) regardless of what backend the caller happens to be running
    under, instead of only working in CI's headless Agg environment.
    """
    canvas = fig.canvas
    if hasattr(canvas, "get_renderer"):
        return canvas.get_renderer()
    from matplotlib.backends.backend_agg import FigureCanvasAgg

    agg_canvas = FigureCanvasAgg(fig)
    agg_canvas.draw()
    return agg_canvas.get_renderer()


def fit_text_to_width(
    ax,
    text: str,
    max_width_frac: float,
    fontsize: float,
    *,
    fontfamily: str | None = None,
    max_lines: int = 3,
    ellipsis: str = "…",
) -> list[str]:
    """Wrap `text` into at most `max_lines` lines that each fit within
    `max_width_frac` of `ax`'s real rendered physical width - measured via
    a throwaway text artist's `get_window_extent()`, not a hardcoded
    character-count guess (audit C.1/D.1: `textwrap.wrap(text, width=16)`
    at a fixed character count is independent of the axes' actual width,
    which is exactly what let annual_recap.py's theme text overrun a
    narrow partial-year card and collide with the bar below it).

    Builds lines greedily, word by word, adding each next word to the
    current line only while the line's real rendered width (measured via a
    throwaway text artist, never estimated from a character count) still
    fits `target_width` - never breaking a word onto two lines mid-word,
    which is what a naive `textwrap.wrap(text, width=N)` search degenerates
    into for a card too narrow to hold even one word per line (it starts
    force-breaking every word into single-character lines, which "fits"
    the line-count and width constraints but is unreadable). If the whole
    text still doesn't fit in `max_lines`, the last line is ellipsized
    (trimmed word-first, then character-by-character if even one word
    doesn't fit) instead of a silent cutoff (B4.4) - so truncation always
    reads as "cut off here", never as "the card ran out of words to say".
    """
    fontfamily = fontfamily or style.BODY_FONT
    fig = ax.figure
    renderer = _get_renderer(fig)
    target_width = ax.get_window_extent(renderer=renderer).width * max_width_frac

    def _measure(s: str) -> float:
        artist = ax.text(0, 0, s, fontsize=fontsize, fontfamily=fontfamily, alpha=0)
        width = artist.get_window_extent(renderer=renderer).width
        artist.remove()
        return width

    words = text.split()
    lines: list[str] = []
    current = ""
    i = 0
    while i < len(words):
        word = words[i]
        candidate = f"{current} {word}".strip()
        # An empty `current` always accepts the next word even if it alone
        # overflows target_width - a single unbreakable word wider than
        # the card is a genuine edge case, not one this function can wrap
        # its way out of without splitting the word itself.
        if not current or _measure(candidate) <= target_width:
            current = candidate
            i += 1
        else:
            lines.append(current)
            current = ""
            if len(lines) == max_lines:
                break
    if current and len(lines) < max_lines:
        lines.append(current)
        current = ""

    ran_out_of_room = i < len(words) or bool(current)
    if not ran_out_of_room:
        return lines or [""]

    lines = lines[:max_lines] or [""]
    last = lines[-1]
    while last and _measure(last + ellipsis) > target_width:
        last = last[:-1].rstrip()
    lines[-1] = (last + ellipsis) if last else ellipsis
    return lines


def stack_below(fig: Figure, anchor_artist, text: str, *, gap_frac: float = 0.02,
                 ha: str = "center", x: float | None = None, **text_kwargs):
    """Place `text` as a `fig.text()` a fixed `gap_frac` (figure-fraction)
    below the REAL rendered bounding box of `anchor_artist` (a legend,
    title, or any already-drawn artist) - replaces the pattern of two
    independently hardcoded coordinate pairs (one in axes-fraction for a
    legend's `bbox_to_anchor`, one in figure-fraction for a caption below
    it) that never agreed with each other in practice (audit B1.1: the
    style-duel legend and TRUSS_CAVEAT overlap because they were each
    positioned by eye in different coordinate systems, not measured).

    `anchor_artist` must already be attached to `fig` (directly or via one
    of its axes). Forces a canvas draw so the bbox reflects the actual
    layout, not stale defaults from before `subplots_adjust`/legend
    placement ran.
    """
    fig.canvas.draw()
    renderer = _get_renderer(fig)
    bbox = anchor_artist.get_window_extent(renderer=renderer)
    bbox_fig = bbox.transformed(fig.transFigure.inverted())
    if x is None:
        x = {"left": bbox_fig.x0, "right": bbox_fig.x1}.get(ha, (bbox_fig.x0 + bbox_fig.x1) / 2)
    y = bbox_fig.y0 - gap_frac
    defaults = dict(fontsize=style.SOURCE_SIZE, color=style.TEXT_SECONDARY,
                     fontfamily=style.BODY_FONT)
    defaults.update(text_kwargs)
    return fig.text(x, y, text, ha=ha, va="top", **defaults)


def plot_footer(fig: Figure, *, x: float = 0.97, y: float = 0.02, ha: str = "right",
                 note: str | None = None, note_gap: float = 0.012,
                 source: str = "Hansard API · hansard-pm-nlp",
                 anchor=None, anchor_gap: float = 0.02):
    """Single entry point for a figure's bottom source line, with an
    optional `note` line stacked directly above it (an abbreviation
    legend, a statistical caveat) - replaces the 4 slightly different
    `fig.text(..., "Source: Hansard API ...")` calls previously duplicated
    across viz/*.py (audit E, I.9).

    Without `anchor`: the note's y-position is computed from the source
    line's REAL rendered top edge plus `note_gap` (D.1), not from a second
    independently eyeballed y-value - a purely additive `y + note_gap`
    guarantees nothing once font size and figure height vary independently
    (a small gap that clears a tall figure can still collide in a short
    one), while "gap above the real rendered top edge" cannot overlap
    regardless of figure size or dpi.

    With `anchor` (an already-drawn artist, e.g. a legend): the whole
    note+source block is positioned below THAT artist's real rendered
    bottom edge instead, at a fixed `y`. This is the fix for a subtler
    version of the same bug the merge-into-footer approach (C.2) was meant
    to prevent in style_duel.py's radar - a fixed `y=0.02` origin is itself
    still a hardcoded coordinate that a tall legend (e.g. one that wraps to
    2 rows) could grow down into. Passing `anchor=legend` makes the block's
    position depend on the legend's actual height instead.
    """
    if anchor is not None:
        fig.canvas.draw()
        renderer = _get_renderer(fig)
        anchor_bbox_fig = anchor.get_window_extent(renderer=renderer).transformed(
            fig.transFigure.inverted()
        )
        cursor_y = anchor_bbox_fig.y0 - anchor_gap
        texts = []
        if note:
            note_text = fig.text(x, cursor_y, note, ha=ha, va="top", fontsize=style.SOURCE_SIZE,
                                  color=style.TEXT_SECONDARY, fontfamily=style.BODY_FONT)
            texts.append(note_text)
            fig.canvas.draw()
            note_bbox_fig = note_text.get_window_extent(
                renderer=_get_renderer(fig)
            ).transformed(fig.transFigure.inverted())
            cursor_y = note_bbox_fig.y0 - note_gap
        texts.append(
            fig.text(x, cursor_y, f"Source: {source}", ha=ha, va="top",
                      fontsize=style.SOURCE_SIZE, color=style.SECONDARY,
                      fontfamily=style.BODY_FONT)
        )
        return texts

    source_text = fig.text(x, y, f"Source: {source}", ha=ha, fontsize=style.SOURCE_SIZE,
                            color=style.SECONDARY, fontfamily=style.BODY_FONT)
    if not note:
        return [source_text]

    fig.canvas.draw()
    renderer = _get_renderer(fig)
    source_bbox_fig = source_text.get_window_extent(renderer=renderer).transformed(
        fig.transFigure.inverted()
    )
    note_text = fig.text(x, source_bbox_fig.y1 + note_gap, note, ha=ha, va="bottom",
                          fontsize=style.SOURCE_SIZE, color=style.TEXT_SECONDARY,
                          fontfamily=style.BODY_FONT)
    return [note_text, source_text]


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
