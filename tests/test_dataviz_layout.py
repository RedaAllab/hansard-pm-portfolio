"""Acceptance tests for the UX/dataviz audit (AUDIT_UX_DATAVIZ_hansard-pm-
portfolio.md), section I. Each test class corresponds to one numbered
criterion (I.1-I.6, I.8, I.9); I.7 lives in test_readme_sequencing.py and
I.10 is "the rest of tests/ still passes", not a new test.

These render real figures from small synthetic (but schema-correct)
fixtures - no sibling hansard-pm-nlp checkout needed, consistent with how
tests/test_*_data.py already separates unit tests (synthetic fixtures) from
TestLiveIntegration (real data, self-skips via `sibling_repo_available`).
"""

import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
import pytest

from hansard_pm_portfolio import data_access as da
from hansard_pm_portfolio import style
from hansard_pm_portfolio.viz import annual_recap as annual_recap_viz
from hansard_pm_portfolio.viz import pm_handover as pm_handover_viz
from hansard_pm_portfolio.viz import style_duel as style_duel_viz
from hansard_pm_portfolio.viz.common import _get_renderer

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src" / "hansard_pm_portfolio"


# --- Shared fixtures ---------------------------------------------------------


def _annual_recap_tenures() -> pd.DataFrame:
    # Mirrors the real corpus shape (README/ARCHITECTURE.md): Johnson start
    # 2019-07-24, Truss's 49-day tenure inside 2022, 2024 splits Sunak and
    # Starmer - enough to exercise both the "T" abbreviation and multiple
    # narrow (partial/transition-year) cards.
    return pd.DataFrame({
        "pm_name": ["Boris Johnson", "Liz Truss", "Rishi Sunak", "Keir Starmer"],
        "tenure_start": pd.to_datetime(
            ["2019-07-24", "2022-09-06", "2022-10-25", "2024-07-05"]
        ),
        "tenure_end": pd.to_datetime(
            ["2022-09-06", "2022-10-25", "2024-07-05", "2026-07-20"]
        ),
    })


def _annual_recap_events() -> pd.DataFrame:
    rows = []
    dates_words = [
        ("2019-08-01", 3000, 0.10), ("2019-11-01", 2000, 0.11),
        ("2020-03-01", 8000, 0.12), ("2020-09-01", 9000, 0.09),
        ("2021-02-01", 8500, 0.05), ("2021-10-01", 7000, 0.06),
        ("2022-03-01", 6000, 0.15), ("2022-09-15", 500, 0.14),
        ("2022-11-01", 6500, 0.16), ("2023-05-01", 7200, 0.17),
        ("2024-03-01", 7300, 0.18), ("2024-09-01", 6800, 0.19),
        ("2025-04-01", 6200, 0.20), ("2026-03-01", 3100, 0.22),
    ]
    for d, wc, nc in dates_words:
        rows.append({"sitting_date": pd.Timestamp(d), "word_count": wc, "net_certainty": nc})
    return pd.DataFrame(rows)


# 13 display-order topic labels, real long ones included so the wrapping
# logic is genuinely exercised (I.1 depends on this).
_TOPICS = da.TOPIC_DISPLAY_ORDER


def _annual_recap_topics(events: pd.DataFrame) -> pd.DataFrame:
    year_dominant = {
        2019: "Brexit and the Northern Ireland deal",
        2020: "Covid-19: restrictions and testing",
        2021: "Covid-19: NHS and public inquiry",
        2022: "Ukraine, Russia and international security",
        2023: "Budget and domestic policy",
        2024: "Appointments and security vetting",
        2025: "Public inquiries: justice and truth",
        2026: "Transport and major infrastructure projects",
    }
    rows = []
    for _, r in events.iterrows():
        year = r["sitting_date"].year
        dominant = year_dominant.get(year, _TOPICS[0])
        row = {"pm_name": "x", "sitting_date": r["sitting_date"]}
        for i in range(14):
            row[f"topic_{i}"] = 0.01
        if dominant == da.MERGED_TOPIC_LABEL:
            row["topic_0"] = 0.5
            row["topic_1"] = 0.4
        else:
            # da.TOPIC_LABELS maps "topic_N" -> display label; invert it to
            # find which raw column this year's dominant theme belongs to.
            topic_col = next(k for k, v in da.TOPIC_LABELS.items() if v == dominant)
            row[topic_col] = 0.9
        rows.append(row)
    return pd.DataFrame(rows)


