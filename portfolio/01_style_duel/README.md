<p align="center">
  <img src="assets/banner.png" alt="Le duel de style" width="100%">
</p>

# Le duel de style

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-22D3EE)](https://www.python.org/)
[![Dashboard live](https://img.shields.io/badge/dashboard-live-22D3EE)](https://hansard-pm-nlp-nhenez39aujxgtejnyjvrg.streamlit.app)
[![hansard-pm-nlp](https://img.shields.io/badge/data-hansard--pm--nlp-7C89A6)](https://github.com/RedaAllab/hansard-pm-nlp)

**Le style de langage à lui seul suffit à identifier qui parle — et voici les 6 traits qui le prouvent.**

## Sommaire

- [Le message en 3 phrases](#le-message-en-3-phrases)
- [Comment ce visuel a été construit](#comment-ce-visuel-a-été-construit)
- [Ce que ça révèle](#ce-que-ça-révèle)
- [Visuels secondaires](#visuels-secondaires)
- [Limites](#limites)
- [Reproduire ce visuel](#reproduire-ce-visuel)
- [Liens](#liens)

<p align="center">
  <img src="assets/radar_main.png" alt="Radar des 6 traits stylométriques par Premier ministre" width="100%">
</p>

## Le message en 3 phrases

Chaque Premier ministre britannique a une signature de style oratoire reconnaissable, mesurée ici sur 6 traits stylométriques — diversité lexicale, lisibilité, nuance, certitude, fréquence de « not », longueur de phrase. Ce n'est pas qu'une impression graphique : un classifieur entraîné uniquement sur ces traits (aucun mot de contenu) retrouve le bon Premier ministre dans 91,5 à 93,2 % des cas, largement au-dessus du hasard (33 %). Le radar ci-dessus visualise ce que le modèle a appris à détecter.

## Comment ce visuel a été construit

- **Aucun nouveau modèle entraîné** : ce visuel relit les artefacts déjà calculés par [`hansard-pm-nlp`](https://github.com/RedaAllab/hansard-pm-nlp) (Phases 3, 4 et 6 — `eda_summary.csv`, `affect_summary.csv`, `phase6_classifier_report.md` et ses exports), sans ré-exécuter aucun script `build_*.py`.
- **6 traits, pas 14** : le radar se limite à 6 axes pour rester lisible (voir [`STYLE_DUEL.md`](../../STYLE_DUEL.md) section 6) — 5 d'entre eux (diversité lexicale, lisibilité, nuance, certitude, mots/phrase) viennent des exports whole-corpus Phase 3/4, identiques à ceux du [dashboard live](https://hansard-pm-nlp-nhenez39aujxgtejnyjvrg.streamlit.app). Le 6ᵉ (fréquence de « not ») est recalculé avec le même tokenizer que `hansard-pm-nlp` (aucune dépendance ajoutée) car ce trait n'existait, dans les exports Phase 6, que pour 3 des 4 Premiers ministres.
- **`pos_INTJ` remplacé par `mean_words_per_sentence`** : la spécification initiale visait le taux d'interjections (`pos_INTJ`, le trait le plus discriminant du classifieur) comme 6ᵉ axe. Ce trait nécessite un tagging POS (spaCy) que Phase 6 n'a exécuté que pour les 3 Premiers ministres du classifieur — Liz Truss (49 jours de mandat, 5 documents) en est exclue en amont, avant même le calcul des traits. Plutôt que d'ajouter spaCy à ce dépôt volontairement léger pour recalculer une seule valeur manquante, le radar utilise `mean_words_per_sentence` : disponible pour les 4 PM sans recalcul, et indépendamment le 5ᵉ trait le plus discriminant du modèle le plus précis (voir plus bas).
- **Preuve du modèle** : le classifieur (logistic regression et HistGradientBoosting, entraînés sur un split temporel — les séances les plus anciennes en train, les plus récentes en test) est documenté intégralement dans [`phase6_classifier_report.md`](https://github.com/RedaAllab/hansard-pm-nlp/blob/main/data/processed/phase6_classifier_report.md).

## Ce que ça révèle

- Rishi Sunak se distingue par une diversité lexicale et une lisibilité nettement supérieures aux trois autres — un style plus mesuré, moins répétitif.
- Boris Johnson domine largement l'axe « nuance » (`hedge_rate`) — un style oratoire qui qualifie et nuance davantage ses affirmations que les autres.
- Liz Truss et Keir Starmer se ressemblent sur plusieurs axes malgré des partis opposés — un rappel que le style oratoire ne recoupe pas nécessairement le clivage politique.
- Le classifieur confirme statistiquement ce que le radar montre visuellement : ces différences de style sont assez stables et distinctes pour identifier l'auteur d'un extrait anonymisé neuf fois sur dix.

## Visuels secondaires

<table>
<tr>
<td width="50%"><img src="assets/feature_importance.png" alt="Importance de permutation des traits stylométriques" width="100%"></td>
<td width="50%"><img src="assets/confusion_matrix.png" alt="Matrice de confusion du classifieur" width="100%"></td>
</tr>
</table>

Le premier montre quels traits comptent le plus pour le modèle le plus précis (HistGradientBoosting) — le taux d'interjections (`pos_INTJ`) et la nuance (`hedge_rate`) arrivent en tête. Le second montre, PM par PM, à quel point le modèle se trompe rarement.

## Limites

- **Liz Truss est hors classifieur** : 5 documents sur 49 jours de mandat sont trop peu pour un split train/test fiable (voir `hansard-pm-nlp/src/hansard_pm_nlp/split.py`) — sa ligne sur le radar (pointillée, astérisque) reste une moyenne sur un échantillon très réduit (n=123 contributions), à lire avec prudence, pas comme un style « établi » au même titre que les trois autres.
- **Style, pas contenu** : ce visuel mesure *comment* chaque PM parle (diversité lexicale, longueur de phrase, nuance...), jamais *de quoi* — aucun mot de contenu n'entre dans le classifieur. Un classifieur sur le contenu thématique donnerait un résultat différent et ne testerait pas la même chose.
- **4 des 6 traits du radar ≠ les 6 traits du graphique d'importance** : voir la note ci-dessus ("Comment ce visuel a été construit") — les deux visuels se recoupent sur 3 traits (`mtld`, `hedge_rate`, `mean_words_per_sentence`), pas sur les 6.
- **Andy Burnham hors périmètre** : devenu Premier ministre le 2026-07-20 (voir `PHASE0_SCOPING.md` du dépôt `hansard-pm-extraction`), il est absent du corpus à la date d'extraction et volontairement exclu du périmètre de ce projet pour l'instant.

## Reproduire ce visuel

Depuis la racine de ce dépôt :

```bash
jupyter nbconvert --to notebook --execute --inplace notebooks/01_style_duel.ipynb
```

Prérequis : `hansard-pm-nlp` cloné en dossier frère (`../hansard-pm-nlp`) — voir le [README racine](../../README.md) de ce dépôt pour le détail.

## Liens

- [Dashboard interactif](https://hansard-pm-nlp-nhenez39aujxgtejnyjvrg.streamlit.app) — l'onglet "Overview" reproduit ce radar en version filtrable
- [`hansard-pm-nlp`](https://github.com/RedaAllab/hansard-pm-nlp) — dépôt source des données et du modèle
- [`phase6_classifier_report.md`](https://github.com/RedaAllab/hansard-pm-nlp/blob/main/data/processed/phase6_classifier_report.md) — rapport technique complet du classifieur
- [`WRITEUP.md`](https://github.com/RedaAllab/hansard-pm-nlp/blob/main/WRITEUP.md) — write-up complet du projet d'analyse
