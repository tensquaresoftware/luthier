# Luthier — Smoke test rc4 (Windows uniquement)

**Tag testé :** `1.0.0-rc4`  
**Date :** 10/07/2026  
**Testeur :** Guillaume DUPONT  
**Public :** complément au [smoke test complet](./smoke-test-v1-trois-os.md) — complète **Phase B** (build/regen) et **Phase D2** non validées sous rc2  
**Durée réelle :** ~30 min  
**Résultat :** ✅ **succès** (RC4-G1 à RC4-G3)

Ce guide a couvert les points bloquants sous rc2/rc3 sur Windows :

- Presets CMake **Visual Studio 2026** (défaut)
- **Régénération en session** avec dossier `.git/` (`WinError 32` — corrigé en rc4)
- Build Cursor + plugins + **D2** (clone Git)

**Historique :** rc3 corrigeait déjà les presets VS 2026 mais le WinError 32 persistait ; rc4 introduit le swap **`Project` → `Project.old`** dans `core/project_writer.py`.

---

## Prérequis

| Élément | Attendu |
| --- | --- |
| **OS** | Windows 10+ |
| **Visual Studio** | **2026** — workload *Desktop development with C++* |
| **CMake** | **4.2+** (`cmake --version`) — requis pour le preset `windows-debug` |
| **Cursor / VS Code** | Extensions **CMake Tools** + **C/C++** |
| **JUCE** | Checkout complet (ex. `C:/Users/Guillaume/Dev/SDKs/JUCE`) |
| **Luthier rc4** | Zip `Luthier-1.0.0-rc4-windows.zip` depuis [GitHub Releases](https://github.com/tensquaresoftware/luthier/releases) |
| **Prefs maître** | `luthier-smoke-prefs.json` (Phase P du smoke complet) |
| **DAW ou AudioPluginHost** | Pour charger le VST3 |

**Chemin projet :** ASCII uniquement (ex. `C:/Users/Guillaume/Desktop/SmokeTest`) — pas d’accents (limitation MSVC).

**Legacy VS 2022 :** si tu n’as **pas** VS 2026, génère le projet avec Luthier rc4 puis sélectionne le preset **`windows-debug-vs2022`** (CMake 3.22+ suffit).

---

## R0 — Obtenir rc4

| ID | Action | ✅ OK | ❌ KO | Remarques |
| --- | --- | :---: | :---: | --- |
| R0-01 | Télécharger `Luthier-1.0.0-rc4-windows.zip` | ✅ | ☐ | |
| R0-02 | Extraire → lancer `Luthier.exe` ou `--check` | ✅ | ☐ | |
| R0-03 | **About** → version `1.0.0-rc4` | ✅ | ☐ | |

---

## W1 — Génération (rappel rapide)

| ID | Action | ✅ OK | ❌ KO | Remarques |
| --- | --- | :---: | :---: | --- |
| W1-01 | **Import Preferences…** (fichier maître Phase P) | ✅ | ☐ | |
| W1-02 | **Create New Project** → `SmokeTest` → **Generate Project** | ✅ | ☐ | Destination ASCII — Bureau |
| W1-03 | Vérifier `CMakeUserPresets.json` : preset `windows-debug` = **Visual Studio 18 2026** | ✅ | ☐ | Vérifié avec Notepad++ |

> Projet **nouveau** généré avec rc4 requis — un `SmokeTest` créé sous rc2/rc3 garde les anciens presets VS 2022.

---

## W2 — Régénération avec `.git/` (correctif WinError)

**Contexte :** rc2 et rc3 échouaient avec `WinError 32` après `git init` + regen en session. **rc4** remplace l’arborescence par un **rename aside** (`SmokeRegen.old`) au lieu de supprimer `.git` sur place.

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| W2-01 | **Create New Project** → `SmokeRegen` → **Generate Project** | Succès | ✅ | ☐ | Même session Luthier |
| W2-02 | Dans `SmokeRegen` : `git init`, `git add .`, `git commit -m "init"` | `.git/` créé | ✅ | ☐ | |
| W2-03 | Luthier : **Version** → `2.0.0` → **Generate Project** | Modale **Regenerate Project** ; défaut **No** | ✅ | ☐ | |
| W2-04 | Choisir **Yes** | Succès — **pas** de `WinError 32` | ✅ | ☐ | |
| W2-05 | Sur disque : version `2.0.0` dans les sources ; dossier `.git/` **présent** | Conforme | ✅ | ☐ | `git log` : commit init conservé |

> **Conseil :** fermer Cursor/Explorateur sur le dossier avant W2-04 limite les verrous fichiers Windows.

**Équivalent smoke complet :** B-405, B-406.

---

## W3 — Build Cursor (VS 2026)

Projet cible : **`SmokeTest`** (W1-02).

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| W3-01 | Cursor → **Open Folder** → `SmokeTest` | Sans erreur | ✅ | ☐ | |
| W3-02 | **CMake: Select Configure Preset** → **`windows-debug`** | Configure OK | ✅ | ☐ | |
| W3-03 | **CMake: Build** / `Ctrl+Shift+B` | Build sans erreur | ✅ | ☐ | |
| W3-04 | **Problems** | Pas d’erreur projet | ✅ | ☐ | |
| W3-05 | Prompt **UAC** copie VST3 système → **Yes** | Logs copie visibles | ✅ | ☐ | |
| W3-06 | **F5** Standalone | Pas de crash | ✅ | ☐ | |
| W3-07 | VST3 dans `C:/Program Files/Common Files/VST3/` + dossier **artefacts** | Présents ; chargement DAW OK | ✅ | ☐ | |

**Équivalent smoke complet :** B-701 à B-706, B-801 à B-805.

---

## W4 — Phase D2 (clone Git, sans Luthier)

**Prérequis :** dépôt `VoyageLuthier` poussé depuis macOS (smoke complet D1).

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| W4-01 | `git clone` du dépôt | Copie locale OK | ✅ | ☐ | |
| W4-02 | Éditer `.luthier.json` : **`juceDirWindows`** → chemin JUCE local | Sauvegardé | ✅ | ☐ | Ne pas rouvrir dans Luthier |
| W4-03 | Cursor → preset **`windows-debug`** → build | Sans erreur | ✅ | ☐ | |
| W4-04 | Standalone **F5** + VST3 système + artefacts | Pas de crash | ✅ | ☐ | |

**Équivalent smoke complet :** D-201 à D-204.

---

## Critères de réussite rc4 (Windows)

| ID | Critère | ✅ OK | ❌ KO |
| --- | --- | :---: | :---: |
| RC4-G1 | W2 — regen avec `.git/` sans WinError | ✅ | ☐ |
| RC4-G2 | W3 — build + Standalone + VST3 | ✅ | ☐ |
| RC4-G3 | W4 — clone Git + build Windows | ✅ | ☐ |

**Verdict :** les trois critères sont ✅ — le smoke test complet peut passer **G-02**, **G-04** et **G-05** à ✅ (voir [smoke test complet](./smoke-test-v1-trois-os.md)).

---

## Références

- [Smoke test complet 3 OS](./smoke-test-v1-trois-os.md)
- README généré du projet (`SmokeTest/README.md`) — prérequis Windows VS 2026
