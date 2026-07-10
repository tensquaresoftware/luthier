# Luthier — Smoke test complet (3 OS)

**Version / tag visé :** _indiquer le tag testé (ex. `1.0.0-rc1`, `1.0.0`)_  
**Révision About attendue :** cohérente avec le tag testé  
**Public :** testeur — parcours autonome, exécutable étape par étape  
**Langue de l’app :** anglais (libellés cités tels qu’à l’écran)

---

## Comment utiliser ce guide

1. **Remplis la fiche de session** (section suivante) avant de commencer.
2. **Exécute les phases dans l’ordre** **P** → **A** → **B** → **C** → **D** (D peut attendre la fin de A/B/C).
   - **Phase P** : onglet **Preferences** uniquement (profil réaliste + fichier partagé entre les 3 OS) — **sans** Generate.
   - **Phases A / B / C** : onglet **Project** (génération, build, DAW) — **Import** du fichier prefs maître au départ.
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
| **Testeur** | Guillaume DUPONT |
| **Date de début** | 09/07/2026 |
| **Commit / tag testé** | `1.0.0-rc2` (smoke complet) — correctifs VS 2026 + WinError → **`1.0.0-rc3`** |
| **Source du build Luthier** | GitHub Release — artefacts du tag testé (`.github/workflows/release.yml`) |
| **CI GitHub** (pytest 3 OS) | ✅ verte sur le commit testé ☐ non vérifiée |
| **DAW utilisé** | ☐ Ableton Live ☐ JUCE AudioPluginHost ✅ les deux |
| **Cursor / VS Code** | Version : Cursor 3.10.20 (Universal) |
| **Machine de dev** | MacBook Pro M5 (2025) / macOS Tahoe 26.5.1 |
| **Fichier prefs partagé** | `/Users/Guillaume/Library/CloudStorage/Dropbox/Dev/Tests/Luthier/luthier-smoke-prefs.json` |

### Avancement par phase

| Phase | Description | Durée ~ | ✅ Terminée | Date | Bloquants ouverts |
| --- | --- | --- | :---: | --- | --- |
| **P** | Preferences (3 OS + fichier partagé) | 60 min | ✅ | 09–10/07/2026 | — |
| **A** | Project — fumée macOS (Apple Silicon) | 45 min | ✅ | 09/07/2026 | — |
| **B** | Project — fumée Windows | 45 min | ⚠️ | 10/07/2026 | Build Cursor (VS 2026) ; WinError regen — retest **rc3** |
| **C** | Project — fumée Linux | 45 min | ✅ | 10/07/2026 | — |
| **D** | Git cross-OS (projet généré) | 45 min | ⚠️ | 10/07/2026 | D2 Windows (VS) ; D-302 clarifié ci-dessous |

---

## Ce que la CI fait déjà (ne pas re-tester ici)

La CI (`.github/workflows/pytest.yml`) exécute **pytest sur Ubuntu, Windows et macOS** à chaque push/PR. Tu n’as **pas** à rejouer manuellement la logique couverte par les tests automatisés (garde-fous Generate, dirty guard, preferences, génération de fichiers, etc.) **sauf** si tu veux une double validation avant release.

La **CD release** (`.github/workflows/release.yml`) construit et publie les bundles PyInstaller sur chaque tag semver. Tu n’as **pas** à builder localement pour ce smoke test.

**Ce guide couvre ce que la CI/CD ne voit pas :** UI réelle sur bundle release, dialogues fichiers, quarantaine macOS, Cursor/CMake Tools, build JUCE du projet généré, chargement DAW, copies vers dossiers système/artefacts.

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
| Chemins Workspace (JUCE, destination) | ⚠️ Par machine | Phase **P** : profil réaliste + **Export / Import** sur les 3 OS → fichier maître avant toute génération |

**macOS — périmètre app Luthier :** l’application autonome `Luthier.app` requiert un Mac **Apple Silicon (arm64)**. Les Mac Intel ne sont **pas** pris en charge pour l’app. Les **projets générés** restent compilables pour Mac Intel via les presets CMake `macos-debug-x86_64` (hors scope de ce smoke test pour la Phase A).

---

