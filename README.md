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
