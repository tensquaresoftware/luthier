# Luthier — Passe QA unique (v1.0.0 — Workspace)

**Version visée :** 1.0.0 (build release pre-publication)  
**Public :** testeur sans connaissance technique  
**Langue de l’app :** anglais (libellés cités tels qu’à l’écran)  
**Durée indicative :** 3 à 5 h sur les trois OS (ou 1 à 2 h si vous ne refaites que les régressions + fin du parcours Git)

> **Objectif :** une seule lecture, une seule passe. Cochez `- [ ]` → `- [x]` au fur et à mesure.  
> Ancienne checklist détaillée : [checklist-qa-manuelle.md](checklist-qa-manuelle.md) (archive détaillée pré-Workspace).

---

## Epic 9 — Fumée scaffold-only (v1.0.0 — 2026-07-04)

> **Changement produit :** plus de bouton **Open Project…**. Luthier génère le projet de démarrage une fois ; `.luthier.json` est **écrit seulement** (jamais relu dans le formulaire).

### S9.1 — Garde dossier non vide (session fraîche)

- [ ] Fermez et relancez Luthier (ou utilisez un chemin jamais généré).
- [ ] **Create New Project** → `TestLuthier` → **Generate Project** une première fois → succès.
- [ ] Fermez et relancez Luthier → même destination / nom → **Generate Project** → **bloqué** : modale + barre *This folder already exists and is not empty…*

### S9.2 — Session regenerate (même session)

- [ ] **Create New Project** → `TestRegen` → **Generate Project** → succès.
- [ ] Modifiez **Version** (ex. `2.0.0`) **sans** fermer Luthier.
- [ ] **Generate Project** → modale **Regenerate Project** (défaut **No**) → **Yes** → succès ; `.git/` préservé si présent.
- [ ] Vérifiez `CMakeLists.txt` / sources reflètent la nouvelle version.

### S9.3 — Accent couleur (Preferences uniquement)

- [ ] Onglet **Project** : **pas** de sélecteur de couleur d’accent.
- [ ] **Preferences** → **Luthier appearance** → autre preset → thème mis à jour sur tous les onglets.
- [ ] **Generate Project** → ouvrez `.luthier.json` : **pas** de clé `accentColor`.

### S9.4 — Plugin Characteristics (optionnel)

- [ ] **Plugin Type** **Instrument** → cochez **Plugin MIDI Output** → **Generate Project** → `CMakeLists.txt` reflète MIDI out (ex. Matrix-Control).

---

## Avant de commencer

### Sur chaque machine

- [x] Build **1.0.0** installé (même type sur les trois OS si possible : app autonome **ou** sources).
- [x] **JUCE** installé localement ; notez le chemin.

- macOS : /Volumes/Guillaume/Dev/SDKs/JUCE
- Windows : C:/Users/Guillaume/Dev/SDKs/JUCE
- Linux : /home/guillaume/Dev/SDKs/JUCE

- [x] Dossier de travail pour les projets tests (ex. Bureau, `Téléchargements`, ou dossier `été 2026` — pour valider les accents).
- [x] **Git** disponible pour la partie cross-plateforme.
- [x] Onglet **About** : version **1.0.0**, revision date **2026-07-01**.

### Fichiers de test suggérés