## Prérequis communs (toutes phases)

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| P-01 | Vérifier **Git** installé (`git --version`) | Version affichée | ✅ | ☐ | Requis Phase D |
| P-02 | Vérifier **CMake** ≥ 3.22 (`cmake --version`) | Version ≥ 3.22 | ✅ | ☐ | |
| P-03 | Vérifier compilateur + **Ninja** (macOS/Linux) ou **VS 2026 + CMake 4.2+** (Windows ; legacy VS 2022 + CMake 3.22 : presets `windows-*-vs2022`) | Outil disponible | ✅ | ☐ | Sous rc2 : VS 2026 installé mais presets ciblent VS 2022 — corrigé en **rc3** |
| P-04 | Installer **Cursor** (ou VS Code) + extensions **CMake Tools** et **C/C++** | Extensions actives | ✅ | ☐ | |
| P-05 | Préparer un dossier de travail **avec accents** possible (ex. `Téléchargements/été 2026`) | Dossier créé | ✅ | ☐ | Valide les chemins UI Luthier |
| P-06 | Installer / localiser **JUCE** (checkout complet, pas seulement headers) | Chemin noté ci-dessous | ✅ | ☐ | |
| P-07 | Préparer **Ableton Live** *ou* build **AudioPluginHost** JUCE (`extras/AudioPluginHost`) | Au moins un outil prêt | ✅ | ☐ | |
| P-08 | Télécharger et extraire le zip GitHub Release pour l’OS en cours (section **Obtenir le build**) | Build prêt avant Phase P sur chaque machine | ✅ | ☐ | |

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

## Obtenir le build Luthier (GitHub Release — avant chaque phase OS)

