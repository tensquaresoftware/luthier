# Luthier — Passe QA unique (post-correctifs 1.0.1)

**Version visée :** 1.0.1 (build contenant les correctifs QA)  
**Public :** testeur sans connaissance technique  
**Langue de l’app :** anglais (libellés cités tels qu’à l’écran)  
**Durée indicative :** 3 à 5 h sur les trois OS (ou 1 à 2 h si vous ne refaites que les régressions + fin du parcours Git)

> **Objectif :** une seule lecture, une seule passe. Cochez `- [ ]` → `- [x]` au fur et à mesure.  
> Ancienne checklist détaillée : [checklist-qa-manuelle.md](checklist-qa-manuelle.md) (archive des tests 1.0.0).

---

## Avant de commencer

### Sur chaque machine

- [ ] Build **1.0.1** installé (même type sur les trois OS si possible : app autonome **ou** sources).
- [ ] **JUCE** installé localement ; notez le chemin.
- [ ] Dossier de travail pour les projets tests (ex. Bureau, `Téléchargements`, ou dossier `été 2026` — pour valider les accents).
- [ ] **Git** disponible pour la partie cross-plateforme.
- [ ] Onglet **About** : version **1.0.1** (ou votre numéro de build).

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

- [ ] **Preferences** → **Destination folder** → **Choose…** → dossier dont le nom contient des **accents** (ex. `Téléchargements`, `été 2026`).
- [ ] **Aucune** erreur rouge sous le champ ; badge **Saved** possible.
- [ ] **Create New Project** → `TestLuthier` → **Generate Project** : succès sans dialogue de dossier intempestif (destination déjà valide).

### R2 — Messages et chemins affichés

- [ ] **Generate Project** → barre de message : chemin avec des **`/`** (pas de `\` sous Windows).
- [ ] **Open Project…** sur un dossier **vide** ou non-Luthier → modale : **Not a Luthier project** (plus « JUCE plugin project »).
- [ ] **Export Preferences…** → message avec le **chemin complet** du fichier exporté.

### R3 — Modales de confirmation

- [ ] **Create New Project** après modification sans générer → modale : **No** à gauche, **Yes** à droite ; **No** est le bouton par défaut (surligné accent).
- [ ] **Generate Project** sur un dossier existant → modale d’écrasement : même ordre **No** / **Yes**, défaut sur **No**.

### R4 — Generate puis Create New Project

- [ ] Créez un projet valide → **Generate Project** (succès).
- [ ] **Create New Project** immédiatement après → **pas** de modale « unsaved changes ».

### R5 — Couleur d’erreur

- [ ] Provoquez une erreur (champ invalide ou import JSON invalide) → texte rouge **bien visible** (plus pastel).

### R6 — Fichier preferences corrompu (une machine suffit, de préférence macOS)

- [ ] Quittez Luthier.
- [ ] Sauvegardez `preferences.json`, remplacez son contenu par `{`.
- [ ] Relancez Luthier → **pas de plantage** ; warning dans la barre de message ; valeurs par défaut utilisables.
- [ ] Restaurez votre sauvegarde de `preferences.json`.

### R7 — Linux uniquement : icône et fenêtre

*(Ignorez sur macOS / Windows.)*

- [ ] Lanceur / barre des tâches : icône **Luthier** (pas l’icône générique Qt).
- [ ] Redimensionnez et déplacez la fenêtre → fermez → rouvrez : position et taille **sensiblement** retrouvées (léger écart WM acceptable).

**Optionnel Linux — raccourci bureau :** dans `dist/Luthier/`, copiez `luthier.desktop` vers `~/.local/share/applications/`, éditez `Exec=` (chemin absolu vers l’exécutable `Luthier`) et `Icon=` (chemin vers `resources/icons/luthier.png` dans le bundle).

---

## Partie 2 — Fumée fonctionnelle (par OS)

> Parcours condensé. Répétez les étapes **A** (macOS), **B** (Windows), **C** (Linux).

**Date / build :** _______________

### 2A — macOS

- [ ] Lancement sans plantage ; onglets **Project**, **Preferences**, **Templates**, **About**.
- [ ] **Preferences** : fabricant, **Generate** codes, chemins JUCE + destination, couleur d’accent, export/import `profil-qa-macos.json`.
- [ ] **Create New Project** → `TestLuthier` → formats **VST3** + **AU** → **Generate Project** → dossier avec `CMakeLists.txt`, `.luthier.json`, `Source/`.
- [ ] **Open Project…** → modifier **Version** → regénérer → rouvrir : changements conservés.
- [ ] Déplacer le projet dans un dossier accentué → **Open Project…** : **Destination folder** mis à jour, **pas** d’erreur sur le chemin.
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

- [ ] `git clone` → **Open Project…** → adapter **JUCE directory** Windows.
- [ ] Version `1.1.0`, **Display name** `Voyage Cross QA Windows` → **Generate Project** OK.
- [ ] Commit + push.
- [ ] *(Recommandé)* Build + chargement VST3 depuis dossiers système et artefacts.

### 3.4 — Machine 3 (ex. Linux)

- [ ] `git pull` → ouvrir projet → JUCE Linux.
- [ ] Override **Templates** local (`// Linux QA` dans `PluginProcessor.h`) → **Save override**.
- [ ] Version `1.2.0`, **Preprocessor defs** `LINUX_QA=1` → **Generate Project**.
- [ ] Commit projet (pas les templates locaux) + push.
- [ ] *(Recommandé)* Build + chargement VST3.

### 3.5 — Retour machine 1 (ex. macOS) — Finalisation

- [ ] `git pull`.
- [ ] **Open Project…** → `VoyageLuthier`.
- [ ] **Version** : `1.2.0` ; **Preprocessor defs** : `LINUX_QA=1`.
- [ ] **JUCE directory** Mac remis → **Generate Project** sans erreur.
- [ ] **Display name** → `Voyage Cross QA Final` → générer → commit + push.

### 3.6 — Vérifications finales cross-plateforme

- [ ] Sur **les trois** OS : **Open Project…** dernière révision Git → projet cohérent (seuls JUCE / destination locaux à adapter).
- [ ] **Import Preferences…** depuis un JSON exporté sur une autre machine : **Preferences** mis à jour, projet ouvert **inchangé**.
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

- [Checklist QA 1.0.0 (archive)](checklist-qa-manuelle.md)
- [Manuel utilisateur (FR)](manuel-utilisateur.md)
- [User manual (EN)](user-manual.md)