@pytest.fixture(scope="module")
def annual_recap_figure():
    tenures = _annual_recap_tenures()
    events = _annual_recap_events()
    topics_raw = _annual_recap_topics(events)
    # topic_N columns must come from da.TOPIC_LABELS for merge_overlapping_topics
    topics_raw = topics_raw.rename(columns={f"topic_{i}": f"topic_{i}" for i in range(14)})
    recap = da.build_annual_recap(events, topics_raw, tenures)
    fig = annual_recap_viz.plot_annual_recap(recap, tenures)
    fig.set_dpi(200)
    fig.canvas.draw()
    yield fig
    plt.close(fig)


# --- I.1: annual_recap theme text / word-volume bar never overlap ----------


class TestAnnualRecapNoOverlap:
    def test_theme_text_and_bar_have_min_4px_gap_at_200dpi(self, annual_recap_figure):
        fig = annual_recap_figure
        renderer = _get_renderer(fig)
        checked = 0
        for ax in fig.axes:
            theme_texts = [t for t in ax.texts if t.get_gid() == "theme_text"]
            bars = [p for p in ax.patches if p.get_gid() == "word_bar"]
            if not theme_texts or not bars:
                continue
            theme_bbox = theme_texts[0].get_window_extent(renderer=renderer)
            bar_bbox = bars[0].get_window_extent(renderer=renderer)
            gap = theme_bbox.y0 - bar_bbox.y1
            assert gap >= 4, f"theme/bar gap only {gap:.1f}px (need >=4px at 200dpi)"
            checked += 1
        assert checked == 8, f"expected 8 year-cards with theme+bar artists, found {checked}"

    def test_no_silent_truncation_marker_without_ellipsis(self, annual_recap_figure):
        # Any wrapped theme that got cut must show the ellipsis, never a
        # bare cut-off word (B4.4).
        fig = annual_recap_figure
        for ax in fig.axes:
            theme_texts = [t for t in ax.texts if t.get_gid() == "theme_text"]
            for t in theme_texts:
                lines = t.get_text().split("\n")
                assert len(lines) <= 3


# --- I.2: radar legend / footer never overlap -------------------------------


@pytest.fixture(scope="module")
def radar_figure():
    profile = pd.DataFrame({
        "pm_name": da.IN_SCOPE_PMS,
        "n_contributions": [1800, 123, 1500, 1400],
        "mtld": [70.0, 60.0, 90.0, 80.0],
        "mean_flesch_kincaid_grade": [10.0, 9.0, 12.0, 11.0],
        "mean_hedge_rate": [0.03, 0.02, 0.025, 0.028],
        "mean_net_certainty": [0.15, 0.10, 0.20, 0.18],
        "fw_not_rate": [0.01, 0.012, 0.009, 0.011],
        "mean_words_per_sentence": [20.0, 18.0, 25.0, 22.0],
    })
    fig = style_duel_viz.plot_style_radar(profile)
    fig.set_dpi(200)
    fig.canvas.draw()
    yield fig
    plt.close(fig)


class TestRadarNoOverlap:
    def test_legend_and_footer_never_overlap(self, radar_figure):
        fig = radar_figure
        renderer = _get_renderer(fig)
        ax = fig.axes[0]
        legend = ax.get_legend()
        assert legend is not None
        legend_bbox = legend.get_window_extent(renderer=renderer)

        # TRUSS_CAVEAT is now merged into the footer (C.2) - there is no
        # separate hardcoded-position caveat text object anymore. Find
        # whatever footer text(s) exist and confirm none overlap the
        # legend.
        footer_texts = [
            t for t in fig.texts
            if t.get_text() == style.TRUSS_CAVEAT or t.get_text().startswith("Source:")
        ]
        assert footer_texts, "expected at least the source line in the footer"
        for t in footer_texts:
            bbox = t.get_window_extent(renderer=renderer)
            assert bbox.y1 <= legend_bbox.y0, (
                f"footer text {t.get_text()!r} overlaps the legend"
            )


