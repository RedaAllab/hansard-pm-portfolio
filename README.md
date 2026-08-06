# hansard-pm-portfolio

[![CI](https://github.com/RedaAllab/hansard-pm-portfolio/actions/workflows/ci.yml/badge.svg)](https://github.com/RedaAllab/hansard-pm-portfolio/actions/workflows/ci.yml)
[![license](https://img.shields.io/badge/license-MIT-7C89A6)](LICENSE)

Portfolio-grade static visuals built on top of [`hansard-pm-nlp`](https://github.com/RedaAllab/hansard-pm-nlp)'s already-computed artifacts (Hansard speeches by UK Prime Ministers, 2019-present), for a non-technical audience (recruiter, LinkedIn), not for further analysis. No new model is trained here; every number and chart traces back to a report already committed in `hansard-pm-nlp`.

## Projects

| # | Project | Spec | Status |
|---|---|---|---|
| 01 | [The style duel](portfolio/01_style_duel/README.md): a 6-trait stylometric radar showing each PM has a distinct, classifier-validated "voice" | [`STYLE_DUEL.md`](STYLE_DUEL.md) | Built |
| 02 | [The thematic heatmap](portfolio/02_topic_heatmap/README.md): a topic-over-time heatmap tracing Brexit, Covid and Ukraine through what PMs actually talked about | [`THEMATIC_HEATMAP.md`](THEMATIC_HEATMAP.md) | Built |
| 03 | [The handover](portfolio/03_pm_handover/README.md): style and sentiment, six weeks either side of each PM transition | [`ROADMAP_PM_HANDOVER.md`](ROADMAP_PM_HANDOVER.md) | Built |
| 04 | [The recap](portfolio/04_annual_recap/README.md): one card per calendar year, the portfolio's executive summary | [`ROADMAP_ANNUAL_RECAP.md`](ROADMAP_ANNUAL_RECAP.md) + [`ANNUAL_RECAP.md`](ANNUAL_RECAP.md) | Built |

All four projects share one design system (`src/hansard_pm_portfolio/style.py`) so they read as one coherent portfolio rather than unrelated one-offs, see `STYLE_DUEL.md` section 7 and `THEMATIC_HEATMAP.md` section 0, which both require it explicitly.

## Architecture

This is a **separate, lightweight, read-only** companion to `hansard-pm-nlp`. It never trains anything and never imports the `hansard_pm_nlp` package (which pulls torch/transformers/spacy/bertopic). It reads `hansard-pm-nlp`'s already-exported `data/processed/` artifacts (parquet/CSV/Markdown) the same way that repo's own Streamlit dashboard does. Every non-obvious structural decision, why a separate repo, why this dependency set, why two of the radar's 6 axes deviate from `STYLE_DUEL.md`'s literal text, is logged in **[`ARCHITECTURE.md`](ARCHITECTURE.md)**.

```
hansard-pm-portfolio/
├── STYLE_DUEL.md              # design spec, project 01
├── THEMATIC_HEATMAP.md        # design spec, project 02
├── ROADMAP_PM_HANDOVER.md     # execution plan, project 03 (no separate design spec)
├── ROADMAP_ANNUAL_RECAP.md    # execution plan, project 04
├── ANNUAL_RECAP.md            # layout decisions, project 04 (written before the rendering code)
├── ARCHITECTURE.md            # why this repo is structured this way
├── assets/fonts/               # Lora, Inter, IBM Plex Mono - static instances (see ARCHITECTURE.md section 8)
├── src/hansard_pm_portfolio/
│   ├── style.py                # shared colors/fonts/sizes, the one design system for every project
│   ├── data_access/            # reads hansard-pm-nlp's artifacts; no writes, no retraining
│   │   ├── _shared.py          # I/O, PM scope, tenures, crisis windows, the LDA topic layer
│   │   ├── style_duel.py       # project 01's data loading
│   │   ├── topic_heatmap.py    # project 02's data loading
│   │   ├── pm_handover.py      # project 03's data loading
│   │   └── annual_recap.py     # project 04's data loading
│   └── viz/
│       ├── common.py           # shared banner/save/dark-axes helpers
│       ├── style_duel.py       # project 01's plotting functions
│       ├── topic_heatmap.py    # project 02's plotting functions
│       ├── pm_handover.py      # project 03's plotting functions
│       └── annual_recap.py     # project 04's plotting function
├── notebooks/
│   ├── 01_style_duel.ipynb     # narrated, already executed, produces project 01's 3 images
│   ├── 02_topic_heatmap.ipynb  # narrated, already executed, produces project 02's 4 images
│   ├── 03_pm_handover.ipynb    # narrated, already executed, produces project 03's 3 images
│   └── 04_annual_recap.ipynb   # narrated, already executed, produces project 04's 2 images
├── portfolio/
│   ├── 01_style_duel/
│   │   ├── README.md           # the polished, recruiter-facing writeup
│   │   └── assets/             # banner.png, radar_main.png, feature_importance.png, confusion_matrix.png
│   ├── 02_topic_heatmap/
│   │   ├── README.md
│   │   └── assets/             # banner.png, heatmap_main.png, small_multiples.png, covid_zoom.png
│   ├── 03_pm_handover/
│   │   ├── README.md
│   │   └── assets/             # banner.png, transition_main.png, transition_timeline_secondary.png
│   └── 04_annual_recap/
│       ├── README.md
│       └── assets/             # banner.png, annual_recap_main.png
└── tests/
```

## Setup

Requires a local clone of `hansard-pm-nlp`, either as a sibling directory (default) or pointed at via an environment variable:

```bash
# from the same parent directory as this repo
git clone https://github.com/RedaAllab/hansard-pm-nlp.git

# or, if it lives somewhere else:
export HANSARD_PM_NLP_DIR=/path/to/hansard-pm-nlp
```

Then, from this repo's root:

```bash
python3 -m pip install -e ".[dev]"
python3 -m pytest tests/
```

## Reproducing a project's visuals

Each project's own README has a one-line reproduction command (e.g. [`portfolio/01_style_duel/README.md`](portfolio/01_style_duel/README.md#reproducing-this-visual)). All of them are `jupyter nbconvert --to notebook --execute --inplace notebooks/<name>.ipynb`, run from this repo's root.

## Links

- [`hansard-pm-nlp`](https://github.com/RedaAllab/hansard-pm-nlp): the source analysis repo (data, models, dashboard)
- [`hansard-pm-extraction`](https://github.com/RedaAllab/hansard-pm-extraction): the corpus extraction repo
- [Live dashboard](https://hansard-pm-nlp-nhenez39aujxgtejnyjvrg.streamlit.app): the interactive version of what these static visuals summarize
