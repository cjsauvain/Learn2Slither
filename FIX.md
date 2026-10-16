# FIX.md

Ce qu'il reste à faire pour être conforme au sujet (partie obligatoire et
bonus, hors visuel). La gestion d'erreurs est traitée à part.

## Bloquant

- [ ] **Ajouter les modèles à git.** Ils ne sont plus ignorés, mais ils
      apparaissent encore comme non suivis (`?? models/`). Seul le dépôt
      git est évalué : sans eux, le rendu n'a aucun modèle.
      ```bash
      git add models/
      git commit -m "feat: add trained models"
      ```
- [ ] **Norme flake8** (obligatoire pour du Python) : 17 violations avec
      `python3 -m flake8 src`.
  - [ ] `agent_snake.py` : lignes 30, 54, 101, 114, 118, 125 (E501)
  - [ ] `agent_snake.py` : ligne 72 (E731) : remplacer le `lambda`
        assigné à `default` par une vraie fonction `def`
  - [ ] `board.py` : ligne 61 (E501)
  - [ ] `main.py` : lignes 85, 99, 118, 120 (E501)
  - [ ] `parsing.py` : lignes 33, 37, 45, 119 (E501)
  - [ ] `renderer.py` : ligne 102 (E501)

  Vérifier à la fin : `python3 -m flake8 src` ne doit rien afficher.

## À vérifier avant le rendu

- [ ] **Module interpréteur.** Le diagramme du sujet (partie 6) montre
      trois modules : environnement, interpréteur (état et récompense) et
      agent. Aujourd'hui l'interpréteur est dans `Board` (`get_state` et
      `REWARDS`). Pas bloquant, mais un correcteur peut le demander :
      envisager un `interpreter.py` qui contient `get_state` et le calcul
      des récompenses.
- [ ] **README** : revérifier qu'il décrit bien l'état actuel (état
      binaire, learning rate et epsilon décroissants, plafond de pas en
      évaluation) et que les commandes données fonctionnent.
