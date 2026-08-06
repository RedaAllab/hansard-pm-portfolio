"""Read-only access to hansard-pm-nlp's precomputed artifacts.

Architecture (see ARCHITECTURE.md for the full rationale): this repo never
imports the `hansard_pm_nlp` package and never re-runs a `build_*.py`
script. It only reads files hansard-pm-nlp already exported to
`data/processed/` and `data/input/` - the same "lightweight consumer"
pattern that repo's own `requirements-app.txt` established for the
Streamlit dashboard (torch/transformers/spacy/bertopic/gensim are never
needed here).

Two small, explicitly-justified exceptions to "never recompute anything",
both documented inline below:
  1. `_function_word_rate()` - one function-word frequency (`fw_not`) that
     Phase 6 only computed for the 3-PM classifier scope, recomputed here
     for all 4 PMs with the exact same pure-regex tokenizer hansard-pm-nlp
     itself uses (lexical.py's tokenize_words), so it needs no new
     dependency and stays methodologically identical to the other
     whole-corpus columns in eda_summary.csv.
  2. `normalize_radar()` - ported, not imported, from
     hansard_pm_nlp.dashboard_helpers (~10 lines of pure pandas) to avoid
     depending on the full hansard_pm_nlp package for one function.
"""

import os
import re
from pathlib import Path

import duckdb
import pandas as pd

# --- Locating the sibling hansard-pm-nlp checkout ---------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]


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

# The 4 PMs STYLE_DUEL.md's radar covers. Andy Burnham (PM from 2026-07-20,
# per PHASE0_SCOPING.md in hansard-pm-extraction) is deliberately excluded:
# he has zero sittings in the current corpus cutoff, and including him is
# out of scope for this project regardless (see conversation history) - kept
# as an explicit allowlist rather than "whichever PMs happen to be in the
# file" so a future corpus refresh can't silently add a 5th line to the
# radar.
IN_SCOPE_PMS = ["Boris Johnson", "Liz Truss", "Rishi Sunak", "Keir Starmer"]

# The 3 PMs Phase 6's classifier covers (Truss excluded upstream - too few
# documents for a train/test split; see hansard-pm-nlp/src/hansard_pm_nlp/split.py).
CLASSIFIER_PMS = ["Boris Johnson", "Rishi Sunak", "Keir Starmer"]


# --- Parquet reading ---------------------------------------------------------


def read_parquet(path: Path) -> pd.DataFrame:
    """Read a parquet file via DuckDB rather than pandas.read_parquet.

    hansard-pm-nlp's parquet files are written with a newer parquet-cpp-arrow
    (24.x) than the pyarrow this repo pins (pandas.read_parquet raises
    "Repetition level histogram size mismatch" on them - a known
    cross-version incompatibility in how column-chunk statistics are
    encoded). DuckDB's own parquet reader decodes the same files without
    issue, so it is used here instead of upgrading pyarrow, which would be
    a heavier, less predictable fix for a one-file dependency swap.
    """
    return duckdb.connect().execute(f"SELECT * FROM '{path}'").df()


# --- Style profile (radar) ---------------------------------------------------

_WORD_RE = re.compile(r"[a-zA-Z']+")


def _tokenize(text: str) -> list[str]:
    """Ported verbatim from hansard_pm_nlp.lexical.tokenize_words: lowercase
    word tokens, alphabetic + apostrophes only.
    """
    return _WORD_RE.findall(text.lower())


def _function_word_rate(contributions: pd.DataFrame, word: str) -> pd.Series:
    """Whole-corpus rate of `word` per PM, computed the same way
    eda_summary.csv's own `mtld` column is (hansard_pm_nlp.eda.py:
    concatenate each PM's contribution_text, then tokenize) - so this joins
    onto the radar's other columns without a methodology mismatch.
    """
    rates = {}
    for pm, group in contributions.groupby("pm_name"):
        tokens = _tokenize(" ".join(group["contribution_text"]))
        rates[pm] = tokens.count(word) / len(tokens) if tokens else float("nan")
    return pd.Series(rates, name=f"fw_{word}_rate")


