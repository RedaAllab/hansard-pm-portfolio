"""Read-only access to hansard-pm-nlp's precomputed artifacts, split by
project so each file stays small enough to read in one sitting:

- `_shared.py`: infrastructure 2+ projects reuse (I/O, PM scope, tenures,
  crisis windows, the LDA topic layer).
- `style_duel.py`, `topic_heatmap.py`, `pm_handover.py`, `annual_recap.py`:
  one project's own logic each.

This module re-exports the combined public API, so existing call sites
(`from hansard_pm_portfolio import data_access as da; da.load_style_profile()`)
are unaffected by the split - see ARCHITECTURE.md §21.

This repo never imports the `hansard_pm_nlp` package and never re-runs a
`build_*.py` script; it only reads files hansard-pm-nlp already exported to
`data/processed/` and `data/input/`, the same "lightweight consumer" pattern
that repo's own Streamlit dashboard uses.
"""

from ._shared import (
    CLASSIFIER_PMS,
    CRISIS_LABELS,
    CRISIS_WINDOWS,
    IN_SCOPE_PMS,
    MERGED_TOPIC_LABEL,
    REPO_ROOT,
    TOPIC_DISPLAY_ORDER,
    TOPIC_LABELS,
    hansard_pm_nlp_dir,
    load_event_study_dataset,
    load_pm_tenures,
    load_topic_weights,
    merge_overlapping_topics,
    read_parquet,
)
from .annual_recap import (
    RECAP_TONE_METRIC,
    build_annual_recap,
    yearly_coverage_fraction,
    yearly_pm_segments,
    yearly_topic_matrix,
)
from .pm_handover import (
    HANDOVER_METRICS,
    TRANSITION_WINDOW_WEEKS,
    build_transition_windows,
    in_crisis_window,
    load_pm_transitions,
    monthly_handover_metrics,
)
from .style_duel import (
    RADAR_AXES,
    build_confusion_matrix,
    load_classifier_metrics,
    load_feature_importance,
    load_style_profile,
    load_test_predictions,
    normalize_radar,
)
from .topic_heatmap import COVID_TOPIC_LABELS, monthly_topic_matrix

__all__ = [
    "CLASSIFIER_PMS",
    "COVID_TOPIC_LABELS",
    "CRISIS_LABELS",
    "CRISIS_WINDOWS",
    "HANDOVER_METRICS",
    "IN_SCOPE_PMS",
    "MERGED_TOPIC_LABEL",
    "RADAR_AXES",
    "RECAP_TONE_METRIC",
    "REPO_ROOT",
    "TOPIC_DISPLAY_ORDER",
    "TOPIC_LABELS",
    "TRANSITION_WINDOW_WEEKS",
    "build_annual_recap",
    "build_confusion_matrix",
    "build_transition_windows",
    "hansard_pm_nlp_dir",
    "in_crisis_window",
    "load_classifier_metrics",
    "load_event_study_dataset",
    "load_feature_importance",
    "load_pm_tenures",
    "load_pm_transitions",
    "load_style_profile",
    "load_test_predictions",
    "load_topic_weights",
    "merge_overlapping_topics",
    "monthly_handover_metrics",
    "monthly_topic_matrix",
    "normalize_radar",
    "read_parquet",
    "yearly_coverage_fraction",
    "yearly_pm_segments",
    "yearly_topic_matrix",
]
