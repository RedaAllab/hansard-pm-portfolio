# THEMATIC_HEATMAP.md: Design specification for "The thematic heatmap"
> This document is a complete, self-sufficient specification: everything needed to build the visual and the README without having to make a new design decision is defined here. The palette, typography, and accessibility rules are **identical** to `STYLE_DUEL.md` to guarantee a consistent visual identity across the whole portfolio; they are reproduced in full below so this file stays usable on its own.
---
## 0. Consistency with the identity already present in the repo
- **Theme already fixed**: like `STYLE_DUEL.md`, this project reuses the dark theme already activated for the dashboard (`.streamlit/config.toml: theme.base = "dark"`), relying on Streamlit's default dark palette unless a review of `_dark()` in `app/app.py` shows different customization.
- **Existing element to reuse as is, not reinvent**: the T0+T1 topic merge (Ukraine/Russia, near identical) documented in `phase5_lda_report.md` and already applied in the dashboard; this visual must replicate that rule exactly, not debate a new one.
- **Crisis windows and PM transition dates**: already defined in `PHASE0_SCOPING.md` (the `hansard-pm-extraction` repo), to be loaded as is, never redefined by eye on the chart.
- **Naming convention**: `THEMATIC_HEATMAP.md` (all caps, no hyphen) follows the same convention as `README.md`/`WRITEUP.md`/`STYLE_DUEL.md`, no change needed. The associated notebook follows the same logic as Project 1: `notebooks/portfolio_02_topic_heatmap.ipynb`.
---
## 1. Project vision
- **Goal**: show in a single image that a Prime Minister's political attention faithfully tracks the great shocks of their era, without any new model being trained to demonstrate it.
- **Target audience**: same as `STYLE_DUEL.md`, a non-technical recruiter/manager/LinkedIn reader.
- **Key message**: *"7 years of British politics, summarized in a single map, and you can literally watch Brexit, Covid, and Ukraine take turns."*
- **Storytelling**: the visual should work as a historical timeline doubled as a data proof; the reader should be able to mentally "recognize" events they already know (Brexit, Covid, Ukraine) even before reading the legend, creating an immediate, rewarding recognition effect.
- **What the visitor should understand in under 10 seconds**: "each colored band corresponds to a topic, and you can clearly see when each major event dominated debate."
---
## 2. Art direction
- **Style chosen**: identical to `STYLE_DUEL.md`, "sober data journalism", inspired by the Financial Times / Our World in Data.
- **Mood sought**: here the mood must also evoke a **chronological timeline / press infographic** (the "anatomy of a crisis" timeline seen in long-form journalism); this is the one point that distinguishes this project's mood from Project 1's, which is more of a "fact sheet".
- **Level of restraint**: high, but slightly less strict than Project 1, since this visual is explicitly meant to carry a "wow effect", expressed through a larger, more horizontal format (a timeline), not through more colors.
- **Level of interactivity**: none in the portfolio deliverable (static image); a link to the existing dashboard's "Topics" tab covers the need for interactive exploration.
- **Visual inspirations**: the *New York Times* and *Financial Times*' "thematic heatmaps" on news cycles; "Our World in Data" timelines combining time bands and event annotations; the dashboard's existing Topics tab (whose logic this visual reuses, in a static, narrated form).
---
## 3. Color palette
*(identical to `STYLE_DUEL.md`, reproduced here for the document's self-sufficiency)*
| Color | Role | HEX | Why |
|---|---|---|---|
| Background | figure background | `#0E1117` | default value of the already-activated Streamlit dark theme |
| Cards / surfaces | callout boxes | `#262730` | Streamlit's default dark `secondaryBackgroundColor` |
| Primary text | titles, labels | `#FAFAFA` | ~18:1 contrast, above the WCAG AAA threshold |
| Secondary text | captions, notes | `#9CA3AF` | contrast > 4.5:1, adds hierarchy without hurting readability |
| Grid / borders | discreet separators | `#3A3D46` | structure without distraction |
| Primary / accent | links, titles, badges | `#22D3EE` | the project's signature color, politically neutral |
| Secondary | support | `#7C89A6` | discreet |
| Positive *(reserved)* | unused here | `#4A90D9` | see `STYLE_DUEL.md` |
| Negative *(reserved)* | unused here | `#D9764A` | see `STYLE_DUEL.md` |
**Scale specific to this project, topic weight (sequential, not categorical)**: unlike Project 1, this visual does not encode categories (PMs) but a **continuous magnitude** (a topic's weight at a given time), so a categorical palette would be the wrong choice. Use **Cividis**, a sequential scale specifically designed and validated to stay readable for color blindness (unlike Viridis, which is optimized for perceived luminance identically across the 3 common forms of color blindness). Range from `#00204D` (low weight, nearly blending into the `#0E1117` background) to `#FFEA46` (high weight, bright yellow, naturally drawing the eye to thematic peaks).
**Crisis windows (overlay bands)**: `#262730` at 40% opacity, deliberately neutral (neither positive nor negative), since a crisis window is not inherently "good" or "bad", just a time marker.
**PM transition lines**: vertical dotted line, `#7C89A6`, 1pt.
---
## 4. Typography
*(identical to `STYLE_DUEL.md`)*
| Usage | Font | Weight | Where to use it |
|---|---|---|---|
| Main title | **Lora** | 700 | heatmap title |
| Subtitles | **Inter** | 600 | axis caption, crisis window labels |
| Body text | **Inter** | 400 | topic labels, source notes |
| Figures | **IBM Plex Mono** | 500 | colorbar values, if shown |
Same caveat as in `STYLE_DUEL.md`: these fonts apply only to exported images (Matplotlib/Plotly) and a possible LinkedIn banner/carousel, never to the GitHub README body, which stays in GitHub's system font.
---
## 5. Layout
- **Overall layout**: a single hero image, but **wide and horizontal** (unlike the radar's square format), to give the 7 year time axis room to breathe.
- **Margins**: 50px on the left (for topic labels), 40px elsewhere.
- **Spacing**: 20px between the title and the chart, 16px between the chart and the colorbar, 12px between the colorbar and the source note.
- **Title sizes**: suptitle 20pt, subtitle 12pt, topic labels 10pt (left column), time labels (years) 10pt.
- **Visual hierarchy**: title > heatmap > colorbar (discreet, at the bottom) > source note.
- **Optimal width**: exported at 2400x1200px (2:1 ratio); the image will display at full README width (about 900px), keep the wide format rather than square to respect the "timeline" nature of the subject.
- **Text/chart balance**: this image carries more "embedded text" than the radar (topic labels, PM labels on transition lines); this is intentional and consistent with the "wow effect but understandable without an external legend" goal.
### ASCII diagram: main figure (heatmap)
```
┌──────────────────────────────────────────────────────────┐
│   THE THEMATIC HEATMAP                                     │  Lora 20pt
│   7 years of British politics, month by month               │  Inter 12pt
│                                                            │
│  Brexit    ▓▓▓▓████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │
│  Covid-19  ░░░░░░████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░  │
│  Ukraine   ░░░░░░░░░░░░░░░░░░████████░░░░░░░░░░░░░░░░░░░  │
│  Economy   ░░░░░░░░░░░░████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │
│  ...       ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │
│            └──┬────┴────┬────┴────┬────┴────┬────┴────┘  │
│              2019      2021      2023      2025           │
│         ┊  Johnson  ┊T┊  Sunak  ┊    Starmer    ┊         │  dotted lines #7C89A6
│         [grey band #262730 = crisis window]                │
│                                                            │
│   low   ▮▯▯▯▯▯▯▯▯▯ high   (Cividis colorbar, horizontal)   │
│                     Source: Hansard API · hansard-pm-nlp   │
└──────────────────────────────────────────────────────────┘
   background #0E1117
```
### ASCII diagram: README page
```
┌─────────────────────────────────────────┐
│ [Banner 1600x400]                        │
├─────────────────────────────────────────┤
│ # The thematic heatmap                   │
│ One-sentence hook                        │
├─────────────────────────────────────────┤
│ [HERO IMAGE: heatmap_main.png]           │
│ (full width, wide 2:1 format)            │
├─────────────────────────────────────────┤
│ ## The message in 3 sentences            │
├─────────────────────────────────────────┤
│ ## How this visual was built             │
│  - link to phase5_lda_report.md          │
│  - explicit mention of LDA vs BERTopic   │
├─────────────────────────────────────────┤
│ ## What it reveals (bullets)             │
├─────────────────────────────────────────┤
│ [streamgraph_secondary.png]              │
│ [covid_zoom_focus.png]                   │
├─────────────────────────────────────────┤
│ ## Limitations                           │
├─────────────────────────────────────────┤
│ ## Reproducing this visual               │
├─────────────────────────────────────────┤
│ Links: live dashboard · write-up · LinkedIn │
└─────────────────────────────────────────┘
```
---
## 6. Visualization design
### Main visual: topics x time heatmap
- **Type**: heatmap, topics as rows (13 after the T0+T1 merge), months as columns (continuous, 2019-2026).
- **Dimensions**: Matplotlib/Seaborn figure 12x6 inches, exported at 200 dpi, giving 2400x1200px.
- **Colors**: Cividis sequential scale (section 3), crisis windows overlaid at `#262730`/40%, PM transition lines dotted `#7C89A6`.
- **Font sizes**: title 20pt, topic labels 10pt (left, right-aligned for a clean look), year labels 10pt (bottom), crisis window legend 9pt.
- **Axis style**: no numeric Y axis (topic labels replace the tick marks); X axis in years only (no monthly gridlines shown, too dense for a non-technical reader; months remain the computation granularity, not the display resolution).
- **Grid style**: no additional grid; the heatmap cells alone are enough to structure the visual; thin 0.3pt cell borders in the background color for subtle separation without creating a visible grid.
- **Annotations**: short, plain language labels for each topic (carried over unchanged from the interpretation already written in `phase5_lda_report.md`, do not reinvent the labels), for example "Ukraine / Russia / security" rather than "Topic 3"; a discreet label per crisis window directly above the corresponding grey band (e.g. "mini-budget") rather than a separate legend to decode.
- **Legend / colorbar**: horizontal, below the chart, with only two text ticks, "low" / "high", rather than numeric LDA weight values (which would not be intuitively meaningful to the target audience).
- **Animation**: none in the static version; see section 9 for the optional GIF as a README complement.
*Why these choices improve readability*: replacing numeric topic labels with plain language interpretations turns an abstract modeling artifact into an immediately recognizable timeline; the "low/high" ticks avoid asking the reader to interpret an LDA probability scale.
### Secondary visual 1: streamgraph (one topic over time)
- **Type**: streamgraph, or simply a series of "small multiples" (one line per topic, stacked vertically, Y scale hidden); the streamgraph is recommended if it stays readable with 13 series, otherwise fall back to small multiples (a safer choice for a "no extra design decision" render, to pick based on how it actually looks once tested).
- **Dimensions**: 10x5 inches, 200 dpi.
- **Colors**: Cividis gradient applied by topic intensity, or a single neutral `#7C89A6` color if using small multiples (more readable at 13 series).
- **Legend**: labels directly at the end of each stream/line rather than a separate legend (more readable given the short expected reading time).
### Secondary visual 2: Covid crisis zoom (3 topics side by side)
- **Type**: 3 small line charts, one per Covid sub-topic (restrictions/testing, vaccines/schools, NHS/inquiry), the window tightened to the Covid period only.
- **Dimensions**: 8x5 inches, 200 dpi (3 panels of about 2.5x5 inches each).
- **Pedagogical goal**: concretely illustrate why the repo chose **not to merge** these 3 topics (unlike T0+T1); a visual that makes a methodological decision from the repo intuitively understandable.
---
## 7. Usability
*(same rules as `STYLE_DUEL.md`, with two additions specific to this project)*
- Readability, contrast, accessibility, simplicity, visual consistency: identical to `STYLE_DUEL.md` section 7.
- **Cognitive load specific to the heatmap**: 13 topic rows is already at the upper limit of what a non-technical reader can absorb; do not add a 14th row "to be exhaustive", and consider visually grouping related topics (e.g. the 3 Covid topics one below the other) rather than scattering them in an arbitrary alphabetical order.
- **Responsive**: the wide format (2400x1200) must stay readable once reduced to a mobile screen width (about 400px displayed); test this case specifically, since 10pt text in a 2400px image can become unreadable once reduced to 400px; if needed, produce a vertically cropped mobile version for the LinkedIn carousel rather than shrinking the single wide image.
---
## 8. Icons and illustrations
*(identical to `STYLE_DUEL.md`)*: **Lucide** library. Pictograms suited here: a "flame" or "layers" icon at the top of a section (evokes the "heatmap" without reproducing a 🔥 emoji, more consistent with the sober register); a "clock" or "timeline" icon next to the link to `PHASE0_SCOPING.md`. Same restrictions as `STYLE_DUEL.md` (no excess emoji, no clipart).
---
## 9. GitHub README
**Recommended structure for `portfolio/02_topic_heatmap/README.md`**: identical to `STYLE_DUEL.md`'s structure (section 9), with two differences:
1. **Banner**: same format (1600x400px) but title "The thematic heatmap".
2. **Method section**: must explicitly mention that LDA was preferred over BERTopic *because of corpus size* (296 documents), not because of intrinsic superiority, an honesty point already documented in `phase5_topic_comparison_report.md`, not to be glossed over even in a simplified version.
3. **GIF (optional but recommended here, unlike Project 1)**: a short GIF (4-6 seconds, looping, under 5MB) showing the time axis "sweeping" left to right can reinforce the "timeline coming alive" effect; produce it only if time allows, it is not a prerequisite (consistent with the development-simplicity constraint).
---
## 10. LinkedIn publication
- **Images to produce**: `heatmap_main.png` cropped to 1080x1350 (portrait; the wide 2:1 version does not work well in a full-frame LinkedIn post), a dedicated crop should be planned from the design stage rather than an after-the-fact resize that would crush the topic labels.
- **Format**: a **3 to 4 slide carousel** is recommended here (unlike Project 1) since the subject lends itself to sequential storytelling: (1) the full heatmap as a teaser, (2) Brexit zoom, (3) Covid zoom, (4) Ukraine zoom; each slide reuses the same visual cropped to a period, creating a "turning the pages of a historical timeline" effect.
- **Post text narration**: open with "7 years, 4 Prime Ministers, one question: what were they really talking about?", unfold the 3-4 events in chronological order as each slide's caption, end with the GitHub/dashboard link.
- **Eye-catching elements**: Cividis's bright yellow (`#FFEA46`) on a dark background creates natural focal points on thematic peaks; make sure at least one bright yellow peak is visible in the LinkedIn preview thumbnail (LinkedIn's automatic crop sometimes truncates images, check before publishing).
---
## 11. Build checklist
**Design**
- [ ] Verify the real colors of `_dark()` in `app/app.py`
- [ ] Test the Cividis scale under a color blindness simulator
- [ ] Reuse the shared style file `src/hansard_pm_nlp/portfolio_style.py` created for Project 1
**Development**
- [ ] Load the document x topic matrix already written in `data/processed/` without re-running `build_lda_topics.py`
- [ ] Reuse the T0+T1 merge rule already implemented in `dashboard_helpers.py` as is
- [ ] Load crisis windows and transition dates from `PHASE0_SCOPING.md` (no manual re-entry)
- [ ] Aggregate weights by month (weighted average)
- [ ] Write `plot_topic_heatmap()`, `plot_topic_streamgraph()`, `plot_crisis_zoom()` in `src/hansard_pm_nlp/portfolio_viz.py`
**Visuals**
- [ ] Main heatmap (2400x1200px, 200 dpi)
- [ ] Secondary streamgraph or small multiples (2000x1000px)
- [ ] Covid zoom, 3 panels (1600x1000px)
**Documentation**
- [ ] Write `portfolio/02_topic_heatmap/README.md` following the section 9 structure
- [ ] Explicitly mention the LDA vs BERTopic choice and its justification
**Exports**
- [ ] Export all images as PNG @2x
- [ ] Check topic label readability once the image is reduced to mobile width
**GitHub publication**
- [ ] Link `portfolio/02_topic_heatmap/` from the root README
- [ ] (Optional) Produce the time-sweep GIF
**LinkedIn publication**
- [ ] Crop to 1080x1350 for each carousel slide
- [ ] Verify the preview thumbnail contains a visible bright yellow peak
- [ ] Write the post text following the section 10 narration
---
## 12. Best practices: pitfalls to avoid
*(same principles as `STYLE_DUEL.md`, extended for this project)*
- **Visual overload**: do not show the original 14 topics without merging; respect the already validated T0+T1 merge, which exists precisely to avoid this overload.
- **Too many colors**: a single color scale (Cividis) for the whole heatmap; never color individual topic rows on top of the cell color, that would create confusing double encoding.
- **Poor contrast**: Cividis's bright yellow on a `#0E1117` background is the visual's highest-contrast point; verify that no label text ever sits directly on a bright yellow cell without a readability halo/outline.
- **Unsuitable fonts**: do not shrink topic labels below 9pt to "fit" the 13 rows; shorten the labels instead of reducing the font below the readability threshold.
- **Hard to read charts**: avoid an X axis with monthly gridlines shown (84 gridlines over 7 years); stick to years as visual markers, consistent with section 6.
- **Unnecessary effects**: no "depth" effect or drop shadow on heatmap cells; the time-sweep GIF (section 9) stays optional and must never become a complex animation (fade, zoom, particles) that would distract from the data message.
