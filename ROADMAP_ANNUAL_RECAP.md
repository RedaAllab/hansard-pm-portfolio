# ROADMAP_ANNUAL_RECAP.md: Execution plan: "5 minutes to understand 7 years of British politics"

English translation of the original French roadmap, kept alongside `STYLE_DUEL.md`, `THEMATIC_HEATMAP.md` and `ROADMAP_PM_HANDOVER.md` as this repo's fourth project reference. This project is the most composite of the four (it aggregates all 4 layers of the source repo into one image); a dedicated design document recommendation is made in Phase 3, produced before the rendering code, see `ANNUAL_RECAP.md`. See `ARCHITECTURE.md` for where the actual build deviates from this plan and why.

---

## 0. Overall status

| | |
|---|---|
| **Project** | 5 minutes to understand 7 years of British politics (no. 13 from the initial brainstorm) |
| **Portfolio numbering** | `04_annual_recap` (follows `01_style_duel`, `02_topic_heatmap`, `03_pm_handover`) |
| **Repo** | `hansard-pm-nlp` in the original plan; built in `hansard-pm-portfolio` instead, consistent with projects 01-03 (see `ARCHITECTURE.md`) |
| **External dependency** | No data to recompute, but technically depends on Phases 3, 4 and 5 already being complete (all done) |
| **Status** | Done |
| **Estimated effort** | 9 to 14 hours (~1.5 to 2 days), the longest of the four projects, since it is a composition, not one chart type |

## 1. Objective and message

**Objective**: condense the whole corpus (2019-2026) into one "front page" image, readable in 5 minutes by a busy audience, aggregating by year the indicators already computed across the repo's 4 layers (volume, style, sentiment, themes).

**Key message**: *"7 years, 4 Prime Ministers, over 10,000 parliamentary contributions: here is what UK Parliament's data says, summarized in a single image."*

**Positioning relative to the other 3 projects**: this project is explicitly the portfolio's **executive summary**: it does not replace the detail of projects 01, 02 and 03, it points back to them. The README must say so clearly ("for the monthly detail of themes, see project 02; for the style detail, see project 01") rather than implying this one visual tells the whole story on its own.

## 2. What already exists (no model recomputation to plan)

| Element needed | Already available in | Action required |
|---|---|---|
| Volume (contributions, words) by PM | `data_README.md` | Re-aggregate by calendar year rather than by tenure (a simple re-slicing, not a recomputation) |
| Readability, MTLD | Phase 3, `eda_report.md` | Yearly average |
| Sentiment, net certainty | Phase 4, `affect_report.md` | Yearly average |
| Topic weights, labels, T0+T1 merge | Phase 5, `phase5_lda_report.md` + `dashboard_helpers.py` logic | Yearly average, dominant topic = argmax |
| PM tenure dates | `data_README.md` | Needed for the frieze at the top of the image |

**Technical risk to check first, specific to this project**: the 4 layers above were produced by 4 different scripts (`eda.py`, `affect.py`, `build_lda_topics.py`, `build_corpus.py`). Nothing in the documentation guarantees they use exactly the same join key (PM + sitting date) in the same format: the one genuinely new technical check in the whole portfolio, to do first.

**New but minor decisions to make (not model recomputations)**:

