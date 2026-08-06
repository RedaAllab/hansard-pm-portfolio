# ANNUAL_RECAP.md: Layout decisions for project 04

`ROADMAP_ANNUAL_RECAP.md` Phase 3 recommends a short design document before writing any rendering code, since this project (unlike 01-03) assembles several elements into one composition rather than one chart type. This is that document, kept intentionally short: no new palette, typography, or sizing is introduced (everything comes from `style.py`, unchanged), only the composition itself is decided here, in writing, before `plot_annual_recap()` is written.

## 1. What Phase 0 found, ahead of any layout decision

The roadmap's own "risque technique" (Phase 0) asks to verify that the layers computed by separate scripts share a usable join key before assuming they do. Checked directly: `event_study_dataset.parquet` (Phase 7, word volume and net certainty) and `lda_topics.parquet` (Phase 5, topic weights) join on `(pm_name, sitting_date)` with **296/296 rows matching on both sides, zero orphans**. Both were already used unchanged in projects 02 and 03. This project is built on those two files alone, not on `eda_report.md` / `affect_report.md`'s whole-PM aggregates (see section 3 for why), which sidesteps the join-key risk entirely rather than resolving it after the fact.

Also found, not anticipated in the roadmap's own text (which only flags 2019 as a partial year): **2026 is a partial year too**, 26 sittings from January to mid-July, because the corpus extraction cuts off there, not because the year ended. Both edge years are handled the same way (section 4).

## 2. The 4 fixed indicators (Phase 2)

1. **PM(s) in office**: a segmented color band, proportional to each PM's tenure days within the calendar year, from `pm_tenures.parquet`.
2. **Word volume**: sum of `word_count` (`event_study_dataset.parquet`) for the year.
3. **Dominant theme**: argmax of the year's mean topic weight, T0+T1 merged and labeled exactly as `data_access.merge_overlapping_topics()` / `TOPIC_LABELS` already do for project 02, not a new labeling pass.
4. **Tone indicator**: mean `net_certainty` for the year.

No 5th indicator is added. Locked here before `plot_annual_recap()` is written, per the roadmap's own explicit warning against scope creep during Phase 4.

## 3. Why `net_certainty`, not MTLD or Flesch-Kincaid, for "tone"

Same reasoning as project 03 (`ARCHITECTURE.md` section 15), not re-litigated here: MTLD needs long, continuous text to be stable and this project's unit (a calendar year) would make that worse, not better, if the goal were still to avoid whole-corpus-only figures; but the deeper reason is that `net_certainty` is already this portfolio's recurring style signature (project 01's radar, project 03's handover), available at full per-sitting-date granularity for all 4 PMs with zero new computation. Reusing the same metric a third time gives the 4-project portfolio one throughline instead of a different "tone" metric per project.

## 4. Composition (GridSpec, one figure)

- **Canvas**: 2400x1000px at 200dpi (12x5in), matching the roadmap's own recommendation and project 02's "frieze" format.
- **Header band** (top ~18% of the figure height): one continuous horizontal strip, 2019 to 2026, segmented by PM tenure exactly like `viz.topic_heatmap._draw_pm_transitions()` already draws transition dividers, so the header reads as a zoomed-out version of the same encoding used in the year-cards below it, not a new visual language.
- **8 year-cards in a single row below the header**, one column per calendar year 2019-2026 (not one column per PM, and not skipping partial years): each card stacks, top to bottom, its own mini PM-tenure segment, the dominant theme label, a word-volume bar, and a small marker on a shared net-certainty scale.
- **2019 and 2026 render at proportionally narrower card width** (6/12 and ~7/12 of a full column, from actual month coverage, not a fixed fraction), each captioned "partial year" in the card itself, not only in a footnote, so the visual difference doesn't need the caption to be noticed.
- **Colors**: PM segments reuse `style.PM_COLORS` unchanged (no 3rd color system introduced for this project); the tone marker and word-volume bar reuse `style.SECONDARY` / `style.ACCENT`, the same before/after-agnostic neutral pair project 03 already established for non-PM-colored data.

## 5. What this project deliberately does not attempt in this build

- The 6-slide LinkedIn carousel (`ROADMAP_ANNUAL_RECAP.md` Phase 9) is not built here, consistent with project 03 leaving its own LinkedIn phase unattempted (`ARCHITECTURE.md`, project 03's Definition of Done).
- No 2nd figure or export variant beyond `annual_recap_main.png`.
