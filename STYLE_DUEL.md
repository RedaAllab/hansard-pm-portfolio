# STYLE_DUEL.md — Spécification de conception : « Le duel de style »
> Ce document est une spécification complète, autosuffisante : tout ce qu'il faut pour construire le visuel et le README sans avoir à prendre de nouvelle décision de design est défini ici.
---
## 0. Cohérence avec l'identité déjà présente dans le dépôt
Avant de proposer quoi que ce soit de nouveau, voici ce que la documentation du dépôt permet de vérifier :
- **Thème déjà fixé** : `.streamlit/config.toml` pin `theme.base = "dark"` pour le dashboard. Le README ne mentionne aucune surcharge de couleurs au-delà de ce pin — le dashboard utilise donc très probablement la palette sombre **par défaut** de Streamlit (`backgroundColor #0E1117`, `secondaryBackgroundColor #262730`, `textColor #FAFAFA`), sauf personnalisation non documentée dans `app.py`. **Point à vérifier toi-même avant de démarrer** : ouvre `app/app.py`, cherche la fonction `_dark()` mentionnée dans le README, et si elle définit des couleurs différentes de celles ci-dessous, aligne la palette de ce document dessus — sinon, les valeurs ci-dessous sont un choix sûr car elles reprennent exactement les valeurs par défaut du thème déjà activé.
- **Convention de nommage des documents racine** : `README.md`, `WRITEUP.md` (tout en majuscules, sans tiret) — `STYLE_DUEL.md` suit exactement cette convention, aucun changement nécessaire.
- **Convention des notebooks** : préfixe numéroté + snake_case (`01_corpus_overview.ipynb`...) — le nouveau notebook doit donc s'appeler `notebooks/portfolio_01_style_duel.ipynb`.
- **Style de documentation** : le `WRITEUP.md` est rédigé pour un lecteur "technique mais non spécialiste" ; ce nouveau document doit descendre encore d'un cran, pour un lecteur **non technique** (recruteur, LinkedIn).
- **Aucune charte graphique explicite (logo, palette documentée, guide de style)** n'existe dans le dépôt au-delà du thème sombre Streamlit — ce document crée donc la première charte graphique formelle du projet, en cohérence avec ce qui existe déjà plutôt qu'en rupture.
---
## 1. Vision du projet
- **Objectif** : montrer, en un seul coup d'œil, que chaque Premier ministre britannique a un style oratoire reconnaissable — et que cette affirmation n'est pas une impression, mais un résultat déjà validé par un modèle de classification (91,5–93,2 % d'exactitude).
- **Public cible** : recruteur ou manager Data qui scrolle un profil GitHub/LinkedIn en quelques secondes ; aucune connaissance en NLP ou en statistiques ne doit être requise pour comprendre le message.
- **Message clé** : *"Le style de langage à lui seul suffit à identifier qui parle — et voici les 6 traits qui le prouvent."*
- **Storytelling** : on part d'une question universelle ("peut-on reconnaître quelqu'un juste à sa façon de parler ?"), on répond avec un visuel immédiat (le radar), puis on ancre la réponse dans un chiffre validé (l'accuracy du classifieur) pour transformer une intuition en preuve.
- **Ce que le visiteur doit comprendre en moins de 10 secondes** : "il existe 4 signatures de style distinctes, une par Premier ministre, et ce n'est pas une coïncidence — c'est mesurable."
---
## 2. Direction artistique
- **Style retenu : "data journalism sobre"**, à mi-chemin entre le Financial Times/The Economist (rigueur, sérieux, données au centre) et un dashboard produit moderne (contraste net, hiérarchie claire). Justification : le public cible (recruteurs Data) reconnaît immédiatement ce registre comme "professionnel", sans tomber dans l'esthétique "corporate PowerPoint" (trop générique) ni "dashboard BI surchargé" (trop dense pour du non-technique).
- **Ambiance recherchée** : sérieuse, factuelle, un peu "presse économique britannique" (cohérent avec le sujet — Parlement de Westminster).
- **Niveau de sobriété** : élevé. Un seul visuel principal par page/post, peu d'éléments décoratifs, aucune icône superflue.
- **Niveau d'interactivité** : nul pour les livrables portfolio (images statiques PNG) — l'interactivité existe déjà via le dashboard Streamlit en ligne, il ne faut pas la dupliquer. Un simple lien "Explorer en interactif →" suffit.
- **Inspirations visuelles** : graphiques du *Financial Times* (fond sombre pour les visuels "long format", séries de couleurs discrètes, titres en une phrase complète plutôt qu'un label sec) ; *Our World in Data* pour la clarté des légendes et l'absence de chrome inutile ; l'esthétique native de Streamlit en mode sombre, pour la continuité avec le dashboard existant.
---
## 3. Palette de couleurs
| Couleur | Rôle | HEX | Pourquoi |
|---|---|---|---|
| Fond | fond des figures et de l'image héros | `#0E1117` | reprend la valeur par défaut du thème sombre Streamlit déjà activé (`theme.base = "dark"`) — continuité visuelle avec le dashboard |
| Cartes / surfaces | encarts, légende, callout box | `#262730` | `secondaryBackgroundColor` par défaut de Streamlit en mode sombre — même famille que le fond |
| Texte principal | titres, labels importants | `#FAFAFA` | contraste ~18:1 sur fond `#0E1117`, largement au-dessus du seuil WCAG AAA (7:1) |
| Texte secondaire | légendes, notes de bas de page | `#9CA3AF` | gris moyen, hiérarchise sans nuire à la lisibilité (contraste > 4,5:1) |
| Grille / bordures | axes discrets du radar | `#3A3D46` | assez visible pour structurer, assez discret pour ne pas distraire |
| Principale / accent de marque | liens, soulignement de titre, badges | `#22D3EE` | couleur signature du projet, neutre politiquement (ni bleu conservateur ni rouge travailliste), cohérente sur tous les visuels |
| Secondaire | éléments de support (axes, texte technique) | `#7C89A6` | bleu-gris neutre, discret |
| Positive *(réservée, non utilisée dans ce projet)* | tendance à la hausse dans de futurs graphiques | `#4A90D9` | bleu plutôt que vert — évite la confusion rouge/vert la plus fréquente chez les daltoniens |
| Négative *(réservée, non utilisée dans ce projet)* | tendance à la baisse | `#D9764A` | orange terracotta, forme une paire bleu/orange lisible pour les 3 types courants de daltonisme |
**Palette catégorielle dédiée aux 4 Premiers ministres** (utilisée uniquement pour le radar — ne jamais la mélanger avec la palette positive/négative ci-dessus dans un même graphique) — issue de la palette **Okabe-Ito**, référence standard pour l'accessibilité daltonisme :
| PM | HEX | Traitement |
|---|---|---|
| Boris Johnson | `#E69F00` (orange) | ligne pleine |
| Liz Truss | `#56B4E9` (bleu ciel) | **ligne pointillée** + astérisque en légende ("49 jours de mandat — à lire avec prudence") |
| Rishi Sunak | `#009E73` (vert bleuté) | ligne pleine |
| Keir Starmer | `#CC79A7` (violet rosé) | ligne pleine |
**Mode clair** : ce projet est pensé fond sombre uniquement (cohérence dashboard + lisibilité maximale pour un radar chart, qui perd en clarté sur fond blanc à cause du remplissage semi-transparent). **Ne pas** produire de version claire séparée — c'est une décision de sobriété, pas un oubli.
**Daltonisme** : la combinaison Okabe-Ito + fond sombre a été spécifiquement conçue pour rester distinguable en deutéranopie, protanopie et tritanopie. Vérifier avec un simulateur (ex. Coblis, gratuit en ligne) avant publication finale.
---
## 4. Typographie
> ⚠️ **Point pratique important** : GitHub ne permet pas de charger des polices personnalisées dans le corps d'un README (le Markdown GitHub s'affiche toujours avec la police système de GitHub, non modifiable). Les choix de police ci-dessous s'appliquent donc à **deux endroits précis seulement** : le texte intégré directement dans les images de graphiques (Matplotlib/Plotly) et, si tu produis une image "bannière" ou un visuel de carrousel LinkedIn (via Pillow ou export HTML→image), le texte de cette image. Le texte du README lui-même reste en police système GitHub — c'est normal, ne pas chercher à le contourner.
| Usage | Police (Google Fonts) | Poids | Où l'utiliser |
|---|---|---|---|
| Titre principal (suptitle du graphique, bannière) | **Lora** | 700 (Bold) | titre du radar, titre de la bannière README |
| Sous-titres | **Inter** | 600 (SemiBold) | sous-titre du graphique, en-têtes de section dans les images de carrousel |
| Texte courant / légendes | **Inter** | 400 (Regular) | légende des 4 PM, notes de source |
| Chiffres mis en avant | **IBM Plex Mono** | 500 (Medium) | le chiffre "91,5 %" affiché en gros dans le visuel secondaire — l'effet "chasse fixe" donne un rendu "précision de données" et évite toute ambiguïté entre 1/l/I |
**Pourquoi ce trio fonctionne** : Lora (serif éditorial) pour le titre apporte le sérieux "presse économique" ; Inter (sans-serif très lisible, standard de facto des interfaces de données) pour tout le reste garde une lecture rapide ; IBM Plex Mono réservé aux chiffres crée un signal visuel clair "ceci est une donnée mesurée", sans multiplier les familles de police (3 maximum, règle de sobriété typographique).
---
## 5. Mise en page
- **Disposition générale** : une image héros unique (le radar), pas de grille multi-graphiques dans la même image — la clarté prime sur l'exhaustivité.
- **Marges** : 60 px minimum de marge intérieure autour du radar dans le canevas de la figure, pour que rien ne touche les bords.
- **Espacement** : 24 px entre le sous-titre et le graphique, 32 px entre le graphique et la légende, 16 px entre la légende et la note de source.
- **Tailles de titre** : suptitle 20 pt, sous-titre 12 pt, labels d'axes du radar 11 pt, légende 11 pt, note de source 9 pt.
- **Hiérarchie visuelle** : titre > radar > légende > note de source, dans cet ordre de poids visuel (taille + contraste de couleur).
- **Largeur optimale** : image héros exportée en 1600×1600 px (carré — un radar chart se lit mieux en format carré), affichée à ~800×800 px dans le README (GitHub redimensionne automatiquement).
- **Équilibre texte/graphique** : dans le README, ne jamais faire suivre le radar de plus de 3 phrases avant la prochaine sous-partie — le visuel doit rester l'élément dominant de la page.
### Schéma ASCII — figure principale (radar)
```
┌──────────────────────────────────────────────┐
│         LE DUEL DE STYLE                      │  Lora 20pt bold, #FAFAFA
│  Ce que 6 traits stylométriques révèlent       │  Inter 12pt, #9CA3AF
│                                                │
│                ╭─────────────╮                │
│             ╱──┤             ├──╲             │
│           ╱    │             │    ╲           │
│          │     │   RADAR     │     │          │  6 axes, grille #3A3D46
│           ╲    │  (6 axes)   │    ╱           │
│             ╲──┤             ├──╱             │
│                ╰─────────────╯                │
│                                                │
│   ● Johnson  ┄ Truss*  ● Sunak  ● Starmer      │  légende horizontale, Inter 11pt
│   * 49 jours de mandat — à lire avec prudence  │  Inter 9pt, #9CA3AF
│                                                │
│         Source : Hansard API · hansard-pm-nlp  │  Inter 9pt, #7C89A6
└──────────────────────────────────────────────┘
   fond #0E1117
```
### Schéma ASCII — page README
```
┌─────────────────────────────────────────┐
│ [Bannière 1600×400, titre + badges]      │
├─────────────────────────────────────────┤
│ # Le duel de style                       │
│ Accroche en 1 phrase                     │
├─────────────────────────────────────────┤
│ [IMAGE HÉROS : radar_main.png]           │
├─────────────────────────────────────────┤
│ ## Le message en 3 phrases               │
├─────────────────────────────────────────┤
│ ## Comment ce visuel a été construit     │
│  - 4 puces + lien phase6_classifier_report.md │
├─────────────────────────────────────────┤
│ ## Ce que ça révèle (bullets)            │
├─────────────────────────────────────────┤
│ [img secondaire 1]  [img secondaire 2]   │
├─────────────────────────────────────────┤
│ ## Limites                               │
├─────────────────────────────────────────┤
│ ## Reproduire ce visuel (commande)       │
├─────────────────────────────────────────┤
│ Liens : dashboard live · write-up · LinkedIn │
└─────────────────────────────────────────┘
```
---
## 6. Design des visualisations
### Visuel principal — Radar chart
- **Type** : radar/spider chart, 6 axes, 4 séries superposées (une par PM), remplissage semi-transparent (alpha 0,15) sous chaque ligne.
- **Dimensions** : figure Matplotlib 8×8 pouces, export à 200 dpi → 1600×1600 px.
- **Couleurs** : palette catégorielle PM définie en section 3 ; fond `#0E1117` ; grille radiale `#3A3D46`.
- **Taille des polices** : titre 20 pt, labels des 6 axes 11 pt (`#FAFAFA`), graduations radiales 8 pt (`#9CA3AF`, à afficher discrètement, 3 graduations maximum).
- **Style des axes** : les 6 axes correspondent aux 6 traits déjà identifiés comme les plus discriminants par le classifieur H1 (MTLD, lisibilité Flesch-Kincaid, `hedge_rate`, certitude nette, `pos_INTJ`, fréquence de "not") — valeurs normalisées 0–1 (min-max sur les 4 PM), pas d'échelle brute affichée (elle n'aurait pas de sens pour un lecteur non technique).
- **Style de la grille** : radiale uniquement (cercles concentriques), 3 niveaux, épaisseur 0,5 pt, aucune grille angulaire supplémentaire.
- **Annotations** : un seul astérisque sur la ligne Truss, renvoyant à la note de bas de légende — aucune autre annotation dans le corps du graphique (garder le radar "propre").
- **Légende** : horizontale, sous le graphique, pas dans un coin (les légendes en coin de radar chevauchent souvent les données).
- **Animation** : aucune — export statique uniquement, cohérent avec le choix "sobre" de la section 2.
*Pourquoi ces choix améliorent la lecture* : limiter à 6 axes évite la saturation visuelle typique des radar charts à 10+ axes (illisibles) ; normaliser 0–1 permet une comparaison directe entre 6 métriques d'échelles très différentes (un score de lisibilité et un taux de hedging n'ont pas la même unité) ; le remplissage semi-transparent laisse voir les zones de chevauchement entre PM, renforçant visuellement le message "les styles se distinguent mais ne sont jamais totalement opposés."
### Visuel secondaire 1 — Importances de permutation (bar chart)
- **Type** : bar chart horizontal, 6 barres (les mêmes 6 traits que le radar, dans le même ordre) — sert à justifier pourquoi ces 6 axes ont été choisis.
- **Dimensions** : 8×5 pouces, 200 dpi.
- **Couleurs** : une seule couleur (`#22D3EE`, l'accent de marque — volontairement différente des couleurs PM pour signaler "ceci concerne le modèle, pas un PM en particulier").
- **Police** : titre 16 pt, labels 11 pt, valeurs affichées en bout de barre en `IBM Plex Mono` 10 pt.
- **Grille** : verticale légère uniquement (`#3A3D46`), spines haut/droite supprimées.
- **Légende** : aucune (une seule série).
### Visuel secondaire 2 — Matrice de confusion simplifiée
- **Type** : heatmap 3×3 (Truss exclue, cohérent avec le dépôt), valeurs en pourcentage.
- **Dimensions** : 6×6 pouces, 200 dpi, carré.
- **Couleurs** : dégradé séquentiel `Cividis` (colorblind-safe), diagonale mise en évidence par un contour `#22D3EE` de 2 pt.
- **Police** : valeurs en cellule `IBM Plex Mono` 14 pt, labels d'axes `Inter` 11 pt.
- **Annotation** : une seule phrase sous le graphique en langage courant ("Le modèle retrouve le bon Premier ministre dans 9 cas sur 10"), pas de jargon "accuracy/precision/recall" dans l'image elle-même (réservé au README).
---
## 7. Ergonomie
- **Lisibilité** : taille de police minimale 9 pt dans toute image exportée (en dessous, illisible une fois l'image redimensionnée par GitHub/LinkedIn).
- **Contraste** : tout texte sur fond `#0E1117` doit atteindre au moins un ratio de 4,5:1 (WCAG AA) ; les couleurs `#FAFAFA` et `#9CA3AF` définies en section 3 respectent cette contrainte, ne pas les assombrir davantage.
- **Accessibilité** : palette Okabe-Ito + vérification par simulateur de daltonisme avant publication (voir section 3) ; ne jamais coder une information uniquement par la couleur — le style de ligne (plein/pointillé pour Truss) double toujours l'information couleur.
- **Simplicité** : un seul message par image ; si une idée nécessite un deuxième graphique, c'est qu'elle doit devenir un visuel secondaire, pas un ajout au visuel principal.
- **Charge cognitive** : maximum 4 séries de couleur simultanées dans un même graphique (ici : 4 PM) — au-delà, la lecture devient un exercice de décodage plutôt qu'une lecture immédiate.
- **Cohérence graphique** : mêmes couleurs PM, même typographie, même style de grille sur les 3 images de ce projet ET sur celles du projet `THEMATIC_HEATMAP.md` (palette catégorielle PM partagée entre les deux projets).
- **Responsive** : non applicable (images statiques) — mais toujours exporter en haute résolution (200 dpi minimum) pour rester net sur mobile, où la majorité du trafic LinkedIn est consultée.
---
## 8. Icônes et illustrations
- **Bibliothèque recommandée** : **Lucide** (lucide.dev) — open-source, licence MIT, style trait fin cohérent avec l'esthétique "sobre" recherchée, disponible en SVG téléchargeable individuellement (pas besoin de framework web).
- **Pictogrammes adaptés** : une icône "radar" ou "target" en en-tête du README (section titre) ; une icône "git-branch" ou "database" à côté du lien vers le dépôt d'extraction ; icônes "github" et "linkedin" pour les badges de fin de README (via shields.io, voir section 9).
- **Où les placer** : uniquement dans le README (jamais dans les images de graphique elles-mêmes, qui doivent rester 100 % données) — en préfixe de titre de section ou dans la ligne de badges.
- **À éviter** : emoji décoratifs en excès (🚀✨🔥…) — au maximum 1 emoji sobre en titre principal si souhaité, aucun dans les sous-titres ; cliparts, mascottes, icônes en dégradé/skeuomorphes qui contrediraient le registre "presse économique" choisi en section 2.
---
## 9. README GitHub
**Structure recommandée pour `portfolio/01_style_duel/README.md`** :
1. **Bannière** (1600×400 px, fond `#0E1117`, titre "Le duel de style" en Lora, sous-titre en Inter) — image statique simple, pas besoin d'animation.
2. **Badges** (via shields.io) : version Python, lien "Dashboard live", lien vers le dépôt principal `hansard-pm-nlp`, badge de licence si applicable.
3. **Accroche** : une phrase, gras, reprenant le message clé de la section 1.
4. **Image héros** : `radar_main.png`, pleine largeur.
5. **Sommaire** (ancres Markdown) si le README dépasse ~150 lignes — sinon superflu pour un document de cette taille.
6. **Section "Le message en 3 phrases"**.
7. **Section "Comment ce visuel a été construit"** : 3-4 puces vulgarisées, avec lien explicite vers `phase6_classifier_report.md` pour le lecteur qui veut la preuve technique complète.
8. **Section "Ce que ça révèle"** : bullets.
9. **Galerie des visuels secondaires** (les 2 images côte à côte si le rendu Markdown le permet, sinon l'une sous l'autre).
10. **Section "Limites"** — honnêteté méthodologique (Truss, portée du style vs contenu).
11. **Section "Reproduire ce visuel"** — une commande unique (`jupyter nbconvert --execute notebooks/portfolio_01_style_duel.ipynb`).
12. **Conclusion / liens** : dashboard interactif, write-up complet, post LinkedIn.
**GIF** : non nécessaire pour ce projet (le radar est un visuel statique par nature) — réserver le budget GIF au projet `THEMATIC_HEATMAP.md`, où l'évolution temporelle s'y prête mieux.
---
## 10. Publication LinkedIn
- **Images à produire** : réutiliser directement `radar_main.png` (déjà au format carré 1600×1600, idéal pour un post LinkedIn) + une version recadrée 1080×1350 (portrait) du visuel d'importances de permutation pour un éventuel second slide.
- **Format** : **image unique** en premier post (le radar seul est suffisamment fort pour ne pas nécessiter de carrousel) ; si carrousel souhaité (2-3 slides), ordre : (1) radar seul avec accroche en légende de post, (2) bar chart des importances avec la question "pourquoi ces 6 traits ?", (3) matrice de confusion simplifiée avec le chiffre clé en gros.
- **Narration du post texte** : commencer par une question ("Peut-on reconnaître un Premier ministre juste à sa façon de parler ?"), donner la réponse en une phrase, mentionner le chiffre (91,5 % / 93,2 %), terminer par un lien vers le dépôt GitHub et le dashboard live.
- **Éléments qui attirent l'œil** : le contraste du fond sombre `#0E1117` contre le fil LinkedIn (très majoritairement blanc/clair) crée un arrêt visuel naturel dans le scroll — argument supplémentaire en faveur du thème sombre choisi en section 3.
---
## 11. Checklist de réalisation
**Design**
- [ ] Vérifier les couleurs réelles de `_dark()` dans `app/app.py` et ajuster la palette si besoin
- [ ] Simuler la palette PM sous un outil de daltonisme (Coblis ou équivalent)
- [ ] Créer un fichier de style partagé (`src/hansard_pm_nlp/portfolio_style.py`) avec les constantes de couleur/police définies ici
**Développement**
- [ ] Charger les artefacts Phase 3/4/6 sans ré-exécuter aucun script `build_*.py`
- [ ] Réutiliser la logique de normalisation déjà présente dans `dashboard_helpers.py`
- [ ] Écrire `plot_style_radar()` et `plot_feature_importance_bar()` dans `src/hansard_pm_nlp/portfolio_viz.py`
**Visualisations**
- [ ] Radar principal (1600×1600 px, 200 dpi)
- [ ] Bar chart des importances (1600×1000 px)
- [ ] Matrice de confusion simplifiée (1200×1200 px)
**Documentation**
- [ ] Rédiger `portfolio/01_style_duel/README.md` selon la structure section 9
- [ ] Rédiger `notebooks/portfolio_01_style_duel.ipynb` (narratif, sorties committées)
**Captures**
- [ ] Exporter toutes les images en PNG @2x (200 dpi minimum)
- [ ] Vérifier le rendu réel dans un README GitHub (mode clair et sombre du viewer)
**Publication GitHub**
- [ ] Lier `portfolio/01_style_duel/` depuis le README racine
- [ ] Vérifier que le notebook s'exécute proprement de bout en bout
**Publication LinkedIn**
- [ ] Recadrer les visuels aux formats LinkedIn (1080×1080 ou 1080×1350)
- [ ] Rédiger le texte du post selon la narration section 10
---
## 12. Bonnes pratiques — erreurs à éviter
- **Surcharge visuelle** : ne pas ajouter d'annotations, flèches ou zones de texte dans le radar au-delà de ce qui est spécifié en section 6 — chaque élément supplémentaire dilue le message principal.
- **Trop de couleurs** : ne jamais dépasser les 4 couleurs PM + 1 couleur d'accent dans une même image ; ne jamais mélanger la palette catégorielle PM avec la palette sémantique positive/négative.
- **Mauvais contrastes** : ne pas utiliser `#9CA3AF` sur fond `#262730` pour du texte important (contraste insuffisant) — réserver ce gris aux fonds `#0E1117` uniquement.
- **Polices inadaptées** : éviter les polices "manuscrites" ou "amusantes" qui contrediraient le registre sobre choisi ; ne jamais utiliser plus de 3 familles de police dans un même livrable.
- **Graphiques difficiles à lire** : un radar à plus de 6-7 axes devient illisible — ne pas céder à la tentation d'ajouter d'autres métriques stylométriques disponibles juste parce qu'elles existent.
- **Effets inutiles** : pas d'ombres portées, de dégradés de fond, de bordures 3D — ces effets datent visuellement une image et contredisent l'esthétique "presse économique" recherchée.
