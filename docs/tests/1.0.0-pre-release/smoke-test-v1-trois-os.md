# Luthier — Smoke test complet (3 OS)

**Version / tag visé :** _indiquer le tag testé (ex. `1.0.0-rc1`, `1.0.0`)_  
**Révision About attendue :** cohérente avec le tag testé  
**Public :** testeur — parcours autonome, exécutable étape par étape  
**Langue de l’app :** anglais (libellés cités tels qu’à l’écran)

---

## Comment utiliser ce guide

1. **Remplis la fiche de session** (section suivante) avant de commencer.
2. **Exécute les phases dans l’ordre** A → B → C → D (D peut attendre la fin de A/B/C).
3. Pour **chaque ligne** du tableau : fais l’action, vérifie le résultat attendu, coche **✅ OK** *ou* **❌ KO** (une seule des deux), note tes remarques dans la dernière colonne si besoin.
4. Si **❌ KO** bloque la suite de la phase, note la gravité dans la **grille des anomalies** (fin de document) et décide si tu continues (gênant/mineur) ou tu arrêtes la phase (bloquant).
5. Les étapes marquées **(opt)** sont optionnelles — ne bloquent pas le go release.

**Légende colonnes**

| Colonne | Signification |
| --- | --- |
| **✅ OK** | Comportement conforme à l’attendu |
| **❌ KO** | Comportement incorrect ou bloquant pour cette étape |
| **Remarques** | Observations, captures, contournement, gravité proposée |

---

## Fiche de session

| Champ | Valeur |
| --- | --- |
| **Testeur** | |
| **Date de début** | |
| **Commit / tag testé** | |
| **Source du build Luthier** | ☐ GitHub Release (artefacts du tag) ☐ `dist/` local (PyInstaller) ☐ sources (`.venv/bin/python main.py`) ☐ autre : |
| **CI GitHub** (pytest 3 OS) | ☐ verte sur le commit testé ☐ non vérifiée |
| **DAW utilisé** | ☐ Ableton Live ☐ JUCE AudioPluginHost ☐ les deux |
| **Cursor / VS Code** | Version : |

### Avancement par phase

| Phase | Description | Durée ~ | ✅ Terminée | Date | Bloquants ouverts |
| --- | --- | --- | :---: | --- | --- |
| **A** | Fumée Luthier macOS (Apple Silicon) | 45 min | ☐ | | |
| **B** | Fumée Luthier Windows | 45 min | ☐ | | |
| **C** | Fumée Luthier Linux | 45 min | ☐ | | |
| **D** | Fumée Git cross-OS (projet généré) | 45 min | ☐ | | |

---

## Ce que la CI fait déjà (ne pas re-tester ici)

La CI (`.github/workflows/pytest.yml`) exécute **pytest sur Ubuntu, Windows et macOS** à chaque push/PR. Tu n’as **pas** à rejouer manuellement la logique couverte par les tests automatisés (garde-fous Generate, dirty guard, preferences, génération de fichiers, etc.) **sauf** si tu veux une double validation avant release.

**Ce guide couvre ce que la CI ne voit pas :** UI réelle, bundle PyInstaller, dialogues fichiers, Cursor/CMake Tools, build JUCE du projet généré, chargement DAW, copies vers dossiers système/artefacts.

---

## Modèle produit v1 — lire avant de tester

| Avant (Epics 1–8) | Maintenant (v1.0.0 — projet de démarrage) |
| --- | --- |
| **Open Project…** pour recharger `.luthier.json` | **Supprimé** — Luthier ne relit jamais le sidecar |
| Modifier le projet sur une autre machine via Luthier | **Impossible** — pas de réouverture |
| **Generate** sur dossier existant | **Bloqué** sauf **régénération en session** (même app ouverte, confirmation explicite) |
| Parcours « Open sur Win → Generate » | **Remplacé par** clone Git → édition manuelle ou build CMake |

| Artefact | Voyage entre OS ? | Comment |
| --- | --- | --- |
| Projet JUCE généré | ✅ Oui | **Git** |
| Réglages projet via Luthier sur machine distante | ❌ Non | — |
| Profil Luthier (`preferences.json`, templates) | ✅ Oui (opt.) | **Export / Import Preferences…** |
| Chemins Workspace (JUCE, destination) | ⚠️ Par machine | Ajuster dans **Preferences** ou `.luthier.json` avant un **nouveau** Generate |

