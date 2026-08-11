"""I.7: all 4 portfolio/*/README.md follow the same "insight vs caveat"
sequencing rule (audit section F) - "## What it reveals" states the
observation alone; the statistical caveat that qualifies it belongs under
"## Limitations", cross-referenced rather than repeated.

Parses each README's own "## What it reveals" section and asserts none of
the audit's named caveat markers appear there.
"""

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
PORTFOLIO_DIR = REPO_ROOT / "portfolio"

README_PATHS = sorted(PORTFOLIO_DIR.glob("*/README.md"))

# Audit section I.7's own list of statistical-caveat phrasings - these
# should only ever appear under "## Limitations".
CAVEAT_MARKERS = [
    "correction",
    "confounded",
    "not separable",
    "should not be read as",
]


def _extract_section(markdown: str, heading: str) -> str:
    """Text between `## {heading}` and the next `## ` heading (or EOF)."""
    pattern = re.compile(
        rf"^## {re.escape(heading)}\s*$(.*?)(?=^## |\Z)", re.MULTILINE | re.DOTALL
    )
    match = pattern.search(markdown)
    return match.group(1) if match else ""


@pytest.fixture(params=README_PATHS, ids=[p.parent.name for p in README_PATHS])
def readme_path(request):
    return request.param


def test_readmes_were_actually_found():
    # Guards against a silent 0-README collection (e.g. a path typo) making
    # every parametrized test below vacuously "pass" by never running.
    assert len(README_PATHS) == 4, f"expected 4 project READMEs, found {README_PATHS}"


class TestWhatItRevealsHasNoStatisticalCaveats:
    def test_no_caveat_markers_in_what_it_reveals(self, readme_path):
        markdown = readme_path.read_text()
        section = _extract_section(markdown, "What it reveals")
        assert section.strip(), f"{readme_path} has no '## What it reveals' section"
        lowered = section.lower()
        found = [marker for marker in CAVEAT_MARKERS if marker in lowered]
        assert not found, (
            f"{readme_path.parent.name}/README.md 'What it reveals' contains "
            f"statistical-caveat marker(s) {found} - move that qualification "
            "to '## Limitations' and cross-reference it instead (audit F.1-F.3)"
        )

    def test_limitations_section_exists_and_is_non_empty(self, readme_path):
        # F.2: Limitations is where every caveat routes to - it must
        # actually exist and have content for the cross-references in
        # "What it reveals" to point somewhere real.
        markdown = readme_path.read_text()
        section = _extract_section(markdown, "Limitations")
        assert section.strip(), f"{readme_path} has no non-empty '## Limitations' section"


class TestAndyBurnhamBulletStandsAloneInEachReadme:
    # F.5: explicitly NOT centralized - each README is sometimes read in
    # isolation (e.g. shared as a single link on LinkedIn), so the
    # out-of-scope note must be self-contained in every one of the 4, not
    # factored out to a shared doc.
    def test_andy_burnham_out_of_scope_bullet_present_in_every_readme(self, readme_path):
        markdown = readme_path.read_text()
        limitations = _extract_section(markdown, "Limitations")
        assert "Andy Burnham" in limitations, (
            f"{readme_path.parent.name}/README.md's Limitations section is missing "
            "the standalone Andy Burnham out-of-scope bullet (F.5)"
        )
