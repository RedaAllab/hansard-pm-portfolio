"""Infrastructure shared by 2+ projects: locating the sibling hansard-pm-nlp
checkout, parquet reading, PM scope, tenure dates, crisis windows, and the
LDA topic-weight layer projects 02 and 04 both build on. Project-specific
logic lives in style_duel.py / topic_heatmap.py / pm_handover.py /
annual_recap.py instead - see the package's own __init__.py.
"""

import os
from pathlib import Path

import duckdb
import pandas as pd

# --- Locating the sibling hansard-pm-nlp checkout ---------------------------

REPO_ROOT = Path(__file__).resolve().parents[3]


def hansard_pm_nlp_dir() -> Path:
    """Resolve the hansard-pm-nlp checkout this repo reads artifacts from.

    Override with the HANSARD_PM_NLP_DIR env var; defaults to a sibling
    checkout (`../hansard-pm-nlp`), matching how a portfolio author
    typically lays out the two repos side by side on disk (see README
    "Reproduire ce visuel").
    """
    override = os.environ.get("HANSARD_PM_NLP_DIR")
    default = REPO_ROOT.parent / "hansard-pm-nlp"
    path = Path(override).expanduser().resolve() if override else default
    if not path.is_dir():
        raise FileNotFoundError(
            f"hansard-pm-nlp checkout not found at {path}. Clone "
            "https://github.com/RedaAllab/hansard-pm-nlp as a sibling "
            "directory, or set HANSARD_PM_NLP_DIR to point at it."
        )
    return path


def _processed_dir() -> Path:
    return hansard_pm_nlp_dir() / "data" / "processed"


def _input_dir() -> Path:
    return hansard_pm_nlp_dir() / "data" / "input"


# --- Scope (STYLE_DUEL.md's radar; Phase 6's classifier) --------------------

# Explicit allowlist, not "whichever PMs are in the file" - excludes Andy
# Burnham by design. See ARCHITECTURE.md §7.
IN_SCOPE_PMS = ["Boris Johnson", "Liz Truss", "Rishi Sunak", "Keir Starmer"]

# Phase 6's classifier scope - Truss excluded upstream. See ARCHITECTURE.md §7.
CLASSIFIER_PMS = ["Boris Johnson", "Rishi Sunak", "Keir Starmer"]


# --- Parquet reading ---------------------------------------------------------


def read_parquet(path: Path) -> pd.DataFrame:
    """Read via DuckDB, not pandas.read_parquet - see ARCHITECTURE.md §4."""
    return duckdb.connect().execute(f"SELECT * FROM '{path}'").df()


# --- PM tenures ---------------------------------------------------------------


def load_pm_tenures() -> pd.DataFrame:
    """PM tenure start/end dates, restricted to IN_SCOPE_PMS.

    hansard-pm-nlp stores these in data/input/pm_tenures.parquet - verified
    by hand to match PHASE0_SCOPING.md (hansard-pm-extraction) exactly, so
    this repo reads them from here rather than cloning a third sibling repo
    for 4 dates.
    """
    tenures = read_parquet(_input_dir() / "pm_tenures.parquet")
    tenures = tenures[tenures["pm_name"].isin(IN_SCOPE_PMS)]
    return tenures.sort_values("tenure_start").reset_index(drop=True)


# --- Crisis windows (project 02's heatmap bands; project 03's overlap flag) --

# Ported from hansard_pm_nlp.event_study.CRISIS_WINDOWS, verified against
# PHASE0_SCOPING.md (hansard-pm-extraction).
CRISIS_WINDOWS = {
    "covid19": ("2020-03-23", "2021-07-19"),
    "mini_budget": ("2022-09-23", "2022-10-17"),
    "ukraine_invasion": ("2022-02-24", "2022-05-24"),
    "labour_leadership_crisis": ("2026-05-07", "2026-07-20"),
}
# Display labels for the bands above - not part of the ported constant, so
# the two can't silently drift if CRISIS_WINDOWS is ever re-synced from
# upstream.
CRISIS_LABELS = {
    "covid19": "Covid-19",
    "mini_budget": "Mini-budget",
    "ukraine_invasion": "Invasion of Ukraine",
    "labour_leadership_crisis": "Labour leadership crisis",
}


