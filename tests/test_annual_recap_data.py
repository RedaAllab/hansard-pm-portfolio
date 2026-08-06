import pandas as pd
import pytest

from hansard_pm_portfolio import data_access as da


def _tenures():
    return pd.DataFrame(
        {
            "pm_name": ["A", "B"],
            "tenure_start": pd.to_datetime(["2019-07-24", "2021-06-15"]),
            "tenure_end": pd.to_datetime(["2021-06-15", "2022-06-30"]),
        }
    )


class TestYearlyPmSegments:
    def test_full_year_sums_to_one(self):
        segments = da.yearly_pm_segments(_tenures(), 2020)
        assert segments == [("A", pytest.approx(1.0))]

    def test_partial_start_year_is_under_one(self):
        # A took office 2019-07-24, so 2019's segment share is under 1.0,
        # not padded to fill the year.
        segments = da.yearly_pm_segments(_tenures(), 2019)
        assert len(segments) == 1
        assert segments[0][0] == "A"
        assert segments[0][1] < 1.0

    def test_transition_year_splits_between_two_pms(self):
        segments = da.yearly_pm_segments(_tenures(), 2021)
        assert [pm for pm, _ in segments] == ["A", "B"]
        total = sum(share for _, share in segments)
        assert total == pytest.approx(1.0)

    def test_partial_end_year_is_under_one(self):
        segments = da.yearly_pm_segments(_tenures(), 2022)
        assert len(segments) == 1
        assert segments[0][0] == "B"
        assert segments[0][1] < 1.0


class TestYearlyCoverageFraction:
    def test_fully_covered_year_is_one(self):
        start, end = pd.Timestamp("2020-01-01"), pd.Timestamp("2020-12-31")
        assert da.yearly_coverage_fraction(2020, start, end) == 1.0

    def test_partial_start_year_is_under_one(self):
        corpus_start = pd.Timestamp("2019-07-25")
        corpus_end = pd.Timestamp("2020-12-31")
        fraction = da.yearly_coverage_fraction(2019, corpus_start, corpus_end)
        assert 0 < fraction < 1

    def test_partial_end_year_is_under_one(self):
        corpus_start = pd.Timestamp("2019-01-01")
        corpus_end = pd.Timestamp("2026-07-15")
        fraction = da.yearly_coverage_fraction(2026, corpus_start, corpus_end)
        assert 0 < fraction < 1

    def test_year_outside_corpus_is_zero(self):
        corpus_start = pd.Timestamp("2020-01-01")
        corpus_end = pd.Timestamp("2020-12-31")
        assert da.yearly_coverage_fraction(2025, corpus_start, corpus_end) == 0.0


class TestYearlyTopicMatrix:
    def _topics(self):
        df = pd.DataFrame({f"topic_{i}": [0.0, 0.0] for i in range(14)})
        df["sitting_date"] = pd.to_datetime(["2020-01-05", "2021-06-10"])
        df["topic_0"] = [0.2, 0.1]
        df["topic_2"] = [0.8, 0.9]
        return df

    def test_one_row_per_year(self):
        yearly = da.yearly_topic_matrix(self._topics())
        assert list(yearly.index.year) == [2020, 2021]

    def test_columns_match_display_order(self):
        yearly = da.yearly_topic_matrix(self._topics())
        assert list(yearly.columns) == da.TOPIC_DISPLAY_ORDER


class TestBuildAnnualRecap:
    def _events(self):
        return pd.DataFrame(
            {
                "pm_name": ["A", "A", "B"],
                "sitting_date": pd.to_datetime(["2020-01-05", "2020-06-10", "2021-06-10"]),
                "word_count": [1000, 2000, 500],
                "net_certainty": [0.01, 0.02, -0.01],
            }
        )

    def _topics(self):
        df = pd.DataFrame({f"topic_{i}": [0.0, 0.0, 0.0] for i in range(14)})
        df["sitting_date"] = pd.to_datetime(["2020-01-05", "2020-06-10", "2021-06-10"])
        df["pm_name"] = ["A", "A", "B"]
        df["topic_2"] = [0.9, 0.9, 0.1]
        df["topic_3"] = [0.1, 0.1, 0.9]
        return df

    def test_word_count_is_summed_per_year(self):
        recap = da.build_annual_recap(self._events(), self._topics(), _tenures())
        row = recap[recap["year"] == 2020].iloc[0]
        assert row["word_count"] == 3000

    def test_net_certainty_is_averaged_per_year(self):
        recap = da.build_annual_recap(self._events(), self._topics(), _tenures())
        row = recap[recap["year"] == 2020].iloc[0]
        assert row["net_certainty"] == pytest.approx((0.01 + 0.02) / 2)

    def test_dominant_theme_is_the_yearly_argmax(self):
        recap = da.build_annual_recap(self._events(), self._topics(), _tenures())
        row_2020 = recap[recap["year"] == 2020].iloc[0]
        row_2021 = recap[recap["year"] == 2021].iloc[0]
        assert row_2020["dominant_theme"] == da.TOPIC_LABELS["topic_2"]
        assert row_2021["dominant_theme"] == da.TOPIC_LABELS["topic_3"]

    def test_one_row_per_year_present_in_events(self):
        recap = da.build_annual_recap(self._events(), self._topics(), _tenures())
        assert sorted(recap["year"]) == [2020, 2021]

    def test_no_fifth_column_beyond_the_four_locked_indicators(self):
        # ANNUAL_RECAP.md section 2: PM segments, word volume, dominant
        # theme, tone, plus the year/coverage bookkeeping columns - no
        # additional metric column should slip in.
        recap = da.build_annual_recap(self._events(), self._topics(), _tenures())
        expected = {
            "year", "word_count", "net_certainty", "dominant_theme",
            "pm_segments", "coverage_fraction", "is_partial_year",
        }
        assert set(recap.columns) == expected


@pytest.fixture
def sibling_repo_available():
    try:
        da.hansard_pm_nlp_dir()
    except FileNotFoundError:
        pytest.skip("hansard-pm-nlp not cloned as a sibling directory")


class TestLiveIntegration:
    def test_recap_spans_2019_to_2026(self, sibling_repo_available):
        recap = da.build_annual_recap()
        assert list(recap["year"]) == list(range(2019, 2027))

    def test_2019_and_2026_are_the_only_partial_years(self, sibling_repo_available):
        recap = da.build_annual_recap()
        partial_years = set(recap[recap["is_partial_year"]]["year"])
        assert partial_years == {2019, 2026}

    def test_2022_and_2024_split_between_two_or_more_pms(self, sibling_repo_available):
        recap = da.build_annual_recap()
        for year in (2022, 2024):
            segments = recap[recap["year"] == year].iloc[0]["pm_segments"]
            assert len(segments) >= 2

    def test_every_dominant_theme_is_a_known_display_label(self, sibling_repo_available):
        recap = da.build_annual_recap()
        assert set(recap["dominant_theme"]) <= set(da.TOPIC_DISPLAY_ORDER)