**macOS — périmètre app Luthier :** l’application autonome `Luthier.app` requiert un Mac **Apple Silicon (arm64)**. Les Mac Intel ne sont **pas** pris en charge pour l’app. Les **projets générés** restent compilables pour Mac Intel via les presets CMake `macos-debug-x86_64` (hors scope de ce smoke test pour la Phase A).

---

## Prérequis communs (toutes phases)

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| P-01 | Vérifier **Git** installé (`git --version`) | Version affichée | ☐ | ☐ | Requis Phase D |
| P-02 | Vérifier **CMake** ≥ 3.22 (`cmake --version`) | Version ≥ 3.22 | ☐ | ☐ | |
| P-03 | Vérifier compilateur + **Ninja** (macOS/Linux) ou **VS 2022** (Windows) | Outil disponible | ☐ | ☐ | |
| P-04 | Installer **Cursor** (ou VS Code) + extensions **CMake Tools** et **C/C++** | Extensions actives | ☐ | ☐ | |
| P-05 | Préparer un dossier de travail **avec accents** possible (ex. `Téléchargements/été 2026`) | Dossier créé | ☐ | ☐ | Valide les chemins UI Luthier |
| P-06 | Installer / localiser **JUCE** (checkout complet, pas seulement headers) | Chemin noté ci-dessous | ☐ | ☐ | |
| P-07 | Préparer **Ableton Live** *ou* build **AudioPluginHost** JUCE (`extras/AudioPluginHost`) | Au moins un outil prêt | ☐ | ☐ | |
| P-08 | Lire la section **Obtenir le build Luthier** pour l’OS de la phase en cours | Build prêt avant A0/B0/C0 | ☐ | ☐ | |

### Chemins de référence (adapter à ta machine)