| Nom | Usage |
| --- | --- |
| `TestLuthier` | Projet local rapide par OS |
| `VoyageLuthier` | Projet Git partagé (dépôt : https://github.com/tensquaresoftware/voyage-luthier ou équivalent) |
| `profil-qa.json` | Export Preferences pour test d’import |

### Emplacement des configs Luthier

| OS | Dossier |
| --- | --- |
| macOS | `~/Library/Preferences/Luthier/` |
| Windows | `%LOCALAPPDATA%\Luthier\` |
| Linux | `~/.config/Luthier/` |

---

## Partie 1 — Régressions des correctifs (à faire sur **chaque** OS)

> Bloc court (~15 min/OS). Si un point échoue, notez-le dans la [grille](#grille-de-suivi) avant de continuer.

### R1 — Chemins avec accents et caractères spéciaux

- [x] **Preferences** → **Workspace** → **Destination folder** (ligne OS hôte) → **Choose…** → dossier dont le nom contient des **accents** (ex. `Téléchargements`, `été 2026`).
- [x] **Aucune** erreur rouge sous le champ ; badge **Saved** possible.
- [x] **Create New Project** → `TestLuthier` → **Generate Project** : succès sans dialogue de dossier intempestif (destination déjà valide).

### R2 — Messages et chemins affichés

- [x] **Generate Project** → barre de message : chemin avec des **`/`** (pas de `\` sous Windows).
- [x] ~~**Open Project…**~~ *(retiré v1.0.0 scaffold-only)* — voir [S9.1–S9.2](#epic-9--fumée-scaffold-only-v100--2026-07-04).
- [x] **Export Preferences…** → message avec le **chemin complet** du fichier exporté.

### R3 — Modales de confirmation

- [x] **Create New Project** après modification sans générer → modale : **No** à gauche, **Yes** à droite ; **No** est le bouton par défaut (surligné accent).

❌ GD : sous Windows, le bouton No est encore à droite et le bouton Yes à sa gauche (inversé par rapport à macOS et Linux)

- [x] **Generate Project** sur un dossier **non vide** (session fraîche ou après redémarrage app) → **bloqué** : modale + barre *This folder already exists and is not empty…*
- [x] **Generate Project** sur le **même chemin** après un Generate réussi **dans cette session** → modale **Regenerate Project** : **No** / **Yes**, défaut sur **No**.

❌ GD : sous Windows, le bouton No est encore à droite et le bouton Yes à sa gauche (inversé par rapport à macOS et Linux)

### R4 — Generate puis Create New Project

- [x] Créez un projet valide → **Generate Project** (succès).
- [x] **Create New Project** immédiatement après → **pas** de modale « unsaved changes ».

### R5 — Couleur d’erreur

- [x] Provoquez une erreur (champ invalide ou import JSON invalide) → texte rouge **bien visible** (plus pastel).

### R6 — Fichier preferences corrompu (une machine suffit, de préférence macOS)

- [x] Quittez Luthier.
- [x] Sauvegardez `preferences.json`, remplacez son contenu par `{`.
- [x] Relancez Luthier → **pas de plantage** ; warning dans la barre de message ; valeurs par défaut utilisables.
- [x] Restaurez votre sauvegarde de `preferences.json`.

### R7 — Linux uniquement : icône et fenêtre

*(Ignorez sur macOS / Windows.)*

- [ ] ❌ Lanceur / barre des tâches : icône **Luthier** (pas l’icône générique Qt). GD : ne fonctionne toujours pas > icône toujours générique (carré bris avec engrenage blanc). D'ailleurs, je ne sais pas comment fixer l'icône de l'app dans la barre des tâches, elle n'apparait pas ici après lancement (je connais mal Linux). Pour info, les icônes des apps fournies avec JUCE (ex : Projucer, AudioPluginHost, etc.) sont génériques également. 
- [ ] ❌ Redimensionnez et déplacez la fenêtre → fermez → rouvrez : position et taille **sensiblement** retrouvées (léger écart WM acceptable). GD : taille conservée mais position ramenée proche de (0;0). En revanche, la taille et la position de AudioPluginHost sont bien conservées entre eux lancements.

**Optionnel Linux — raccourci bureau :** dans `dist/Luthier/`, copiez `luthier.desktop` vers `~/.local/share/applications/`, éditez `Exec=` (chemin absolu vers l’exécutable `Luthier`) et `Icon=` (chemin vers `resources/icons/luthier.png` dans le bundle).

✅ Ça fonctionne ! C'est un peu laborieux à mettre en place mais j'ai maintenant l'icône de l'app dans la barre des tâches avec l'icone de Luthier. 👍

---

## Partie 2 — Fumée fonctionnelle (par OS)

> Parcours condensé. Répétez les étapes **A** (macOS), **B** (Windows), **C** (Linux).

**Date / build :** _______________

### 2A — macOS

- [ ] Lancement sans plantage ; onglets **Project**, **Preferences**, **Templates**, **About**.
- [ ] **Preferences** : fabricant, **Generate** codes, section **Workspace** (destination + JUCE pour les trois OS), couleur d’accent, export/import `profil-qa-macos.json`.
- [ ] **Create New Project** → `TestLuthier` → formats **VST3** + **AU** → **Generate Project** → dossier avec `CMakeLists.txt`, `.luthier.json`, `Source/`.
- [ ] **Session regenerate** (même session) : modifiez **Version** → **Generate Project** → confirmez **Regenerate Project** → changements visibles sur disque.
- [ ] *(Après redémarrage app)* **Generate Project** sur le même dossier → **bloqué** (dossier non vide).
- [ ] **Templates** : override `PluginProcessor.cpp` → nouveau projet → override visible → **Reset to default** → disparaît sur les nouveaux projets.
- [ ] *(Optionnel)* Build CMake du projet généré : OK.

### 2B — Windows

- [ ] Même parcours que 2A (formats **VST3** ; **AU** coché ne doit pas bloquer).
- [ ] Chemins affichés avec **`/`** dans l’UI et les messages.
- [ ] **Generate Project** sur `TestLuthier` dans un dépôt Git cloné : **pas** d’erreur WinError / accès refusé sur `.git`.
- [ ] *(Optionnel)* Build CMake : OK.

### 2C — Linux

- [ ] Même parcours que 2A (formats **VST3**).
- [ ] **Generate Project** avec destination `~/Desktop` (ou équivalent) : **pas** de sélecteur de dossier si le dossier existe.
- [ ] *(Optionnel)* Build CMake : OK.

---

## Partie 3 — Parcours cross-plateforme `VoyageLuthier`

> Si vous aviez déjà fait les étapes 2.2–2.4 de l’ancienne checklist, enchaînez directement sur **3.4**. Sinon, suivez tout le fil.

### 3.1 — Préparation

- [ ] Dépôt Git vide ou `voyage-luthier` prêt.
- [ ] JUCE installé sur **chaque** machine (chemins locaux différents).

### 3.2 — Machine 1 (ex. macOS) — Création

- [ ] **Create New Project** → `VoyageLuthier`, version `1.0.0`, **VST3** + **Standalone** (+ **AU** si Mac).
- [ ] Chemins **Artefacts** renseignés pour les trois OS.
- [ ] **Generate Project** ; `.luthier.json` présent.
- [ ] `git init` / commit / push.

### 3.3 — Machine 2 (ex. Windows)

- [ ] `git clone` → éditez **JUCE directory** Windows dans `.luthier.json` → **build CMake** (pas d’Open Luthier).
- [ ] Vérifiez metadata dans `.luthier.json` (version `1.1.0`, **Display name** `Voyage Cross QA Windows` si commitée sur machine 1) ; build + chargement VST3 depuis dossiers système et artefacts.
- [ ] *(Optionnel — nouvelle génération Luthier)* Dossier **vide** + **Create New Project** → regénérez le projet si vous devez changer les métadonnées côté Luthier ; sinon éditez `.luthier.json` / `CMakeLists.txt` à la main.

### 3.4 — Machine 3 (ex. Linux)

- [ ] `git pull` → éditez **JUCE directory** Linux dans `.luthier.json` → **build CMake**.
- [ ] Override **Templates** local (`// Linux QA` dans `PluginProcessor.h`) → **Save override** (s’applique aux **nouvelles** générations Luthier uniquement).
- [ ] Vérifiez metadata commitée (version `1.2.0`, **Preprocessor defs** `LINUX_QA=1` si présents dans le dépôt) ; build + chargement VST3.
- [ ] Commit projet (pas les templates locaux) + push si vous avez modifié des fichiers.

### 3.5 — Retour machine 1 (ex. macOS) — Finalisation

- [ ] `git pull`.
- [ ] Vérifiez `.luthier.json` dans `VoyageLuthier` cloné (metadata) ; **build CMake** sur Mac (chemins **Workspace** hôte adaptés dans `.luthier.json` si besoin).
- [ ] **Version** : `1.2.0` ; **Preprocessor defs** : `LINUX_QA=1` ; **Display name** : `Voyage Cross QA Final` — reflétés dans le dépôt ou édités manuellement.
- [ ] *(Pas de **Generate Project** sur le dossier cloné après redémarrage Luthier — dossier non vide ; build CMake ou session regenerate volontaire uniquement.)*

### 3.6 — Vérifications finales cross-plateforme

- [ ] Sur **les trois** OS : clone Git dernière révision → build CMake cohérent (chemins **Workspace** hôte adaptés manuellement si besoin).
- [ ] **Import Preferences…** depuis un JSON exporté sur une autre machine : **Preferences** mis à jour ; formulaire **Project** inchangé jusqu’à **Create New Project**.
- [ ] Conflit Git simulé (versions différentes sans pull) : merge → `.luthier.json` reflète le dépôt.
- [ ] **Aucun plantage** Luthier pendant toute la Partie 3.

### Récapitulatif VoyageLuthier

| Étape | Machine | Version | Display name |
| --- | --- | --- | --- |
| Création | | 1.0.0 | Voyage Cross QA macOS |
| Windows | | 1.1.0 | … Windows |
| Linux | | 1.2.0 | (inchangé ou …) |
| Final Mac | | 1.2.0 | … Final |

---

## Critères de réussite

La passe QA est **réussie** si :

- [ ] Partie 1 (régressions) : **tous** les points R1–R6 OK sur chaque OS concerné ; R7 OK sur Linux.
- [ ] Partie 2 : fumée OK sur macOS, Windows et Linux.
- [ ] Partie 3 : parcours Git complet (au minimum 3.5 si le reste était déjà fait).
- [ ] Aucun point **bloquant** ouvert dans la grille ci-dessous.

---

## Grille de suivi

| # | OS | Section | Que faisiez-vous ? | Attendu | Obtenu | Gravité |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | | | | | | bloquant / gênant / mineur |
| 2 | | | | | | |
| 3 | | | | | | |

**Gravité :** **bloquant** = impossible de continuer ; **gênant** = contournement pénible ; **mineur** = cosmétique.

---

## Références

- [Checklist QA détaillée (archive)](checklist-qa-manuelle.md)
- [Manuel utilisateur (FR)](../user/manuel-utilisateur.md)
- [User manual (EN)](../user/user-manual.md)
