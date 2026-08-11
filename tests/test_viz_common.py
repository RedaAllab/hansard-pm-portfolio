"""Unit tests for viz/common.py's 3 shared layout primitives (audit section
E), written and passing BEFORE they're wired into the 4 projects' own
plotting functions (audit section H, implementation order step 2) - known
text, known widths, expected results, isolated from any real chart.
"""

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pytest

from hansard_pm_portfolio import style
from hansard_pm_portfolio.viz.common import fit_text_to_width, plot_footer, stack_below


@pytest.fixture
def ax():
    style.register_fonts()
    fig, ax = plt.subplots(figsize=(4, 4))
    yield ax
    plt.close(fig)


class TestFitTextToWidth:
    def test_short_text_stays_on_one_line(self, ax):
        lines = fit_text_to_width(ax, "Brexit", max_width_frac=0.9, fontsize=9)
        assert lines == ["Brexit"]

    def test_long_text_wraps_to_multiple_lines(self, ax):
        text = "Covid-19: restrictions and testing"
        lines = fit_text_to_width(ax, text, max_width_frac=0.3, fontsize=9)
        assert len(lines) > 1
        assert len(lines) <= 3

    def test_never_exceeds_max_lines(self, ax):
        text = "Appointments and security vetting, plus a great deal of additional context"
        lines = fit_text_to_width(ax, text, max_width_frac=0.15, fontsize=9, max_lines=3)
        assert len(lines) <= 3

    def test_every_line_fits_within_the_target_width(self, ax):
        text = "Public inquiries: justice and truth"
        max_width_frac = 0.4
        lines = fit_text_to_width(ax, text, max_width_frac=max_width_frac, fontsize=9)
        fig = ax.figure
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        target_width = ax.get_window_extent(renderer=renderer).width * max_width_frac
        for line in lines:
            artist = ax.text(0, 0, line, fontsize=9, fontfamily=style.BODY_FONT)
            width = artist.get_window_extent(renderer=renderer).width
            artist.remove()
            assert width <= target_width + 1e-6

    def test_impossible_fit_falls_back_to_ellipsis_not_silent_truncation(self, ax):
        # A single long word can't be wrapped onto multiple lines at all -
        # textwrap.wrap only breaks on whitespace, so a width so narrow
        # that even the narrowest wrap doesn't fit must hit the ellipsis
        # fallback (B4.4: never a silent [:3] cutoff with no indication).
        text = "Supercalifragilisticexpialidocious " * 3
        lines = fit_text_to_width(ax, text, max_width_frac=0.01, fontsize=9, max_lines=2)
        assert len(lines) <= 2
        assert lines[-1].endswith("…")

    def test_wrapping_narrower_for_a_narrower_axis(self):
        # The bug this replaces (B4.1): a fixed character-width wrap is
        # blind to how physically wide the axes actually is. A real
        # narrower axes must produce more (or equal), not fewer, lines
        # than a wider one for the same text/fontsize.
        style.register_fonts()
        text = "Budget and domestic policy"
        fig = plt.figure(figsize=(6, 2))
        ax_wide = fig.add_axes([0.0, 0.0, 0.9, 1.0])
        ax_narrow = fig.add_axes([0.91, 0.0, 0.08, 1.0])
        wide_lines = fit_text_to_width(ax_wide, text, max_width_frac=0.9, fontsize=9)
        narrow_lines = fit_text_to_width(ax_narrow, text, max_width_frac=0.9, fontsize=9)
        assert len(narrow_lines) >= len(wide_lines)
        plt.close(fig)


class TestStackBelow:
    def test_positions_text_below_the_anchors_real_bbox(self, ax):
        fig = ax.figure
        anchor = fig.text(0.5, 0.8, "Anchor", ha="center", fontsize=14)
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        anchor_bbox_fig = anchor.get_window_extent(renderer=renderer).transformed(
            fig.transFigure.inverted()
        )

        placed = stack_below(fig, anchor, "Below text", gap_frac=0.02, ha="center")

        placed_bbox_fig = placed.get_window_extent(renderer=fig.canvas.get_renderer()).transformed(
            fig.transFigure.inverted()
        )
        # The placed text's top edge must sit at (or very near) gap_frac
        # below the anchor's real bottom edge, not a hardcoded coordinate.
        assert placed_bbox_fig.y1 == pytest.approx(anchor_bbox_fig.y0 - 0.02, abs=1e-6)

    def test_never_overlaps_the_anchor_regardless_of_anchor_position(self, ax):
        fig = ax.figure
        # Move the anchor to an arbitrary y - stack_below must still avoid
        # overlap because it measures, rather than assuming a fixed offset
        # from a hardcoded position (the root cause of audit B1.1).
        anchor = fig.text(0.5, 0.35, "Legend-like text", ha="center", fontsize=11)
        placed = stack_below(fig, anchor, "Caveat", gap_frac=0.015, ha="center")
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        anchor_bbox = anchor.get_window_extent(renderer=renderer)
        placed_bbox = placed.get_window_extent(renderer=renderer)
        assert placed_bbox.y1 < anchor_bbox.y0

    def test_x_defaults_to_centered_under_the_anchor(self, ax):
        fig = ax.figure
        anchor = fig.text(0.3, 0.6, "Off-center anchor", ha="left", fontsize=10)
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        anchor_bbox_fig = anchor.get_window_extent(renderer=renderer).transformed(
            fig.transFigure.inverted()
        )
        expected_x = (anchor_bbox_fig.x0 + anchor_bbox_fig.x1) / 2

        placed = stack_below(fig, anchor, "Below", ha="center")
        assert placed.get_position()[0] == pytest.approx(expected_x, abs=1e-6)


class TestPlotFooter:
    def test_returns_only_source_text_when_no_note(self):
        fig = plt.figure()
        texts = plot_footer(fig)
        assert len(texts) == 1
        assert texts[0].get_text() == "Source: Hansard API · hansard-pm-nlp"
        plt.close(fig)

    def test_note_is_stacked_above_source_with_no_overlap(self):
        fig = plt.figure(figsize=(8, 4))
        texts = plot_footer(fig, note="T = Liz Truss (49 days)")
        assert len(texts) == 2
        note_text, source_text = texts
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        note_bbox = note_text.get_window_extent(renderer=renderer)
        source_bbox = source_text.get_window_extent(renderer=renderer)
        assert note_bbox.y0 >= source_bbox.y1
        plt.close(fig)

    def test_custom_source_string_is_used(self):
        fig = plt.figure()
        texts = plot_footer(fig, source="Custom Source")
        assert texts[0].get_text() == "Source: Custom Source"
        plt.close(fig)

    def test_anchor_positions_block_below_anchors_real_bbox_regardless_of_y(self):
        # Regression test: a fixed y=0.02 origin (the no-anchor default)
        # can still collide with a variable-height element like a legend
        # that wraps to more rows than expected. With anchor=<artist>, the
        # footer must always land below that artist's REAL bbox.
        fig = plt.figure(figsize=(8, 8))
        ax = fig.add_subplot(111)
        ax.plot([0, 1], [0, 1], label="a")
        ax.plot([0, 1], [1, 0], label="b")
        legend = ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.3), ncol=2)
        texts = plot_footer(fig, x=0.5, ha="center", note="A caveat", anchor=legend)
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        legend_bbox = legend.get_window_extent(renderer=renderer)
        for t in texts:
            t_bbox = t.get_window_extent(renderer=renderer)
            assert t_bbox.y1 <= legend_bbox.y0, (
                f"{t.get_text()!r} overlaps the anchor legend"
            )
        plt.close(fig)
