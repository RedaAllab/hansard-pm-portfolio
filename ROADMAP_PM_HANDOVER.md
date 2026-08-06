# ROADMAP_PM_HANDOVER.md: Execution plan: "The handover: how the tone changes with every new Prime Minister"

> Execution plan only (order, dependencies, effort). No dedicated design document exists yet for this project; visual choices not already settled elsewhere are flagged explicitly below rather than left open, following the same method already applied to the first two projects.

English translation of the original French roadmap, kept alongside `STYLE_DUEL.md` and `THEMATIC_HEATMAP.md` as this repo's third project reference. See `ARCHITECTURE.md` for where the actual build deviates from this plan and why.

---

## 0. Overall status

| | |
|---|---|
| **Project** | The handover (no. 12 from the initial brainstorm) |
| **Portfolio numbering** | `03_pm_handover` (follows `01_style_duel`, `02_topic_heatmap`) |
| **Repo** | `hansard-pm-nlp` in the original plan; built in `hansard-pm-portfolio` instead, consistent with projects 01-02 (see `ARCHITECTURE.md`) |
| **External dependency** | None (data already computed, Phases 3 and 4) |
| **Status** | Done |
| **Estimated effort** | 6 to 8 hours (~1 day) |

## 1. Objective and message

**Objective**: visually isolate the effect of a change of Prime Minister, independent of the general political context, by comparing style and sentiment metrics right before / right after each of the 3 transitions in the period (Johnson→Truss, Truss→Sunak, Sunak→Starmer).

**Key message**: *"Some changes of Prime Minister transform the tone of Parliament overnight, others change almost nothing in the short term."*

**Link to the original project**: this visual extends the exploratory question **H4** (already asked but not statistically tested in the repo: "do themes drift continuously, or snap at PM transitions?") to style and sentiment rather than topics. **Line not to cross**: this project stays descriptive/visual: it must not be presented as a formal statistical break test, which the repo has not done.

## 2. What already exists (no model recomputation to plan)

| Element needed | Already available in | Action required |
|---|---|---|
| MTLD, readability (Flesch-Kincaid) | `data/processed/` (Phase 3, `eda_report.md`) | Load as is |
| Net certainty, `hedge_rate` | `data/processed/` (Phase 4, `affect_report.md`) | Load as is |
| Exact dates of the 3 transitions | `data_README.md` | Copy as is |
| Palette, typography, shared style | `src/hansard_pm_nlp/portfolio_style.py` (created in project 01) | Reuse without modification |

**New but minor decision to make (not a model recomputation)**: the width of the before/after window around each transition is not defined anywhere in the repo, a plain descriptive-aggregation choice. **Decision taken**: +/- 6 weeks of sittings either side of each transition date, on aggregated documents (PM x sitting-date level, as for the other projects).

> **Constraint to accept, not to work around**: for the 2 transitions involving Liz Truss (Johnson→Truss and Truss→Sunak), the 6-week window cannot be filled symmetrically on the Truss side: her entire tenure is only 49 days. The window will therefore be **deliberately asymmetric** for these two transitions, and this must be stated explicitly in the README, not hidden behind a smoothing trick.
>
> **Overlap with an already-documented crisis window**: the Truss→Sunak transition (25/10/2022) falls right after the mini-budget (12/10/2022), already flagged elsewhere in the repo as a crisis window reduced to a single sitting and statistically uninterpretable on its own. For this specific transition, the chart must signal that "PM effect" and "crisis effect" are not separable in the data, not claim to isolate one from the other.

## 3. Phases

### Phase 0: Preliminary checks

- [x] Confirm the 3 exact transition dates in `data_README.md` / `pm_tenures.parquet`
- [x] Count the documents available on the Truss side of each of the 2 windows concerned, to size the asymmetry actually shown
- [x] Choose the 2 "star" metrics to display per panel

### Phase 1: Data preparation

- [x] Load the already-computed Phase 3/4 (and Phase 7) layers, without re-running `eda.py`, `affect.py`, or `event_study.py`
- [x] For each of the 3 transitions, extract the +/- 6 week sitting window
- [x] Label each document "before" / "after" relative to the transition date
- [x] Compute the 2 chosen metrics over each window

### Phase 2: Rendering functions

- [x] Write `plot_transition_panel()`, one panel per transition, timeline with a vertical marker at the transition date, "before" color (`#7C89A6`, neutral grey-blue) vs. "after" color (`#22D3EE`, brand accent), deliberately **not** the chart's positive/negative pair, reserved for value judgments this project does not make
- [x] Write `plot_transition_timeline()` (secondary visual: single continuous view with the 3 markers, for the reader who wants full context rather than 3 separate zooms)

### Phase 3: Producing the visuals

- [x] Export `transition_main.png`, small multiples, 3 panels side by side (one per transition), 1600x900 px, 200 dpi
- [x] Export `transition_timeline_secondary.png`, continuous view, 2000x800 px
- [x] Verify that the Truss windows' asymmetry stays visually honest (axis not artificially stretched to mask the low data volume)

### Phase 4: Narrative notebook

- [x] Create `notebooks/03_pm_handover.ipynb`, logic imported from the package only

### Phase 5: Documentation

- [x] Write `portfolio/03_pm_handover/README.md` (same structure as the previous two projects: hook, hero image, message in 3 sentences, method in plain language, findings, **limitations** (mandatory here given the 2 warnings in section 2), reproduction, links)
- [x] Explicitly mention the link with H4 and the fact that no formal statistical test is performed here
- [x] Add the link from the root README

### Phase 6: GitHub publication

- [ ] Verify the README renders correctly (GitHub light/dark mode)

### Phase 7: LinkedIn publication

- [ ] Not attempted in this build (publication is non-blocking for project completion)

## 4. Final expected tree

```
notebooks/
  03_pm_handover.ipynb
src/hansard_pm_portfolio/
  viz/pm_handover.py   (functions added to projects 01 and 02's)
portfolio/03_pm_handover/
  README.md
  assets/
    banner.png
    transition_main.png
    transition_timeline_secondary.png
```

## 5. Python dependencies

`pandas`, `duckdb`, `matplotlib`; no new dependency compared to projects 01 and 02.

## 6. Limitations to state explicitly in the deliverable

- Asymmetric before/after windows for the 2 transitions involving Truss (a real feature of her tenure's length, not a computation artifact).
- The Truss→Sunak transition is confounded with the already-documented mini-budget crisis window: "PM effect" and "crisis effect" are not separable there.
- Descriptive project: no formal causal isolation (unlike the Phase 7 event study, which itself found a null effect for H2/H3), the patterns observed here should not be presented as statistically significant.
- Found during the build, not anticipated in this plan: the Johnson→Truss and Sunak→Starmer transitions also have an empty "before" window in practice, for reasons unrelated to Truss's short tenure (summer recess, and Parliament's dissolution ahead of the 2024 general election). See `ARCHITECTURE.md` and the project README.

## 7. Definition of Done

- [x] The 2 visuals are exported and readable
- [x] The notebook runs end to end, outputs committed
- [x] The README states the limitations from section 6, plus the recess/dissolution finding above
- [x] Link added to the root README
- [ ] LinkedIn post (not attempted, non-blocking)