| Rôle | macOS | Windows | Linux |
| --- | --- | --- | --- |
| **JUCE** | `/Volumes/Guillaume/Dev/SDKs/JUCE` | `C:/Users/Guillaume/Dev/SDKs/JUCE` | `/home/guillaume/Dev/SDKs/JUCE` |
| **Artefacts racine** (si copie centralisée) | `/Users/Guillaume/Library/CloudStorage/Dropbox/Dev/Artefacts/` | `C:/Users/Guillaume/Dropbox/Dev/Artefacts` | `/home/guillaume/Dropbox/Dev/Artefacts` |
| **Config Luthier** | `~/Library/Preferences/Luthier/` | `%LOCALAPPDATA%\Luthier\` | `~/.config/Luthier/` |
| **VST3 système** | `~/Library/Audio/Plug-Ins/VST3/` | `C:/Program Files/Common Files/VST3/` | `~/.vst3/` |
| **AU système** (macOS) | `~/Library/Audio/Plug-Ins/Components/` | — | — |

**Projets de test**

| Nom | Usage |
| --- | --- |
| `SmokeTest` | Une génération locale par OS (Phases A / B / C) |
| `SmokeRegen` | Garde-fous régénération (A4 / B4 / C4) |
| `VoyageLuthier` | Dépôt Git partagé — Phase D ([exemple](https://github.com/tensquaresoftware/voyage-luthier)) |

---

## Obtenir le build Luthier (avant chaque phase OS)

Choisis **une** méthode par machine. Pour un **RC** (`1.0.0-rc1`, etc.), privilégie **Option R** (artefacts publiés par la CI). Pour une validation locale avant tag, utilise les options A/B.

### Option R — GitHub Release (recommandé pour RC)

Après `git push origin <tag>`, la CI publie une [GitHub Release](https://github.com/tensquaresoftware/luthier/releases) avec quatre zips : `Luthier-<tag>-{macos,windows,linux,docs}.zip`.

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| R-01 | Ouvrir la Release du **tag testé** sur GitHub | Release marquée **Pre-release** si le tag contient un suffixe (`-rc1`, `-beta2`, …) | ☐ | ☐ | |
| R-02 | Télécharger `Luthier-<tag>-macos.zip` (Phase A), `-windows.zip` (Phase B), `-linux.zip` (Phase C) | Archives présentes ; taille non nulle | ☐ | ☐ | |
| R-03 | **macOS :** extraire le zip → `Luthier.app` ; si « est endommagé » : `xattr -cr /chemin/vers/Luthier.app` puis lancer ; sinon `--check` | Code **0** sur `--check` ; app démarre | ☐ | ☐ | Quarantaine navigateur = normal sur build non signé |
| R-04 | **Windows :** extraire → `Luthier\Luthier.exe` ; lancer ou `--check` | Code **0** ; app démarre | ☐ | ☐ | |
| R-05 | **Linux :** extraire → `Luthier/Luthier` exécutable ; lancer ou `--check` | Code **0** ; app démarre | ☐ | ☐ | |
| R-06 | Onglet **About** sur chaque OS | Version = **tag testé** ; date de révision cohérente | ☐ | ☐ | |

### macOS (Apple Silicon uniquement) — build local

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| M-01 | **Option A — Bundle :** depuis la racine du dépôt, avec `.venv` et deps installées : `python publish/build-dist.py` | `dist/Luthier.app` créé ; `--check` termine avec code **0** | ☐ | ☐ | |
| M-02 | **Option B — Dev :** `.venv/bin/python main.py` | Fenêtre Luthier s’ouvre | ☐ | ☐ | |
| M-03 | Si macOS affiche « est endommagé » après téléchargement : `xattr -cr dist/Luthier.app` ; sinon clic droit → **Ouvrir** pour développeur non identifié | App lance sans blocage persistant | ☐ | ☐ | Bundle non signé = normal |
| M-04 | Onglet **About** : version = **tag testé**, date de révision cohérente | Infos correctes | ☐ | ☐ | |

**Vérification rapide bundle (optionnel)**

```bash
dist/Luthier.app/Contents/MacOS/Luthier --check
# code de sortie 0 = templates embarqués OK
```

### Windows — build local

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| W-01 | **Option A — Bundle :** `python publish/build-dist.py` | `dist\Luthier\Luthier.exe` créé ; `--check` → code **0** | ☐ | ☐ | |
| W-02 | **Option B — Dev :** `.venv\Scripts\python main.py` | Fenêtre s’ouvre | ☐ | ☐ | |
| W-03 | **About** : version = **tag testé** | Infos correctes | ☐ | ☐ | |

```bat
dist\Luthier\Luthier.exe --check
```

### Linux — build local

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| L-01 | **Option A — Bundle :** `python publish/build-dist.py` | `dist/Luthier/Luthier` exécutable ; `--check` → code **0** | ☐ | ☐ | |
| L-02 | **Option B — Dev :** `.venv/bin/python main.py` | Fenêtre s’ouvre | ☐ | ☐ | |
| L-03 | **About** : version = **tag testé** | Infos correctes | ☐ | ☐ | |
| L-04 | (opt.) Raccourci `.desktop` si tu testes l’icône barre des tâches | Icône visible | ☐ | ☐ | Mineur si absent |

```bash
dist/Luthier/Luthier --check
```

---

## Phase A — Fumée Luthier (macOS Apple Silicon)

**Machine :** Mac **Apple Silicon** (M1/M2/M3/M4…) — **pas** Mac Intel.  
**Build testé :** | **Date :** |

### A0 — Lancement et shell UI

| ID | Action (faire exactement) | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| A-001 | Lancer Luthier (double-clic `Luthier.app` ou `python main.py`) | Pas de crash au démarrage | ☐ | ☐ | |
| A-002 | Parcourir les onglets | **Project**, **Preferences**, **Templates**, **About** visibles | ☐ | ☐ | |
| A-003 | Chercher **Open Project…** (menu, barre d’action) | **Absent** partout | ☐ | ☐ | |
| A-004 | Regarder au-dessus des boutons d’action | Barre de statut / message dédiée visible | ☐ | ☐ | |

### A1 — Preferences et Workspace

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| A-101 | **Preferences → Workspace** | 6 champs : destination + JUCE × Windows / macOS / Linux | ☐ | ☐ | |
| A-102 | Observer les boutons **Choose…** | Uniquement sur les lignes **macOS** ; Windows/Linux = saisie texte | ☐ | ☐ | |
| A-103 | **Choose…** destination macOS → sélectionner un dossier **avec accents** (ex. `été 2026`) | Pas de message d’erreur rouge ; badge **Saved** possible | ☐ | ☐ | |
| A-104 | Renseigner JUCE **macOS** (chemin réel) ; saisir des chemins **plausibles** pour Windows et Linux | Champs acceptés sans erreur | ☐ | ☐ | |
| A-105 | Fermer Luthier complètement, relancer | Les 6 valeurs sont conservées | ☐ | ☐ | |
| A-106 | **Export Preferences…** → enregistrer un fichier JSON | Fichier créé | ☐ | ☐ | |
| A-107 | Modifier une pref, puis **Import Preferences…** (fichier exporté) | Profil restauré ; champs attendus réappliqués | ☐ | ☐ | |

### A2 — Accent et apparence

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| A-201 | Onglet **Project** | **Aucun** sélecteur de couleur d’accent | ☐ | ☐ | |
| A-202 | **Preferences → Luthier appearance** : changer de preset | Thème mis à jour sur **tous** les onglets | ☐ | ☐ | |
| A-203 | Regarder sous **Workspace** et **Artefacts** | Connecteurs en arbre visibles (lignes Win / macOS / Linux) | ☐ | ☐ | |

### A3 — Génération initiale (`SmokeTest`)

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| A-301 | **Create New Project** | Formulaire vierge, valeurs par défaut des Preferences | ☐ | ☐ | |
| A-302 | **Project name** = `SmokeTest` ; cocher **VST3** + **AU** + **Standalone** | Formats cochés sans conflit UI | ☐ | ☐ | |
| A-303 | **Artefacts** : activer **Copy to system folders** et **Copy to central artefacts folder** ; renseigner chemins macOS (+ saisie Win/Linux) | Champs valides | ☐ | ☐ | |
| A-304 | **Generate Project** | Succès ; message avec chemin en **`/`** (slashes avant) | ☐ | ☐ | Noter le chemin absolu : |
| A-305 | Ouvrir le dossier généré dans le Finder | Présents : `CMakeLists.txt`, `CMakeUserPresets.json`, `Source/`, `.luthier.json`, `.gitignore`, `README.md`, `.vscode/`, `.cursorrules` | ☐ | ☐ | |
| A-306 | Ouvrir `.luthier.json` | Chemins Workspace présents ; **pas** de clé `accentColor` | ☐ | ☐ | |

### A4 — Garde-fous Generate

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| A-401 | **Fermer et relancer Luthier** (session fraîche) | App redémarre normalement | ☐ | ☐ | |
| A-402 | Sans changer la destination : **Project name** = `SmokeTest` → **Generate Project** | **Bloqué** : modale + barre *This folder already exists and is not empty…* | ☐ | ☐ | |
| A-403 | **Create New Project** → **Project name** = `SmokeRegen` → **Generate Project** | Succès dans un **nouveau** dossier | ☐ | ☐ | |
| A-404 | Dans le dossier `SmokeRegen` : `git init`, `git add .`, `git commit -m "init"` | Dépôt Git initialisé | ☐ | ☐ | Prépare le test suivant |
| A-405 | **Sans fermer Luthier** : sur `SmokeRegen`, changer **Version** → `2.0.0` → **Generate Project** | Modale **Regenerate Project** ; défaut **No** ; choisir **Yes** → succès | ☐ | ☐ | |
| A-406 | Vérifier sur disque | Fichiers reflètent `2.0.0` ; dossier `.git/` **toujours présent** | ☐ | ☐ | |

### A5 — Create New Project et dirty guard

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| A-501 | Juste après un **Generate** réussi : cliquer **Create New Project** | **Pas** de modale « unsaved changes » | ☐ | ☐ | |
| A-502 | Modifier un champ (ex. version) **sans** générer → **Create New Project** | Modale de confirmation ; bouton **No** par défaut ; **No** annule, **Yes** réinitialise | ☐ | ☐ | |

### A6 — Templates **(opt.)**

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| A-601 | **Templates** → override `PluginProcessor.cpp` → **Save override** | Override enregistré | ☐ | ☐ | |
| A-602 | **Create New Project** → nouveau nom → **Generate Project** | Override visible dans les sources générées | ☐ | ☐ | |
| A-603 | **Reset to default** → nouvelle génération | Plus d’override dans les sources | ☐ | ☐ | |

### A7 — Cursor : ouverture, presets, build

**Projet cible :** dossier `SmokeTest` créé en A-304.

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| A-701 | Cursor → **File → Open Folder…** → dossier `SmokeTest` | Ouverture sans erreur bloquante | ☐ | ☐ | |
| A-702 | Vérifier `.vscode/` | `settings.json`, `tasks.json`, `launch.json` présents | ☐ | ☐ | |
| A-703 | Attendre la fin de la configuration CMake (barre de statut) | Configure **réussie** (pas d’échec rouge) | ☐ | ☐ | |
| A-704 | Palette (`Cmd+Shift+P`) → **CMake: Select Configure Preset** | Presets **macOS** listés (`macos-debug-arm64`, `macos-release-arm64`, …) | ☐ | ☐ | |
| A-705 | Sélectionner **`macos-debug-arm64`** | Dossier de build cohérent (ex. `Builds/macOS/ARM/Debug`) | ☐ | ☐ | **Ne pas** utiliser `macos-debug-x86_64` sur ce test (host ARM) sauf test Rosetta volontaire |
| A-706 | **CMake: Build** ou `Cmd+Shift+B` | Build **sans erreur** | ☐ | ☐ | |
| A-707 | Panneau **Problems** | Aucune **erreur** ; aucun warning **du projet** (warnings headers JUCE tiers = noter mineur) | ☐ | ☐ | |
| A-708 | Logs de build / terminal | Traces de copie vers dossiers **système** et **artefacts** visibles | ☐ | ☐ | |

### A8 — Standalone et chargement plugins

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| A-801 | **Run and Debug** → config **Standalone** → **F5** | Standalone s’ouvre **sans crash** ; fermeture propre | ☐ | ☐ | |
| A-802 | Finder : `~/Library/Audio/Plug-Ins/VST3/` | `SmokeTest.vst3` (ou nom équivalent) présent | ☐ | ☐ | |
| A-803 | Finder : `~/Library/Audio/Plug-Ins/Components/` | `SmokeTest.component` présent | ☐ | ☐ | |
| A-804 | DAW : rescan plugins si nécessaire | Scan terminé sans erreur | ☐ | ☐ | |
| A-805 | Charger **VST3** depuis dossier **système** | Pas de crash ; UI plugin visible | ☐ | ☐ | |
| A-806 | Charger **AU** depuis dossier **système** | Pas de crash | ☐ | ☐ | |
| A-807 | Dossier **artefacts** : sous `…/macOS/ARM/` (ou équivalent) | VST3, AU, Standalone présents | ☐ | ☐ | |
| A-808 | Charger **VST3** depuis **artefacts** | Pas de crash | ☐ | ☐ | |
| A-809 | Charger **AU** depuis **artefacts** | Pas de crash | ☐ | ☐ | |
| A-810 | Lancer **Standalone** depuis le dossier **artefacts** | Pas de crash | ☐ | ☐ | |

---

## Phase B — Fumée Luthier (Windows)

**Build testé :** | **Date :**  
**Important :** chemin du projet `SmokeTest` en **ASCII uniquement** (pas d’accents — limitation MSVC).

### B0 — Lancement et shell UI

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| B-001 | Lancer `Luthier.exe` ou `python main.py` | Pas de crash | ☐ | ☐ | |
| B-002 | Onglets | **Project**, **Preferences**, **Templates**, **About** | ☐ | ☐ | |
| B-003 | Chercher **Open Project…** | **Absent** | ☐ | ☐ | |
| B-004 | Barre de statut au-dessus des boutons d’action | Visible | ☐ | ☐ | |

### B1 — Preferences et Workspace

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| B-101 | **Preferences → Workspace** | 6 champs destination + JUCE × 3 OS | ☐ | ☐ | |
| B-102 | Boutons **Choose…** | Uniquement lignes **Windows** | ☐ | ☐ | |
| B-103 | **Choose…** destination Windows → dossier avec accents | Pas d’erreur rouge ; **Saved** possible | ☐ | ☐ | |
| B-104 | JUCE **Windows** renseigné ; chemins plausibles macOS/Linux | Champs valides | ☐ | ☐ | |
| B-105 | Fermer / rouvrir Luthier | 6 valeurs conservées | ☐ | ☐ | |
| B-106 | **Export Preferences…** puis **Import Preferences…** | Profil restauré | ☐ | ☐ | |

### B2 — Accent et apparence

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| B-201 | Onglet **Project** | Pas de sélecteur d’accent | ☐ | ☐ | |
| B-202 | **Preferences → Luthier appearance** : changer preset | Thème à jour sur tous les onglets | ☐ | ☐ | |
| B-203 | Connecteurs sous **Workspace** / **Artefacts** | Visibles | ☐ | ☐ | |

### B3 — Génération initiale (`SmokeTest`)

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| B-301 | **Create New Project** | Formulaire vierge | ☐ | ☐ | |
| B-302 | **Project name** = `SmokeTest` ; **VST3** + **Standalone** (AU coché ne doit **pas** bloquer) | OK | ☐ | ☐ | |
| B-303 | **Artefacts** : copies système + artefacts activées ; chemins renseignés | OK | ☐ | ☐ | |
| B-304 | **Generate Project** | Succès ; chemins affichés avec **`/`** (pas `\`) | ☐ | ☐ | Chemin : |
| B-305 | Contenu du dossier | Fichiers requis présents (cf. A-305) | ☐ | ☐ | |
| B-306 | `.luthier.json` | Workspace OK ; **pas** de `accentColor` | ☐ | ☐ | |

### B4 — Garde-fous Generate

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| B-401 | Fermer / relancer Luthier | OK | ☐ | ☐ | |
| B-402 | **Generate** vers dossier `SmokeTest` existant | Bloqué (modale + barre) | ☐ | ☐ | |
| B-403 | **Create New Project** → `SmokeRegen` → **Generate** | Succès | ☐ | ☐ | |
| B-404 | `git init` + commit dans `SmokeRegen` | `.git/` créé | ☐ | ☐ | |
| B-405 | **Generate** dans dossier avec `.git/` | Pas de WinError / accès refusé | ☐ | ☐ | |
| B-406 | Régénération en session (version `2.0.0`, modale **Yes**) | Succès ; `.git/` préservé | ☐ | ☐ | |

### B5 — Create New Project et dirty guard

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| B-501 | **Create New Project** juste après Generate | Pas de modale unsaved | ☐ | ☐ | |
| B-502 | Modifier champ → **Create New Project** | Modale ; **No** par défaut | ☐ | ☐ | |
| B-503 | Ordre boutons modale **No** / **Yes** | Inversé vs Mac = **mineur** si fonctionnel | ☐ | ☐ | |

### B6 — Templates **(opt.)**

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| B-601 | Override template → Generate nouveau projet | Override visible | ☐ | ☐ | |
| B-602 | **Reset to default** → Generate | Override absent | ☐ | ☐ | |

### B7 — Cursor : build

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| B-701 | Ouvrir dossier `SmokeTest` dans Cursor | Sans accroc | ☐ | ☐ | |
| B-702 | `.vscode/` + configure CMake | Réussie | ☐ | ☐ | |
| B-703 | Preset **`windows-debug`** | Build dir `Builds/Windows` | ☐ | ☐ | |
| B-704 | **CMake: Build** / `Ctrl+Shift+B` | Sans erreur | ☐ | ☐ | |
| B-705 | **Problems** | Pas d’erreur projet | ☐ | ☐ | |
| B-706 | Prompt **UAC** à la copie VST3 système | Cliquer **Yes** ; logs artefacts visibles | ☐ | ☐ | |

### B8 — Standalone et plugins

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| B-801 | **F5** Standalone | Pas de crash | ☐ | ☐ | |
| B-802 | `C:/Program Files/Common Files/VST3/` | VST3 présent | ☐ | ☐ | |
| B-803 | DAW : VST3 **système** | Pas de crash | ☐ | ☐ | |
| B-804 | DAW : VST3 **artefacts** | Pas de crash | ☐ | ☐ | |
| B-805 | Standalone depuis **artefacts** | Pas de crash | ☐ | ☐ | |

---

## Phase C — Fumée Luthier (Linux)

**Build testé :** | **Date :**

### C0 — Lancement et shell UI

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| C-001 | Lancer Luthier | Pas de crash | ☐ | ☐ | |
| C-002 | Onglets + absence **Open Project…** | Conforme | ☐ | ☐ | |
| C-003 | Barre de statut visible | Oui | ☐ | ☐ | |
| C-004 | Icône lanceur / barre des tâches | Visible (ou via `.desktop`) | ☐ | ☐ | Mineur si absent |
| C-005 | Fermer / rouvrir : taille fenêtre | Taille sensiblement conservée ; position non garantie (Wayland = mineur) | ☐ | ☐ | |

### C1 — Preferences et Workspace

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| C-101 | **Workspace** : 6 champs | OK | ☐ | ☐ | |
| C-102 | **Choose…** uniquement lignes **Linux** | OK | ☐ | ☐ | |
| C-103 | Destination avec accents via **Choose…** | Pas d’erreur rouge | ☐ | ☐ | |
| C-104 | JUCE Linux + chemins plausibles autres OS | OK | ☐ | ☐ | |
| C-105 | Fermer / rouvrir ; Export / Import prefs | Valeurs conservées ; import OK | ☐ | ☐ | |

### C2 — Accent et apparence

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| C-201 | Pas d’accent sur **Project** ; preset **Luthier appearance** | Conforme Epic 9 | ☐ | ☐ | |
| C-202 | Connecteurs arbre Workspace / Artefacts | Visibles | ☐ | ☐ | |

### C3 — Génération (`SmokeTest`)

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| C-301 | **Create New Project** → `SmokeTest` ; **VST3** + **Standalone** | OK | ☐ | ☐ | |
| C-302 | **Generate Project** | Succès ; chemins en `/` | ☐ | ☐ | |
| C-303 | Fichiers + `.luthier.json` | Conformes (cf. A-305 / A-306) | ☐ | ☐ | |

### C4 — Garde-fous Generate

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| C-401 | Session fraîche → Generate vers `SmokeTest` existant | Bloqué | ☐ | ☐ | |
| C-402 | `SmokeRegen` + `git init` + régénération session | OK ; `.git/` préservé | ☐ | ☐ | |

### C5 — Dirty guard

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| C-501 | Create New Project après Generate / après modification | Comportement identique A-501 / A-502 | ☐ | ☐ | |

### C6 — Templates **(opt.)**

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| C-601 | Override + Generate + Reset | Conforme A6 | ☐ | ☐ | |

### C7 — Cursor : build

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| C-701 | Ouvrir `SmokeTest` ; preset **`linux-debug`** | `Builds/Linux/Debug` | ☐ | ☐ | |
| C-702 | Build sans erreur ; Problems clean | OK | ☐ | ☐ | |
| C-703 | Logs copie `~/.vst3/` et artefacts | Visibles | ☐ | ☐ | |

### C8 — Standalone et plugins

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| C-801 | **F5** Standalone | Pas de crash | ☐ | ☐ | |
| C-802 | `~/.vst3/` + DAW système | VST3 chargeable | ☐ | ☐ | |
| C-803 | Artefacts + Standalone artefacts | Pas de crash | ☐ | ☐ | |

---

## Phase D — Fumée Git cross-plateforme (projet généré)

Valide que le **projet JUCE** voyage via Git et compile sur chaque OS **sans** rouvrir le projet dans Luthier.  
**Prérequis :** Phases A, B, C terminées (ou au minimum génération OK sur chaque OS).

### D0 — Préparation

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| D-001 | Créer ou vider un dépôt distant `VoyageLuthier` (GitHub ou local) | Dépôt prêt | ☐ | ☐ | URL : |
| D-002 | JUCE installé sur **chaque** machine avec chemins locaux notés | Prêt pour D1–D3 | ☐ | ☐ | |

### D1 — Machine 1 (macOS Apple Silicon) — Création

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| D-101 | Luthier : **Create New Project** → `VoyageLuthier`, v `1.0.0`, **VST3** + **Standalone** + **AU** | Formulaire OK | ☐ | ☐ | |
| D-102 | Workspace + Artefacts renseignés pour **3 OS** ; copies système + artefacts **ON** | OK | ☐ | ☐ | |
| D-103 | **Generate Project** | Dossier + `.luthier.json` | ☐ | ☐ | |
| D-104 | `git init` → `git add .` → `git commit` → `git push` | Dépôt distant à jour | ☐ | ☐ | |
| D-105 | Cursor : preset **`macos-debug-arm64`** → build | Sans erreur ni warning projet | ☐ | ☐ | |
| D-106 | **F5** Standalone + plugins **système** et **artefacts** | Pas de crash | ☐ | ☐ | |

### D2 — Machine 2 (Windows)

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| D-201 | `git clone` du dépôt | Copie locale OK | ☐ | ☐ | |
| D-202 | Éditer `.luthier.json` : **JUCE directory** ligne **Windows** (chemin local) | Fichier sauvegardé | ☐ | ☐ | |
| D-203 | Cursor : **`windows-debug`** → build | Sans erreur | ☐ | ☐ | |
| D-204 | Standalone **F5** + VST3 système + artefacts | Pas de crash | ☐ | ☐ | |
| D-205 | (opt.) Modifier `Source/` → commit → push | Remote à jour | ☐ | ☐ | |

> **Ne pas** utiliser **Generate Project** sur le clone après redémarrage Luthier (dossier non vide). Regénération complète = dossier vide + nouvelle session Luthier sur machine 1, ou régénération **en session** sur machine 1.

### D3 — Machine 3 (Linux)

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| D-301 | `git pull` (ou clone) | À jour | ☐ | ☐ | |
| D-302 | Éditer JUCE **Linux** dans `.luthier.json` | OK | ☐ | ☐ | |
| D-303 | Cursor : **`linux-debug`** → build + plugins | Conforme D-204 | ☐ | ☐ | |
| D-304 | (opt.) commit + push si modifications | OK | ☐ | ☐ | |

### D4 — Retour machine 1 (macOS)

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| D-401 | `git pull` | Sources + `.luthier.json` + `CMakeLists.txt` cohérents | ☐ | ☐ | |
| D-402 | Ajuster JUCE **macOS** si besoin → build + plugins | Toujours OK | ☐ | ☐ | |
| D-403 | Pendant D1–D4 : Luthier utilisé **uniquement en D1** | Aucun plantage Luthier | ☐ | ☐ | |

### D5 — Import Preferences cross-OS **(opt.)**

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| D-501 | Machine A : **Export Preferences…** vers cloud/USB | Fichier partagé | ☐ | ☐ | |
| D-502 | Machine B : **Import Preferences…** | Preferences mises à jour | ☐ | ☐ | |
| D-503 | Onglet **Project** sans **Create New Project** | Formulaire **inchangé** | ☐ | ☐ | |

---

## Critères de réussite (go release v1.0.0)

| ID | Critère | ✅ OK | ❌ KO | Remarques |
| --- | --- | :---: | :---: | --- |
| G-01 | Phase **A** complète (A0–A8, hors opt.) | ☐ | ☐ | |
| G-02 | Phase **B** complète (B0–B8, hors opt.) | ☐ | ☐ | |
| G-03 | Phase **C** complète (C0–C8, hors opt.) | ☐ | ☐ | |
| G-04 | Phase **D** complète (D1–D4 minimum) | ☐ | ☐ | |
| G-05 | **Aucun bloquant** ouvert dans la grille ci-dessous | ☐ | ☐ | |
| G-06 | Mineurs connus acceptés (si présents) | ☐ | ☐ | Voir liste |

**Mineurs acceptés sans échec release :**

- Ordre boutons modales Windows (B-503)
- Position fenêtre Linux non garantie (C-005)
- Icône Linux sans `.desktop` (C-004)
- Warnings compilateur dans headers JUCE tiers uniquement
- Faux positifs CMake Tools « Task has errors » après copie post-build (README projet généré)

---

## Grille des anomalies (à remplir au fil de l’eau)

Pour chaque **❌ KO** significatif, ajouter une ligne. Référencer l’**ID** d’étape (ex. `A-705`).

| # | ID étape | OS | Résumé | Attendu | Obtenu | Gravité | Suite |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | | | | | | bloquant / gênant / mineur | |
| 2 | | | | | | | |
| 3 | | | | | | | |

**Gravité :** **bloquant** = impossible de continuer ou risque perte de données ; **gênant** = contournement pénible ; **mineur** = cosmétique ou cas rare.

---

## Ce qu’il n’est **plus** nécessaire de tester

- Round-trip **Open Project…** → Generate sans changement
- Fidélité byte-for-byte après Open sur une autre machine
- Migration sidecar / Open fallback CMake regex
- Parcours « Open sur Windows → Generate » sur clone Git
- **Luthier sur Mac Intel** (hors périmètre v1.0.0)
- Rejouer en manuel toute la logique déjà couverte par **pytest CI** (sauf décision de double contrôle)

---

## Références

- [Manuel utilisateur (FR)](../../user/manuel-utilisateur.md) — §8 app autonome, §16 workflows, §18 stockage
- [User manual (EN)](../../user/user-manual.md)
- [CONTRIBUTING.md](../../../CONTRIBUTING.md) — build bundle, CI
- README du projet généré (`SmokeTest/README.md`) — presets Cursor, debugging
- [Checklist QA archive (beta)](../1.0.0-beta/checklist-qa-pre-release-v1.md)
