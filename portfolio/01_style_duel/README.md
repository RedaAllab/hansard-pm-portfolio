<p align="center">
  <img src="assets/banner.png" alt="The style duel" width="100%">
</p>

# The style duel

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-22D3EE)](https://www.python.org/)
[![Dashboard live](https://img.shields.io/badge/dashboard-live-22D3EE)](https://hansard-pm-nlp-nhenez39aujxgtejnyjvrg.streamlit.app)
[![hansard-pm-nlp](https://img.shields.io/badge/data-hansard--pm--nlp-7C89A6)](https://github.com/RedaAllab/hansard-pm-nlp)

**Language style alone is enough to identify who is speaking, and here are the 6 traits that prove it.**

## Contents

- [The message in 3 sentences](#the-message-in-3-sentences)
- [How this visual was built](#how-this-visual-was-built)
- [What it reveals](#what-it-reveals)
- [Secondary visuals](#secondary-visuals)
- [Limitations](#limitations)
- [Reproducing this visual](#reproducing-this-visual)
- [Links](#links)

<p align="center">
  <img src="assets/radar_main.png" alt="Radar of 6 stylometric traits by Prime Minister" width="100%">
</p>

## The message in 3 sentences

Every UK Prime Minister has a recognizable speaking style, measured here across 6 stylometric traits: lexical diversity, readability, hedging, certainty, frequency of "not", sentence length. This is not just a visual impression: a classifier trained only on these traits (no content words at all) identifies the correct Prime Minister in 91.5 to 93.2% of cases, far above chance (33%). The radar above visualizes what the model learned to detect.

## How this visual was built

- **No new model trained**: this visual reads artifacts already computed by [`hansard-pm-nlp`](https://github.com/RedaAllab/hansard-pm-nlp) (Phases 3, 4 and 6: `eda_summary.csv`, `affect_summary.csv`, `phase6_classifier_report.md` and its exports), without re-running any `build_*.py` script.
- **6 traits, not 14**: the radar is limited to 6 axes to stay readable (see [`STYLE_DUEL.md`](../../STYLE_DUEL.md) section 6). 5 of them (lexical diversity, readability, hedging, certainty, words per sentence) come from the whole-corpus Phase 3/4 exports, the same ones the [live dashboard](https://hansard-pm-nlp-nhenez39aujxgtejnyjvrg.streamlit.app) uses. The 6th (frequency of "not") is recomputed with the same tokenizer as `hansard-pm-nlp` (no dependency added) because that trait only existed, in the Phase 6 exports, for 3 of the 4 Prime Ministers.
- **`pos_INTJ` replaced with `mean_words_per_sentence`**: the original specification called for the interjection rate (`pos_INTJ`, the classifier's most discriminant trait) as the 6th axis. That trait needs POS tagging (spaCy), which Phase 6 only ran for the classifier's 3 Prime Ministers. Liz Truss (49 day tenure, 5 documents) is excluded upstream, before the stylometric traits are even computed. Rather than adding spaCy to this deliberately lightweight repo to recompute one missing value, the radar uses `mean_words_per_sentence`: available for all 4 PMs with no recomputation, and independently the 5th most discriminant trait for the more accurate model (see below).
- **Model evidence**: the classifier (logistic regression and HistGradientBoosting, trained on a temporal split, earlier sittings for training, later ones for testing) is documented in full in [`phase6_classifier_report.md`](https://github.com/RedaAllab/hansard-pm-nlp/blob/main/data/processed/phase6_classifier_report.md).

## What it reveals

- Rishi Sunak stands out with markedly higher lexical diversity and readability than the other three: a more measured, less repetitive style.
- Boris Johnson dominates the "hedging" axis (`hedge_rate`) by a wide margin: a speaking style that qualifies and hedges its claims more than the others.
- Liz Truss and Keir Starmer look similar on several axes despite opposing parties, a reminder that speaking style does not necessarily track the political divide.
- The classifier statistically confirms what the radar shows visually: these style differences are stable and distinct enough to identify the author of an anonymized excerpt nine times out of ten.

## Secondary visuals

<table>
<tr>
<td width="50%"><img src="assets/feature_importance.png" alt="Permutation importance of stylometric traits" width="100%"></td>
<td width="50%"><img src="assets/confusion_matrix.png" alt="Classifier confusion matrix" width="100%"></td>
</tr>
</table>

The first shows which traits matter most to the more accurate model (HistGradientBoosting): interjection rate (`pos_INTJ`) and hedging (`hedge_rate`) come out on top. The second shows, PM by PM, how rarely the model gets it wrong.

## Limitations

- **Liz Truss is outside the classifier**: 5 documents over a 49 day tenure are too few for a reliable train/test split (see `hansard-pm-nlp/src/hansard_pm_nlp/split.py`). Her line on the radar (dashed, asterisked) is an average over a very small sample (n=123 contributions), to be read with caution, not as an "established" style on the same footing as the other three.
- **Style, not content**: this visual measures *how* each PM speaks (lexical diversity, sentence length, hedging...), never *what about*. No content word ever enters the classifier. A classifier on topical content would give a different result and would not be testing the same thing.
- **4 of the radar's 6 traits are not the bar chart's 6 traits**: see the note above ("How this visual was built"). The two visuals overlap on 3 traits (`mtld`, `hedge_rate`, `mean_words_per_sentence`), not all 6.
- **Andy Burnham is out of scope**: he became Prime Minister on 2026-07-20 (see `PHASE0_SCOPING.md` in the `hansard-pm-extraction` repo), after this corpus's extraction cutoff, and is deliberately excluded from this project's scope for now.

## Reproducing this visual

From this repo's root:

```bash
jupyter nbconvert --to notebook --execute --inplace notebooks/01_style_duel.ipynb
```

Prerequisite: `hansard-pm-nlp` cloned as a sibling directory (`../hansard-pm-nlp`), see this repo's [root README](../../README.md) for details.

## Links

- [Interactive dashboard](https://hansard-pm-nlp-nhenez39aujxgtejnyjvrg.streamlit.app): the "Overview" tab reproduces this radar in a filterable form
- [`hansard-pm-nlp`](https://github.com/RedaAllab/hansard-pm-nlp): source repo for the data and model
- [`phase6_classifier_report.md`](https://github.com/RedaAllab/hansard-pm-nlp/blob/main/data/processed/phase6_classifier_report.md): full technical report of the classifier
- [`WRITEUP.md`](https://github.com/RedaAllab/hansard-pm-nlp/blob/main/WRITEUP.md): full write-up of the analysis project
- [Project 04, the recap](../04_annual_recap/README.md): this radar's traits condensed into one tone marker per year, alongside the other 3 projects