def load_style_profile() -> pd.DataFrame:
    """One row per in-scope PM: the 6 STYLE_DUEL.md radar axes plus
    n_contributions (for the Truss sample-size caveat).

    5 of the 6 columns are hansard-pm-nlp's own whole-corpus Phase 3/4
    exports (eda_summary.csv, affect_summary.csv) - the same two files
    app.py's own "Stylometric profile by PM" radar tab merges
    (`profile = eda.merge(affect_sum, on=["pm_name", "n_contributions"])`),
    reused here identically for consistency with the live dashboard.

    STYLE_DUEL.md's 6th axis (pos_INTJ) only has a computed value for the
    3 classifier PMs (Phase 6 excludes Truss upstream, and POS-tagging
    needs spaCy, which this lightweight repo deliberately doesn't depend
    on - see ARCHITECTURE.md). `mean_words_per_sentence` is used instead:
    it is app.py's own 5th radar axis already, available for all 4 PMs
    with no recomputation, and it is independently the #5 permutation-
    importance feature for the better-performing Phase 6 model (see
    load_feature_importance("hgb")) - so the substitution keeps the
    "classifier-validated trait" framing honest rather than silently
    dropping it.
    """
    eda = pd.read_csv(_processed_dir() / "eda_summary.csv")
    affect = pd.read_csv(_processed_dir() / "affect_summary.csv")
    profile = eda.merge(affect, on=["pm_name", "n_contributions"])

    contributions = read_parquet(_processed_dir() / "pm_contributions_clean.parquet")
    contributions = contributions[contributions["pm_name"].isin(IN_SCOPE_PMS)]
    fw_not = _function_word_rate(contributions, "not")
    profile = profile.merge(fw_not.rename("fw_not_rate"), left_on="pm_name", right_index=True)

    profile = profile[profile["pm_name"].isin(IN_SCOPE_PMS)].reset_index(drop=True)
    missing = set(IN_SCOPE_PMS) - set(profile["pm_name"])
    if missing:
        raise ValueError(f"Style profile is missing PM(s): {missing}")
    return profile


RADAR_AXES = [
    ("mtld", "Lexical diversity (MTLD)"),
    ("mean_flesch_kincaid_grade", "Readability (Flesch-Kincaid)"),
    ("mean_hedge_rate", "Hedging rate"),
    ("mean_net_certainty", "Net certainty"),
    ("fw_not_rate", "Frequency of 'not'"),
    ("mean_words_per_sentence", "Words per sentence"),
]


def normalize_radar(
    profile: pd.DataFrame, cols: list[str], selected_pms: list[str]
) -> pd.DataFrame:
    """Min-max normalize each stylometric column across only `selected_pms`.

    Ported verbatim from hansard_pm_nlp.dashboard_helpers.normalize_radar
    (see module docstring). Scoping min/max to the current selection means
    a column where every selected PM ties is centered at 0.5 rather than
    left as NaN (division by zero).
    """
    subset = profile.set_index("pm_name").loc[selected_pms, cols].astype("float64")
    span = (subset.max() - subset.min()).replace(0, float("nan"))
    return ((subset - subset.min()) / span).fillna(0.5)


# --- Classifier outputs (feature importance, confusion matrix) --------------


def load_test_predictions() -> pd.DataFrame:
    return pd.read_csv(_processed_dir() / "phase6_test_predictions.csv")


def load_classifier_metrics() -> pd.DataFrame:
    return pd.read_csv(_processed_dir() / "phase6_metrics.csv")


def load_feature_importance(model: str) -> pd.DataFrame:
    """model: 'logreg' or 'hgb'. Top-15 permutation importances Phase 6
    exported for that model (phase6_classifier_report.md's own numbers -
    the CSV mirrors it exactly).
    """
    if model not in ("logreg", "hgb"):
        raise ValueError(f"model must be 'logreg' or 'hgb', got {model!r}")
    return pd.read_csv(_processed_dir() / f"phase6_feature_importance_{model}.csv")


def build_confusion_matrix(predictions: pd.DataFrame, pred_col: str) -> pd.DataFrame:
    """Row-normalized (% of each actual PM's test documents) confusion
    matrix, actual x predicted, ordered by CLASSIFIER_PMS on both axes so
    the diagonal is stable regardless of pandas' default label sort order.
    """
    counts = pd.crosstab(predictions["pm_name"], predictions[pred_col])
    counts = counts.reindex(index=CLASSIFIER_PMS, columns=CLASSIFIER_PMS, fill_value=0)
    return counts.div(counts.sum(axis=1), axis=0) * 100


# --- Topic heatmap (THEMATIC_HEATMAP.md) -------------------------------------

# Ported from hansard_pm_nlp.event_study.CRISIS_WINDOWS (4 date-string tuples
# - not worth a package dependency). These also match PHASE0_SCOPING.md in
# hansard-pm-extraction verbatim (verified by hand) - THEMATIC_HEATMAP.md
# section 0 asks for that repo's dates specifically, and this is where
# hansard-pm-nlp itself sources the same numbers from.
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

# Hand-written from phase5_lda_report.md's keyword lists (K=14). Neither
# phase5_lda_report.md nor app.py's own topic_labels dict contain a
# human-language interpretation anywhere in hansard-pm-nlp - both only ever
# show algorithmic top-3-keyword labels (e.g. "T2: hs, project, rail") - so
# writing these is new editorial work for this project, not a rename of
# something that already existed elsewhere. Topic numbers (see
# phase5_lda_report.md) are noted in comments for traceability back to the
# keyword lists these were written from.
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
# Row order for the heatmap - grouped thematically (international security,
# the 3 Covid sub-topics kept together, then domestic) rather than raw
# topic-number order, per THEMATIC_HEATMAP.md section 7's explicit request
# to avoid "an arbitrary alphabetical scatter" of related topics.
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

