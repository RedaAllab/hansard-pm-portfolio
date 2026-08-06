# Architecture decisions

This document justifies the structural decisions in this repo that deviate from, or make more specific, `STYLE_DUEL.md`. It is deliberately short: a decision log, not a second specification.

## 1. A separate repo, not a subfolder of `hansard-pm-nlp`

`STYLE_DUEL.md` implicitly assumes (`src/hansard_pm_nlp/portfolio_style.py`, `portfolio/01_style_duel/`) that this project lives **inside** `hansard-pm-nlp`. On explicit request, it lives here instead, in a separate repo (`hansard-pm-portfolio`), which will also host project 02 (`THEMATIC_HEATMAP.md`) later. Hence `portfolio/01_style_duel/` and `portfolio/02_topic_heatmap/` are subfolders of *this* repo, not of `hansard-pm-nlp`.

Direct consequence: this repo cannot import `hansard_pm_nlp` as a Python module from the same code tree, it reads its artifacts as external data instead. See section 3.

## 2. `hansard_pm_portfolio`, not `hansard_pm_nlp`

`STYLE_DUEL.md` names the files `src/hansard_pm_nlp/portfolio_style.py` and `portfolio_viz.py`, consistent with a subfolder of `hansard-pm-nlp`, but a separate repo with a package of the same name (`hansard_pm_nlp`) would collide in any environment where both are installed (two different distributions claiming the same import name). The package is therefore called `hansard_pm_portfolio`. The spec's `portfolio_` file name prefix becomes redundant once the whole package *is* the portfolio: `portfolio_style.py` becomes `style.py`, `portfolio_viz.py` becomes `viz/style_duel.py` (see section 6). Same renaming for the notebook: `notebooks/portfolio_01_style_duel.ipynb` becomes `notebooks/01_style_duel.ipynb`.

## 3. Lightweight dependency, read-only access to already-exported artifacts

`hansard-pm-nlp` already solved this problem for its own dashboard: `requirements-app.txt` installs neither torch, transformers, spacy, nor bertopic, only what is needed to read files that are already computed (`pandas`, `pyarrow`, `plotly`, `gensim`). This repo follows the exact same principle:

- **No dependency on the `hansard_pm_nlp` package**: installing it would pull in all of `hansard-pm-nlp`'s `pyproject.toml` (torch, transformers, spacy, bertopic, gensim), unnecessary here since all the heavy computation has already happened.
- **Two functions ported, not imported**: `normalize_radar()` (10 lines of pure pandas) and `lexical.py`'s regex tokenizer (3 lines) are copied into `data_access.py` with an attribution note, rather than depending on the full package for about 15 lines.
- **Data location**: `data_access.hansard_pm_nlp_dir()` resolves a sibling repo (`../hansard-pm-nlp`, as on this machine) or the `HANSARD_PM_NLP_DIR` environment variable.

## 4. DuckDB to read Parquet files, not `pandas.read_parquet`

`hansard-pm-nlp`'s Parquet files (written with `parquet-cpp-arrow` 24.x) trigger `OSError: Repetition level histogram size mismatch` with `pandas.read_parquet` under pyarrow 19, a known cross-version incompatibility in how column-chunk statistics are encoded. DuckDB reads the same files without issue and returns a pandas `DataFrame` via `.df()`. `data_access.read_parquet()` centralizes this workaround rather than forcing a pyarrow upgrade, whose side effects on the rest of the environment are less predictable.

## 5. The radar: 5 traits carried over unchanged, 1 recomputed, 1 substituted

`STYLE_DUEL.md` section 6 proposes 6 axes: MTLD, Flesch-Kincaid, `hedge_rate`, `net_certainty`, `pos_INTJ`, frequency of "not". In practice:

