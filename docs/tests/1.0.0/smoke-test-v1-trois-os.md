# Luthier v1.0.0 — Smoke test complet (3 OS)

**Version visée :** 1.0.0 release  
**Révision About attendue :** 2026-07-04 (ou plus récente)  
**Public :** testeur (Guillaume) — parcours autonome  
**Langue de l’app :** anglais (libellés cités tels qu’à l’écran)  
**Durée indicative :**

| Phase | Contenu | Durée |
| --- | --- | --- |
| **A** — Fumée Luthier macOS | Luthier + Cursor / build / DAW | ~45 min |
| **B** — Fumée Luthier Windows | Luthier + Cursor / build / DAW | ~45 min |
| **C** — Fumée Luthier Linux | Luthier + Cursor / build / DAW | ~45 min |
| **D** — Fumée Git cross-OS | Clone + Cursor / build sur les 3 machines | ~45 min (total, réparti) |

> **Objectif :** valider la release publique v1.0.0 **scaffold-only** (Epic 9) : app Luthier, projet généré, ouverture **Cursor**, presets CMake, build propre, Standalone et plugins chargeables depuis les dossiers **système** et **artefacts**.

---

## Modèle produit v1 — à comprendre avant de tester

| Avant (Epics 1–8) | Maintenant (v1.0.0 scaffold-only) |
| --- | --- |
| **Open Project…** pour recharger `.luthier.json` | **Supprimé** — Luthier ne relit jamais le sidecar |
| Modifier les réglages projet sur une autre machine via Luthier | **Impossible** — pas de réouverture |
| **Generate** sur dossier existant (overwrite) | **Bloqué** sauf **régénération en session** (même app, confirmation explicite) |
| Parcours QA « voyage » : Open sur Win → changer version → Generate | **Remplacé** par : clone Git → édition manuelle ou build CMake |

### Ce qui voyage entre OS

| Artefact | Voyage ? | Comment |
| --- | --- | --- |
| **Projet JUCE généré** (sources, `CMakeLists.txt`, `.luthier.json`) | ✅ Oui | **Git** (`git clone` / `pull`) |
| **Réglages projet via Luthier** sur une machine distante | ❌ Non | Luthier ne rouvre pas le projet |
| **Profil Luthier** (`preferences.json`, templates locaux) | ✅ Oui (optionnel) | **Export / Import Preferences…** — indépendant du projet |
| **Chemins Workspace hôte** (JUCE, destination) | ⚠️ Par machine | À ajuster **manuellement** dans `.luthier.json` ou **Preferences** avant un **nouveau** Generate |

**En résumé :** le smoke test Luthier se fait **indépendamment sur chaque OS**. Le seul parcours cross-plateforme du **projet généré** passe par **Git + CMake** — pas par Luthier.

---

## Prérequis communs

> Détails par OS (JUCE, config, `--check`) : voir l’en-tête de chaque phase A / B / C.

- [ ] Dossier de travail avec **accents** possible (ex. `Téléchargements`, `été 2026`) — valide les chemins UI.
- [ ] **Git** installé (Phase D).
- [ ] **CMake** 3.22+ + compilateur + Ninja (macOS / Linux) ou VS 2022 (Windows).
- [ ] **Cursor** (ou VS Code) avec extensions **CMake Tools** et **C/C++**.
- [ ] **Ableton Live** *ou* **JUCE AudioPluginHost** (`extras/AudioPluginHost` dans votre checkout JUCE) pour tester le chargement des plugins.

### Chemins JUCE (exemples)

| OS | JUCE |
| --- | --- |
| macOS | `/Volumes/Guillaume/Dev/SDKs/JUCE` |
| Windows | `C:/Users/Guillaume/Dev/SDKs/JUCE` |
| Linux | `/home/guillaume/Dev/SDKs/JUCE` |

### Chemins artefacts (exemples — si copie centralisée activée)

| OS | Dossier artefacts racine |
| --- | --- |
| macOS | `/Users/Guillaume/Library/CloudStorage/Dropbox/Dev/Artefacts/` |
| Windows | `C:/Users/Guillaume/Dropbox/Dev/Artefacts` |
| Linux | `/home/guillaume/Dropbox/Dev/Artefacts` |

Structure après build : `{artefacts}/{OS}/{arch}/{format}/` (ex. `macOS/ARM/VST3/`, `Windows/VST3/`, `Linux/Standalone/`).