# THEMATIC_HEATMAP.md's own "3 Covid topics, deliberately not merged" visual
# (visuel secondaire 2) - unlike STYLE_DUEL.md's pos_INTJ gap, this rationale
# genuinely exists already: app.py's own Topics tab caption states it
# verbatim ("the three Covid-related topics ... track distinct sub-phases
# (restrictions/testing, vaccines/schools, NHS pay/inquiry) rather than one
# duplicated topic"), sourced from inspecting the K=14 word lists directly.
COVID_TOPIC_LABELS = [
    "Covid-19: restrictions and testing",
    "Covid-19: vaccines and schools",
    "Covid-19: NHS and public inquiry",
]


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
    """Sum topic_0 and topic_1 (documented as one near-duplicate Ukraine/
    Russia/security pair, see MERGED_TOPIC_LABEL) into a single column,
    rename the remaining 12 via TOPIC_LABELS.

    Ported from hansard_pm_nlp.dashboard_helpers.merge_overlapping_topics
    (see module docstring). The signature drops that function's
    `topic_labels`/`merged_label` parameters since this repo only ever
    merges the one documented pair - they're this module's own constants,
    not passed in per call.
    """
    merged = topic_weights.copy()
    merged[MERGED_TOPIC_LABEL] = merged["topic_0"] + merged["topic_1"]
    return merged.drop(columns=["topic_0", "topic_1"]).rename(columns=TOPIC_LABELS)


def monthly_topic_matrix(topics: pd.DataFrame | None = None) -> pd.DataFrame:
    """13 merged topics x month, mean weight, all in-scope PMs pooled -
    same aggregation as app.py's Topics tab
    (`merged.set_index("sitting_date").resample("MS").mean()`), columns
    reindexed to TOPIC_DISPLAY_ORDER.
    """
    topics = topics if topics is not None else load_topic_weights()
    topic_cols = [c for c in topics.columns if c.startswith("topic_")]
    merged = merge_overlapping_topics(topics[topic_cols])
    merged["sitting_date"] = topics["sitting_date"].values
    monthly = merged.set_index("sitting_date").resample("MS").mean().dropna(how="all")
    return monthly[TOPIC_DISPLAY_ORDER]


# --- PM handover (ROADMAP_PM_HANDOVER.md) ------------------------------------

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
    side="before"/"after" and with `days_from_transition` (negative before,
    zero or positive after) so the 3 transitions plot on a shared x-axis
    regardless of their real calendar dates.

    The window is a fixed +/-`weeks` on both sides (ROADMAP_PM_HANDOVER.md
    section 2's own decision) - it is not stretched to backfill a thin side.
    In practice two distinct causes leave a side sparse or empty, both kept
    visible rather than smoothed over:
      - Liz Truss's 49-day tenure is shorter than 2x the window, so it
        cannot fill either side symmetrically (anticipated in the roadmap).
      - Summer recess (before Johnson -> Truss) and the Parliament
        dissolution ahead of the 2024 general election (before Sunak ->
        Starmer) leave the "before" side with zero sittings in the strict
        6-week window for both of those transitions - a real gap in when
        Parliament sat, not a data-coverage problem, and not anticipated in
        the roadmap's own text (which only flagged the Truss-tenure case).
        See ARCHITECTURE.md.
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


# --- Annual recap (ROADMAP_ANNUAL_RECAP.md, see ANNUAL_RECAP.md) ------------

# The "tone" indicator: net_certainty again, not a 3rd distinct style metric.
# Same reasoning as HANDOVER_METRICS (ARCHITECTURE.md section 15) plus one
# more: net_certainty already recurs across project 01's radar and project
# 03's handover, so reusing it a third time gives the 4-project portfolio one
# throughline rather than a different "tone" metric per project. See
# ANNUAL_RECAP.md section 3.
RECAP_TONE_METRIC = "net_certainty"


def yearly_pm_segments(tenures: pd.DataFrame, year: int) -> list[tuple[str, float]]:
    """[(pm_name, share_of_the_calendar_year), ...] for `year`, clipped to
    [Jan 1, Jan 1 of next year]. Segments do not sum to 1.0 for a PM whose
    tenure only partly overlaps the year (2019: Johnson took office in
    July; 2026: Starmer's tenure continues past the corpus's last sitting)
    - a shorter bar is the honest picture, not padded to fill the card.
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
    """Share of `year` actually covered by the corpus's sitting dates, for
    sizing a year-card's width. 1.0 for a fully-covered year; under 1.0 for
    2019 (corpus starts 2019-07-25) and 2026 (corpus's last sitting is
    2026-07-15, an extraction cutoff, not the actual end of Starmer's
    tenure - found in Phase 0, not anticipated in the roadmap's own text,
    which only flagged 2019). See ANNUAL_RECAP.md section 1.
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
