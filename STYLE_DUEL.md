# STYLE_DUEL.md: Design specification for "The style duel"
> This document is a complete, self-sufficient specification: everything needed to build the visual and the README without having to make a new design decision is defined here.
---
## 0. Consistency with the identity already present in the repo
Before proposing anything new, here is what the repo's documentation lets us verify:
- **Theme already fixed**: `.streamlit/config.toml` pins `theme.base = "dark"` for the dashboard. The README mentions no color overrides beyond that pin, so the dashboard very likely uses Streamlit's **default** dark palette (`backgroundColor #0E1117`, `secondaryBackgroundColor #262730`, `textColor #FAFAFA`), unless there is undocumented customization in `app.py`. **Point to verify yourself before starting**: open `app/app.py`, look for the `_dark()` function mentioned in the README, and if it defines colors different from the ones below, align this document's palette with it. Otherwise, the values below are a safe choice since they reuse exactly the already-activated theme's default values.
- **Root document naming convention**: `README.md`, `WRITEUP.md` (all caps, no hyphen). `STYLE_DUEL.md` follows this convention exactly, no change needed.
- **Notebook convention**: numbered prefix + snake_case (`01_corpus_overview.ipynb`...). The new notebook should therefore be called `notebooks/portfolio_01_style_duel.ipynb`.
- **Documentation style**: `WRITEUP.md` is written for a "technical but not a specialist" reader; this new document should go one level further, for a **non-technical** reader (recruiter, LinkedIn).
- **No explicit visual identity** (logo, documented palette, style guide) exists in the repo beyond the Streamlit dark theme, so this document creates the project's first formal visual identity, in keeping with what already exists rather than breaking from it.
---
## 1. Project vision
- **Goal**: show, at a single glance, that every UK Prime Minister has a recognizable speaking style, and that this claim is not an impression but a result already validated by a classification model (91.5 to 93.2% accuracy).
- **Target audience**: a recruiter or Data manager scrolling a GitHub/LinkedIn profile for a few seconds; no NLP or statistics knowledge should be required to understand the message.
- **Key message**: *"Language style alone is enough to identify who is speaking, and here are the 6 traits that prove it."*
- **Storytelling**: start from a universal question ("can you recognize someone just from how they talk?"), answer it with an immediate visual (the radar), then anchor the answer in a validated number (the classifier's accuracy) to turn an intuition into evidence.
- **What the visitor should understand in under 10 seconds**: "there are 4 distinct style signatures, one per Prime Minister, and it is not a coincidence, it is measurable."
---
## 2. Art direction
- **Style chosen: "sober data journalism"**, halfway between the Financial Times/The Economist (rigor, seriousness, data at the center) and a modern product dashboard (sharp contrast, clear hierarchy). Rationale: the target audience (Data recruiters) immediately recognizes this register as "professional", without falling into "corporate PowerPoint" aesthetics (too generic) or an "overloaded BI dashboard" (too dense for a non-technical reader).
- **Mood sought**: serious, factual, a bit "British financial press" (fitting given the subject: the Westminster Parliament).
- **Level of restraint**: high. One single main visual per page/post, few decorative elements, no superfluous icons.
- **Level of interactivity**: none for the portfolio deliverables (static PNG images), interactivity already exists via the live Streamlit dashboard, no need to duplicate it. A simple "Explore interactively" link is enough.
- **Visual inspirations**: *Financial Times* charts (dark background for "long format" visuals, understated color series, titles as a full sentence rather than a terse label); *Our World in Data* for legend clarity and the absence of unnecessary chrome; Streamlit's native dark aesthetic, for continuity with the existing dashboard.
---
## 3. Color palette
| Color | Role | HEX | Why |
|---|---|---|---|
| Background | figure and hero image background | `#0E1117` | reuses the default value of the already-activated Streamlit dark theme (`theme.base = "dark"`), visual continuity with the dashboard |
| Cards / surfaces | callout boxes, legend | `#262730` | Streamlit's default `secondaryBackgroundColor` in dark mode, same family as the background |
| Primary text | titles, important labels | `#FAFAFA` | ~18:1 contrast on `#0E1117` background, well above the WCAG AAA threshold (7:1) |
| Secondary text | captions, footnotes | `#9CA3AF` | medium grey, adds hierarchy without hurting readability (contrast > 4.5:1) |
| Grid / borders | discreet radar axes | `#3A3D46` | visible enough to structure, discreet enough not to distract |
| Primary / brand accent | links, title underline, badges | `#22D3EE` | the project's signature color, politically neutral (neither Conservative blue nor Labour red), consistent across all visuals |
| Secondary | supporting elements (axes, technical text) | `#7C89A6` | neutral blue-grey, discreet |
| Positive *(reserved, unused in this project)* | upward trend in future charts | `#4A90D9` | blue rather than green, avoids the most common red/green confusion for colorblind readers |
| Negative *(reserved, unused in this project)* | downward trend | `#D9764A` | terracotta orange, forms a blue/orange pair readable across the 3 common types of color blindness |
**Categorical palette dedicated to the 4 Prime Ministers** (used only for the radar, never mix with the positive/negative palette above in the same chart), taken from the **Okabe-Ito** palette, the standard reference for colorblind accessibility:
| PM | HEX | Treatment |
|---|---|---|
| Boris Johnson | `#E69F00` (orange) | solid line |
| Liz Truss | `#56B4E9` (sky blue) | **dashed line** + asterisk in the legend ("49 day tenure, read with caution") |
| Rishi Sunak | `#009E73` (teal green) | solid line |
| Keir Starmer | `#CC79A7` (pink-purple) | solid line |
**Light mode**: this project is designed dark-background only (consistency with the dashboard + maximum readability for a radar chart, which loses clarity on a white background because of the semi-transparent fill). **Do not** produce a separate light version; this is a restraint decision, not an oversight.
**Color blindness**: the Okabe-Ito + dark background combination was specifically designed to stay distinguishable under deuteranopia, protanopia, and tritanopia. Verify with a simulator (e.g. Coblis, free online) before final publication.
---
## 4. Typography
> ⚠️ **Important practical note**: GitHub does not allow loading custom fonts inside a README's body (GitHub Markdown always renders with GitHub's system font, which cannot be changed). The font choices below therefore apply to **two specific places only**: text embedded directly in chart images (Matplotlib/Plotly) and, if a "banner" image or a LinkedIn carousel visual is produced (via Pillow or an HTML-to-image export), that image's text. The README's own body text stays in GitHub's system font; that is expected, do not try to work around it.
| Usage | Font (Google Fonts) | Weight | Where to use it |
|---|---|---|---|
| Main title (chart suptitle, banner) | **Lora** | 700 (Bold) | radar title, README banner title |
| Subtitles | **Inter** | 600 (SemiBold) | chart subtitle, section headers in carousel images |
| Body text / captions | **Inter** | 400 (Regular) | the 4 PM legend, source notes |
| Highlighted figures | **IBM Plex Mono** | 500 (Medium) | the "91.5%" figure shown large in the secondary visual; the monospace effect gives a "precise data" feel and removes any ambiguity between 1/l/I |
**Why this trio works**: Lora (an editorial serif) for the title brings "financial press" seriousness; Inter (a highly readable sans-serif, the de facto standard for data interfaces) for everything else keeps reading fast; IBM Plex Mono reserved for figures creates a clear "this is a measured data point" signal, without adding more font families (3 maximum, a typographic restraint rule).
---
## 5. Layout
- **Overall layout**: a single hero image (the radar), no multi-chart grid in the same image; clarity comes before exhaustiveness.
- **Margins**: at least 60px of inner padding around the radar in the figure canvas, so nothing touches the edges.
- **Spacing**: 24px between the subtitle and the chart, 32px between the chart and the legend, 16px between the legend and the source note.
- **Title sizes**: suptitle 20pt, subtitle 12pt, radar axis labels 11pt, legend 11pt, source note 9pt.
- **Visual hierarchy**: title > radar > legend > source note, in that order of visual weight (size + color contrast).
- **Optimal width**: hero image exported at 1600x1600px (square, a radar chart reads better in a square format), displayed at about 800x800px in the README (GitHub resizes automatically).
- **Text/chart balance**: in the README, never let more than 3 sentences follow the radar before the next subsection; the visual must stay the dominant element on the page.
### ASCII diagram: main figure (radar)
```
┌──────────────────────────────────────────────┐
│         THE STYLE DUEL                        │  Lora 20pt bold, #FAFAFA
│  What 6 stylometric traits reveal              │  Inter 12pt, #9CA3AF
│                                                │
│                ╭─────────────╮                │
│             ╱──┤             ├──╲             │
│           ╱    │             │    ╲           │
│          │     │   RADAR     │     │          │  6 axes, grid #3A3D46
│           ╲    │  (6 axes)   │    ╱           │
│             ╲──┤             ├──╱             │
│                ╰─────────────╯                │
│                                                │
│   ● Johnson  ┄ Truss*  ● Sunak  ● Starmer      │  horizontal legend, Inter 11pt
│   * 49 day tenure, read with caution           │  Inter 9pt, #9CA3AF
│                                                │
│         Source: Hansard API · hansard-pm-nlp  │  Inter 9pt, #7C89A6
└──────────────────────────────────────────────┘
   background #0E1117
```
### ASCII diagram: README page
```
┌─────────────────────────────────────────┐
│ [Banner 1600x400, title + badges]        │
├─────────────────────────────────────────┤
│ # The style duel                         │
│ One-sentence hook                        │
├─────────────────────────────────────────┤
│ [HERO IMAGE: radar_main.png]             │
├─────────────────────────────────────────┤
│ ## The message in 3 sentences            │
├─────────────────────────────────────────┤
│ ## How this visual was built             │
│  - 4 bullets + link to phase6_classifier_report.md │
├─────────────────────────────────────────┤
│ ## What it reveals (bullets)             │
├─────────────────────────────────────────┤
│ [secondary image 1]  [secondary image 2] │
├─────────────────────────────────────────┤
│ ## Limitations                           │
├─────────────────────────────────────────┤
│ ## Reproducing this visual (command)     │
├─────────────────────────────────────────┤
│ Links: live dashboard · write-up · LinkedIn │
└─────────────────────────────────────────┘
```
---
## 6. Visualization design
### Main visual: radar chart
- **Type**: radar/spider chart, 6 axes, 4 overlaid series (one per PM), semi-transparent fill (alpha 0.15) under each line.
- **Dimensions**: Matplotlib figure 8x8 inches, exported at 200 dpi, giving 1600x1600px.
- **Colors**: PM categorical palette defined in section 3; background `#0E1117`; radial grid `#3A3D46`.
- **Font sizes**: title 20pt, the 6 axis labels 11pt (`#FAFAFA`), radial tick labels 8pt (`#9CA3AF`, shown discreetly, 3 gridlines maximum).
- **Axis design**: the 6 axes correspond to the 6 traits already identified as the most discriminant by the H1 classifier (MTLD, Flesch-Kincaid readability, `hedge_rate`, net certainty, `pos_INTJ`, frequency of "not"), values normalized 0-1 (min-max across the 4 PMs), no raw scale shown (it would not be meaningful to a non-technical reader).
- **Grid style**: radial only (concentric circles), 3 levels, 0.5pt thickness, no additional angular grid.
- **Annotations**: a single asterisk on Truss's line, referring to the footnote below the legend; no other annotation inside the chart body (keep the radar "clean").
- **Legend**: horizontal, below the chart, not in a corner (corner legends on a radar often overlap the data).
- **Animation**: none, static export only, consistent with the "restrained" choice in section 2.
*Why these choices improve readability*: limiting to 6 axes avoids the visual saturation typical of radar charts with 10+ axes (unreadable); normalizing 0-1 allows a direct comparison across 6 metrics with very different scales (a readability score and a hedging rate do not share a unit); the semi-transparent fill lets overlap areas between PMs show through, visually reinforcing the message that "styles are distinct but never fully opposite."
### Secondary visual 1: permutation importance (bar chart)
- **Type**: horizontal bar chart, 6 bars (the same 6 traits as the radar, in the same order), used to justify why these 6 axes were chosen.
- **Dimensions**: 8x5 inches, 200 dpi.
- **Colors**: a single color (`#22D3EE`, the brand accent, deliberately different from the PM colors to signal "this is about the model, not a specific PM").
- **Font**: title 16pt, labels 11pt, values shown at the end of each bar in `IBM Plex Mono` 10pt.
- **Grid**: light vertical grid only (`#3A3D46`), top/right spines removed.
- **Legend**: none (a single series).
### Secondary visual 2: simplified confusion matrix
- **Type**: 3x3 heatmap (Truss excluded, consistent with the repo), values in percent.
- **Dimensions**: 6x6 inches, 200 dpi, square.
- **Colors**: `Cividis` sequential gradient (colorblind-safe), diagonal highlighted with a 2pt `#22D3EE` outline.
- **Font**: cell values in `IBM Plex Mono` 14pt, axis labels in `Inter` 11pt.
- **Annotation**: a single plain language sentence below the chart ("The model identifies the correct Prime Minister 9 times out of 10"), no "accuracy/precision/recall" jargon inside the image itself (reserved for the README).
---
## 7. Usability
- **Readability**: minimum font size 9pt in any exported image (below that, unreadable once GitHub/LinkedIn resizes the image).
- **Contrast**: any text on a `#0E1117` background must reach at least a 4.5:1 ratio (WCAG AA); the `#FAFAFA` and `#9CA3AF` colors defined in section 3 meet this constraint, do not darken them further.
- **Accessibility**: Okabe-Ito palette + verification with a color blindness simulator before publishing (see section 3); never encode information through color alone, line style (solid/dashed for Truss) always doubles the color information.
- **Simplicity**: one message per image; if an idea needs a second chart, it should become a secondary visual, not an addition to the main one.
- **Cognitive load**: maximum 4 simultaneous color series in a single chart (here: 4 PMs); beyond that, reading becomes a decoding exercise rather than an immediate read.
- **Visual consistency**: same PM colors, same typography, same grid style across the 3 images of this project AND those of the `THEMATIC_HEATMAP.md` project (PM categorical palette shared between the two projects).
- **Responsive**: not applicable (static images), but always export at high resolution (200 dpi minimum) to stay sharp on mobile, where most LinkedIn traffic is viewed.
---
## 8. Icons and illustrations
- **Recommended library**: **Lucide** (lucide.dev), open source, MIT license, thin-stroke style consistent with the "restrained" aesthetic sought, available as individually downloadable SVGs (no web framework needed).
- **Suitable pictograms**: a "radar" or "target" icon at the top of the README (title section); a "git-branch" or "database" icon next to the link to the extraction repo; "github" and "linkedin" icons for the badges at the end of the README (via shields.io, see section 9).
- **Where to place them**: only in the README (never inside the chart images themselves, which must stay 100% data), as a prefix to a section title or in the badge row.
- **To avoid**: excessive decorative emoji (🚀✨🔥...), at most 1 sober emoji in the main title if desired, none in subtitles; clipart, mascots, gradient/skeuomorphic icons that would contradict the "financial press" register chosen in section 2.
---
## 9. GitHub README
**Recommended structure for `portfolio/01_style_duel/README.md`**:
1. **Banner** (1600x400px, `#0E1117` background, title "The style duel" in Lora, subtitle in Inter), a simple static image, no animation needed.
2. **Badges** (via shields.io): Python version, "Live dashboard" link, link to the main `hansard-pm-nlp` repo, license badge if applicable.
3. **Hook**: one bold sentence, reusing the key message from section 1.
4. **Hero image**: `radar_main.png`, full width.
5. **Table of contents** (Markdown anchors) if the README exceeds about 150 lines; otherwise unnecessary for a document this size.
6. **"The message in 3 sentences" section**.
7. **"How this visual was built" section**: 3 to 4 plain language bullets, with an explicit link to `phase6_classifier_report.md` for the reader who wants the full technical proof.
8. **"What it reveals" section**: bullets.
9. **Secondary visuals gallery** (the 2 images side by side if the Markdown rendering allows it, otherwise stacked).
10. **"Limitations" section**: methodological honesty (Truss, style vs. content scope).
11. **"Reproducing this visual" section**: a single command (`jupyter nbconvert --execute notebooks/portfolio_01_style_duel.ipynb`).
12. **Conclusion / links**: interactive dashboard, full write-up, LinkedIn post.
**GIF**: not needed for this project (the radar is inherently a static visual); reserve the GIF budget for the `THEMATIC_HEATMAP.md` project, where the time evolution suits it better.
---
## 10. LinkedIn publication
- **Images to produce**: reuse `radar_main.png` directly (already square at 1600x1600, ideal for a LinkedIn post) + a cropped 1080x1350 (portrait) version of the permutation importance visual for a possible second slide.
- **Format**: **single image** for the first post (the radar alone is strong enough not to need a carousel); if a carousel is wanted (2-3 slides), order: (1) the radar alone with the hook as the post caption, (2) the importance bar chart with the question "why these 6 traits?", (3) the simplified confusion matrix with the key figure shown large.
- **Post text narration**: open with a question ("Can you recognize a Prime Minister just from how they speak?"), give the answer in one sentence, mention the figure (91.5% / 93.2%), end with a link to the GitHub repo and the live dashboard.
- **Eye-catching elements**: the contrast of the `#0E1117` dark background against the LinkedIn feed (mostly white/light) creates a natural visual stop while scrolling, an additional argument in favor of the dark theme chosen in section 3.
---
## 11. Build checklist
**Design**
- [ ] Verify the real colors of `_dark()` in `app/app.py` and adjust the palette if needed
- [ ] Simulate the PM palette under a color blindness tool (Coblis or equivalent)
- [ ] Create a shared style file (`src/hansard_pm_nlp/portfolio_style.py`) with the color/font constants defined here
**Development**
- [ ] Load the Phase 3/4/6 artifacts without re-running any `build_*.py` script
- [ ] Reuse the normalization logic already present in `dashboard_helpers.py`
- [ ] Write `plot_style_radar()` and `plot_feature_importance_bar()` in `src/hansard_pm_nlp/portfolio_viz.py`
**Visuals**
- [ ] Main radar (1600x1600px, 200 dpi)
- [ ] Importance bar chart (1600x1000px)
- [ ] Simplified confusion matrix (1200x1200px)
**Documentation**
- [ ] Write `portfolio/01_style_duel/README.md` following the section 9 structure
- [ ] Write `notebooks/portfolio_01_style_duel.ipynb` (narrated, committed outputs)
**Exports**
- [ ] Export all images as PNG @2x (200 dpi minimum)
- [ ] Check the actual rendering in a GitHub README (light and dark viewer modes)
**GitHub publication**
- [ ] Link `portfolio/01_style_duel/` from the root README
- [ ] Verify the notebook runs cleanly end to end
**LinkedIn publication**
- [ ] Crop visuals to LinkedIn formats (1080x1080 or 1080x1350)
- [ ] Write the post text following the section 10 narration
---
## 12. Best practices: pitfalls to avoid
- **Visual overload**: do not add annotations, arrows, or text boxes to the radar beyond what section 6 specifies; every extra element dilutes the main message.
- **Too many colors**: never exceed the 4 PM colors + 1 accent color in a single image; never mix the PM categorical palette with the positive/negative semantic palette.
- **Poor contrast**: do not use `#9CA3AF` on a `#262730` background for important text (insufficient contrast); reserve that grey for `#0E1117` backgrounds only.
- **Unsuitable fonts**: avoid "handwritten" or "playful" fonts that would contradict the sober register chosen; never use more than 3 font families in a single deliverable.
- **Hard to read charts**: a radar with more than 6-7 axes becomes unreadable; do not give in to the temptation of adding other available stylometric metrics just because they exist.
- **Unnecessary effects**: no drop shadows, background gradients, or 3D borders; these effects visually date an image and contradict the "financial press" aesthetic sought.