- **Partial years**: the corpus starts 2019-07-24 (Johnson's arrival), so 2019 is half a year of data. To be treated visually as such (e.g. a visually narrower or "6 months"-annotated 2019 card), not as an anomaly to fix.
- **Transition years** (2022: Johnson→Truss→Sunak; 2024: Sunak→Starmer): a single PM per year cannot be shown honestly. **Decision taken**: a color band segmented proportionally to each PM's tenure days within the year, rather than one PM name per year-card.
- **KPI set per year-card**: lock to **4 fixed indicators** before coding (PM(s) in office, word volume, dominant theme, tone indicator). Do not add a 5th "for completeness" mid-development: the overload trap already identified in this portfolio's other documents.

## 3. Phases

### Phase 0: Preliminary checks

- [x] Verify that the 4 layer artifacts (Phases 3, 4, 5 + tenure table) share a usable join key (PM + sitting date)
- [x] List the years actually covered by the corpus (2019 partial to probably 2026 partial too, depending on the extraction date)
- [x] Count the documents available per year to spot any year too thinly covered to be reliable (e.g. if extraction stops mid-2026)

### Phase 1: Multi-layer annual aggregation

- [x] Join the 4 layers on the common key validated in Phase 0
- [x] Aggregate by calendar year: mean for readability/MTLD/sentiment/certainty, sum for word volume, argmax for the dominant theme (highest mean-weight topic for the year, reusing the T0+T1 merge already applied elsewhere)
- [x] Compute, for transition years, the proportional split of tenure days per PM

### Phase 2: Locking the KPI set

- [x] Validate the 4 chosen indicators (section 2) and their planned representation (segmented band / bar / colored dot / chip)
- [x] Write this list into the README at this stage to avoid scope drift in Phase 4

### Phase 3: Composition design (recommended before coding)

- [x] *Optional but recommended*: produce an `ANNUAL_RECAP.md` on the model of `STYLE_DUEL.md` / `THEMATIC_HEATMAP.md` before Phase 4, since this project assembles several visual elements into one composition (frieze + grid of year-cards): a real layout choice to fix in advance, not to improvise while coding
- [x] If this document is not produced, at minimum fix in writing: the number of grid columns (one per year), the height of the PM frieze at the top, and each year-card's size, before writing the rendering function

### Phase 4: Rendering functions

- [x] Write `plot_annual_recap()` in `src/hansard_pm_nlp/portfolio_viz.py`, composed via Matplotlib `GridSpec` (a horizontal frieze at the top plus a row of year-cards below), rather than several figures assembled after the fact in an external tool
- [x] Explicitly handle transition year-cards (segmented band, see section 2)
- [x] Explicitly handle the 2019 card (half year)

### Phase 5: Producing the visual

- [x] Export `annual_recap_main.png`, wide format (recommended 2400x1000px, 200dpi, consistent with project 02's "frieze" format)
- [x] Cut a per-year/segment version for an eventual 6-slide LinkedIn carousel (see section 9)
- [x] Verify each year-card's readability once shrunk to mobile width - originally a one-off eyeball check (UX/dataviz audit D.6 flagged this as not reproducible); now backed by `tests/test_dataviz_layout.py::TestMobileReadability`, which computes effective glyph height at a simulated 400px width for every font size used and fails if any drops below ~2.5px, so this stays verified on every test run rather than only once

### Phase 6: Narrative notebook

- [x] Create `notebooks/portfolio_04_annual_recap.ipynb`, logic imported from the package only

### Phase 7: Documentation

- [x] Write `portfolio/04_annual_recap/README.md`
- [x] Add explicit cross-references to projects 01 and 02 for the detail (see section 1, "positioning")
- [x] Mandatory "Limitations" section (see section 6 below)
- [x] Add the link from the root README, and **update projects 01/02/03's READMEs so they also point back to this synthesis**, so the portfolio reads as one whole rather than 4 isolated pieces

### Phase 8: GitHub publication

- [ ] Not attempted in this build session

### Phase 9: LinkedIn publication

- [ ] Build the 6-slide carousel already sketched in the initial brainstorm ("carousel 1/6"): (1) full image as a teaser, (2)-(5) zooms per major period (Brexit, Covid, mini-budget/Truss, Ukraine/Starmer), (6) call to explore the full repo/dashboard
- [ ] Publish last of the 4 projects, closing the editorial sequence ("after style, themes and transitions, here is everything above summarized in one image"); not attempted in this build

## 4. Final expected tree

```
notebooks/
  04_annual_recap.ipynb
src/hansard_pm_portfolio/
  viz/annual_recap.py   (functions added to projects 01, 02 and 03's)
portfolio/04_annual_recap/
  README.md
  assets/
    banner.png
    annual_recap_main.png
ANNUAL_RECAP.md   (produced, see section 3)
```

## 5. Python dependencies

`pandas`, `duckdb`, `matplotlib` (with `GridSpec` for the composition), no new dependency.

## 6. Limitations to state explicitly in the deliverable

- The "dominant theme" per year is a simplification: a year can have 2-3 themes close in weight, and the argmax hides that nuance, to be said explicitly, with a pointer to project 02's heatmap for the detail.
- Transition years compress 2-3 tenures into a single card; the segmented band limits but does not eliminate this simplification.
- 2019 is half a year of data (the corpus starts in July), "per year" comparisons must flag this specific card.
- Found during the build, not anticipated in this plan: 2026 is also a partial year, because the corpus extraction cuts off in July, not because the year ended.
- This synthesis smooths, by construction, the monthly dynamics already visible in project 02: it is complementary, not more precise.

## 7. Definition of Done

- [x] The 4-layer join is verified and documented (Phase 0)
- [x] The main visual is exported and readable
- [x] The notebook runs end to end, outputs committed
- [x] The README states the limitations from section 6 and points to projects 01 and 02
- [x] The other 3 projects' READMEs are updated to point back to this synthesis
- [x] Link added to the root README
- [ ] LinkedIn carousel (not attempted, non-blocking)