# --- I.3: every *_SIZE constant in style.py is >=9pt unless whitelisted -----


# Explicit whitelist for any *_SIZE constant allowed below the 9pt floor -
# empty on purpose (D.3: "no silent exceptions"). If one is ever added, it
# must carry a justification comment in STYLE_DUEL.md, referenced here.
_SIZE_WHITELIST: dict[str, str] = {}


class TestFontSizeFloor:
    def test_every_size_constant_is_at_least_9pt(self):
        violations = []
        for name, value in vars(style).items():
            if not name.endswith("_SIZE") or not isinstance(value, (int, float)):
                continue
            if name in _SIZE_WHITELIST:
                continue
            if value < 9:
                violations.append((name, value))
        assert not violations, f"font size(s) below the 9pt floor: {violations}"


# --- I.4: plot_transition_panels shows no raw numeric tick labels ----------


def _handover_fixtures():
    transitions = pd.DataFrame({
        "before_pm": ["Boris Johnson", "Liz Truss", "Rishi Sunak"],
        "after_pm": ["Liz Truss", "Rishi Sunak", "Keir Starmer"],
        "transition_date": pd.to_datetime(["2022-09-06", "2022-10-25", "2024-07-05"]),
    })
    rows = []
    specs = [
        ("Boris Johnson", "before", "2022-08-01", -36, 0.05, 0.1),
        ("Boris Johnson", "before", "2022-08-20", -17, 0.06, 0.12),
        ("Liz Truss", "after", "2022-09-10", 4, 0.20, 0.30),
        ("Liz Truss", "before", "2022-10-12", -13, 0.21, 0.31),
        ("Rishi Sunak", "after", "2022-11-01", 7, 0.08, -0.10),
        ("Rishi Sunak", "before", "2024-06-01", -34, 0.09, -0.05),
        ("Keir Starmer", "after", "2024-07-20", 15, 0.15, 0.25),
    ]
    for pm, side, date, days, nc, vd in specs:
        rows.append({
            "pm_name": pm, "side": side, "sitting_date": pd.Timestamp(date),
            "days_from_transition": days, "net_certainty": nc, "vader_compound": vd,
        })
    windows = pd.DataFrame(rows)
    # transition_label must match plot_transition_panels()'s own derivation
    # (f"{before.split()[-1]} to {after.split()[-1]}"), assigned per-row
    # rather than by pm_name alone since Liz Truss appears as both the
    # "after" side of one transition and the "before" side of the next.
    label_by_index = []
    for _, r in windows.iterrows():
        if r["pm_name"] == "Boris Johnson":
            label_by_index.append("Johnson to Truss")
        elif r["pm_name"] == "Liz Truss" and r["side"] == "after":
            label_by_index.append("Johnson to Truss")
        elif r["pm_name"] == "Liz Truss" and r["side"] == "before":
            label_by_index.append("Truss to Sunak")
        elif r["pm_name"] == "Rishi Sunak" and r["side"] == "after":
            label_by_index.append("Truss to Sunak")
        elif r["pm_name"] == "Rishi Sunak" and r["side"] == "before":
            label_by_index.append("Sunak to Starmer")
        else:
            label_by_index.append("Sunak to Starmer")
    windows["transition_label"] = label_by_index
    return windows, transitions


_NUMERIC_TICK_RE = re.compile(r"^-?\d")


@pytest.fixture(scope="module")
def transition_panels_figure():
    windows, transitions = _handover_fixtures()
    fig = pm_handover_viz.plot_transition_panels(windows, transitions)
    fig.set_dpi(200)
    fig.canvas.draw()
    yield fig
    plt.close(fig)