- **MTLD, Flesch-Kincaid, `hedge_rate`, `net_certainty`, `mean_words_per_sentence`** come unchanged from `eda_summary.csv` / `affect_summary.csv` (Phases 3-4), available for all 4 PMs with no recomputation, the same columns the live dashboard's "Stylometric profile by PM" tab uses.
- **Frequency of "not"** is recomputed here (whole corpus per PM, same tokenizer as `lexical.py`) because Phase 6 only exported it for 3 PMs (see section 7): a trivial computation, no heavy dependency, so it was kept.
- **`pos_INTJ` replaced with `mean_words_per_sentence`**: `pos_INTJ` needs spaCy (POS tagging), and Phase 6 only computed it for the classifier's 3 PMs. Liz Truss is excluded *before* the stylometric traits are even computed, not only before training. Adding spaCy to this repo for one missing value would contradict section 3. `mean_words_per_sentence` replaces it: available for all 4 PMs, and the 5th most discriminant trait of the more accurate model (HistGradientBoosting), so the substitution keeps a "classifier-validated" anchor rather than silently losing it.

Also documented in the project's README (the "How this visual was built" and "Limitations" sections), not only here.

## 6. One viz file per project, plus a shared `viz/common.py`

`STYLE_DUEL.md` section 11 suggests a single `portfolio_viz.py` for `plot_style_radar()` and `plot_feature_importance_bar()`. Since this repo hosts both projects in the same tree, plotting functions are split by project (`viz/style_duel.py`, `viz/topic_heatmap.py`) rather than accumulating both in one growing file. `style.py` (colors, fonts) stays single and shared: this is the point `STYLE_DUEL.md` section 7 and `THEMATIC_HEATMAP.md` section 0 both explicitly require ("PM categorical palette shared between the two projects"). Once project 02 was written, `plot_banner()` and the dark-axes utilities turned out to be identical across projects, moved into `viz/common.py` rather than duplicated a second time.

## 7. Prime Minister scope

- `data_access.IN_SCOPE_PMS` (radar, 4 PMs) explicitly excludes Andy Burnham (PM since 2026-07-20, see `PHASE0_SCOPING.md` in the `hansard-pm-extraction` repo): absent from the corpus at the current extraction date, and out of scope for this project for now, by explicit decision rather than accidental filtering.
- `data_access.CLASSIFIER_PMS` (confusion matrix, permutation importance, 3 PMs) excludes Liz Truss, as Phase 6 itself does (`split.py`): not a decision made by this repo, a like-for-like carryover from `hansard-pm-nlp`.

## 8. Fonts: static instances, not Google Fonts' variable files

Lora and Inter are only distributed by Google Fonts as variable fonts (`Lora[wght].ttf`, `Inter[opsz,wght].ttf`), a single file covering the whole weight range. Matplotlib does not reliably resolve a precise weight (700, 600...) from within a variable file. `assets/fonts/` therefore contains static instances, generated once with `fontTools.varLib.instancer` (`wght=700` for Lora, `600` and `400` for Inter) with their name table cleaned up (name IDs 16/17 removed) so each weight resolves a distinct, unambiguous family name (`Lora`, `Inter SemiBold`, `Inter`). IBM Plex Mono is natively distributed as static per-weight files, no instancing needed.

## 9. An inaccuracy found in `STYLE_DUEL.md`

Section 12 claims that `#9CA3AF` on `#262730` is insufficient contrast and should be reserved for the `#0E1117` background. Measured (`tests/test_style.py`), that contrast is actually 5.84:1, above the WCAG AA threshold (4.5:1) the spec applies everywhere else. No visual consequence here (no secondary text sits on `#262730` in this project), but noted rather than silently carried forward.

## 10. Project 02: the 13 topic labels are new editorial work

