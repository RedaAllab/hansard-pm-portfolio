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
    ("mtld", "Diversité lexicale (MTLD)"),
    ("mean_flesch_kincaid_grade", "Lisibilité (Flesch-Kincaid)"),
    ("mean_hedge_rate", "Nuance (« hedging »)"),
    ("mean_net_certainty", "Certitude nette"),
    ("fw_not_rate", "Fréquence de « not »"),
    ("mean_words_per_sentence", "Mots par phrase"),
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
# French display labels for the bands above - not part of the ported
# constant, so the two can't silently drift if CRISIS_WINDOWS is ever
# re-synced from upstream.
CRISIS_LABELS = {
    "covid19": "Covid-19",
    "mini_budget": "Mini-budget",
    "ukraine_invasion": "Invasion de l'Ukraine",
    "labour_leadership_crisis": "Leadership travailliste",
}

# Hand-written from phase5_lda_report.md's keyword lists (K=14). Neither
# phase5_lda_report.md nor app.py's own topic_labels dict contain a
# human-language interpretation anywhere in hansard-pm-nlp - both only ever
# show algorithmic top-3-keyword labels (e.g. "T2: hs, project, rail") - so
# writing these is new editorial work for this project, not a rename of
# something that already existed elsewhere. Topic numbers (see
# phase5_lda_report.md) are noted in comments for traceability back to the
# keyword lists these were written from.
MERGED_TOPIC_LABEL = "Ukraine, Russie et sécurité internationale"  # topic_0 + topic_1
TOPIC_LABELS = {
    "topic_6": "Brexit et l'accord nord-irlandais",
    "topic_3": "Relations commerciales post-Brexit",
    "topic_5": "Covid-19 : restrictions et tests",
    "topic_7": "Covid-19 : vaccins et écoles",
    "topic_9": "Covid-19 : NHS et enquête publique",
    "topic_11": "Afghanistan et le retrait de Kaboul",
    "topic_8": "Climat et sommet de la COP26",
    "topic_10": "Israël, Gaza et le Moyen-Orient",
    "topic_2": "Transports et grands projets d'infrastructure",
    "topic_12": "Budget et politique intérieure",
    "topic_4": "Enquêtes publiques : justice et vérité",
    "topic_13": "Nominations et vetting de sécurité",
}
# Row order for the heatmap - grouped thematically (international security,
# the 3 Covid sub-topics kept together, then domestic) rather than raw
# topic-number order, per THEMATIC_HEATMAP.md section 7's explicit request
# to avoid "an arbitrary alphabetical scatter" of related topics.
TOPIC_DISPLAY_ORDER = [
    MERGED_TOPIC_LABEL,
    "Brexit et l'accord nord-irlandais",
    "Relations commerciales post-Brexit",
    "Covid-19 : restrictions et tests",
    "Covid-19 : vaccins et écoles",
    "Covid-19 : NHS et enquête publique",
    "Afghanistan et le retrait de Kaboul",
    "Climat et sommet de la COP26",
    "Israël, Gaza et le Moyen-Orient",
    "Transports et grands projets d'infrastructure",
    "Budget et politique intérieure",
    "Enquêtes publiques : justice et vérité",
    "Nominations et vetting de sécurité",
]

# THEMATIC_HEATMAP.md's own "3 Covid topics, deliberately not merged" visual
# (visuel secondaire 2) - unlike STYLE_DUEL.md's pos_INTJ gap, this rationale
# genuinely exists already: app.py's own Topics tab caption states it
# verbatim ("the three Covid-related topics ... track distinct sub-phases
# (restrictions/testing, vaccines/schools, NHS pay/inquiry) rather than one
# duplicated topic"), sourced from inspecting the K=14 word lists directly.
COVID_TOPIC_LABELS = [
    "Covid-19 : restrictions et tests",
    "Covid-19 : vaccins et écoles",
    "Covid-19 : NHS et enquête publique",
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
