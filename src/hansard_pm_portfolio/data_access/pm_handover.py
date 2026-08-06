"""Data layer for project 03 (ROADMAP_PM_HANDOVER.md): the +/- 6 week
transition windows around each PM handover.
"""

import pandas as pd

from ._shared import CRISIS_WINDOWS, load_event_study_dataset, load_pm_tenures

# Phase 0's own recommendation to pair MTLD with net_certainty does not
# survive contact with the data: MTLD is a whole-corpus statistic (McCarthy &
# Jarvis 2010's segment-based algorithm needs long stretches of text to be
# stable - see mtld_over_time.parquet's own 1,500-word floor per bin), so a
# single sitting is far too short a unit to compute it on without the number
# being an artifact of sample size rather than style. Recomputing it from raw
# text at sitting-date granularity would also be new computation this repo
# has otherwise avoided (see ARCHITECTURE.md section 3). `vader_compound` is
# used instead of MTLD: it is already computed per sitting date for all 4
# in-scope PMs in `event_study_dataset.parquet` (Phase 7 built exactly this
# table for its own PM x crisis regressions, Truss's 5 sittings included,
# unlike Phase 6's classifier), so pairing it with `net_certainty` needs zero
# new computation and reads two genuinely different axes ("style" and
# "sentiment", per this project's own stated objective) rather than two
# style metrics. Documented in ARCHITECTURE.md.
HANDOVER_METRICS = [
    ("net_certainty", "Net certainty"),
    ("vader_compound", "Sentiment (VADER)"),
]

TRANSITION_WINDOW_WEEKS = 6


def load_pm_transitions() -> pd.DataFrame:
    """The 3 consecutive-PM handovers within IN_SCOPE_PMS, derived from
    `load_pm_tenures()` rather than hardcoded, so a change in PM scope
    propagates automatically instead of leaving a stale 4th row.
    """
    tenures = load_pm_tenures()
    rows = [
        {
            "before_pm": tenures.loc[i - 1, "pm_name"],
            "after_pm": tenures.loc[i, "pm_name"],
            "transition_date": pd.Timestamp(tenures.loc[i, "tenure_start"]),
        }
        for i in range(1, len(tenures))
    ]
    return pd.DataFrame(rows)


def in_crisis_window(date: pd.Timestamp, crisis_key: str) -> bool:
    """Whether `date` falls inside the named CRISIS_WINDOWS band (inclusive).
    Used to flag the one sitting (2022-10-12, Liz Truss) that sits in both
    the Truss -> Sunak "before" window and the mini-budget crisis window -
    ROADMAP_PM_HANDOVER.md section 2 asks that this overlap be shown, not
    treated as an isolated "PM effect".
    """
    start, end = CRISIS_WINDOWS[crisis_key]
    return pd.Timestamp(start) <= pd.Timestamp(date) <= pd.Timestamp(end)


def build_transition_windows(
    events: pd.DataFrame | None = None,
    transitions: pd.DataFrame | None = None,
    weeks: int = TRANSITION_WINDOW_WEEKS,
) -> pd.DataFrame:
    """One row per sitting within `weeks` of any transition, labeled
    side="before"/"after", with `days_from_transition` for a shared x-axis
    across the 3 transitions. Fixed window, never stretched to fill a thin
    side - two of the six sides are sparse or empty for reasons beyond
    Truss's short tenure; see ARCHITECTURE.md §17.
    """
    events = events if events is not None else load_event_study_dataset()
    transitions = transitions if transitions is not None else load_pm_transitions()
    delta = pd.Timedelta(weeks=weeks)

    frames = []
    for _, t in transitions.iterrows():
        d = t["transition_date"]
        before = events[
            (events["pm_name"] == t["before_pm"])
            & (events["sitting_date"] < d)
            & (events["sitting_date"] >= d - delta)
        ].copy()
        before["side"] = "before"
        after = events[
            (events["pm_name"] == t["after_pm"])
            & (events["sitting_date"] >= d)
            & (events["sitting_date"] < d + delta)
        ].copy()
        after["side"] = "after"

        window = pd.concat([before, after], ignore_index=True)
        window["transition_label"] = f"{t['before_pm'].split()[-1]} to {t['after_pm'].split()[-1]}"
        window["transition_date"] = d
        window["days_from_transition"] = (window["sitting_date"] - d).dt.days
        frames.append(window)

    return pd.concat(frames, ignore_index=True)


def monthly_handover_metrics(events: pd.DataFrame | None = None) -> pd.DataFrame:
    """HANDOVER_METRICS x month, mean value, all in-scope PMs pooled on one
    continuous timeline - same "MS" resampling convention as
    `monthly_topic_matrix()`, for the secondary full-corpus timeline visual.
    """
    events = events if events is not None else load_event_study_dataset()
    cols = [key for key, _ in HANDOVER_METRICS]
    monthly = events.set_index("sitting_date")[cols].resample("MS").mean()
    return monthly.dropna(how="all")
