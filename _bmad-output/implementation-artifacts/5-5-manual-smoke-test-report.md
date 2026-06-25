# Rapport de tests manuels — Story 5.5

**Create New Project (Full Reset + Dirty Guard)**

Complétez ce document pendant ou après vos essais UI, puis renvoyez-le (fichier rempli ou copier-coller dans le chat).

---

## 1. Informations de session

| Champ | Valeur |
|-------|--------|
| **Testeur** | Guillaume |
| **Date** | 2026-06-25 |
| **Story** | `5-5-create-new-project-full-reset-dirty-guard` |
| **Build testée** | ☐ Dev (`.venv/bin/python main.py`)<br />☑️ Packagée (`Dist/Luthier.app`) |
| **Commit / branche** | ??? |
| **OS** | macOS ___ (version ___) macOS Tahoe 26.5.1 |
| **Python** | 3.14.0 |
| **PySide6** | 6.11.1 |

**Chemin `preferences.json` utilisé pour le scénario 5 :**

```
/Users/Guillaume/Library/Preferences/Luthier/preferences.json
```

**Projet Luthier ouvert pour le scénario 2** (dossier avec `.luthier.json`) :

```
(chemin absolu ou « N/A » si non testé)
```

**Fichier JSON importé pour le scénario 4** (plugin type différent des prefs actuelles) :

```
(chemin absolu ou « N/A » si non testé)
```

---

## 2. Légende résultats

Pour chaque scénario, cochez **un** résultat global :

| Symbole | Signification |
|---------|---------------|
| **PASS** | Comportement conforme à l’attendu |
| **FAIL** | Comportement incorrect ou bloquant |
| **PARTIAL** | Globalement OK mais écart mineur (détailler) |
| **SKIP** | Non testé (préciser pourquoi) |

---

## 3. Scénarios

### Scénario 1 — Démarrage à froid, formulaire propre

**Objectif (AC1)** : sans modification, **Create New Project** ne doit **pas** afficher de dialog ; le formulaire reste cohérent avec les Preferences (identité vide, version `1.0.0`).

**Étapes**

1. Fermer Luthier, relancer (démarrage à froid).
2. Onglet **Project** : vérifier alignement avec **Preferences** (type, formats, destination, JUCE, etc.).
3. Vérifier : Project name / Display name vides ; version `1.0.0`.
4. Ne pas modifier** le formulaire.
5. Cliquer **Create New Project**.

**Attendu**

- [x] Aucune boîte de dialogue
- [x] Identité toujours vide ; version `1.0.0`
- [x] Autres champs inchangés (toujours seedés depuis prefs)
- [x] Message de statut acceptable (ex. *New project — defaults from Preferences.*)

**Résultat global :** ☑️ PASS ☐ FAIL ☐ PARTIAL ☐ SKIP

**Observations :**

```
Le message "New project — defaults from Preferences" apparaît bien. Le remplacer par "New project created — defaults from Preferences". En revanche, il s'affiche à gauche des boutons, dans la barre du bas. Il n'y a pas la place suffisante , cet emplacement n'est pas idéal. Prévoir une zone dédiée aux messages utilisateur, pourquoi pas dans une barre dédiée à placer au-dessus de la barre des boutons, dans un ton plus sombre (ex : #262F34) avec même bordure que la barre des boutons, deux fois moins épaisse que cette dernière. Les messages seront centrés dans la barre. Utiliser la couleur principale (orange) pour les afficher (au lieu de vert), utiliser le rouge pour les messages d'erreur.
```

---

### Scénario 2 — Open + édition + dialog No / Yes

**Objectif (AC2, AC4, AC5)** : après ouverture d’un projet et modification, le dialog apparaît ; **No** conserve les edits ; **Yes** re-seed depuis **Preferences**, pas depuis le projet ouvert.

**Étapes**

1. **Open Project…** → ouvrir un projet existant.
2. Noter le **Plugin type** (et un autre champ si utile) du projet ouvert.
3. Modifier le **Plugin type** (ex. Synth → Effect).
4. Cliquer **Create New Project**.

**Attendu (1er passage — No)**

- [x] Dialog affiché (*unsaved changes…*)
- [ ] Bouton par défaut = **No**
- [x] Clic **No** → formulaire **inchangé** (modification conservée)

5. [ ] Re-cliquer **Create New Project**, puis **Yes**.

**Attendu (2e passage — Yes)**

- [x] Project name / Display name vides ; version `1.0.0`
- [x] Plugin type (formats, compilation, artefacts…) = valeurs **Preferences**, **pas** le projet ouvert

**Résultat global :** ☑️ PASS ☐ FAIL ☐ PARTIAL ☐ SKIP