`THEMATIC_HEATMAP.md` section 6 asks for "short, plain language labels... carried over unchanged from the interpretation already written in `phase5_lda_report.md`, do not reinvent the labels." Verified directly in that report and in `app.py` (the live dashboard's Topics tab): neither contains a plain language label, only raw keyword lists (`phase5_lda_report.md`) or algorithmic labels like `"T2: hs, project, rail"` (`app.py`, the first 3 keywords concatenated). `data_access.TOPIC_LABELS` (13 entries, one per post-merge topic) was therefore written for this project from those same keyword lists, an editorial choice documented as such in the code and the project's README, not presented as a neutral reuse of existing text.

## 11. Project 02: the Covid zoom's rationale genuinely exists, in `app.py`, not in a report

Unlike the previous point, the live dashboard's Topics tab caption (`app.py`) already explicitly states that the 3 Covid topics "track distinct sub-phases (restrictions/testing, vaccines/schools, NHS pay/inquiry) rather than one duplicated topic", exactly the point `THEMATIC_HEATMAP.md` section 6 asks to illustrate to justify not merging them. That sentence is carried over (translated, not invented) into `data_access.COVID_TOPIC_LABELS` and the project's README, with attribution to `app.py` rather than presented as a new observation from this project.

## 12. Project 02: tenure dates read from `hansard-pm-nlp`, not from a third cloned repo

`THEMATIC_HEATMAP.md` section 0 asks for PM transition dates to be loaded from `PHASE0_SCOPING.md` (the `hansard-pm-extraction` repo). Rather than cloning a third repo for 4 dates, `data_access.load_pm_tenures()` reads them from `data/input/pm_tenures.parquet`, already present in the `hansard-pm-nlp` checkout this repo reads everything else from, verified by hand that the two sources match exactly (same 4 PMs, same start and end dates).

## 13. Project 02: Cividis scaled 0 to max, not to a percentile

An LDA topic weight has no naturally interpretable upper bound. `plot_topic_heatmap()` sets `vmax` to the maximum observed in the monthly matrix rather than to 1.0 (the model's raw scale, where no cell ever approaches 1 since the monthly mean smooths out peaks) or to an arbitrary percentile, so that "high" on the colorbar always corresponds to the actually most visible peak on the map, whichever PM window is shown.

## 14. Project 03: built in this repo, from a roadmap, not a design spec

`ROADMAP_PM_HANDOVER.md` (project 03) is an execution plan, not a design document like `STYLE_DUEL.md` or `THEMATIC_HEATMAP.md`: it says so in its own header. Two consequences, both consistent with decisions already made for projects 01-02, not new ones:

- It targets `hansard-pm-nlp` as the repo (section 0), same as `THEMATIC_HEATMAP.md` originally did. Built in `hansard-pm-portfolio` instead, for the same reason as section 1: this repo already exists as the separate, lightweight home for every portfolio project.
- No palette/typography/sizing is specified beyond the one color pair the roadmap itself pins down (section 2: `#7C89A6` before / `#22D3EE` after). Everything else (fonts, title/subtitle sizing, source note, panel layout) reuses `style.py` and `viz/common.py` unchanged, the same shared system `STYLE_DUEL.md` section 7 and `THEMATIC_HEATMAP.md` section 0 require across projects.

## 15. Project 03: `vader_compound` replaces MTLD as the second "star" metric

`ROADMAP_PM_HANDOVER.md` Phase 0 recommends net certainty + MTLD as the two metrics per panel ("pour rester lisible"). MTLD does not survive contact with the actual unit of analysis here: it is a whole-corpus statistic (McCarthy & Jarvis 2010's segment algorithm needs long, continuous text to be stable, see `mtld_over_time.parquet`'s own 1,500-word floor per monthly bin), and this project's unit is a single sitting, often a few hundred words. Computing it at that granularity would also be new per-document computation this repo otherwise avoids (section 3).

`vader_compound` is used instead: already present per sitting date for all 4 in-scope PMs (Truss included) in `event_study_dataset.parquet` (Phase 7's own event-study table), so the substitution costs zero new computation. It also better matches the roadmap's own stated objective ("comparing style and sentiment metrics", section 1) than the original pairing would have: net certainty + MTLD are both style metrics with no sentiment axis at all, while net certainty + `vader_compound` covers both. Documented in the project's README (`portfolio/03_pm_handover/README.md`, "How this visual was built") as well.

## 16. Project 03: `event_study_dataset.parquet` as the single data source, not Phase 3/4's own exports

`ROADMAP_PM_HANDOVER.md` section 2 points at Phase 3's `eda_report.md` (MTLD, readability) and Phase 4's `affect_report.md` (net certainty, hedge rate) as the source tables. Neither is used directly: both only export **whole-PM** aggregates (one row per PM), not the per-sitting-date granularity this project's before/after windows need. `pm_style_features.parquet` (which does have sitting-date rows) is Phase 6's classifier export and excludes Liz Truss entirely, upstream, the same restriction `CLASSIFIER_PMS` already documents in section 7. `event_study_dataset.parquet` (Phase 7) is used instead: it is the one hansard-pm-nlp artifact that is both per-(PM, sitting date) and includes all 4 in-scope PMs, because Phase 7 itself needed Truss's 5 sittings for the mini-budget crisis window. Reusing it here needs no new computation and stays consistent with never recomputing what Phase 6 or 7 already restricted or computed for a reason.

## 17. Project 03: a fixed +/- 6 week window surfaces a real, unanticipated gap

`ROADMAP_PM_HANDOVER.md` section 2 anticipates one asymmetry: Liz Truss's 49-day tenure is too short to fill a 6-week window on either side of her two transitions. Counting the actual sittings (`data_access.build_transition_windows()`, verified by hand before writing any plotting code) surfaces a second, unanticipated one: the Johnson→Truss and Sunak→Starmer transitions both have **zero** sittings in the strict 6-week window before the handover, not from a short tenure, but because Parliament was not sitting (summer recess before Johnson's resignation; the Parliament dissolved ahead of the 2024 general election before Starmer took office). Per the roadmap's own instruction not to stretch the axis to hide a thin sample (section 3), the window is not widened to compensate: `plot_transition_panels()` shows the true gap and annotates it in words ("No sittings (recess / election)") rather than showing a blank axis with no explanation. Documented in the project's README and in `ROADMAP_PM_HANDOVER.md`'s own limitations section (added there as a finding, not left silently outside the plan).

## 18. Project 04: a design document written before the rendering code, per the roadmap's own recommendation

`ROADMAP_ANNUAL_RECAP.md`'s header flags this project as the most composite of the four (it assembles a header frieze and 8 year-cards in one `GridSpec` composition, not one chart type) and recommends producing a short design document before Phase 4, on the same model as `STYLE_DUEL.md` / `THEMATIC_HEATMAP.md`, "if you want to keep the same zero-improvised-design-decision method as the previous projects." That recommendation was followed: [`ANNUAL_RECAP.md`](ANNUAL_RECAP.md) fixes the 4 indicators, the join-key check, the tone-metric substitution, and the composition's exact layout before `viz/annual_recap.py` was written, not after.

## 19. Project 04: built on `event_study_dataset.parquet` + `lda_topics.parquet` alone, not the roadmap's suggested 4 layers

`ROADMAP_ANNUAL_RECAP.md` section 2 points at `eda_report.md` (Phase 3) and `affect_report.md` (Phase 4) as sources for readability/MTLD and sentiment/certainty, alongside Phase 5's topic weights and the tenure table, 4 separate artifacts whose join-key compatibility the roadmap itself flags as unverified. In practice only 2 files are used: `event_study_dataset.parquet` (Phase 7: word volume and net certainty, all 4 in-scope PMs, per sitting date) and `lda_topics.parquet` (Phase 5: topic weights, same key). Verified by hand (`ANNUAL_RECAP.md` section 1) that the two join on `(pm_name, sitting_date)` with 296/296 rows matching on both sides, zero orphans. This sidesteps the roadmap's join-key risk rather than resolving it after the fact for 4 files, and follows project 03's same substitution of `net_certainty` for MTLD (section 15), reused here a third time as this portfolio's recurring "tone" signature (`ANNUAL_RECAP.md` section 3).

## 20. Project 04: 2026 is a second partial year, not anticipated in the roadmap

`ROADMAP_ANNUAL_RECAP.md` section 2 anticipates one partial year: 2019, since the corpus starts in July with Johnson's tenure. Checking the corpus's actual date bounds (Phase 0, before writing `build_annual_recap()`) surfaces a second one the roadmap's own text does not mention: 2026 is also partial, because the corpus extraction's last sitting is 2026-07-15, well short of the calendar year's end, and short of Starmer's own tenure end date (2026-07-20) recorded in `pm_tenures.parquet`. Both years are treated the same way: `yearly_coverage_fraction()` computes each one from the corpus's actual sitting-date bounds rather than hardcoding "2019 only," and `plot_annual_recap()` renders both as a visibly narrower, "partial year"-captioned card, consistent with project 03's own principle (section 17) of surfacing a gap the roadmap didn't anticipate rather than smoothing over it.
