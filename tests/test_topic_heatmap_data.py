import pandas as pd
import pytest

from hansard_pm_portfolio import data_access as da


def test_crisis_windows_and_labels_have_matching_keys():
    assert set(da.CRISIS_WINDOWS) == set(da.CRISIS_LABELS)


def test_crisis_windows_start_before_end():
    for name, (start, end) in da.CRISIS_WINDOWS.items():
        assert pd.Timestamp(start) < pd.Timestamp(end), name


class TestTopicLabels:
    def test_topic_labels_cover_exactly_the_12_non_merged_topics(self):
        # K=14 topics (topic_0..topic_13), topic_0/topic_1 merged into
        # MERGED_TOPIC_LABEL - the other 12 must each have a hand-written
        # label, no more, no fewer.
        expected = {f"topic_{i}" for i in range(2, 14)}
        assert set(da.TOPIC_LABELS) == expected

    def test_display_order_has_no_duplicates_and_covers_all_13(self):
        assert len(da.TOPIC_DISPLAY_ORDER) == 13
        assert len(set(da.TOPIC_DISPLAY_ORDER)) == 13

    def test_display_order_matches_labels_plus_merged(self):
        expected = {da.MERGED_TOPIC_LABEL, *da.TOPIC_LABELS.values()}
        assert set(da.TOPIC_DISPLAY_ORDER) == expected

    def test_covid_labels_are_a_subset_of_display_order(self):
        assert len(da.COVID_TOPIC_LABELS) == 3
        assert set(da.COVID_TOPIC_LABELS) <= set(da.TOPIC_DISPLAY_ORDER)

    def test_no_label_below_9pt_readability_floor_by_being_empty(self):
        # Not a font-size test (that's a plotting concern) - just guards
        # against an accidental empty-string label slipping in, which would
        # render as a blank row with no way to tell which topic it is.
        for label in da.TOPIC_DISPLAY_ORDER:
            assert label.strip()


class TestMergeOverlappingTopics:
    def _weights(self):
        return pd.DataFrame(
            {
                "topic_0": [0.1, 0.2],
                "topic_1": [0.05, 0.1],
                "topic_2": [0.3, 0.4],
                "topic_13": [0.55, 0.3],
            }
        )

    def test_sums_topic_0_and_1(self):
        merged = da.merge_overlapping_topics(self._weights())
        assert merged[da.MERGED_TOPIC_LABEL].tolist() == pytest.approx([0.15, 0.3])

    def test_drops_original_columns(self):
        merged = da.merge_overlapping_topics(self._weights())
        assert "topic_0" not in merged.columns
        assert "topic_1" not in merged.columns

    def test_renames_the_rest_via_topic_labels(self):
        merged = da.merge_overlapping_topics(self._weights())
        assert da.TOPIC_LABELS["topic_2"] in merged.columns
        assert da.TOPIC_LABELS["topic_13"] in merged.columns


class TestMonthlyTopicMatrix:
    def _topics(self):
        # Two documents in the same month (Jan 2020), one in Feb 2020 - mean
        # aggregation should average the two January rows, not sum them.
        # All 14 raw topic columns are required (production LDA output
        # always has topic_0..topic_13 for K=14) - the ones not under test
        # here are zero-filled.
        df = pd.DataFrame(
            {f"topic_{i}": [0.0, 0.0, 0.0] for i in range(14)},
        )
        df["sitting_date"] = pd.to_datetime(["2020-01-05", "2020-01-20", "2020-02-10"])
        df["topic_0"] = [0.2, 0.4, 0.1]
        df["topic_2"] = [0.8, 0.6, 0.9]
        return df

    def test_averages_within_a_month(self):
        monthly = da.monthly_topic_matrix(self._topics())
        jan = monthly.loc["2020-01-01", da.MERGED_TOPIC_LABEL]
        assert jan == pytest.approx(0.3)

    def test_columns_match_full_display_order(self):
        monthly = da.monthly_topic_matrix(self._topics())
        assert list(monthly.columns) == da.TOPIC_DISPLAY_ORDER

    def test_index_is_month_start(self):
        monthly = da.monthly_topic_matrix(self._topics())
        assert list(monthly.index) == [pd.Timestamp("2020-01-01"), pd.Timestamp("2020-02-01")]


@pytest.fixture
def sibling_repo_available():
    try:
        da.hansard_pm_nlp_dir()
    except FileNotFoundError:
        pytest.skip("hansard-pm-nlp not cloned as a sibling directory")


class TestLiveIntegration:
    def test_topic_weights_include_truss_unlike_the_classifier(self, sibling_repo_available):
        # Phase 5's LDA run was never PM-restricted, unlike Phase 6 -
        # Truss's 5 documents should be present here.
        topics = da.load_topic_weights()
        assert "Liz Truss" in set(topics["pm_name"])
        assert sorted(topics["pm_name"].unique()) == sorted(da.IN_SCOPE_PMS)

    def test_pm_tenures_are_four_in_scope_pms_in_date_order(self, sibling_repo_available):
        tenures = da.load_pm_tenures()
        assert tenures["pm_name"].tolist() == sorted(
            da.IN_SCOPE_PMS, key=lambda pm: tenures.set_index("pm_name")["tenure_start"][pm]
        )
        assert "Andy Burnham" not in set(tenures["pm_name"])

    def test_monthly_matrix_spans_all_13_display_topics(self, sibling_repo_available):
        monthly = da.monthly_topic_matrix()
        assert list(monthly.columns) == da.TOPIC_DISPLAY_ORDER
        assert monthly.shape[0] > 12  # more than a year of months