**Valeurs observées après Yes** (optionnel) :

| Champ | Attendu (prefs) | Observé |
|-------|-----------------|---------|
| Plugin type | Synthesizer | Synthesizer |
| Formats | AU/VST3/Standalone | AU/VST3/Standalone |
| Destination | /Users/Guillaume/Desktop | /Users/Guillaume/Desktop |

**Observations :**

```
Impossible de savoir si au premier passage le bouton No est celui par défaut, son apparence ne diffère pas de celle du bouton Yes, il aurait fallu qu'il soit orange pour lever l'ambiguité.
```

---

### Scénario 3 — Generate ne fige pas l’état « propre »

**Objectif (AC4, AC5)** : après **Generate Project**, si le formulaire a encore été modifié, **Create New Project** doit **toujours** avertir.

**Étapes**

1. Repartir d’un état propre (Create New Project ou relance app).
2. Renseigner un **Project name** valide + champs obligatoires.
3. Modifier un champ visible (ex. plugin type ou format).
4. Cliquer **Generate Project** (laisser le flux aller au bout ou jusqu’à génération effective).
5. **Sans autre modification**, cliquer **Create New Project**.

**Attendu**

- [x] Dialog de confirmation **affiché** (formulaire considéré « dirty »)

**Résultat global :** ☑️ PASS ☐ FAIL ☐ PARTIAL ☐ SKIP

**Observations :**

```
Même ambiguïté que précédemment concernant le bouton No par défaut.
```

---

### Scénario 4 — Import prefs vs Create New Project

**Objectif (AC1, AD-2)** : **Import Preferences…** ne change pas Project immédiatement ; **Create New Project** applique le profil importé.

**Étapes**

1. Noter le **Plugin type** sur l’onglet **Project**.
2. Onglet **Preferences** → **Import Preferences…** (JSON avec type **différent**).
3. Revenir sur **Project** **sans** Create New Project.

**Attendu (avant Create New Project)**

- [x] Onglet Project **inchangé** (ancien type toujours visible)

4. Cliquer **Create New Project** (accepter dialog si nécessaire).

**Attendu (après Create New Project)**

- [ ] Type / formats / etc. = profil **importé**

**Résultat global :** ☐ PASS ☑️ FAIL ☐ PARTIAL ☐ SKIP

| Étape | Plugin type attendu | Observé |
|-------|---------------------|---------|
| Après import, avant Create New | (ancien, inchangé) | |
| Après Create New Project | (importé) | |

**Observations :**

```
L'import d'un fichier de prefs semble ne pas affecter le Plugin Type dans Preferences.
```

---

### Scénario 5 — `preferences.json` non modifié par Create New Project

**Objectif (AC3, AD-5)** : **Create New Project** lit les prefs ; il ne les écrit pas.

**Étapes**

1. Noter **mtime** (date/heure de modification) de `preferences.json` :
   
   ```
   mtime avant : 25/06/2026 à 21:52
   ```
2. Onglet **Project** → cliquer **Create New Project** (1–2 fois, avec ou sans dialog).
3. Re-noter le **mtime** :
   ```
   mtime après : 25/06/2026 à 21:52
   ```

**Attendu**

- [x] `mtime` **identique** (fichier non réécrit par Create New Project seul)

**Résultat global :** ☑️ PASS ☐ FAIL ☐ PARTIAL ☐ SKIP

**Observations :**

```
```

---

## 4. Synthèse

| # | Scénario | Résultat |
|---|----------|----------|
| 1 | Cold start, formulaire propre | |
| 2 | Open + dialog No/Yes | |
| 3 | Generate puis dirty guard | |
| 4 | Import prefs puis Create New | |
| 5 | mtime `preferences.json` | |

**Verdict global :** ☐ Tous PASS → story prête pour `done` ☐ Échecs / PARTIAL → corrections ou re-test requis

**Bugs / écarts relevés** (liste numérotée, du plus bloquant au plus mineur) :

1.
2.
3.

**Captures d’écran / enregistrements** (chemins ou liens, si any) :

```
```

---

## 5. Sign-off testeur

| | |
|--|--|
| **Nom** | Guillaume |
| **Date** | 2026-06-25 |
| **Recommandation** | ☐ Merger / marquer story done ☐ Retour dev ☑️ Re-test après fix |

**Commentaire libre :**

```
La taille et la position de la fenêtre ne sont pas persistées. À l'ouverture de l'app, la fenêtre est placée en (0;0).
```

---

*Généré pour Story 5.5 — `_bmad-output/implementation-artifacts/5-5-create-new-project-full-reset-dirty-guard.md`*
