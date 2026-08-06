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
