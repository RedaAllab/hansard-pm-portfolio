"""Data layer for project 04 (ROADMAP_ANNUAL_RECAP.md / ANNUAL_RECAP.md):
the year-by-year recap table, built on project 03's event-study loader and
project 02's topic-weight layer rather than recomputing either.
"""

import pandas as pd

from ._shared import (
    TOPIC_DISPLAY_ORDER,
    load_event_study_dataset,
    load_pm_tenures,
    load_topic_weights,
    merge_overlapping_topics,
)

# net_certainty again, not a 3rd style metric - this portfolio's recurring
# tone signature (project 01's radar, project 03's handover). See
# ARCHITECTURE.md §19 / ANNUAL_RECAP.md §3.
RECAP_TONE_METRIC = "net_certainty"


def yearly_pm_segments(tenures: pd.DataFrame, year: int) -> list[tuple[str, float]]:
    """[(pm_name, share_of_the_calendar_year), ...] for `year`. Segments
    don't sum to 1.0 for a PM whose tenure only partly overlaps the year -
    a shorter bar is the honest picture, not padded to fill the card.
    """
    year_start = pd.Timestamp(f"{year}-01-01")
    year_end = pd.Timestamp(f"{year + 1}-01-01")
    total_days = (year_end - year_start).days

    segments = []
    for _, row in tenures.iterrows():
        start = max(pd.Timestamp(row["tenure_start"]), year_start)
        end = min(pd.Timestamp(row["tenure_end"]), year_end)
        if end > start:
            segments.append((row["pm_name"], (end - start).days / total_days))
    return segments


def yearly_coverage_fraction(
    year: int, corpus_start: pd.Timestamp, corpus_end: pd.Timestamp
) -> float:
    """Share of `year` covered by the corpus's sitting dates, for sizing a
    year-card's width. Under 1.0 for 2019 and 2026, both partial - see
    ANNUAL_RECAP.md §1.
    """
    year_start = pd.Timestamp(f"{year}-01-01")
    year_end = pd.Timestamp(f"{year + 1}-01-01")
    total_days = (year_end - year_start).days
    covered_start = max(year_start, corpus_start)
    covered_end = min(year_end, corpus_end + pd.Timedelta(days=1))
    covered_days = max((covered_end - covered_start).days, 0)
    return covered_days / total_days


def yearly_topic_matrix(topics: pd.DataFrame | None = None) -> pd.DataFrame:
    """13 merged topics x calendar year, mean weight, all in-scope PMs
    pooled - the same aggregation as `monthly_topic_matrix()`, resampled to
    "YS" instead of "MS", for `build_annual_recap()`'s dominant-theme
    column.
    """
    topics = topics if topics is not None else load_topic_weights()
    topic_cols = [c for c in topics.columns if c.startswith("topic_")]
    merged = merge_overlapping_topics(topics[topic_cols])
    merged["sitting_date"] = topics["sitting_date"].values
    yearly = merged.set_index("sitting_date").resample("YS").mean().dropna(how="all")
    return yearly[TOPIC_DISPLAY_ORDER]


def build_annual_recap(
    events: pd.DataFrame | None = None,
    topics: pd.DataFrame | None = None,
    tenures: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """One row per calendar year covered by the corpus (2019-2026): word
    volume (sum), tone (mean net_certainty), dominant theme (argmax of the
    year's mean topic weight), the PM tenure segments for the header/card
    band, and whether the year is only partially covered. The 4 fixed
    indicators locked in ANNUAL_RECAP.md section 2, no 5th column added.
    """
    events = events if events is not None else load_event_study_dataset()
    topics = topics if topics is not None else load_topic_weights()
    tenures = tenures if tenures is not None else load_pm_tenures()

    events = events.copy()
    events["year"] = events["sitting_date"].dt.year
    yearly_words = events.groupby("year")["word_count"].sum()
    yearly_tone = events.groupby("year")[RECAP_TONE_METRIC].mean()

    topic_matrix = yearly_topic_matrix(topics)
    dominant_theme = topic_matrix.idxmax(axis=1)
    dominant_theme.index = dominant_theme.index.year

    corpus_start, corpus_end = events["sitting_date"].min(), events["sitting_date"].max()

    rows = []
    for year in sorted(events["year"].unique()):
        coverage = yearly_coverage_fraction(year, corpus_start, corpus_end)
        rows.append(
            {
                "year": year,
                "word_count": int(yearly_words.get(year, 0)),
                "net_certainty": yearly_tone.get(year, float("nan")),
                "dominant_theme": dominant_theme.get(year),
                "pm_segments": yearly_pm_segments(tenures, year),
                "coverage_fraction": coverage,
                "is_partial_year": coverage < 0.99,
            }
        )
    return pd.DataFrame(rows)
