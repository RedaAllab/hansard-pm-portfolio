# Choix d'architecture

Ce document justifie les décisions structurelles de ce dépôt qui s'écartent de, ou précisent, `STYLE_DUEL.md`. Il est volontairement court — un journal de décisions, pas une deuxième spécification.

## 1. Un dépôt séparé, pas un sous-dossier de `hansard-pm-nlp`

`STYLE_DUEL.md` suppose implicitement (`src/hansard_pm_nlp/portfolio_style.py`, `portfolio/01_style_duel/`) que ce projet vit **dans** `hansard-pm-nlp`. Sur demande explicite, il vit ici, dans un dépôt séparé (`hansard-pm-portfolio`), qui accueillera aussi le projet 02 (`THEMATIC_HEATMAP.md`) plus tard — d'où `portfolio/01_style_duel/` et `portfolio/02_topic_heatmap/` comme sous-dossiers de *ce* dépôt, pas de `hansard-pm-nlp`.

Conséquence directe : ce dépôt ne peut pas importer `hansard_pm_nlp` comme un module Python du même arbre de code — il lit ses artefacts comme des données externes. Voir §3.

## 2. `hansard_pm_portfolio`, pas `hansard_pm_nlp`

`STYLE_DUEL.md` nomme les fichiers `src/hansard_pm_nlp/portfolio_style.py` et `portfolio_viz.py` — cohérent avec un sous-dossier de `hansard-pm-nlp`, mais un dépôt séparé avec un package du même nom (`hansard_pm_nlp`) collisionnerait dans tout environnement où les deux sont installés (deux distributions différentes revendiquant le même nom d'import). Le package s'appelle donc `hansard_pm_portfolio`. Le préfixe `portfolio_` des noms de fichiers de la spec devient redondant une fois que le package entier *est* le portfolio — `portfolio_style.py` → `style.py`, `portfolio_viz.py` → `viz/style_duel.py` (voir §6). Même renommage pour le notebook : `notebooks/portfolio_01_style_duel.ipynb` → `notebooks/01_style_duel.ipynb`.

## 3. Dépendance légère, lecture seule des artefacts déjà exportés

`hansard-pm-nlp` a déjà résolu ce problème pour son propre dashboard : `requirements-app.txt` n'installe ni torch, ni transformers, ni spacy, ni bertopic — seulement ce qu'il faut pour lire des fichiers déjà calculés (`pandas`, `pyarrow`, `plotly`, `gensim`). Ce dépôt suit exactement le même principe :

- **Aucune dépendance sur le package `hansard_pm_nlp`** — l'installer entraînerait tout `pyproject.toml` de `hansard-pm-nlp` (torch, transformers, spacy, bertopic, gensim), inutile ici puisque tout le calcul lourd a déjà eu lieu.
- **Deux fonctions portées, pas importées** : `normalize_radar()` (10 lignes de pandas pur) et le tokenizer regex de `lexical.py` (3 lignes) sont recopiées dans `data_access.py` avec une note d'attribution, plutôt que de dépendre du package complet pour ~15 lignes.
- **Emplacement des données** : `data_access.hansard_pm_nlp_dir()` résout un dépôt frère (`../hansard-pm-nlp`, comme sur cette machine) ou la variable d'environnement `HANSARD_PM_NLP_DIR`.

## 4. DuckDB pour lire les fichiers Parquet, pas `pandas.read_parquet`

Les fichiers Parquet de `hansard-pm-nlp` (écrits avec `parquet-cpp-arrow` 24.x) déclenchent `OSError: Repetition level histogram size mismatch` avec `pandas.read_parquet` sous pyarrow 19 — une incompatibilité connue entre versions dans l'encodage des statistiques de colonne. DuckDB lit les mêmes fichiers sans problème et retourne un `DataFrame` pandas via `.df()`. `data_access.read_parquet()` centralise ce contournement plutôt que de forcer une mise à niveau de pyarrow, dont l'effet de bord sur le reste de l'environnement est moins prévisible.

## 5. Le radar : 5 traits repris tels quels, 1 recalculé, 1 substitué

`STYLE_DUEL.md` §6 propose 6 axes : MTLD, Flesch-Kincaid, `hedge_rate`, `net_certainty`, `pos_INTJ`, fréquence de « not ». En pratique :

- **MTLD, Flesch-Kincaid, `hedge_rate`, `net_certainty`, `mean_words_per_sentence`** viennent tels quels de `eda_summary.csv` / `affect_summary.csv` (Phases 3-4), disponibles pour les 4 PM sans recalcul — les mêmes colonnes que l'onglet "Stylometric profile by PM" du dashboard live.
- **Fréquence de « not »** est recalculée ici (whole-corpus par PM, même tokenizer que `lexical.py`) car Phase 6 ne l'a exportée que pour 3 PM (voir §7) — un calcul trivial, sans dépendance lourde, donc gardé.
- **`pos_INTJ` → `mean_words_per_sentence`** : `pos_INTJ` nécessite spaCy (POS-tagging), et Phase 6 ne l'a calculé que pour les 3 PM du classifieur — Liz Truss en est exclue *avant* le calcul des traits stylométriques, pas seulement avant l'entraînement. Ajouter spaCy à ce dépôt pour une seule valeur manquante contredirait §3. `mean_words_per_sentence` le remplace : disponible pour les 4 PM, et 5ᵉ trait le plus discriminant du modèle le plus précis (HistGradientBoosting) — la substitution garde un ancrage "validé par le classifieur" plutôt que de le perdre silencieusement.

Documenté aussi dans le README du projet (section "Comment ce visuel a été construit" et "Limites"), pas seulement ici.

## 6. Un fichier de viz par projet, pas un `portfolio_viz.py` unique

`STYLE_DUEL.md` §11 suggère un seul `portfolio_viz.py` pour `plot_style_radar()` et `plot_feature_importance_bar()`. Comme ce dépôt est prévu pour accueillir un deuxième projet (`THEMATIC_HEATMAP.md`, plus tard) dans le même arbre, les fonctions de tracé sont scindées par projet dès maintenant (`viz/style_duel.py`, futur `viz/topic_heatmap.py`) plutôt que d'accumuler les deux projets dans un seul fichier grandissant. `style.py` (couleurs, polices) reste, lui, unique et partagé — c'est le point que `STYLE_DUEL.md` §7 et `THEMATIC_HEATMAP.md` §0 demandent explicitement ("palette catégorielle PM partagée entre les deux projets").

## 7. Périmètre des Premiers ministres

- `data_access.IN_SCOPE_PMS` (radar, 4 PM) exclut explicitement Andy Burnham (PM depuis le 2026-07-20, voir `PHASE0_SCOPING.md` du dépôt `hansard-pm-extraction`) — absent du corpus à la date d'extraction actuelle, et hors périmètre pour ce projet pour l'instant, par décision explicite plutôt que par un filtrage accidentel.
- `data_access.CLASSIFIER_PMS` (matrice de confusion, importance de permutation, 3 PM) exclut Liz Truss, comme Phase 6 elle-même (`split.py`) — pas une décision de ce dépôt, une reprise à l'identique de celle de `hansard-pm-nlp`.

## 8. Polices : instances statiques, pas les fichiers variables de Google Fonts

Lora et Inter ne sont distribuées par Google Fonts qu'en polices variables (`Lora[wght].ttf`, `Inter[opsz,wght].ttf`) — un seul fichier couvrant toute la plage de graisse. Matplotlib ne résout pas de façon fiable une graisse précise (700, 600...) à l'intérieur d'un fichier variable. `assets/fonts/` contient donc des instances statiques, générées une fois avec `fontTools.varLib.instancer` (`wght=700` pour Lora, `600` et `400` pour Inter) et leur table de noms nettoyée (name ID 16/17 supprimés) pour que chaque poids résolve un nom de famille distinct et sans ambiguïté (`Lora`, `Inter SemiBold`, `Inter`). IBM Plex Mono est distribuée nativement en fichiers statiques par graisse, aucune instanciation nécessaire.

## 9. Une inexactitude relevée dans `STYLE_DUEL.md`

§12 affirme que `#9CA3AF` sur `#262730` est un contraste insuffisant et doit être réservé au fond `#0E1117`. Mesuré (`tests/test_style.py`), ce contraste est en réalité de 5,84:1 — au-dessus du seuil WCAG AA (4,5:1) que la spec applique partout ailleurs. Sans conséquence visuelle ici (aucun texte secondaire n'est posé sur `#262730` dans ce projet), mais noté plutôt que silencieusement propagé.