# --- Event-study table (project 03's windows; project 04's word/tone cols) --


def load_event_study_dataset() -> pd.DataFrame:
    """One row per (PM, sitting date), 296 sittings, all 4 in-scope PMs -
    Phase 7's own event-study table (`event_study_dataset.parquet`), reused
    unchanged rather than recomputed. Unlike Phase 6's classifier, Liz Truss
    is included (her 5 sittings are the only overlap with the mini-budget
    crisis window).
    """
    events = read_parquet(_processed_dir() / "event_study_dataset.parquet")
    events = events[events["pm_name"].isin(IN_SCOPE_PMS)].copy()
    events["sitting_date"] = pd.to_datetime(events["sitting_date"])
    return events.sort_values("sitting_date").reset_index(drop=True)


# --- LDA topic-weight layer (project 02's heatmap; project 04's dominant theme)

# Hand-written editorial labels, not a reuse of existing text - see
# ARCHITECTURE.md §10.
MERGED_TOPIC_LABEL = "Ukraine, Russia and international security"  # topic_0 + topic_1
TOPIC_LABELS = {
    "topic_6": "Brexit and the Northern Ireland deal",
    "topic_3": "Post-Brexit trade relations",
    "topic_5": "Covid-19: restrictions and testing",
    "topic_7": "Covid-19: vaccines and schools",
    "topic_9": "Covid-19: NHS and public inquiry",
    "topic_11": "Afghanistan and the withdrawal from Kabul",
    "topic_8": "Climate and the COP26 summit",
    "topic_10": "Israel, Gaza and the Middle East",
    "topic_2": "Transport and major infrastructure projects",
    "topic_12": "Budget and domestic policy",
    "topic_4": "Public inquiries: justice and truth",
    "topic_13": "Appointments and security vetting",
}
# Grouped thematically, not raw topic-number order - THEMATIC_HEATMAP.md §7.
TOPIC_DISPLAY_ORDER = [
    MERGED_TOPIC_LABEL,
    "Brexit and the Northern Ireland deal",
    "Post-Brexit trade relations",
    "Covid-19: restrictions and testing",
    "Covid-19: vaccines and schools",
    "Covid-19: NHS and public inquiry",
    "Afghanistan and the withdrawal from Kabul",
    "Climate and the COP26 summit",
    "Israel, Gaza and the Middle East",
    "Transport and major infrastructure projects",
    "Budget and domestic policy",
    "Public inquiries: justice and truth",
    "Appointments and security vetting",
]


def load_topic_weights() -> pd.DataFrame:
    """Document x topic weight matrix (Phase 5): one row per (PM,
    sitting_date), topic_0..topic_13 columns, all 4 in-scope PMs - unlike
    Phase 6's classifier, Phase 5's LDA run was never PM-restricted, so
    Truss's 5 documents are present here.
    """
    topics = read_parquet(_processed_dir() / "lda_topics.parquet")
    topics = topics[topics["pm_name"].isin(IN_SCOPE_PMS)]
    return topics.sort_values("sitting_date").reset_index(drop=True)


def merge_overlapping_topics(topic_weights: pd.DataFrame) -> pd.DataFrame:
    """Sum topic_0 + topic_1 into MERGED_TOPIC_LABEL, rename the rest via
    TOPIC_LABELS. Ported from hansard_pm_nlp.dashboard_helpers.
    """
    merged = topic_weights.copy()
    merged[MERGED_TOPIC_LABEL] = merged["topic_0"] + merged["topic_1"]
    return merged.drop(columns=["topic_0", "topic_1"]).rename(columns=TOPIC_LABELS)
