<p align="center">
  <img src="assets/banner.png" alt="La carte thermique des thèmes" width="100%">
</p>

# La carte thermique des thèmes

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-22D3EE)](https://www.python.org/)
[![Dashboard live](https://img.shields.io/badge/dashboard-live-22D3EE)](https://hansard-pm-nlp-nhenez39aujxgtejnyjvrg.streamlit.app)
[![hansard-pm-nlp](https://img.shields.io/badge/data-hansard--pm--nlp-7C89A6)](https://github.com/RedaAllab/hansard-pm-nlp)

**7 ans de politique britannique, résumés dans une seule carte — et on y voit littéralement Brexit, le Covid et l'Ukraine se succéder.**

## Sommaire

- [Le message en 3 phrases](#le-message-en-3-phrases)
- [Comment ce visuel a été construit](#comment-ce-visuel-a-été-construit)
- [Ce que ça révèle](#ce-que-ça-révèle)
- [Visuels secondaires](#visuels-secondaires)
- [Limites](#limites)
- [Reproduire ce visuel](#reproduire-ce-visuel)
- [Liens](#liens)

<p align="center">
  <img src="assets/heatmap_main.png" alt="Carte thermique des 13 thèmes par mois, 2019-2026" width="100%">
</p>

## Le message en 3 phrases

L'attention parlementaire d'un Premier ministre britannique suit fidèlement les chocs de son époque — pas besoin d'un nouveau modèle pour le voir, seulement de mettre en image ce qu'un modèle de topics déjà entraîné (LDA, Phase 5) a déjà capturé. Chaque bande de couleur est un thème ; plus elle est jaune vif, plus il a dominé les débats ce mois-là. En sept ans, quatre séquences ressortent sans qu'il faille les expliquer : l'accord nord-irlandais post-Brexit en janvier 2020, le Covid-19 sur près de deux ans, le retrait de Kaboul en quelques semaines à l'été 2021, puis l'invasion de l'Ukraine à partir de février 2022.

## Comment ce visuel a été construit

- **Aucun nouveau modèle entraîné** : la matrice document × thème vient telle quelle de `lda_topics.parquet` (Phase 5, [`hansard-pm-nlp`](https://github.com/RedaAllab/hansard-pm-nlp)) — 296 documents (PM × séance), K=14 thèmes, jamais restreinte aux 3 PM du classifieur (contrairement à Phase 6), donc Liz Truss y figure.
- **LDA plutôt que BERTopic — par contrainte, pas par supériorité** : [`phase5_topic_comparison_report.md`](https://github.com/RedaAllab/hansard-pm-nlp/blob/main/data/processed/phase5_topic_comparison_report.md) documente que BERTopic, sur un corpus de seulement 296 documents, regroupe 61 % d'entre eux dans un unique thème fourre-tout. LDA a été retenu pour cette taille de corpus précise, pas parce qu'il serait intrinsèquement meilleur — BERTopic est conçu pour des corpus plusieurs ordres de grandeur plus grands.
- **La fusion Ukraine/Russie (T0+T1) est reprise à l'identique**, pas redécidée : [`phase5_lda_report.md`](https://github.com/RedaAllab/hansard-pm-nlp/blob/main/data/processed/phase5_lda_report.md) documente ces deux thèmes comme quasi-identiques à tous les K testés — sommés en un seul avant tout affichage.
- **Les 13 libellés en langage courant sont un travail éditorial de ce projet**, pas une reprise : ni le rapport Phase 5 ni le dashboard live n'en proposent — tous deux n'affichent que des listes de mots-clés bruts ou des labels algorithmiques (« T2: hs, project, rail »). Les libellés utilisés ici (ex. « Brexit et l'accord nord-irlandais ») ont été écrits à partir de ces mêmes listes de mots-clés, traçabilité conservée dans `src/hansard_pm_portfolio/data_access.py`.
- **Fenêtres de crise et dates de mandat** viennent de `PHASE0_SCOPING.md` ([`hansard-pm-extraction`](https://github.com/RedaAllab/hansard-pm-extraction)), jamais redéfinies à l'œil sur le graphique.

## Ce que ça révèle

- **L'accord commercial post-Brexit domine dès le premier mois** (janvier 2020) — le pic le plus net de toute la carte, avant même que Covid n'apparaisse.
- **Le Covid-19 occupe near-continûment 16 mois**, mais sous 3 angles distincts (restrictions/tests, vaccins/écoles, personnel NHS/enquête publique) qui montent et descendent à des moments différents — voir le zoom ci-dessous.
- **L'Afghanistan est le pic le plus brutal de la carte** : quasiment invisible avant et après, dominant sur 2-3 mois pile au moment du retrait de Kaboul (été 2021).
- **« Budget et politique intérieure » devient le thème le plus constamment présent à partir de fin 2022** — sous Sunak puis Starmer, l'attention se déplace nettement du choc externe vers la gestion intérieure.
- **La « crise de leadership travailliste » (mai-juillet 2026) est la moins reconnaissable des 4 fenêtres de crise** — contrairement à Brexit/Covid/Ukraine, c'est un événement récent et propre au corpus (transition Starmer → Burnham), pas un choc mondial déjà familier au lecteur.

## Visuels secondaires

<table>
<tr>
<td width="60%"><img src="assets/small_multiples.png" alt="Les 13 thèmes séparément, un panneau par thème" width="100%"></td>
<td width="40%"><img src="assets/covid_zoom.png" alt="Zoom sur les 3 thèmes Covid-19" width="100%"></td>
</tr>
</table>

Le premier éclate les 13 thèmes en petits panneaux individuels plutôt qu'une seule légende à 13 couleurs — le dashboard live a déjà testé les deux formats pour son propre onglet Topics et documenté pourquoi les small multiples l'emportent à cette échelle ; repris à l'identique plutôt que retesté. Le second zoome sur les 3 thèmes Covid pour montrer concrètement pourquoi ils n'ont jamais été fusionnés (contrairement à Ukraine/Russie) : ce sont 3 sous-phases distinctes de la même crise, pas un doublon.

## Limites

- **Liz Truss (5 documents, 49 jours)** : les colonnes de septembre-octobre 2022 reposent sur un échantillon très réduit — à lire comme un signal bruité, pas comme une politique thématique établie.
- **Les libellés de thèmes sont une interprétation, pas une vérité du modèle** : LDA ne produit que des distributions de mots ; les phrases en langage courant utilisées ici sont une lecture humaine de ces mots-clés, pas une sortie du modèle lui-même — un autre lecteur des mêmes mots-clés aurait pu choisir d'autres formulations.
- **Le duplicata Ukraine/Russie (T0+T1) est un vrai signal du corpus, pas un artefact à corriger** — documenté dans `phase5_lda_report.md` comme reflétant des sous-périodes distinctes du conflit (invasion 2022, aide militaire continue, sommets OTAN) avec un vocabulaire différent à chaque fois, pas une instabilité du modèle.
- **LDA sur 296 documents reste un corpus modeste** : la comparaison avec BERTopic (voir ci-dessus) montre que le choix de méthode a été contraint par la taille du corpus, pas validé comme optimal dans l'absolu.
- **Andy Burnham hors périmètre** : devenu Premier ministre le 2026-07-20, après la dernière séance du corpus à cette date d'extraction — absent de cette carte par construction, pas par filtrage a posteriori.

## Reproduire ce visuel

Depuis la racine de ce dépôt :

```bash
jupyter nbconvert --to notebook --execute --inplace notebooks/02_topic_heatmap.ipynb
```

Prérequis : `hansard-pm-nlp` cloné en dossier frère (`../hansard-pm-nlp`) — voir le [README racine](../../README.md) de ce dépôt pour le détail.

## Liens

- [Dashboard interactif](https://hansard-pm-nlp-nhenez39aujxgtejnyjvrg.streamlit.app) — l'onglet "Topics" reproduit cette carte en version filtrable, avec les mots-clés bruts de chaque thème
- [`hansard-pm-nlp`](https://github.com/RedaAllab/hansard-pm-nlp) — dépôt source des données et du modèle
- [`phase5_lda_report.md`](https://github.com/RedaAllab/hansard-pm-nlp/blob/main/data/processed/phase5_lda_report.md) — rapport technique complet du modèle LDA
- [`phase5_topic_comparison_report.md`](https://github.com/RedaAllab/hansard-pm-nlp/blob/main/data/processed/phase5_topic_comparison_report.md) — comparaison LDA vs BERTopic
- [`WRITEUP.md`](https://github.com/RedaAllab/hansard-pm-nlp/blob/main/WRITEUP.md) — write-up complet du projet d'analyse