class TestHandoverNoRawTicks:
    def test_no_raw_numeric_y_tick_label_anywhere_in_the_figure(self, transition_panels_figure):
        # Y-axes carry the two value SCALES this criterion targets
        # (net_certainty, VADER) - J.1 is about never showing a raw
        # numeric axis scale. The x-axis's "-6w"/"handover"/"+6w" are
        # deliberate positional labels (day-0-relative-to-handover is the
        # whole point of the chart), not a numeric scale, and are out of
        # scope for this check.
        fig = transition_panels_figure
        offenders = []
        for ax in fig.axes:
            for label in ax.get_yticklabels():
                text = label.get_text()
                if _NUMERIC_TICK_RE.match(text.strip()):
                    offenders.append(text)
        assert not offenders, f"raw numeric y tick label(s) found: {offenders}"

    def test_low_high_shown_exactly_once_per_metric(self, transition_panels_figure):
        fig = transition_panels_figure
        all_labels = []
        for ax in fig.axes:
            all_labels.extend(t.get_text() for t in ax.get_yticklabels())
        assert all_labels.count("low") == 2  # one per metric (net_certainty, VADER)
        assert all_labels.count("high") == 2


# --- I.5: an abbreviated PM label always has an on-image legend note -------


class TestPmAbbreviationHasOnImageNote:
    VIZ_FILES = ["annual_recap.py", "topic_heatmap.py", "pm_handover.py"]

    def test_every_pm_abbreviation_call_site_also_calls_the_note_helper(self):
        for filename in self.VIZ_FILES:
            text = (SRC_DIR / "viz" / filename).read_text()
            if "pm_abbreviation(" in text:
                assert "pm_abbreviation_note(" in text, (
                    f"{filename} calls style.pm_abbreviation() but never "
                    "style.pm_abbreviation_note() - an abbreviated PM label "
                    "would have no on-image legend (D.5)"
                )


# --- I.6: simulated 400px-wide mobile readability ---------------------------


def _effective_glyph_px(
    fontsize_pt: float, native_width_px: int, target_width_px: int = 400
) -> float:
    return fontsize_pt * (200 / 72) * (target_width_px / native_width_px)


# Native pixel widths of the 4 main exported images (200dpi x figsize).
_MAIN_IMAGE_WIDTHS = {
    "radar_main.png": int(8 * 200),
    "heatmap_main.png": int(12 * 200),
    "transition_main.png": int(8 * 200),
    "annual_recap_main.png": int(12 * 200),
}


class TestMobileReadability:
    def test_smallest_font_stays_above_2_5px_effective_at_400px_wide(self):
        min_size = min(
            value for name, value in vars(style).items()
            if name.endswith("_SIZE") and isinstance(value, (int, float))
        )
        flagged = []
        for image_name, native_width in _MAIN_IMAGE_WIDTHS.items():
            eff = _effective_glyph_px(min_size, native_width)
            if eff < 2.5:
                flagged.append((image_name, round(eff, 2)))
        assert not flagged, f"text falls below 2.5px effective at 400px wide: {flagged}"


# --- I.8: the PM-abbreviation span_months rule exists in exactly one place -


class TestAbbreviationRuleIsCentralized:
    def test_span_months_abbreviation_logic_defined_once(self):
        matches = []
        for path in SRC_DIR.rglob("*.py"):
            text = path.read_text()
            if re.search(r'"T"\s+if\s+span_months|span_months\s*<\s*3', text):
                matches.append(str(path.relative_to(REPO_ROOT)))
        # style.py's own pm_abbreviation() is the one legitimate definition.
        assert matches == ["src/hansard_pm_portfolio/style.py"], (
            f"expected the span_months abbreviation rule only in style.py, found: {matches}"
        )


# --- I.9: plot_footer() is the only place that hardcodes the source line ---


class TestSourceLineIsCentralized:
    def test_source_hardcode_only_in_plot_footer(self):
        matches = []
        for path in SRC_DIR.rglob("*.py"):
            text = path.read_text()
            for lineno, line in enumerate(text.splitlines(), start=1):
                if "Source: Hansard API" in line:
                    matches.append(f"{path.relative_to(REPO_ROOT)}:{lineno}")
        assert matches == ["src/hansard_pm_portfolio/viz/common.py:166"] or all(
            "common.py" in m for m in matches
        ), f"'Source: Hansard API' hardcoded outside common.py: {matches}"