Ce smoke test valide les **artefacts publiés par la CD** sur tag semver — pas un build local. Après `git push origin <tag>`, la CI publie une [GitHub Release](https://github.com/tensquaresoftware/luthier/releases) avec quatre zips : `Luthier-<tag>-{macos,windows,linux,docs}.zip`.

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| R-01 | Ouvrir la Release du **tag testé** sur GitHub | Release marquée **Pre-release** si le tag contient un suffixe (`-rc1`, `-beta2`, …) | ✅ | ☐ | |
| R-02 | Télécharger `Luthier-<tag>-macos.zip` (Phases **P-A** et **A**), `-windows.zip` (**P-B** / **B**), `-linux.zip` (**P-C** / **C**) | Archives présentes ; taille non nulle | ✅ | ☐ | |
| R-03 | **macOS :** extraire le zip → `Luthier.app` ; si « est endommagé » : `xattr -cr /chemin/vers/Luthier.app` puis lancer ; sinon `--check` | Code **0** sur `--check` ; app démarre | ✅ | ☐ | Quarantaine navigateur = normal sur build non signé |
| R-04 | **Windows :** extraire → `Luthier\Luthier.exe` ; lancer ou `--check` | Code **0** ; app démarre | ✅ | ☐ | |
| R-05 | **Linux :** extraire → `Luthier/Luthier` exécutable ; lancer ou `--check` | Code **0** ; app démarre | ✅ | ☐ | |
| R-06 | Onglet **About** sur chaque OS | Version = **tag testé** ; date de révision cohérente | ✅ | ☐ | |

---

## Phase P — Preferences (3 OS, fichier partagé)

**Objectif :** valider l’onglet **Preferences** avec un profil proche d’un **cas d’usage réel**, puis constituer `luthier-smoke-prefs.json` en le faisant voyager sur les **trois machines**. **Ne pas** ouvrir l’onglet **Project** ni cliquer **Generate Project** pendant la Phase P.

**Ordre obligatoire :** **P-A** (macOS) → **Export** → **P-B** (Windows) → **Export** → **P-C** (Linux) → **Export maître** → Phases **A / B / C** (Project).

**Fichier cible :** `luthier-smoke-prefs.json` (Dropbox, USB, etc.) — noter le chemin dans la fiche de session.

**Règle Workspace :** sur chaque OS, ne renseigner que les lignes **hôte** (destination + JUCE via **Choose…** quand disponible). Les chemins des autres OS arrivent via **Import** des étapes précédentes.

**Profil réaliste suggéré** (adapter à ton environnement ; voir aussi [Chemins de référence](#chemins-de-référence-adapté-à-ta-machine)) :

| Zone Preferences | Valeurs suggérées |
| --- | --- |
| **Plugin identity** | Fabricant *Ten Square Software* (ou le tien) ; codes fabricant/plugin via **Generate** ; site et e-mail plausibles |
| **Formats par défaut** | **VST3** + **AU** + **Standalone** cochés |
| **Workspace (OS hôte)** | Destination avec accents (test chemins UI) ; JUCE = chemin réel du SDK |
| **Artefacts** | **Copy to system folders** + **Copy to central artefacts folder** ON ; chemins **OS hôte** (dossier artefacts cloud si tu l’utilises) |
| **Luthier appearance** | Changer de preset d’accent ; vérifier connecteurs arbre sous Workspace / Artefacts |

---

### P-A — macOS (Apple Silicon)

**Prérequis :** R-01 à R-03 (build release extrait).

#### P-A-0 — Lancement (shell, sans Project)

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| P-A-001 | Lancer Luthier (double-clic `Luthier.app`) | Pas de crash | ✅ | ☐ | |
| P-A-002 | Parcourir les onglets | **Project**, **Preferences**, **Templates**, **About** visibles | ✅ | ☐ | |
| P-A-003 | Chercher **Open Project…** | **Absent** partout | ✅ | ☐ | |
| P-A-004 | Zone au-dessus des boutons d’action (**Create New Project** / **Generate Project**) | **Aucun** message tant qu’aucune action Project (barre repliée) | ✅ | ☐ | |

#### P-A-1 — Onglet Preferences (profil réaliste, macOS)

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| P-A-101 | **Preferences → Workspace** | 6 champs : destination + JUCE × 3 OS | ✅ | ☐ | |
| P-A-102 | Boutons **Choose…** | Uniquement lignes **macOS** | ✅ | ☐ | |
| P-A-103 | **Choose…** destination **macOS** → dossier **avec accents** | Pas d’erreur rouge ; badge **Saved** possible | ✅ | ☐ | |
| P-A-104 | JUCE **macOS** (chemin réel). **Ne pas** saisir Windows/Linux à la main | Champ accepté | ✅ | ☐ | |
| P-A-110 | **Plugin identity** : fabricant, codes (**Generate**), site, e-mail — profil crédible | Pas d’erreur rouge | ✅ | ☐ | |
| P-A-111 | **Formats par défaut** : **VST3** + **AU** + **Standalone** | Cochés sans conflit | ✅ | ☐ | |
| P-A-120 | **Artefacts** : copies système + central **ON** ; chemins **macOS** réels | Champs valides | ✅ | ☐ | |
| P-A-130 | **Luthier appearance** : changer preset | Thème à jour sur tous les onglets | ✅ | ☐ | |
| P-A-131 | Connecteurs arbre sous **Workspace** / **Artefacts** | Visibles | ✅ | ☐ | |

#### P-A-2 — Persistance, Export, Import

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| P-A-150 | Fermer Luthier, relancer | Preferences **macOS** conservées | ✅ | ☐ | |
| P-A-160 | **Export Preferences…** → `luthier-smoke-prefs.json` | Fichier créé (v1 — macOS seul) | ✅ | ☐ | Copier vers stockage partagé |
| P-A-170 | Modifier une pref → **Import Preferences…** (fichier P-A-160) | Profil restauré (round-trip) | ✅ | ☐ | |

---

### P-B — Windows

**Prérequis :** R-04 ; fichier exporté en **P-A-160**.

#### P-B-0 — Lancement

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| P-B-001 | Lancer `Luthier\Luthier.exe` | Pas de crash | ✅ | ☐ | |
| P-B-002 | Onglets + absence **Open Project…** | Conforme | ✅ | ☐ | |
| P-B-003 | Barre de statut (zone boutons Project) | Repliée (aucune action Project) | ✅ | ☐ | |

#### P-B-1 — Import + compléter Preferences (Windows)

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| P-B-101 | **Import Preferences…** (`luthier-smoke-prefs.json` v1) | Profil macOS + identity + formats + appearance restaurés | ✅ | ☐ | |
| P-B-102 | **Choose…** uniquement lignes **Windows** | Conforme | ✅ | ☐ | |
| P-B-103 | Destination **Windows** (accents via **Choose…**) | Pas d’erreur rouge | ✅ | ☐ | |
| P-B-104 | JUCE **Windows** (chemin réel) | Champ accepté | ✅ | ☐ | |
| P-B-120 | **Artefacts** : chemins **Windows** réels (si activés en P-A) | Champs valides | ✅ | ☐ | |
| P-B-130 | Vérifier **Luthier appearance** + connecteurs arbre | Inchangés / cohérents après Import | ✅ | ☐ | |

#### P-B-2 — Export

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| P-B-150 | Fermer / rouvrir | Valeurs conservées | ✅ | ☐ | |
| P-B-160 | **Export Preferences…** → mettre à jour `luthier-smoke-prefs.json` | v2 — macOS + Windows | ✅ | ☐ | |

---

### P-C — Linux

**Prérequis :** R-05 ; fichier exporté en **P-B-160**.

#### P-C-0 — Lancement

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| P-C-001 | Lancer Luthier | Pas de crash | ✅ | ☐ | |
| P-C-002 | Onglets + absence **Open Project…** | Conforme | ✅ | ☐ | |
| P-C-003 | Barre de statut | Repliée | ✅ | ☐ | |
| P-C-004 | Icône lanceur / barre des tâches | Visible (ou `.desktop`) | ✅ | ☐ | Mineur si absent |

#### P-C-1 — Import + compléter Preferences (Linux)

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| P-C-101 | **Import Preferences…** (v2) | Chemins **macOS** + **Windows** + profil identity présents | ✅ | ☐ | |
| P-C-102 | **Choose…** uniquement lignes **Linux** | OK | ✅ | ☐ | |
| P-C-103 | Destination **Linux** (accents via **Choose…**) | Pas d’erreur rouge | ✅ | ☐ | |
| P-C-104 | JUCE **Linux** (chemin réel) | Champ accepté | ✅ | ☐ | |
| P-C-120 | **Artefacts** : chemins **Linux** réels | Champs valides | ✅ | ☐ | |

#### P-C-2 — Export maître

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| P-C-150 | Fermer / rouvrir ; **Import** round-trip (fichier C-160) | OK | ✅ | ☐ | |
| P-C-160 | **Export Preferences…** → **`luthier-smoke-prefs.json` maître** | **6 chemins Workspace réels** + profil réaliste complet | ✅ | ☐ | Utiliser pour Phases A/B/C |

---

## Phase A — Project (macOS Apple Silicon)

**Machine :** Mac **Apple Silicon** (M1/M2/M3/M4…) — **pas** Mac Intel.  
**Build testé :** 1.0.0-rc2 | **Date :** 09/07/2026  
**Prérequis :** Phase **P** terminée ; fichier **`luthier-smoke-prefs.json` maître** (P-C-160).

### A0 — Préparation (Import prefs, onglet Project)

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| A-001 | Lancer Luthier (ou reprendre après Phase P-A) | Pas de crash | ✅ | ☐ | Shell UI déjà couvert en P-A-001–004 |
| A-002 | **Import Preferences…** (fichier maître P-C-160) | 6 chemins Workspace + identity + formats + appearance restaurés | ✅ | ☐ | |
| A-003 | **Preferences** : vérifier profil Phase P (identity, formats, Artefacts macOS) | Conforme sans resaisie manuelle | ✅ | ☐ | |
| A-004 | Onglet **Project** | **Aucun** sélecteur de couleur d’accent ; barre de statut repliée tant qu’aucune action Project | ✅ | ☐ | |

### A3 — Génération initiale (`SmokeTest`)

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| A-301 | **Create New Project** | Formulaire vierge, valeurs par défaut des Preferences ; message de statut visible au-dessus des boutons d’action (ex. *New project — defaults from Preferences.*) | ✅ | ☐ | |
| A-302 | **Project name** = `SmokeTest` ; formats hérités des Preferences (VST3 + AU + Standalone si configurés en P-A) | Formats cochés sans conflit UI | ✅ | ☐ | |
| A-303 | **Artefacts** : options et chemins déjà renseignés en Phase P — vérifier cohérence **macOS** | Champs valides | ✅ | ☐ | |
| A-304 | **Generate Project** | Succès ; message avec chemin en **`/`** (slashes avant) | ✅ | ☐ | Noter le chemin absolu : '/Users/Guillaume/Desktop/été 2026/SmokeTest' |
| A-305 | Ouvrir le dossier généré dans le Finder | Présents : `CMakeLists.txt`, `CMakeUserPresets.json`, `Source/`, `.luthier.json`, `.gitignore`, `README.md`, `.vscode/`, `.cursorrules` | ✅ | ☐ | |
| A-306 | Ouvrir `.luthier.json` | Chemins Workspace présents ; **pas** de clé `accentColor` | ✅ | ☐ | |

### A4 — Garde-fous Generate

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| A-401 | **Fermer et relancer Luthier** (session fraîche) | App redémarre normalement | ✅ | ☐ | |
| A-402 | Sans changer la destination : **Project name** = `SmokeTest` → **Generate Project** | **Bloqué** : modale + barre *This folder already exists and is not empty…* | ✅ | ☐ | |
| A-403 | **Create New Project** → **Project name** = `SmokeRegen` → **Generate Project** | Succès dans un **nouveau** dossier | ✅ | ☐ | |
| A-404 | Dans le dossier `SmokeRegen` : `git init`, `git add .`, `git commit -m "init"` | Dépôt Git initialisé | ✅ | ☐ | Prépare le test suivant |
| A-405 | **Sans fermer Luthier** : sur `SmokeRegen`, changer **Version** → `2.0.0` → **Generate Project** | Modale **Regenerate Project** ; défaut **No** ; choisir **Yes** → succès | ✅ | ☐ | |
| A-406 | Vérifier sur disque | Fichiers reflètent `2.0.0` ; dossier `.git/` **toujours présent** | ✅ | ☐ | |

### A5 — Create New Project et dirty guard

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| A-501 | Juste après un **Generate** réussi : cliquer **Create New Project** | **Pas** de modale « unsaved changes » | ✅ | ☐ | |
| A-502 | Modifier un champ (ex. version) **sans** générer → **Create New Project** | Modale de confirmation ; bouton **No** par défaut ; **No** annule, **Yes** réinitialise | ✅ | ☐ | |

### A6 — Templates **(opt.)**

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| A-601 | **Templates** → override `PluginProcessor.cpp` → **Save override** | Override enregistré | ✅ | ☐ | |
| A-602 | **Create New Project** → nouveau nom → **Generate Project** | Override visible dans les sources générées | ✅ | ☐ | |
| A-603 | **Reset to default** → nouvelle génération | Plus d’override dans les sources | ✅ | ☐ | |

### A7 — Cursor : ouverture, presets, build

**Projet cible :** dossier `SmokeTest` créé en A-304.

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| A-701 | Cursor → **File → Open Folder…** → dossier `SmokeTest` | Ouverture sans erreur bloquante | ✅ | ☐ | |
| A-702 | Vérifier `.vscode/` | `settings.json`, `tasks.json`, `launch.json` présents | ✅ | ☐ | |
| A-703 | Attendre la fin de la configuration CMake (barre de statut) | Configure **réussie** (pas d’échec rouge) | ✅ | ☐ | |
| A-704 | Palette (`Cmd+Shift+P`) → **CMake: Select Configure Preset** | Presets **macOS** listés (`macos-debug-arm64`, `macos-release-arm64`, …) | ✅ | ☐ | |
| A-705 | Sélectionner **`macos-debug-arm64`** | Dossier de build cohérent (ex. `Builds/macOS/ARM/Debug`) | ✅ | ☐ | **Ne pas** utiliser `macos-debug-x86_64` sur ce test (host ARM) sauf test Rosetta volontaire |
| A-706 | **CMake: Build** ou `Cmd+Shift+B` | Build **sans erreur** | ✅ | ☐ | |
| A-707 | Panneau **Problems** | Aucune **erreur** ; aucun warning **du projet** (warnings headers JUCE tiers = noter mineur) | ✅ | ☐ | |
| A-708 | Logs de build / terminal | Traces de copie vers dossiers **système** et **artefacts** visibles | ✅ | ☐ | |

### A8 — Standalone et chargement plugins

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| A-801 | **Run and Debug** → config **Standalone** → **F5** | Standalone s’ouvre **sans crash** ; fermeture propre | ✅ | ☐ | |
| A-802 | Finder : `~/Library/Audio/Plug-Ins/VST3/` | `SmokeTest.vst3` (ou nom équivalent) présent | ✅ | ☐ | |
| A-803 | Finder : `~/Library/Audio/Plug-Ins/Components/` | `SmokeTest.component` présent | ✅ | ☐ | |
| A-804 | DAW : rescan plugins si nécessaire | Scan terminé sans erreur | ✅ | ☐ | Testé avec Ableton Live 12 |
| A-805 | Charger **VST3** depuis dossier **système** | Pas de crash ; UI plugin visible | ✅ | ☐ | Testé avec Ableton Live 12 |
| A-806 | Charger **AU** depuis dossier **système** | Pas de crash | ✅ | ☐ | Testé avec Ableton Live 12 |
| A-807 | Dossier **artefacts** : sous `…/macOS/ARM/` (ou équivalent) | VST3, AU, Standalone présents | ✅ | ☐ | |
| A-808 | Charger **VST3** depuis **artefacts** | Pas de crash | ✅ | ☐ | Testé avec AudioHostPlugin |
| A-809 | Charger **AU** depuis **artefacts** | Pas de crash | ✅ | ☐ | Testé avec AudioHostPlugi |
| A-810 | Lancer **Standalone** depuis le dossier **artefacts** | Pas de crash | ✅ | ☐ | |

---

## Phase B — Project (Windows)

**Build testé :** 1.0.0-rc2 | **Date :** 10/07/2026 
**Important :** chemin du projet `SmokeTest` en **ASCII uniquement** (pas d’accents — limitation MSVC) : projets générés sur le Bureau.  
**Prérequis :** Phase **P** terminée ; fichier prefs maître (P-C-160).

### B0 — Préparation (Import prefs)

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| B-001 | Lancer Luthier (shell UI : cf. P-B-001–003) | Pas de crash | ✅ | ☐ | |
| B-002 | **Import Preferences…** (fichier maître P-C-160) | Profil complet restauré (6 chemins Workspace + identity + appearance) | ✅ | ☐ | |
| B-003 | **Preferences** : vérifier sans resaisie (Artefacts Windows si activés en P-B) | Conforme | ✅ | ☐ | |

### B3 — Génération initiale (`SmokeTest`)

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| B-301 | **Create New Project** | Formulaire vierge ; message de statut visible au-dessus des boutons d’action (ex. *New project — defaults from Preferences.*) | ✅ | ☐ | |
| B-302 | **Project name** = `SmokeTest` ; formats hérités des Preferences | OK | ✅ | ☐ | |
| B-303 | **Artefacts** : vérifier cohérence depuis Phase P | OK | ✅ | ☐ | |
| B-304 | **Generate Project** | Succès ; chemins affichés avec **`/`** (pas `\`) | ✅ | ☐ | Chemin : C:/Users/Guillaume/Desktop |
| B-305 | Contenu du dossier | Fichiers requis présents (cf. A-305) | ✅ | ☐ | |
| B-306 | `.luthier.json` | Workspace OK ; **pas** de `accentColor` | ✅ | ☐ | |

### B4 — Garde-fous Generate

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| B-401 | Fermer / relancer Luthier | OK | ✅ | ☐ | |
| B-402 | **Generate** vers dossier `SmokeTest` existant | Bloqué (modale + barre) | ✅ | ☐ | |
| B-403 | **Create New Project** → `SmokeRegen` → **Generate** | Succès | ✅ | ☐ | |
| B-404 | `git init` + commit dans `SmokeRegen` | `.git/` créé | ✅ | ☐ | |
| B-405 | **Generate** dans dossier avec `.git/` | Pas de WinError / accès refusé | ☐ | ❌ | rc2 : `WinError 32` — correctif `project_writer` + retest **rc3** |
| B-406 | Régénération en session (version `2.0.0`, modale **Yes**) | Succès ; `.git/` préservé | ☐ | ❌ | Même erreur rc2 — retest **rc3** |

### B5 — Create New Project et dirty guard

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| B-501 | **Create New Project** juste après Generate | Pas de modale unsaved | ✅ | ☐ | |
| B-502 | Modifier champ → **Create New Project** | Modale ; **No** par défaut | ✅ | ☐ | |
| B-503 | Ordre boutons modale **No** / **Yes** | Inversé vs Mac = **mineur** si fonctionnel | ✅ | ☐ | |

### B6 — Templates **(opt.)**

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| B-601 | Override template → Generate nouveau projet | Override visible | ✅ | ☐ | |
| B-602 | **Reset to default** → Generate | Override absent | ✅ | ☐ | |

### B7 — Cursor : build

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| B-701 | Ouvrir dossier `SmokeTest` dans Cursor | Sans accroc | ☐ | ❌ | rc2 : preset VS 2022 — retest **rc3** avec `windows-debug` (VS 2026) |
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

## Phase C — Project (Linux)

**Build testé :** | **Date :**  
**Prérequis :** Phase **P** terminée ; fichier prefs maître (P-C-160).

### C0 — Préparation (Import prefs)

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| C-001 | Lancer Luthier (shell UI : cf. P-C-001–004) | Pas de crash | ✅ | ☐ | |
| C-002 | **Import Preferences…** (fichier maître P-C-160) | Profil complet restauré | ✅ | ☐ | |
| C-003 | Fermer / rouvrir : taille fenêtre | Taille sensiblement conservée ; position non garantie (Wayland = mineur) | ✅ | ☐ | |

### C3 — Génération (`SmokeTest`)

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| C-301 | **Create New Project** → `SmokeTest` ; **VST3** + **Standalone** | OK ; message de statut visible après **Create New Project** (ex. *New project — defaults from Preferences.*) | ✅ | ☐ | |
| C-302 | **Generate Project** | Succès ; chemins en `/` | ✅ | ☐ | |
| C-303 | Fichiers + `.luthier.json` | Conformes (cf. A-305 / A-306) | ✅ | ☐ | |

### C4 — Garde-fous Generate

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| C-401 | Session fraîche → Generate vers `SmokeTest` existant | Bloqué | ✅ | ☐ | |
| C-402 | `SmokeRegen` + `git init` + régénération session | OK ; `.git/` préservé | ✅ | ☐ | |

### C5 — Dirty guard

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| C-501 | Create New Project après Generate / après modification | Comportement identique A-501 / A-502 | ✅ | ☐ | |

### C6 — Templates **(opt.)**

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| C-601 | Override + Generate + Reset | Conforme A6 | ✅ | ☐ | |

### C7 — Cursor : build

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| C-701 | Ouvrir `SmokeTest` ; preset **`linux-debug`** | `Builds/Linux/Debug` | ✅ | ☐ | |
| C-702 | Build sans erreur ; Problems clean | OK | ✅ | ☐ | |
| C-703 | Logs copie `~/.vst3/` et artefacts | Visibles | ✅ | ☐ | |

### C8 — Standalone et plugins

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| C-801 | **F5** Standalone | Pas de crash | ✅ | ☐ | |
| C-802 | `~/.vst3/` + DAW système | VST3 chargeable | ✅ | ☐ | Testé avec AudioHostPlugin |
| C-803 | Artefacts + Standalone artefacts | Pas de crash | ✅ | ☐ | |

---

## Phase D — Fumée Git cross-plateforme (projet généré)

Valide que le **projet JUCE** voyage via Git et compile sur chaque OS **sans** rouvrir le projet dans Luthier.  
**Prérequis :** Phases A, B, C terminées (ou au minimum génération OK sur chaque OS).

### D0 — Préparation

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| D-001 | Créer ou vider un dépôt distant `VoyageLuthier` (GitHub ou local) | Dépôt prêt | ✅ | ☐ | URL : |
| D-002 | JUCE installé sur **chaque** machine avec chemins locaux notés | Prêt pour D1–D3 | ✅ | ☐ | |

### D1 — Machine 1 (macOS Apple Silicon) — Création

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| D-101 | Luthier : **Create New Project** → `VoyageLuthier`, v `1.0.0`, **VST3** + **Standalone** + **AU** | Formulaire OK | ✅ | ☐ | |
| D-102 | Workspace + Artefacts renseignés pour **3 OS** ; copies système + artefacts **ON** | OK | ✅ | ☐ | |
| D-103 | **Generate Project** | Dossier + `.luthier.json` | ✅ | ☐ | |
| D-104 | `git init` → `git add .` → `git commit` → `git push` | Dépôt distant à jour | ✅ | ☐ | |
| D-105 | Cursor : preset **`macos-debug-arm64`** → build | Sans erreur ni warning projet | ✅ | ☐ | |
| D-106 | **F5** Standalone + plugins **système** et **artefacts** | Pas de crash | ✅ | ☐ | |

### D2 — Machine 2 (Windows)

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| D-201 | `git clone` du dépôt | Copie locale OK | ☐ | ☐ | Retest **rc3** Windows (guide dédié) |
| D-202 | Éditer `.luthier.json` : **JUCE directory** ligne **Windows** (chemin local) | Fichier sauvegardé | ☐ | ☐ | |
| D-203 | Cursor : **`windows-debug`** → build | Sans erreur | ☐ | ☐ | |
| D-204 | Standalone **F5** + VST3 système + artefacts | Pas de crash | ☐ | ☐ | |
| D-205 | (opt.) Modifier `Source/` → commit → push | Remote à jour | ☐ | ☐ | |

> **Ne pas** utiliser **Generate Project** sur le clone après redémarrage Luthier (dossier non vide). Regénération complète = dossier vide + nouvelle session Luthier sur machine 1, ou régénération **en session** sur machine 1.

### D3 — Machine 3 (Linux)

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| D-301 | `git pull` (ou clone) | À jour | ✅ | ☐ | |
| D-302 | Éditer JUCE **Linux** dans `.luthier.json` | OK | ✅ | ☐ | Voir encadré **D-302** ci-dessous |
| D-303 | Cursor : **`linux-debug`** → build + plugins | Conforme D-204 | ✅ | ☐ | |
| D-304 | (opt.) commit + push si modifications | OK | ✅ | ☐ | J'ai modifié le texte de la GUI en "Voyage Luthier - Linux" |

### D4 — Retour machine 1 (macOS)

| ID | Action | Résultat attendu | ✅ OK | ❌ KO | Remarques |
| --- | --- | --- | :---: | :---: | --- |
| D-401 | `git pull` | Sources + `.luthier.json` + `CMakeLists.txt` cohérents | ✅ | ☐ | |
| D-402 | Ajuster JUCE **macOS** si besoin → build + plugins | Toujours OK | ✅ | ☐ | |
| D-403 | Pendant D1–D4 : Luthier utilisé **uniquement en D1** | Aucun plantage Luthier | ✅ | ☐ | |

> **D-302 — Éditer JUCE Linux dans `.luthier.json`**
>
> Sur la machine **Linux**, après clone ou pull du dépôt `VoyageLuthier` :
>
> 1. Ouvrir le dossier cloné dans Cursor (ou éditeur).
> 2. Ouvrir `.luthier.json` à la racine du projet.
> 3. Repérer la clé **`juceDirLinux`** (ou équivalent workspace Linux selon le schéma sidecar).
> 4. Remplacer la valeur par le **chemin JUCE local sur cette machine** (ex. `/home/guillaume/Dev/SDKs/JUCE`).
> 5. Sauvegarder — **ne pas** utiliser Luthier pour rouvrir le projet.
> 6. Enchaîner **D-303** : preset `linux-debug` → build.
>
> Les chemins **macOS** et **Windows** dans le même fichier restent ceux des autres machines ; seul le chemin **hôte Linux** doit correspondre à la machine courante.

---

## Critères de réussite (go release v1.0.0)

| ID | Critère | ✅ OK | ❌ KO | Remarques |
| --- | --- | :---: | :---: | --- |
| G-00 | Phase **P** complète (P-A → P-C, fichier maître exporté) | ✅ | ☐ | |
| G-01 | Phase **A** complète (A0 + A3–A8, hors opt.) | ✅ | ☐ | |
| G-02 | Phase **B** complète (B0 + B3–B8, hors opt.) | ☐ | ❌ | Génération OK ; build/regen Windows → retest **rc3** |
| G-03 | Phase **C** complète (C0 + C3–C8, hors opt.) | ✅ | ☐ | |
| G-04 | Phase **D** complète (D1–D4 minimum) | ☐ | ❌ | D2 Windows en attente **rc3** |
| G-05 | **Aucun bloquant** ouvert dans la grille ci-dessous | ☐ | ❌ | #1–#2 ouverts jusqu’à validation rc3 |
| G-06 | Mineurs connus acceptés (si présents) | ✅ | ☐ | B-503, C-003, P-C-004 |

**Mineurs acceptés sans échec release :**

- Ordre boutons modales Windows (B-503)
- Position fenêtre Linux non garantie (C-003)
- Icône Linux sans `.desktop` (P-C-004)
- Warnings compilateur dans headers JUCE tiers uniquement
- Faux positifs CMake Tools « Task has errors » après copie post-build (README projet généré)

---

## Grille des anomalies (à remplir au fil de l’eau)

Pour chaque **❌ KO** significatif, ajouter une ligne. Référencer l’**ID** d’étape (ex. `A-705`).

| # | ID étape | OS | Résumé | Attendu | Obtenu | Gravité | Suite |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | B-701 | Windows | Presets CMake ciblent VS 2022 | Configure avec VS 2026 installé | Échec configure (générateur introuvable) | **bloquant** (build) | Corrigé **rc3** : preset `windows-debug` → VS 2026 ; retest guide rc3 |
| 2 | B-405, B-406 | Windows | Régénération en session avec `.git/` | Regen OK, `.git/` préservé | `WinError 32` (fichier verrouillé) | **gênant** | Correctif `core/project_writer.py` (retries + copie `.git` sous Windows) ; retest **rc3** |
| 3 | D-302 | Linux | Chemin JUCE Linux sur clone Git | Édition `.luthier.json` claire | Question testeur | **mineur** (doc) | Encadré D-302 ajouté dans ce guide |

**Gravité :** **bloquant** = impossible de continuer ou risque perte de données ; **gênant** = contournement pénible ; **mineur** = cosmétique ou cas rare.

---

## Ce qu’il n’est **plus** nécessaire de tester

- Round-trip **Open Project…** → Generate sans changement
- Fidélité byte-for-byte après Open sur une autre machine
- Migration sidecar / Open fallback CMake regex
- Parcours « Open sur Windows → Generate » sur clone Git
- **Luthier sur Mac Intel** (hors périmètre v1.0.0)
- Rejouer en manuel toute la logique déjà couverte par **pytest CI** (sauf décision de double contrôle)
- Build PyInstaller local (`publish/build-dist.py`) ou exécution depuis sources — couvert par la **CD release** sur tag

---

## Références

- [Manuel utilisateur (FR)](../../user/manuel-utilisateur.md) — §8 app autonome, §16 workflows, §18 stockage
- [User manual (EN)](../../user/user-manual.md)
- [Smoke test rc3 Windows (allégé)](./smoke-test-rc3-windows.md) — retest Phase B + D2 après correctifs
- [CONTRIBUTING.md](../../../CONTRIBUTING.md) — build bundle, CI
- README du projet généré (`SmokeTest/README.md`) — presets Cursor, debugging
- [Checklist QA archive (beta)](../1.0.0-beta/checklist-qa-pre-release-v1.md)
