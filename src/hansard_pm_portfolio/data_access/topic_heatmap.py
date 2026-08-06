"""Data layer for project 02 (THEMATIC_HEATMAP.md): the monthly topic
matrix. Topic loading, the T0+T1 merge, and the 13 display labels live in
_shared.py instead - project 04 reuses that same layer for its yearly
dominant-theme column.
"""

import pandas as pd

from ._shared import TOPIC_DISPLAY_ORDER, load_topic_weights, merge_overlapping_topics

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
