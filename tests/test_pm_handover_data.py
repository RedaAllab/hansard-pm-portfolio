import pandas as pd
import pytest

from hansard_pm_portfolio import data_access as da


def _events():
    # Two PMs, one transition on 2022-09-06. Sittings chosen to exercise
    # the window edges (inclusive start of "after", exclusive end of
    # "before") and the mini-budget overlap flag. 2022-07-04 sits outside
    # the 6-week window (42 days before 2022-09-06 is 2022-07-26); the two
    # August sittings share a month, for the monthly-average test.
    return pd.DataFrame(
        {
            "pm_name": ["A", "A", "A", "A", "B", "B", "B"],
            "sitting_date": pd.to_datetime(
                ["2022-07-04", "2022-08-05", "2022-08-10", "2022-09-06",
                 "2022-09-07", "2022-10-12", "2022-11-01"]
            ),
            "net_certainty": [0.01, 0.02, 0.04, 0.03, 0.04, 0.05, 0.06],
            "vader_compound": [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
        }
    )


def _transitions():
    return pd.DataFrame(
        {"before_pm": ["A"], "after_pm": ["B"], "transition_date": [pd.Timestamp("2022-09-06")]}
    )


class TestLoadPmTransitions:
    def _tenures(self):
        return pd.DataFrame(
            {
                "pm_name": ["A", "B", "C"],
                "tenure_start": pd.to_datetime(["2020-01-01", "2021-01-01", "2022-01-01"]),
                "tenure_end": pd.to_datetime(["2021-01-01", "2022-01-01", "2023-01-01"]),
            }
        )

    def test_one_row_fewer_than_tenures(self, monkeypatch):
        monkeypatch.setattr(da, "load_pm_tenures", self._tenures)
        transitions = da.load_pm_transitions()
        assert len(transitions) == 2
        assert transitions.iloc[0].to_dict() == {
            "before_pm": "A", "after_pm": "B", "transition_date": pd.Timestamp("2021-01-01"),
        }


class TestBuildTransitionWindows:
    def test_before_side_excludes_the_transition_date_itself(self):
        windows = da.build_transition_windows(_events(), _transitions(), weeks=6)
        before = windows[windows["side"] == "before"]
        assert pd.Timestamp("2022-09-06") not in set(before["sitting_date"])

    def test_before_side_excludes_sittings_outside_the_window(self):
        # 2022-07-04 is more than 6 weeks (42 days) before 2022-09-06.
        windows = da.build_transition_windows(_events(), _transitions(), weeks=6)
        before = windows[windows["side"] == "before"]
        assert pd.Timestamp("2022-07-04") not in set(before["sitting_date"])
        assert pd.Timestamp("2022-08-10") in set(before["sitting_date"])
        assert pd.Timestamp("2022-08-05") in set(before["sitting_date"])

    def test_after_side_includes_the_transition_date_itself(self):
        windows = da.build_transition_windows(_events(), _transitions(), weeks=6)
        after = windows[windows["side"] == "after"]
        assert pd.Timestamp("2022-09-07") in set(after["sitting_date"])

    def test_days_from_transition_sign(self):
        windows = da.build_transition_windows(_events(), _transitions(), weeks=6)
        row = windows[windows["sitting_date"] == pd.Timestamp("2022-08-10")].iloc[0]
        assert row["days_from_transition"] < 0
        row = windows[windows["sitting_date"] == pd.Timestamp("2022-09-07")].iloc[0]
        assert row["days_from_transition"] >= 0

    def test_transition_label_uses_surnames(self):
        windows = da.build_transition_windows(_events(), _transitions(), weeks=6)
        assert set(windows["transition_label"]) == {"A to B"}


class TestInCrisisWindow:
    def test_inside_mini_budget_window(self):
        assert da.in_crisis_window(pd.Timestamp("2022-10-12"), "mini_budget")

    def test_outside_mini_budget_window(self):
        assert not da.in_crisis_window(pd.Timestamp("2022-11-01"), "mini_budget")

    def test_boundary_dates_are_inclusive(self):
        start, end = da.CRISIS_WINDOWS["mini_budget"]
        assert da.in_crisis_window(pd.Timestamp(start), "mini_budget")
        assert da.in_crisis_window(pd.Timestamp(end), "mini_budget")


class TestMonthlyHandoverMetrics:
    def test_averages_within_a_month(self):
        events = _events()
        monthly = da.monthly_handover_metrics(events)
        august = monthly.loc["2022-08-01", "net_certainty"]
        assert august == pytest.approx((0.02 + 0.04) / 2)

    def test_columns_match_handover_metrics(self):
        monthly = da.monthly_handover_metrics(_events())
        assert list(monthly.columns) == [key for key, _ in da.HANDOVER_METRICS]


@pytest.fixture
def sibling_repo_available():
    try:
        da.hansard_pm_nlp_dir()
    except FileNotFoundError:
        pytest.skip("hansard-pm-nlp not cloned as a sibling directory")


class TestLiveIntegration:
    def test_event_study_dataset_includes_truss_unlike_the_classifier(self, sibling_repo_available):
        events = da.load_event_study_dataset()
        assert "Liz Truss" in set(events["pm_name"])
        assert sorted(events["pm_name"].unique()) == sorted(da.IN_SCOPE_PMS)

    def test_three_transitions_for_four_in_scope_pms(self, sibling_repo_available):
        transitions = da.load_pm_transitions()
        assert len(transitions) == 3
        assert "Andy Burnham" not in set(transitions["before_pm"]) | set(transitions["after_pm"])

    def test_truss_tenure_is_split_across_both_of_her_transitions(self, sibling_repo_available):
        # Her 49-day tenure is shorter than 2x the 6-week window, so her 5
        # sittings appear on both sides of her two transitions - the one on
        # 2022-10-12 specifically appears as both an "after" sitting for
        # Johnson -> Truss and a "before" sitting for Truss -> Sunak.
        windows = da.build_transition_windows()
        truss_appearances = windows[windows["sitting_date"] == pd.Timestamp("2022-10-12")]
        assert set(truss_appearances["transition_label"]) == {"Johnson to Truss", "Truss to Sunak"}

    def test_mini_budget_overlap_sitting_is_flagged(self, sibling_repo_available):
        assert da.in_crisis_window(pd.Timestamp("2022-10-12"), "mini_budget")