### Dossiers système (scan DAW)

| OS | VST3 | AU (macOS) |
| --- | --- | --- |
| macOS | `~/Library/Audio/Plug-Ins/VST3/` | `~/Library/Audio/Plug-Ins/Components/` |
| Windows | `C:/Program Files/Common Files/VST3/` | — |
| Linux | `~/.vst3/` | — |

### Emplacement config Luthier

| OS | Dossier |
| --- | --- |
| macOS | `~/Library/Preferences/Luthier/` |
| Windows | `%LOCALAPPDATA%\Luthier\` |
| Linux | `~/.config/Luthier/` |

### Vérification rapide du bundle (optionnel)

```bash
# macOS — Phase A
dist/Luthier.app/Contents/MacOS/Luthier --check

# Windows — Phase B
dist\Luthier\Luthier.exe --check

# Linux — Phase C
dist/Luthier/Luthier --check
```

Code de sortie **0** = templates embarqués OK.

### Projets de test suggérés

| Nom | Usage |
| --- | --- |
| `SmokeTest` | Projet local — une génération par OS (Phases A / B / C) |
| `VoyageLuthier` | Dépôt Git partagé — Phase D ([exemple](https://github.com/tensquaresoftware/voyage-luthier)) |

---

## Phase A — Fumée Luthier (macOS)

**Build testé :** 1.0.0
**Date :** JJ/MM/AAAA

### Prérequis macOS

- [ ] Build Luthier **1.0.0** installé (`Luthier.app` ou sources).
- [ ] **About** : version **1.0.0**, revision date cohérente.
- [ ] JUCE : ex. `/Volumes/Guillaume/Dev/SDKs/JUCE`
- [ ] Config : `~/Library/Preferences/Luthier/`
- [ ] *(Optionnel)* `dist/Luthier.app/Contents/MacOS/Luthier --check` → code **0**

### A0 — Lancement et shell UI

- [ ] Lancement sans plantage.
- [ ] Onglets visibles : **Project**, **Preferences**, **Templates**, **About**.
- [ ] **Pas** de bouton **Open Project…** (menu ni barre d’action).
- [ ] Barre de statut dédiée visible au-dessus des boutons d’action.

### A1 — Preferences et Workspace

- [ ] **Preferences → Workspace** : six champs (destination + JUCE × Windows / macOS / Linux).
- [ ] Lignes **macOS** seules ont **Choose…** ; Windows / Linux = saisie texte.
- [ ] **Choose…** destination macOS → dossier avec accents → pas d’erreur rouge ; badge **Saved** possible.
- [ ] Renseignez JUCE **macOS** ; chemins plausibles pour Windows et Linux.
- [ ] Fermez / rouvrez Luthier : les six valeurs conservées.
- [ ] **Export Preferences…** → **Import Preferences…** : profil restauré.

### A2 — Accent et apparence (Epic 9)

- [ ] Onglet **Project** : **aucun** sélecteur de couleur d’accent.
- [ ] **Preferences → Luthier appearance** : changement de preset → thème mis à jour sur tous les onglets.
- [ ] Connecteurs en arbre visibles sous **Workspace** et **Artefacts** (lignes Windows / macOS / Linux).

### A3 — Génération initiale

- [ ] **Create New Project** → formulaire vierge avec defaults Preferences.
- [ ] **Project name** : `SmokeTest` ; formats **VST3** + **AU** + **Standalone**.
- [ ] Section **Artefacts** : **Copy to system folders** et **Copy to central artefacts folder** activés ; chemins renseignés (macOS + saisie Windows/Linux).
- [ ] Formats **AU** + **VST3** coexistent sans conflit UI.
- [ ] **Generate Project** → succès ; message avec chemin en **`/`**.
- [ ] Dossier contient : `CMakeLists.txt`, `CMakeUserPresets.json`, `Source/`, `.luthier.json`, `.gitignore`, `README.md`, `.vscode/`, `.cursorrules`.
- [ ] `.luthier.json` : chemins Workspace présents ; **pas** de clé `accentColor`.

### A4 — Garde-fous Generate (Epic 9)

- [ ] **Fermez et relancez Luthier** (session fraîche).
- [ ] Même destination + `SmokeTest` → **Generate Project** → **bloqué** : modale + barre *This folder already exists and is not empty…*
- [ ] **Create New Project** → `SmokeRegen` → **Generate Project** → succès.
- [ ] **Sans fermer Luthier** : changez **Version** (ex. `2.0.0`) → **Generate Project** → modale **Regenerate Project** (défaut **No**) → **Yes** → succès.
- [ ] Fichiers sur disque reflètent la nouvelle version ; `.git/` préservé si dépôt Git initialisé avant regenerate.

### A5 — Create New Project et dirty guard

- [ ] Après un **Generate** réussi : **Create New Project** immédiatement → **pas** de modale « unsaved changes ».
- [ ] Modifiez un champ sans générer → **Create New Project** → modale confirmation ; **No** par défaut.

### A6 — Templates (optionnel, ~5 min)

- [ ] **Templates** → override `PluginProcessor.cpp` → **Save override**.
- [ ] **Create New Project** → nouveau nom → **Generate Project** → override visible dans les sources.
- [ ] **Reset to default** → nouvelle génération sans override.

### A7 — Cursor : ouverture, presets et build

> Projet cible : dossier `SmokeTest` généré en A3. Sous **Windows**, évitez un chemin projet avec accents (limitation MSVC).

#### Ouverture et presets

- [ ] **File → Open Folder…** → dossier `SmokeTest` — ouverture **sans accroc** (pas d’erreur bloquante au chargement).
- [ ] Dossier `.vscode/` présent (`settings.json`, `tasks.json`, `launch.json`).
- [ ] Extensions **CMake Tools** et **C/C++** actives ; configuration CMake démarre puis **se termine sans échec** (barre de statut).
- [ ] Palette → **CMake: Select Configure Preset** : presets **macOS** listés (ex. `macos-debug-arm64`, `macos-release-arm64`, … — pas seulement Windows/Linux).
- [ ] Sélection du preset **`macos-debug-arm64`** (Apple Silicon) ou **`macos-debug-x86_64`** (Intel natif) → répertoire de build cohérent (ex. `Builds/macOS/ARM/Debug`).

#### Compilation

- [ ] **CMake: Build** ou `Cmd+Shift+B` → build **sans erreur**.
- [ ] Panneau **Problems** : **aucune erreur** ; **aucun warning compilateur** du projet (warnings dans les headers JUCE tiers = noter en **mineur** si présents).
- [ ] Logs de post-build : copies vers dossiers **système** et **artefacts** visibles (cibles `CopyToArtefactsDir`, etc.).

### A8 — Cursor : Standalone et chargement plugins

#### Standalone depuis Cursor

- [ ] **Run and Debug** → configuration **Standalone** (`.vscode/launch.json`).
- [ ] **F5** → application Standalone s’ouvre **sans crash** ; fermeture propre.

#### Dossier système

- [ ] **VST3** présent dans `~/Library/Audio/Plug-Ins/VST3/`.
- [ ] **AU** présent dans `~/Library/Audio/Plug-Ins/Components/` (si format AU coché).
- [ ] **Ableton Live** *ou* **AudioPluginHost** : rescan si nécessaire.
- [ ] Chargement **VST3** depuis dossier **système** → **sans crash**, UI plugin fonctionnelle.
- [ ] Chargement **AU** depuis dossier **système** → **sans crash** (Ableton ou AudioPluginHost).

#### Dossier artefacts

- [ ] **VST3**, **AU** et **Standalone** présents sous le dossier artefacts (ex. `…/macOS/ARM/VST3/`, `…/AU/`, `…/Standalone/`).
- [ ] **Ableton Live** *ou* **AudioPluginHost** : chargement **VST3** depuis **artefacts** → **sans crash**.
- [ ] Chargement **AU** depuis **artefacts** → **sans crash** (si applicable).
- [ ] Lancement **Standalone** depuis le dossier **artefacts** → **sans crash**.

---

## Phase B — Fumée Luthier (Windows)

**Build testé :** 1.0.0  
**Date :** JJ/MM/AAAA

### Prérequis Windows

- [ ] Build Luthier **1.0.0** installé (`Luthier.exe` ou sources).
- [ ] **About** : version **1.0.0**, revision date cohérente.
- [ ] JUCE : ex. `C:/Users/Guillaume/Dev/SDKs/JUCE`
- [ ] Config : `%LOCALAPPDATA%\Luthier\`
- [ ] *(Optionnel)* `dist\Luthier\Luthier.exe --check` → code **0**

### B0 — Lancement et shell UI

- [ ] Lancement sans plantage.
- [ ] Onglets visibles : **Project**, **Preferences**, **Templates**, **About**.
- [ ] **Pas** de bouton **Open Project…** (menu ni barre d’action).
- [ ] Barre de statut dédiée visible au-dessus des boutons d’action.

### B1 — Preferences et Workspace

- [ ] **Preferences → Workspace** : six champs (destination + JUCE × Windows / macOS / Linux).
- [ ] Lignes **Windows** seules ont **Choose…** ; macOS / Linux = saisie texte.
- [ ] **Choose…** destination Windows → dossier avec accents → pas d’erreur rouge ; badge **Saved** possible.
- [ ] Renseignez JUCE **Windows** ; chemins plausibles pour macOS et Linux.
- [ ] Fermez / rouvrez Luthier : les six valeurs conservées.
- [ ] **Export Preferences…** → **Import Preferences…** : profil restauré.

### B2 — Accent et apparence (Epic 9)

- [ ] Onglet **Project** : **aucun** sélecteur de couleur d’accent.
- [ ] **Preferences → Luthier appearance** : changement de preset → thème mis à jour sur tous les onglets.
- [ ] Connecteurs en arbre visibles sous **Workspace** et **Artefacts** (lignes Windows / macOS / Linux).

### B3 — Génération initiale

- [ ] **Create New Project** → formulaire vierge avec defaults Preferences.
- [ ] **Project name** : `SmokeTest` ; formats **VST3** + **Standalone** (AU coché ne doit **pas** bloquer).
- [ ] Section **Artefacts** : **Copy to system folders** et **Copy to central artefacts folder** activés ; chemins renseignés (Windows + saisie macOS/Linux).
- [ ] **Generate Project** → succès ; message et chemins affichés avec **`/`** (pas de `\`).
- [ ] Dossier contient : `CMakeLists.txt`, `CMakeUserPresets.json`, `Source/`, `.luthier.json`, `.gitignore`, `README.md`, `.vscode/`, `.cursorrules`.
- [ ] `.luthier.json` : chemins Workspace présents ; **pas** de clé `accentColor`.

### B4 — Garde-fous Generate (Epic 9)

- [ ] **Fermez et relancez Luthier** (session fraîche).
- [ ] Même destination + `SmokeTest` → **Generate Project** → **bloqué** : modale + barre *This folder already exists and is not empty…*
- [ ] **Create New Project** → `SmokeRegen` → **Generate Project** → succès.
- [ ] **Generate** dans un dossier contenant `.git/` : **pas** de WinError / accès refusé.
- [ ] **Sans fermer Luthier** : changez **Version** (ex. `2.0.0`) → **Generate Project** → modale **Regenerate Project** (défaut **No**) → **Yes** → succès.
- [ ] Fichiers sur disque reflètent la nouvelle version ; `.git/` préservé si dépôt Git initialisé avant regenerate.

### B5 — Create New Project et dirty guard

- [ ] Après un **Generate** réussi : **Create New Project** immédiatement → **pas** de modale « unsaved changes ».
- [ ] Modifiez un champ sans générer → **Create New Project** → modale confirmation ; **No** par défaut.
- [ ] Ordre boutons modales : **No** / **Yes** (inversion vs Mac/Linux = **mineur**, non bloquant si fonctionnel).

### B6 — Templates (optionnel, ~5 min)

- [ ] **Templates** → override `PluginProcessor.cpp` → **Save override**.
- [ ] **Create New Project** → nouveau nom → **Generate Project** → override visible dans les sources.
- [ ] **Reset to default** → nouvelle génération sans override.

### B7 — Cursor : ouverture, presets et build

> Projet cible : dossier `SmokeTest` généré en B3. **Chemin ASCII obligatoire** (pas d’accents dans le chemin du projet).

#### Ouverture et presets

- [ ] **File → Open Folder…** → dossier `SmokeTest` — ouverture **sans accroc**.
- [ ] Dossier `.vscode/` présent (`settings.json`, `tasks.json`, `launch.json`).
- [ ] Extensions **CMake Tools** et **C/C++** actives ; configuration CMake **sans échec**.
- [ ] Palette → **CMake: Select Configure Preset** : presets **Windows** listés (`windows-debug`, `windows-release`).
- [ ] Sélection du preset **`windows-debug`** → répertoire de build `Builds/Windows`.

#### Compilation

- [ ] **CMake: Build** ou `Ctrl+Shift+B` → build **sans erreur**.
- [ ] Panneau **Problems** : **aucune erreur** ; **aucun warning compilateur** du projet.
- [ ] Prompt **UAC** à la copie VST3 système : cliquer **Yes** ; logs de copie **artefacts** visibles.

### B8 — Cursor : Standalone et chargement plugins

#### Standalone depuis Cursor

- [ ] **Run and Debug** → configuration **Standalone**.
- [ ] **F5** → Standalone **sans crash** ; fermeture propre.

#### Dossier système

- [ ] **VST3** présent dans `C:/Program Files/Common Files/VST3/`.
- [ ] **Ableton Live** *ou* **AudioPluginHost** : rescan si nécessaire.
- [ ] Chargement **VST3** depuis dossier **système** → **sans crash**.

#### Dossier artefacts

- [ ] **VST3** et **Standalone** sous le dossier artefacts (ex. `…/Windows/VST3/`, `…/Standalone/`).
- [ ] **Ableton Live** *ou* **AudioPluginHost** : chargement **VST3** depuis **artefacts** → **sans crash**.
- [ ] Lancement **Standalone** depuis le dossier **artefacts** → **sans crash**.

---

## Phase C — Fumée Luthier (Linux)

**Build testé :** 1.0.0  
**Date :** JJ/MM/AAAA

### Prérequis Linux

- [ ] Build Luthier **1.0.0** installé (exécutable `Luthier` ou sources).
- [ ] **About** : version **1.0.0**, revision date cohérente.
- [ ] JUCE : ex. `/home/guillaume/Dev/SDKs/JUCE`
- [ ] Config : `~/.config/Luthier/`
- [ ] *(Optionnel)* `dist/Luthier/Luthier --check` → code **0**
- [ ] *(Optionnel)* raccourci `.desktop` si icône barre des tâches requise (manuel §17).

### C0 — Lancement et shell UI

- [ ] Lancement sans plantage.
- [ ] Onglets visibles : **Project**, **Preferences**, **Templates**, **About**.
- [ ] **Pas** de bouton **Open Project…** (menu ni barre d’action).
- [ ] Barre de statut dédiée visible au-dessus des boutons d’action.
- [ ] Icône Luthier dans le lanceur / barre des tâches (ou via `.desktop`).
- [ ] Géométrie fenêtre : taille sensiblement conservée après fermeture / réouverture ; position non garantie (Wayland = **mineur** accepté).

### C1 — Preferences et Workspace

- [ ] **Preferences → Workspace** : six champs (destination + JUCE × Windows / macOS / Linux).
- [ ] Lignes **Linux** seules ont **Choose…** ; macOS / Windows = saisie texte.
- [ ] **Choose…** destination Linux → dossier avec accents → pas d’erreur rouge ; badge **Saved** possible.
- [ ] Renseignez JUCE **Linux** ; chemins plausibles pour macOS et Windows.
- [ ] Fermez / rouvrez Luthier : les six valeurs conservées.
- [ ] **Export Preferences…** → **Import Preferences…** : profil restauré.

### C2 — Accent et apparence (Epic 9)

- [ ] Onglet **Project** : **aucun** sélecteur de couleur d’accent.
- [ ] **Preferences → Luthier appearance** : changement de preset → thème mis à jour sur tous les onglets.
- [ ] Connecteurs en arbre visibles sous **Workspace** et **Artefacts** (lignes Windows / macOS / Linux).

### C3 — Génération initiale

- [ ] **Create New Project** → formulaire vierge avec defaults Preferences.
- [ ] **Project name** : `SmokeTest` ; formats **VST3** + **Standalone**.
- [ ] Section **Artefacts** : **Copy to system folders** et **Copy to central artefacts folder** activés ; chemins renseignés (Linux + saisie macOS/Windows).
- [ ] **Generate Project** → succès ; message avec chemin en **`/`**.
- [ ] Dossier contient : `CMakeLists.txt`, `CMakeUserPresets.json`, `Source/`, `.luthier.json`, `.gitignore`, `README.md`, `.vscode/`, `.cursorrules`.
- [ ] `.luthier.json` : chemins Workspace présents ; **pas** de clé `accentColor`.

### C4 — Garde-fous Generate (Epic 9)

- [ ] **Fermez et relancez Luthier** (session fraîche).
- [ ] Même destination + `SmokeTest` → **Generate Project** → **bloqué** : modale + barre *This folder already exists and is not empty…*
- [ ] **Create New Project** → `SmokeRegen` → **Generate Project** → succès.
- [ ] **Sans fermer Luthier** : changez **Version** (ex. `2.0.0`) → **Generate Project** → modale **Regenerate Project** (défaut **No**) → **Yes** → succès.
- [ ] Fichiers sur disque reflètent la nouvelle version ; `.git/` préservé si dépôt Git initialisé avant regenerate.

### C5 — Create New Project et dirty guard

- [ ] Après un **Generate** réussi : **Create New Project** immédiatement → **pas** de modale « unsaved changes ».
- [ ] Modifiez un champ sans générer → **Create New Project** → modale confirmation ; **No** par défaut.

### C6 — Templates (optionnel, ~5 min)

- [ ] **Templates** → override `PluginProcessor.cpp` → **Save override**.
- [ ] **Create New Project** → nouveau nom → **Generate Project** → override visible dans les sources.
- [ ] **Reset to default** → nouvelle génération sans override.

### C7 — Cursor : ouverture, presets et build

> Projet cible : dossier `SmokeTest` généré en C3.

#### Ouverture et presets

- [ ] **File → Open Folder…** → dossier `SmokeTest` — ouverture **sans accroc**.
- [ ] Dossier `.vscode/` présent (`settings.json`, `tasks.json`, `launch.json`).
- [ ] Extensions **CMake Tools** et **C/C++** actives ; configuration CMake **sans échec**.
- [ ] Palette → **CMake: Select Configure Preset** : presets **Linux** listés (`linux-debug`, `linux-release`).
- [ ] Sélection du preset **`linux-debug`** → répertoire de build `Builds/Linux/Debug`.

#### Compilation

- [ ] **CMake: Build** ou `Ctrl+Shift+B` → build **sans erreur**.
- [ ] Panneau **Problems** : **aucune erreur** ; **aucun warning compilateur** du projet.
- [ ] Logs de post-build : copies vers `~/.vst3/` et dossier **artefacts** visibles.

### C8 — Cursor : Standalone et chargement plugins

#### Standalone depuis Cursor

- [ ] **Run and Debug** → configuration **Standalone** (GDB si configuré).
- [ ] **F5** → Standalone **sans crash** ; fermeture propre.

#### Dossier système

- [ ] **VST3** présent dans `~/.vst3/`.
- [ ] **Ableton Live** *ou* **AudioPluginHost** : rescan si nécessaire.
- [ ] Chargement **VST3** depuis dossier **système** → **sans crash**.

#### Dossier artefacts

- [ ] **VST3** et **Standalone** sous le dossier artefacts (ex. `…/Linux/VST3/`, `…/Standalone/`).
- [ ] **Ableton Live** *ou* **AudioPluginHost** : chargement **VST3** depuis **artefacts** → **sans crash**.
- [ ] Lancement **Standalone** depuis le dossier **artefacts** → **sans crash**.

---

## Phase D — Fumée Git cross-plateforme (projet généré)

> Valide que le **projet JUCE de démarrage** voyage via Git et compile sur chaque OS **sans Luthier Open**. Une seule passe suffit si les Phases A, B et C sont OK.

### D0 — Préparation

- [ ] Dépôt Git vide ou `VoyageLuthier` prêt.
- [ ] JUCE installé sur **chaque** machine (chemins locaux différents).

### D1 — Machine 1 (ex. macOS) — Création

- [ ] Luthier : **Create New Project** → `VoyageLuthier`, version `1.0.0`, **VST3** + **Standalone** (+ **AU** si Mac).
- [ ] Chemins **Workspace** et **Artefacts** renseignés pour les trois OS ; copies **système** + **artefacts** activées.
- [ ] **Generate Project** ; `.luthier.json` présent.
- [ ] `git init` → commit → push.
- [ ] **Cursor** : ouverture sans accroc → preset hôte → build **sans erreur ni warning** → Standalone **F5** sans crash → plugins OK (**système** + **artefacts**).

### D2 — Machine 2 (ex. Windows)

- [ ] `git clone` du dépôt.
- [ ] Éditez **JUCE directory** ligne **Windows** dans `.luthier.json` (chemin local).
- [ ] **Cursor** : ouverture sans accroc → preset `windows-debug` → build **sans erreur ni warning**.
- [ ] Standalone **F5** sans crash ; **VST3** chargeable depuis **système** et **artefacts** (Ableton ou AudioPluginHost).
- [ ] *(Optionnel)* Modifiez `Source/` ou metadata dans Git → commit → push.

> **Ne pas** utiliser **Generate Project** sur le clone après redémarrage Luthier (dossier non vide). Pour regénérer le projet entier : dossier vide + nouvelle session Luthier, ou **session regenerate** volontaire sur machine 1.

### D3 — Machine 3 (ex. Linux)

- [ ] `git pull`.
- [ ] Éditez **JUCE directory** ligne **Linux** dans `.luthier.json`.
- [ ] **Cursor** : ouverture sans accroc → preset `linux-debug` → build **sans erreur ni warning**.
- [ ] Standalone **F5** sans crash ; **VST3** chargeable depuis **système** et **artefacts** (Ableton ou AudioPluginHost).
- [ ] Commit + push si modifications.

### D4 — Retour machine 1 — Cohérence finale

- [ ] `git pull` → contenu cohérent (sources, `.luthier.json`, `CMakeLists.txt`).
- [ ] Éditez chemin JUCE **macOS** si besoin.
- [ ] **Cursor** : build + chargement plugins (**système** + **artefacts**) toujours OK sur la dernière révision Git.
- [ ] **Aucun plantage** Luthier pendant D1–D4 (Luthier utilisé uniquement en D1).

### D5 — Import Preferences cross-OS (optionnel, ~5 min)

> Teste le profil **Luthier**, pas le projet Git.

- [ ] Machine A : **Export Preferences…** vers fichier partagé (cloud, clé USB).
- [ ] Machine B : **Import Preferences…** → **Preferences** mis à jour.
- [ ] Formulaire **Project** **inchangé** jusqu’à **Create New Project**.

---

## Critères de réussite (go release v1.0.0)

Le smoke test est **réussi** si :

- [ ] **Phase A** complète (macOS) — A0–A8 minimum.
- [ ] **Phase B** complète (Windows) — B0–B8 minimum.
- [ ] **Phase C** complète (Linux) — C0–C8 minimum.
- [ ] **Phase D** complète (D1–D4) — clone Git + parcours **Cursor** sur les **trois** OS.
- [ ] **Aucun bloquant** ouvert dans la grille ci-dessous.
- [ ] Points **mineurs** connus acceptés :
  - ordre boutons modales Windows (Phase B, B5) ;
  - position fenêtre Linux non garantie (Phase C, C0) ;
  - icône Linux sans `.desktop` (Phase C, C0) ;
  - warnings compilateur dans headers JUCE tiers uniquement ;
  - faux positifs CMake Tools « Task has errors » après copie post-build (README projet généré).

---

## Grille de suivi

| # | OS | Phase | Action | Attendu | Obtenu | Gravité |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | | | | | | bloquant / gênant / mineur |
| 2 | | | | | | |
| 3 | | | | | | |

**Gravité :** **bloquant** = impossible de continuer ou risque perte de données ; **gênant** = contournement pénible ; **mineur** = cosmétique ou cas rare.

---

## Ce qu’il n’est **plus** nécessaire de tester

Par rapport aux checklists pré–Epic 9, **ne pas refaire** :

- Round-trip **Open Project…** → formulaire rechargé → Generate sans changement → diff vide.
- Fidélité byte-for-byte après Open sur une autre machine.
- Migration sidecar / Open fallback CMake regex.
- Parcours « Open sur Windows → changer version dans Luthier → Generate » sur clone Git.
- Sync Preferences via Open/Generate (supprimé en Epic 5, confirmé Epic 9).

---

## Références

- [Manuel utilisateur (FR)](../../user/manuel-utilisateur.md) — §16.7 multi-OS, §18 stockage, §22 app autonome
- [User manual (EN)](../../user/user-manual.md)
- README du projet généré (`SmokeTest/README.md`) — presets Cursor, dossiers système / artefacts, debugging
- [Checklist QA passe unique (archive)](../1.0.0-beta/checklist-qa-passe-unique.md)
- [Checklist QA pré-release (archive)](../1.0.0-beta/checklist-qa-pre-release-v1.md)
