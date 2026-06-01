# Espaces projectifs, corps finis et jeu Dobble

Ce dépôt contient un petit projet Python pour produire les résultats du TIPE - L3 Mathématiques université de lorraine.

Le notebook contient des figures autour du thème :

- espaces projectifs ;
- corps finis ;
- plan de Fano ;
- lien combinatoire avec le jeu Dobble.

## Contenu

- `dobble_utils.py` : logique mathématique et combinatoire.
- `plot_utils.py` : génération des figures et export des sorties.
- `cours_projectif_dobble.ipynb` : notebook de présentation.

## Sorties générées

Les sorties sont écrites dans le dossier `exports/` :

- `exports/figures/svg/` : figures vectorielles au format SVG ;
- `exports/logs/` : résumés texte et traces associées.

## Organisation du code

Le projet est séparé en deux parties :

- `dobble_utils.py` ne contient que les constructions mathématiques ;
- `plot_utils.py` contient uniquement le code de tracé, d’affichage et d’export.

###simulation du dobble
Dobble — 2 robots théoriques : une simulation Python/pygame du jeu Dobble (Spot It!) où deux robots s'affrontent automatiquement pour repérer le symbole commun entre leur carte et une carte centrale partagée, sur fond noir avec des symboles en emojis. Le deck est généré via un plan projectif d'ordre 7 (57 cartes, 8 symboles par carte), ce qui garantit que deux cartes partagent toujours exactement un symbole. Chaque robot reçoit un temps de réaction aléatoire par manche : le plus rapide marque le point et le symbole trouvé clignote. Installation : pip install pygame puis python dobble_robots.py (commandes : ESPACE pause, R reset, ÉCHAP quitter ; sous Linux, sudo apt install fonts-noto-color-emoji si les emojis ne s'affichent pas en couleur).
