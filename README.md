# hansard-pm-portfolio

Portfolio-grade static visuals built on top of [`hansard-pm-nlp`](https://github.com/RedaAllab/hansard-pm-nlp)'s already-computed artifacts (Hansard speeches by UK Prime Ministers, 2019-present) — for a non-technical audience (recruiter, LinkedIn), not for further analysis. No new model is trained here; every number and chart traces back to a report already committed in `hansard-pm-nlp`.

## Projects

| # | Project | Spec | Status |
|---|---|---|---|
| 01 | [Le duel de style](portfolio/01_style_duel/README.md) — a 6-trait stylometric radar showing each PM has a distinct, classifier-validated "voice" | [`STYLE_DUEL.md`](STYLE_DUEL.md) | ✅ built |
| 02 | La carte thermique des thèmes — a topic-over-time heatmap tracing Brexit → Covid → Ukraine through what PMs actually talked about | [`THEMATIC_HEATMAP.md`](THEMATIC_HEATMAP.md) | not started |

Both projects share one design system (`src/hansard_pm_portfolio/style.py`) so the two read as one coherent portfolio rather than two unrelated one-offs — see `STYLE_DUEL.md` §7 and `THEMATIC_HEATMAP.md` §0, which both require it explicitly.

## Architecture

This is a **separate, lightweight, read-only** companion to `hansard-pm-nlp` — it never trains anything and never imports the `hansard_pm_nlp` package (which pulls torch/transformers/spacy/bertopic). It reads `hansard-pm-nlp`'s already-exported `data/processed/` artifacts (parquet/CSV/Markdown) the same way that repo's own Streamlit dashboard does. Every non-obvious structural decision — why a separate repo, why this dependency set, why two of the radar's 6 axes deviate from `STYLE_DUEL.md`'s literal text — is logged in **[`ARCHITECTURE.md`](ARCHITECTURE.md)**.

```
hansard-pm-portfolio/
├── STYLE_DUEL.md              # design spec, project 01
├── THEMATIC_HEATMAP.md        # design spec, project 02
├── ARCHITECTURE.md            # why this repo is structured this way
├── assets/fonts/               # Lora, Inter, IBM Plex Mono - static instances (see ARCHITECTURE.md §8)
├── src/hansard_pm_portfolio/
│   ├── style.py                # shared colors/fonts/sizes - the one design system for every project
│   ├── data_access.py          # reads hansard-pm-nlp's artifacts; no writes, no retraining
│   └── viz/
│       └── style_duel.py       # project 01's plotting functions
├── notebooks/
│   └── 01_style_duel.ipynb     # narrated, already-executed - produces project 01's 3 images
├── portfolio/
│   └── 01_style_duel/
│       ├── README.md           # the polished, recruiter-facing writeup
│       └── assets/             # banner.png, radar_main.png, feature_importance.png, confusion_matrix.png
└── tests/
```

## Setup

Requires a local clone of `hansard-pm-nlp` — either as a sibling directory (default) or pointed at via an environment variable:

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

Each project's own README has a one-line reproduction command (e.g. [`portfolio/01_style_duel/README.md`](portfolio/01_style_duel/README.md#reproduire-ce-visuel)) — all of them are `jupyter nbconvert --to notebook --execute --inplace notebooks/<name>.ipynb`, run from this repo's root.

## Links

- [`hansard-pm-nlp`](https://github.com/RedaAllab/hansard-pm-nlp) — the source analysis repo (data, models, dashboard)
- [`hansard-pm-extraction`](https://github.com/RedaAllab/hansard-pm-extraction) — the corpus extraction repo
- [Live dashboard](https://hansard-pm-nlp-nhenez39aujxgtejnyjvrg.streamlit.app) — the interactive version of what these static visuals summarize
