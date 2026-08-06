import pandas as pd
import pytest

from hansard_pm_portfolio import data_access as da
from hansard_pm_portfolio.data_access.style_duel import _function_word_rate


def test_in_scope_pms_excludes_burnham():
    # See data_access.IN_SCOPE_PMS docstring: Andy Burnham (PM from
    # 2026-07-20) is out of scope for this project, kept as an explicit
    # allowlist rather than inferred from whatever the corpus happens to
    # contain.
    assert "Andy Burnham" not in da.IN_SCOPE_PMS
    assert da.IN_SCOPE_PMS == ["Boris Johnson", "Liz Truss", "Rishi Sunak", "Keir Starmer"]


def test_classifier_pms_excludes_truss():
    assert "Liz Truss" not in da.CLASSIFIER_PMS
    assert len(da.CLASSIFIER_PMS) == 3


class TestNormalizeRadar:
    def _profile(self):
        return pd.DataFrame(
            {
                "pm_name": ["A", "B", "C"],
                "x": [0.0, 5.0, 10.0],
                "y": [2.0, 2.0, 2.0],  # zero span across all 3
            }
        )

    def test_min_max_scaling(self):
        result = da.normalize_radar(self._profile(), ["x"], ["A", "B", "C"])
        assert result.loc["A", "x"] == 0.0
        assert result.loc["B", "x"] == 0.5
        assert result.loc["C", "x"] == 1.0

    def test_zero_span_centers_at_half(self):
        result = da.normalize_radar(self._profile(), ["y"], ["A", "B", "C"])
        assert (result["y"] == 0.5).all()

    def test_scoped_to_selection_only(self):
        # Deselecting C should rescale A/B's axis rather than leaving it
        # compressed by a PM no longer drawn (dashboard_helpers.py's own
        # rationale, ported here unchanged).
        result = da.normalize_radar(self._profile(), ["x"], ["A", "B"])
        assert result.loc["A", "x"] == 0.0
        assert result.loc["B", "x"] == 1.0


class TestFunctionWordRate:
    def test_counts_whole_word_occurrences_only(self):
        contributions = pd.DataFrame(
            {
                "pm_name": ["A", "A", "B"],
                "contribution_text": ["I will not do that", "Cannot is not not", "Notable point"],
            }
        )
        rates = _function_word_rate(contributions, "not")
        # A: tokens = [i, will, not, do, that, cannot, is, not, not] -> 3/9
        assert rates["A"] == pytest.approx(3 / 9)
        # B: "Notable" tokenizes to "notable", not "not" - must not
        # substring-match.
        assert rates["B"] == 0.0

    def test_empty_text_gives_nan(self):
        contributions = pd.DataFrame({"pm_name": ["A"], "contribution_text": [""]})
        rates = _function_word_rate(contributions, "not")
        assert pd.isna(rates["A"])


class TestBuildConfusionMatrix:
    def test_row_normalized_to_100(self):
        predictions = pd.DataFrame(
            {
                "pm_name": ["Boris Johnson"] * 4 + ["Rishi Sunak"] * 2 + ["Keir Starmer"] * 3,
                "pred_hgb": [
                    "Boris Johnson", "Boris Johnson", "Boris Johnson", "Rishi Sunak",
                    "Rishi Sunak", "Rishi Sunak",
                    "Keir Starmer", "Keir Starmer", "Boris Johnson",
                ],
            }
        )
        matrix = da.build_confusion_matrix(predictions, "pred_hgb")
        assert list(matrix.index) == da.CLASSIFIER_PMS
        assert list(matrix.columns) == da.CLASSIFIER_PMS
        for row_sum in matrix.sum(axis=1):
            assert row_sum == pytest.approx(100.0)
        assert matrix.loc["Boris Johnson", "Boris Johnson"] == pytest.approx(75.0)

    def test_missing_class_filled_with_zero_not_dropped(self):
        # A PM with zero test documents (e.g. a very small evaluation slice)
        # must still appear as an all-zero row rather than vanishing, or the
        # heatmap would silently show a 2x2 matrix.
        predictions = pd.DataFrame(
            {"pm_name": ["Boris Johnson"], "pred_hgb": ["Boris Johnson"]}
        )
        matrix = da.build_confusion_matrix(predictions, "pred_hgb")
        assert matrix.shape == (3, 3)
        assert matrix.loc["Rishi Sunak"].sum() == 0


@pytest.fixture
def sibling_repo_available():
    try:
        da.hansard_pm_nlp_dir()
    except FileNotFoundError:
        pytest.skip("hansard-pm-nlp not cloned as a sibling directory")


class TestLiveIntegration:
    """Exercises the real sibling checkout - skipped automatically when it
    is not present (e.g. a CI runner that only has this repo)."""

    def test_load_style_profile_covers_all_four_pms(self, sibling_repo_available):
        profile = da.load_style_profile()
        assert sorted(profile["pm_name"]) == sorted(da.IN_SCOPE_PMS)
        for col, _ in da.RADAR_AXES:
            assert col in profile.columns
            assert profile[col].notna().all()

    def test_confusion_matrix_diagonal_is_dominant(self, sibling_repo_available):
        predictions = da.load_test_predictions()
        matrix = da.build_confusion_matrix(predictions, "pred_hgb")
        for pm in da.CLASSIFIER_PMS:
            assert matrix.loc[pm, pm] > 50
