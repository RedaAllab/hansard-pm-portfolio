# THEMATIC_HEATMAP.md — Spécification de conception : « La carte thermique des thèmes »
> Ce document est une spécification complète, autosuffisante : tout ce qu'il faut pour construire le visuel et le README sans avoir à prendre de nouvelle décision de design est défini ici. La palette, la typographie et les règles d'accessibilité sont **identiques** à `STYLE_DUEL.md` pour garantir une identité graphique homogène sur l'ensemble du portfolio — elles sont reproduites intégralement ci-dessous pour que ce fichier reste utilisable seul.
---
## 0. Cohérence avec l'identité déjà présente dans le dépôt
- **Thème déjà fixé** : comme pour `STYLE_DUEL.md`, ce projet reprend le thème sombre déjà activé pour le dashboard (`.streamlit/config.toml: theme.base = "dark"`), en s'appuyant sur la palette sombre par défaut de Streamlit tant qu'un examen de `_dark()` dans `app/app.py` n'a pas montré de personnalisation différente.
- **Élément déjà existant à reprendre à l'identique, pas à réinventer** : la fusion des topics T0+T1 (Ukraine/Russie, quasi-identiques) documentée dans `phase5_lda_report.md` et déjà appliquée dans le dashboard — ce visuel doit répliquer exactement cette règle, pas en discuter une nouvelle.
- **Fenêtres de crise et dates de transition de PM** : déjà définies dans `PHASE0_SCOPING.md` (dépôt `hansard-pm-extraction`) — à charger telles quelles, jamais à redéfinir visuellement "à l'œil" sur le graphique.
- **Convention de nommage** : `THEMATIC_HEATMAP.md` (majuscules, sans tiret) suit la même convention que `README.md`/`WRITEUP.md`/`STYLE_DUEL.md` — aucun changement nécessaire. Le notebook associé suit la même logique que pour le Projet 1 : `notebooks/portfolio_02_topic_heatmap.ipynb`.
---
## 1. Vision du projet
- **Objectif** : montrer en une seule image que l'attention politique d'un Premier ministre suit fidèlement les grands chocs de son époque — sans qu'aucun nouveau modèle n'ait été entraîné pour le démontrer.
- **Public cible** : identique à `STYLE_DUEL.md` — recruteur/manager/lecteur LinkedIn non technique.
- **Message clé** : *"7 ans de politique britannique, résumés dans une seule carte — et on y voit littéralement Brexit, le Covid et l'Ukraine se succéder."*
- **Storytelling** : le visuel doit fonctionner comme une frise historique doublée d'une preuve de données — le lecteur doit pouvoir "retrouver" mentalement les événements qu'il connaît déjà (Brexit, Covid, Ukraine) avant même de lire la légende, ce qui crée un effet de reconnaissance immédiat et gratifiant.
- **Ce que le visiteur doit comprendre en moins de 10 secondes** : "chaque bande de couleur correspond à un sujet, et on voit clairement quand chaque grand événement a dominé les débats."
---
## 2. Direction artistique
- **Style retenu** : identique à `STYLE_DUEL.md` — "data journalism sobre", inspiré Financial Times / Our World in Data.
- **Ambiance recherchée** : ici, l'ambiance doit en plus évoquer une **frise chronologique/infographie de presse** (type "chronologie d'une crise" que l'on voit dans les longs formats journalistiques) — c'est le seul point qui distingue l'ambiance de ce projet de celle du Projet 1, plus "fiche technique".
- **Niveau de sobriété** : élevé, mais légèrement moins strict que le Projet 1 car ce visuel doit porter un "effet waouh" explicitement demandé — cela se traduit par un format plus grand et plus horizontal (frise), pas par plus de couleurs.
- **Niveau d'interactivité** : nul dans le livrable portfolio (image statique) — un lien vers l'onglet "Topics" du dashboard existant couvre le besoin d'exploration interactive.
- **Inspirations visuelles** : les "heatmaps thématiques" du *New York Times* et du *Financial Times* sur les cycles d'actualité ; les frises "Our World in Data" combinant bandes temporelles et annotations d'événements ; l'onglet Topics déjà existant du dashboard (dont ce visuel reprend la logique, en version statique et narrée).
---
## 3. Palette de couleurs
*(identique à `STYLE_DUEL.md`, reproduite ici pour l'autosuffisance du document)*
| Couleur | Rôle | HEX | Pourquoi |
|---|---|---|---|
| Fond | fond de la figure | `#0E1117` | valeur par défaut du thème sombre Streamlit déjà activé |
| Cartes / surfaces | encarts, callout box | `#262730` | `secondaryBackgroundColor` par défaut Streamlit dark |
| Texte principal | titres, labels | `#FAFAFA` | contraste ~18:1, au-delà du seuil WCAG AAA |
| Texte secondaire | légendes, notes | `#9CA3AF` | contraste > 4,5:1, hiérarchise sans nuire |
| Grille / bordures | séparations discrètes | `#3A3D46` | structure sans distraire |
| Principale / accent | liens, titres, badges | `#22D3EE` | signature du projet, neutre politiquement |
| Secondaire | support | `#7C89A6` | discret |
| Positive *(réservée)* | non utilisée ici | `#4A90D9` | cf. `STYLE_DUEL.md` |
| Négative *(réservée)* | non utilisée ici | `#D9764A` | cf. `STYLE_DUEL.md` |
**Échelle spécifique à ce projet — poids des topics (séquentielle, pas catégorielle)** : contrairement au Projet 1, ce visuel n'encode pas des catégories (PM) mais une **magnitude continue** (poids d'un topic à un instant donné) → une palette catégorielle serait un contresens. Utiliser **Cividis**, une échelle séquentielle spécifiquement conçue et validée pour rester lisible en cas de daltonisme (contrairement à Viridis, optimisée sur la luminance perçue de façon identique pour les trois formes courantes de daltonisme). Aller de `#00204D` (poids faible, presque fondu dans le fond `#0E1117`) à `#FFEA46` (poids fort, jaune vif — attire naturellement l'œil vers les pics thématiques).
**Fenêtres de crise (bandes de superposition)** : `#262730` à 40 % d'opacité — volontairement neutre (ni positive ni négative), car une fenêtre de crise n'est pas en soi "bonne" ou "mauvaise", juste un repère temporel.
**Lignes de transition de PM** : pointillé vertical `#7C89A6`, 1 pt.
---
## 4. Typographie
*(identique à `STYLE_DUEL.md`)*
| Usage | Police | Poids | Où l'utiliser |
|---|---|---|---|
| Titre principal | **Lora** | 700 | titre de la heatmap |
| Sous-titres | **Inter** | 600 | légende d'axe, labels des fenêtres de crise |
| Texte courant | **Inter** | 400 | labels de topics, notes de source |
| Chiffres | **IBM Plex Mono** | 500 | valeurs de la colorbar si affichées |
Même avertissement que dans `STYLE_DUEL.md` : ces polices ne s'appliquent qu'aux images exportées (Matplotlib/Plotly) et à une éventuelle bannière/carrousel LinkedIn — jamais au corps du README GitHub, qui reste en police système GitHub.
---
## 5. Mise en page
- **Disposition générale** : une image héros unique, mais **horizontale et large** (contrairement au format carré du radar), pour laisser respirer l'axe temporel sur 7 ans.
- **Marges** : 50 px à gauche (pour les labels de topics), 40 px ailleurs.
- **Espacement** : 20 px entre le titre et le graphique, 16 px entre le graphique et la colorbar, 12 px entre la colorbar et la note de source.
- **Tailles de titre** : suptitle 20 pt, sous-titre 12 pt, labels de topics 10 pt (rangée de gauche), labels temporels (années) 10 pt.
- **Hiérarchie visuelle** : titre > carte thermique > colorbar (discrète, en bas) > note de source.
- **Largeur optimale** : export 2400×1200 px (ratio 2:1) — l'image sera affichée en pleine largeur README (~900 px), garder le format large plutôt que carré pour respecter la nature "frise temporelle" du sujet.
- **Équilibre texte/graphique** : cette image porte davantage de "texte intégré" que le radar (labels de topics, labels de PM sur les lignes de transition) — c'est volontaire et cohérent avec l'objectif "effet waouh mais compréhensible sans légende externe".
### Schéma ASCII — figure principale (heatmap)
```
┌──────────────────────────────────────────────────────────┐
│   LA CARTE THERMIQUE DES THÈMES                            │  Lora 20pt
│   7 ans de politique britannique, mois par mois            │  Inter 12pt
│                                                            │
│  Brexit    ▓▓▓▓████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │
│  Covid-19  ░░░░░░████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░  │
│  Ukraine   ░░░░░░░░░░░░░░░░░░████████░░░░░░░░░░░░░░░░░░░  │
│  Économie  ░░░░░░░░░░░░████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │
│  ...       ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │
│            └──┬────┴────┬────┴────┬────┴────┬────┴────┘  │
│              2019      2021      2023      2025           │
│         ┊  Johnson  ┊T┊  Sunak  ┊    Starmer    ┊         │  lignes pointillées #7C89A6
│         [bande grisée #262730 = fenêtre de crise]          │
│                                                            │
│   faible ▮▯▯▯▯▯▯▯▯▯ élevé   (colorbar Cividis, horizontale)│
│                     Source : Hansard API · hansard-pm-nlp  │
└──────────────────────────────────────────────────────────┘
   fond #0E1117
```
### Schéma ASCII — page README
```
┌─────────────────────────────────────────┐
│ [Bannière 1600×400]                      │
├─────────────────────────────────────────┤
│ # La carte thermique des thèmes          │
│ Accroche en 1 phrase                     │
├─────────────────────────────────────────┤
│ [IMAGE HÉROS : heatmap_main.png]         │
│ (pleine largeur, format large 2:1)       │
├─────────────────────────────────────────┤
│ ## Le message en 3 phrases               │
├─────────────────────────────────────────┤
│ ## Comment ce visuel a été construit     │
│  - lien phase5_lda_report.md             │
│  - mention explicite LDA vs BERTopic     │
├─────────────────────────────────────────┤
│ ## Ce que ça révèle (bullets)            │
├─────────────────────────────────────────┤
│ [streamgraph_secondary.png]              │
│ [covid_zoom_focus.png]                   │
├─────────────────────────────────────────┤
│ ## Limites                               │
├─────────────────────────────────────────┤
│ ## Reproduire ce visuel                  │
├─────────────────────────────────────────┤
│ Liens : dashboard live · write-up · LinkedIn │
└─────────────────────────────────────────┘
```
---
## 6. Design des visualisations
### Visuel principal — Heatmap thèmes × temps
- **Type** : heatmap, topics en lignes (13 après fusion T0+T1), mois en colonnes (continu 2019–2026).
- **Dimensions** : figure Matplotlib/Seaborn 12×6 pouces, export 200 dpi → 2400×1200 px.
- **Couleurs** : échelle séquentielle Cividis (section 3), fenêtres de crise en superposition `#262730`/40 %, lignes de transition PM en pointillé `#7C89A6`.
- **Taille des polices** : titre 20 pt, labels de topics 10 pt (à gauche, alignés à droite pour un rendu propre), labels d'années 10 pt (en bas), légende des fenêtres de crise 9 pt.
- **Style des axes** : pas d'axe Y numérique (les labels de topics remplacent les graduations) ; axe X en années seulement (pas de graduation mensuelle affichée, trop dense pour un lecteur non technique — les mois restent la granularité de calcul, pas d'affichage).
- **Style de la grille** : aucune grille supplémentaire — les cellules de la heatmap suffisent à structurer visuellement ; fines bordures de cellule 0,3 pt dans la couleur de fond pour une séparation subtile sans créer de grille visible.
- **Annotations** : labels courts et en langage courant pour chaque topic (repris tels quels de l'interprétation déjà rédigée dans `phase5_lda_report.md` — ne pas réinventer les intitulés), par exemple "Ukraine / Russie / sécurité" plutôt que "Topic 3" ; un label discret par fenêtre de crise directement au-dessus de la bande grisée correspondante (ex. "mini-budget") plutôt qu'une légende séparée à décoder.
- **Légende / colorbar** : horizontale, sous le graphique, avec seulement deux graduations textuelles "faible" / "élevé" plutôt que des valeurs numériques de poids LDA (qui n'ont pas de sens intuitif pour le public cible).
- **Animation** : aucune dans la version statique — voir section 9 pour l'option GIF en complément README.
*Pourquoi ces choix améliorent la lecture* : remplacer les intitulés numériques de topics par leurs interprétations en langage courant transforme un artefact de modélisation abstrait en une frise historique immédiatement reconnaissable ; les graduations "faible/élevé" évitent de faire porter au lecteur la charge d'interpréter une échelle de probabilité LDA.
### Visuel secondaire 1 — Streamgraph (un topic dans le temps)
- **Type** : streamgraph ou simple série de "small multiples" (une ligne par topic, empilées verticalement, échelle Y masquée) — le streamgraph est recommandé s'il reste lisible avec 13 séries, sinon basculer sur les small multiples (plus sûr pour un rendu "sans décision de design supplémentaire", à choisir en fonction du rendu réel une fois testé).
- **Dimensions** : 10×5 pouces, 200 dpi.
- **Couleurs** : dégradé Cividis appliqué par intensité de topic, ou une couleur neutre `#7C89A6` unique si small multiples (plus lisible à 13 séries).
- **Légende** : labels directement au bout de chaque flux/ligne plutôt qu'une légende séparée (plus lisible pour un temps de lecture court).
### Visuel secondaire 2 — Zoom crise Covid (3 topics côte à côte)
- **Type** : 3 mini-graphiques en ligne, un par sous-topic Covid (restrictions/tests, vaccins/écoles, NHS/enquête), fenêtre resserrée sur la période Covid uniquement.
- **Dimensions** : 8×5 pouces, 200 dpi (3 panneaux de ~2,5×5 pouces chacun).
- **Objectif pédagogique** : illustrer concrètement pourquoi le dépôt a choisi de **ne pas fusionner** ces 3 topics (contrairement à T0+T1) — visuel qui rend une décision méthodologique du dépôt intuitivement compréhensible.
---
## 7. Ergonomie
*(mêmes règles que `STYLE_DUEL.md`, avec deux ajouts spécifiques à ce projet)*
- Lisibilité, contraste, accessibilité, simplicité, cohérence graphique : identiques à la section 7 de `STYLE_DUEL.md`.
- **Charge cognitive spécifique à la heatmap** : 13 lignes de topics est déjà à la limite haute de ce qu'un lecteur non technique peut absorber — ne pas ajouter de 14e ligne "pour être exhaustif", et envisager de grouper visuellement les topics apparentés (ex. les 3 topics Covid l'un sous l'autre) plutôt que de les disperser dans un ordre alphabétique arbitraire.
- **Responsive** : le format large (2400×1200) doit rester lisible une fois réduit à la largeur d'un écran de mobile (~400 px affichés) — tester spécifiquement ce cas, car du texte à 10 pt dans une image de 2400 px peut devenir illisible une fois réduit à 400 px ; si besoin, produire une version mobile recadrée verticalement pour le carrousel LinkedIn plutôt que de réduire l'unique image large.
---
## 8. Icônes et illustrations
*(identique à `STYLE_DUEL.md`)* — bibliothèque **Lucide**. Pictogrammes adaptés ici : une icône "flame" ou "layers" en en-tête de section (évoque la "carte thermique" sans reproduire un émoji 🔥, plus cohérent avec le registre sobre) ; icône "clock" ou "timeline" à côté du lien vers `PHASE0_SCOPING.md`. Mêmes interdits que dans `STYLE_DUEL.md` (pas d'emoji en excès, pas de clipart).
---
## 9. README GitHub
**Structure recommandée pour `portfolio/02_topic_heatmap/README.md`** — identique à la structure de `STYLE_DUEL.md` (section 9), avec deux différences :
1. **Bannière** : même format (1600×400 px) mais titre "La carte thermique des thèmes".
2. **Section méthode** : doit explicitement mentionner que LDA a été préféré à BERTopic *à cause de la taille du corpus* (296 documents), pas par supériorité intrinsèque — point d'honnêteté déjà documenté dans `phase5_topic_comparison_report.md`, à ne pas passer sous silence même dans une version vulgarisée.
3. **GIF (optionnel mais recommandé ici, contrairement au Projet 1)** : un GIF court (4-6 secondes, boucle, < 5 Mo) montrant l'axe temporel "balayé" de gauche à droite peut renforcer l'effet "frise qui prend vie" — à produire uniquement si le temps le permet, ce n'est pas un prérequis (cohérent avec la contrainte de simplicité de développement).
---
## 10. Publication LinkedIn
- **Images à produire** : `heatmap_main.png` recadrée en 1080×1350 (portrait, la version large 2:1 ne fonctionne pas bien en post LinkedIn plein cadre) — prévoir un recadrage dédié dès la conception plutôt qu'un redimensionnement a posteriori qui écraserait les labels de topics.
- **Format** : **carrousel de 3-4 slides** recommandé ici (contrairement au Projet 1) car le sujet se prête à une narration séquentielle : (1) la heatmap complète en teaser, (2) zoom Brexit, (3) zoom Covid, (4) zoom Ukraine — chaque slide reprend le même visuel recadré sur une période, créant un effet de "on tourne les pages d'une frise historique".
- **Narration du post texte** : ouvrir par "7 ans, 4 Premiers ministres, une seule question : de quoi parlaient-ils vraiment ?", dérouler les 3-4 événements dans l'ordre chronologique en légende de chaque slide, terminer par le lien GitHub/dashboard.
- **Éléments qui attirent l'œil** : le jaune vif de Cividis (`#FFEA46`) sur fond sombre crée des points de focalisation naturels sur les pics thématiques — s'assurer qu'au moins un pic jaune vif soit visible dans la vignette de preview LinkedIn (le crop automatique de LinkedIn tronque parfois les images, à vérifier avant publication).
---
## 11. Checklist de réalisation
**Design**
- [ ] Vérifier les couleurs réelles de `_dark()` dans `app/app.py`
- [ ] Tester l'échelle Cividis sous un simulateur de daltonisme
- [ ] Réutiliser le fichier de style partagé `src/hansard_pm_nlp/portfolio_style.py` créé pour le Projet 1
**Développement**
- [ ] Charger la matrice document × topic déjà écrite dans `data/processed/` sans ré-exécuter `build_lda_topics.py`
- [ ] Reprendre telle quelle la règle de fusion T0+T1 déjà implémentée dans `dashboard_helpers.py`
- [ ] Charger les fenêtres de crise et dates de transition depuis `PHASE0_SCOPING.md` (pas de ressaisie manuelle)
- [ ] Agréger les poids par mois (moyenne pondérée)
- [ ] Écrire `plot_topic_heatmap()`, `plot_topic_streamgraph()`, `plot_crisis_zoom()` dans `src/hansard_pm_nlp/portfolio_viz.py`
**Visualisations**
- [ ] Heatmap principale (2400×1200 px, 200 dpi)
- [ ] Streamgraph ou small multiples secondaire (2000×1000 px)
- [ ] Zoom Covid 3 panneaux (1600×1000 px)
**Documentation**
- [ ] Rédiger `portfolio/02_topic_heatmap/README.md` selon la structure section 9
- [ ] Mentionner explicitement le choix LDA vs BERTopic et sa justification
**Captures**
- [ ] Exporter toutes les images en PNG @2x
- [ ] Vérifier la lisibilité des labels de topics une fois l'image réduite à la largeur mobile
**Publication GitHub**
- [ ] Lier `portfolio/02_topic_heatmap/` depuis le README racine
- [ ] (Optionnel) Produire le GIF de balayage temporel
**Publication LinkedIn**
- [ ] Recadrer en 1080×1350 pour chaque slide du carrousel
- [ ] Vérifier que la vignette de preview contient un pic jaune vif visible
- [ ] Rédiger le texte du post selon la narration section 10
---
## 12. Bonnes pratiques — erreurs à éviter
*(mêmes principes que `STYLE_DUEL.md`, complétés pour ce projet)*
- **Surcharge visuelle** : ne pas afficher les 14 topics d'origine sans fusion — respecter la fusion T0+T1 déjà validée, qui existe précisément pour éviter cette surcharge.
- **Trop de couleurs** : une seule échelle de couleur (Cividis) pour toute la heatmap — ne jamais colorer les lignes de topics individuellement en plus de la couleur de cellule, cela créerait un double encodage confus.
- **Mauvais contrastes** : le jaune vif de Cividis sur fond `#0E1117` est le point le plus contrasté du visuel — vérifier qu'aucun texte de label ne se retrouve superposé directement sur une cellule jaune vif sans halo/contour de lisibilité.
- **Polices inadaptées** : ne pas réduire les labels de topics en dessous de 9 pt pour "faire tenir" les 13 lignes — préférer raccourcir les libellés plutôt que réduire la police sous le seuil de lisibilité.
- **Graphiques difficiles à lire** : éviter un axe X avec une graduation mensuelle affichée (84 graduations sur 7 ans) — s'en tenir aux années comme repères visuels, cohérent avec la section 6.
- **Effets inutiles** : pas d'effet de "profondeur" ou d'ombre portée sur les cellules de heatmap ; le GIF de balayage temporel (section 9) reste optionnel et ne doit jamais devenir une animation complexe (fondu, zoom, particules) qui détournerait l'attention du message de données.
