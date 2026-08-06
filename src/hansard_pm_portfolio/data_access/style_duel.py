"""Data layer for project 01 (STYLE_DUEL.md): the style-profile radar and
the classifier outputs (feature importance, confusion matrix).

One explicitly-justified exception to "never recompute anything":
`_function_word_rate()` recomputes one function-word frequency (`fw_not`)
that Phase 6 only computed for the 3-PM classifier scope, using the exact
same pure-regex tokenizer hansard-pm-nlp itself uses (lexical.py's
tokenize_words) - no new dependency, methodologically identical to the
other whole-corpus columns in eda_summary.csv.
"""

import re

import pandas as pd

from ._shared import CLASSIFIER_PMS, IN_SCOPE_PMS, _processed_dir, read_parquet

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
    n_contributions. pos_INTJ is substituted with mean_words_per_sentence -
    see ARCHITECTURE.md §5.
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
