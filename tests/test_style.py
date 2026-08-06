"""STYLE_DUEL.md section 7 states specific WCAG contrast ratios for the
palette ("~18:1" for primary text, "> 4.5:1" for secondary) - these tests
hold the actual constants to those claims instead of trusting them by eye.
"""

from hansard_pm_portfolio import style


def test_text_primary_meets_wcag_aaa_on_background():
    assert style.contrast_ratio(style.TEXT_PRIMARY, style.BACKGROUND) >= 7.0


def test_text_secondary_meets_wcag_aa_on_background():
    assert style.contrast_ratio(style.TEXT_SECONDARY, style.BACKGROUND) >= 4.5


def test_text_secondary_on_surface_actually_passes_wcag_aa():
    # STYLE_DUEL.md section 12 claims #9CA3AF on #262730 is "contraste
    # insuffisant" and should be reserved for #0E1117 only. The measured
    # ratio is 5.84:1 - above the 4.5:1 AA threshold the spec itself uses
    # everywhere else (this repo's plots never actually put secondary text
    # on the surface color, so the discrepancy has no visual consequence -
    # it's a documentation inaccuracy in STYLE_DUEL.md, not a broken
    # constant; noted here rather than silently "fixed" by asserting the
    # spec's claim instead of the real math).
    assert style.contrast_ratio(style.TEXT_SECONDARY, style.SURFACE) >= 4.5


def test_contrast_ratio_of_black_and_white_is_max():
    assert style.contrast_ratio("#000000", "#FFFFFF") == 21.0


def test_contrast_ratio_is_symmetric():
    a, b = style.contrast_ratio(style.TEXT_PRIMARY, style.BACKGROUND), style.contrast_ratio(
        style.BACKGROUND, style.TEXT_PRIMARY
    )
    assert a == b


def test_every_pm_has_a_color_and_linestyle():
    from hansard_pm_portfolio.data_access import IN_SCOPE_PMS

    for pm in IN_SCOPE_PMS:
        assert pm in style.PM_COLORS
        assert pm in style.PM_LINESTYLES


def test_truss_is_the_only_dashed_line():
    # STYLE_DUEL.md section 3/7: line style must double the color coding for
    # Truss specifically - never color-only.
    dashed = [pm for pm, ls in style.PM_LINESTYLES.items() if ls == "--"]
    assert dashed == ["Liz Truss"]
