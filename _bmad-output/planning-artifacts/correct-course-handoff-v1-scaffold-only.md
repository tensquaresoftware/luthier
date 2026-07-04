# Correct Course — Passation v1.0.0 « Scaffold Only »

**Project:** Luthier  
**Date:** 2026-07-04  
**Author:** Guillaume DUPONT (PO)  
**Version cible:** **1.0.0** — **inchangée** (déjà `app/version.py` ; repo **private**, app non diffusée ; première publication publique après refonte)  
**Date About :** seule **`REVISION_DATE`** dans `app/version.py` / onglet **About** sera mise à jour au moment de la release  
**Nature du changement:** **Pivot produit majeur** — abandon du modèle « rouvrir / régénérer », repositionnement en **générateur de squelette initial uniquement**

---

## 1. Comment utiliser ce document

Nouvelle conversation BMad — **enchaînement recommandé :**

```
Étape 1 — Correct Course (analyse + proposal)
  /bmad-correct-course
  Passation : _bmad-output/planning-artifacts/correct-course-handoff-v1-scaffold-only.md

Étape 2 — Create Epics and Stories (Epic 9)
  /bmad-create-epics-and-stories
  Proposal approuvée : _bmad-output/planning-artifacts/sprint-change-proposal-YYYY-MM-DD-v1-scaffold-only.md
  Passation : (ce document)

Étape 3 — Pour chaque story 9.x
  /bmad-create-story  → story file
  /bmad-dev-story     → implémentation
  /bmad-code-review   → revue
```

**Langue :** conversation **français** ; artefacts BMad (`epics.md`, stories, proposal) en **anglais** (NFR5 / convention existante).

**Document de référence produit (PO-validated, juillet 2026) :**

- `docs/user/guide-juce-cmake-et-luthier.md` (FR) — vision, Projucer vs CMake, limites Luthier, workflow IDE agentique
- `docs/user/juce-cmake-and-luthier-guide.md` (EN) — same content, English edition

---

## 2. Résumé exécutif — décision PO

### 2.1 Vision produit v1.0.0

| Avant (MVP Epics 1–8) | Après (v1.0.0) |
|----------------------|----------------|
| Créer **et rouvrir** un projet Luthier | **Créer uniquement** le squelette initial |
| **Generate** sur projet existant (destructif) | **Generate interdit** si dossier non vide / projet existant |
| `.luthier.json` relu via **Open Project…** | `.luthier.json` **écrit au generate**, jamais relu par l'app |
| Couleur d'accent sur onglet **Project** + sidecar | Couleur d'accent **Preferences uniquement** (look Luthier) |
| 3 types plugin exclusifs avec flags figés | **Presets** Instrument / Effect / MIDI Effect + **caractéristiques indépendantes** |
| Formats : AU, VST3, Standalone | **Identique** — **pas d'AUv3** (décision PO : oublié complètement) |

**Positionnement public :**

> **Luthier = générateur de squelette JUCE/CMake.** Il pose le projet une fois ; le développement et la maintenance CMake se font ensuite dans l'IDE (manuellement ou via IA agentique — approche recommandée par Guillaume).

### 2.2 Décisions PO verrouillées (ne pas renégocier en implémentation)

| Sujet | Décision |
|-------|----------|
| **Open Project…** | **Supprimer** (bouton, menu, code, tests, docs) |
| **Generate sur dossier existant** | **Bloquer** — pas d'overwrite avec simple avertissement en v1.0 |
| **AUv3** | **Hors scope** — rester sur AU classique |
| **AAX, LV2, ARA, VST2, GUI App** | **Hors scope v1.0** |
| **Reopen / resync / merge CMake** | **Hors scope** — pas en v1.0, pas en v1.0.1 sauf nouveau Correct Course |
| **Numéro de version release** | **Rester en 1.0.0** — déjà le cas (`VERSION` dans `app/version.py`) ; **ne pas** passer en 1.1.0 / 2.0.0 pour cette refonte |
| **Date de révision (About)** | **Mettre à jour** `REVISION_DATE` dans `app/version.py` (affichée « Revision date » dans l'onglet About) — **seul** changement de métadonnée release |
| **Guide JUCE/CMake** | Intégrer dans repo + manuels EN/FR + README |
| **Couleur d'accent (Project tab)** | **Supprimer** — plus de picker sur l'onglet Project |
| **Couleur d'accent (Preferences tab)** | **Conserver** — personnalise uniquement l'apparence de Luthier |
| **`accentColor` dans `.luthier.json`** | **Retirer** — n'était utile que pour reopen / thème par projet |
| **Connecteurs visuels OS (Workspace & Artefacts)** | **Ajouter** — lignes d'arborescence pour Windows / macOS / Linux (§5.8) |
| **Rétrocompatibilité** | **Aucune** — pas de code legacy, pas de migration des projets Luthier déjà générés (§2.3) |

### 2.3 Aucune rétrocompatibilité (v1.0.0 = première release publique)

**Formulation PO (à reprendre telle quelle dans proposal / stories) :**

> **Aucune rétrocompatibilité requise.** Supprimer le code mort et les chemins de compatibilité ascendante ; ne pas migrer les projets ni les sidecars `.luthier.json` créés avant cette refonte.

**Vocabulaire utile (FR) :**

| Expression | Sens |
|------------|------|
| **Rétrocompatibilité** | Terme standard = *backward compatibility* |
| **Aucune rétrocompatibilité** | Pas besoin de supporter l'ancien comportement |
| **Code legacy** | Anglicisme courant en dev ; en français formel : **code hérité** ou **code de compatibilité ascendante** |
| **Chemins de migration** | Logique pour upgrader d'ancien → nouveau format (ex. lire un vieux `.luthier.json`) |

**Contexte PO :**

- Repo **private**, app **non diffusée** ; **1.0.0** est déjà le numéro affiché et **le restera** après refonte (pas de bump semver).
- Seule la **date de révision** (About) sera actualisée — pas un changement de version produit.
- Un seul utilisateur de projets générés (PO) — dossiers surtout de **test**, sans valeur de conservation.
- **Matrix-Control** et autres vrais plugins ne passent **pas** par une réouverture Luthier : ce sont des projets CMake vivants à part.

**Conséquences pour l'implémentation (ne pas renégocier) :**

- **Supprimer** `project_reader.py` et tests associés — **pas** de mode dégradé « si sidecar ancien format… ».
- **Retirer** `accentColor` de `ProjectSpec` / `.luthier.json` **sans** lire ni convertir les sidecars existants.
- **Pas** de détection « projet Luthier v0 » vs « v1 » ; **pas** de script de migration sidecar.
- Les anciens dossiers de test PO peuvent être **regénérés from scratch** ou ignorés.

---

## 3. Contexte — pourquoi ce pivot

Synthèse de la réflexion PO (juillet 2026) — détail dans `docs/user/guide-juce-cmake-et-luthier.md` :

1. **Projucer** fusionne métadonnées + arborescence sources ; resync = écrasement IDE depuis `.jucer`. Incompatible avec workflow Cursor/IA.
2. **CMake** vit dans `CMakeLists.txt` ; resync IDE = `cmake --preset`, sans toucher aux sources.
3. **Luthier Generate** (`ProjectWriter.write()`) remplace **tout** le répertoire projet → dangereux sur projet brownfield (ex. Matrix-Control).
4. Rouvrir + régénérer proprement exigerait zones CMake protégées, merge partiel, migrations — **effort disproportionné** vs bénéfice pour l'usage PO (scaffold + IA pour la suite).
5. Le précurseur **JUCE-Project-Generator** (Terminal) avait déjà le bon modèle : **one-shot**, pas de reload.

**Epic 2 « Reliable Project Reload »** (done) est **superseded** par ce pivot — ne pas restaurer reload ; retirer le code et mettre à jour la doc/architecture.

---

## 4. État actuel du dépôt

| Artefact | Statut |
|----------|--------|
| Epics 1–8 | **done** (`sprint-status.yaml`, last_updated 2026-07-01) |
| Epic 9 | **Absent** — à créer via Correct Course + CE |
| Guides JUCE/CMake/Luthier (`docs/user/`) | **Présents** (FR 2026-07-04, EN 2026-07-04) — référencés depuis manuels |
| README | Mentionne encore **reopen** — **STALE** |
| Manuels `docs/user/user-manual.md`, `manuel-utilisateur.md` | Sections Open Project — **STALE** |
| `core/project_reader.py` | Existe — **à retirer** (ou réduire à zero usage app) |
| `app/main_window.py` | `_on_open`, `_load_project`, bouton Open — **à retirer** ; bascule accent par onglet — **à simplifier** |
| `app/pages/project.py` | `AccentColorSection` — **à retirer** |
| `app/pages/workspace.py`, `artefacts.py` | Indentation marge seule — **connecteurs OS à ajouter** (§5.8.2) |
| `core/plugin_settings.py` | Flags figés par type — **à refactorer** |
| QA checklists `docs/tests/` | Références Open / round-trip — **STALE** |

---

## 5. Périmètre fonctionnel v1.0.0 — enrichissements configuration

### 5.1 Formats plugin (inchangé)

- **AU**, **VST3**, **Standalone** (multi-choix, au moins un requis)
- AU filtré côté CMake sur non-Apple (comportement template existant)

### 5.2 Plugin type — modèle « presets + toggles »

**Conserver** les 3 presets radio (UX actuelle) :

| Preset | Pré-cochage |
|--------|-------------|
| Instrument | `IS_SYNTH`, `NEEDS_MIDI_INPUT` |
| Audio Effect | (aucun synth/midi par défaut) |
| MIDI Effect | `IS_MIDI_EFFECT`, `NEEDS_MIDI_INPUT`, `NEEDS_MIDI_OUTPUT` |

**Ajouter** checkboxes indépendantes (alignées Projucer « Plugin Characteristics ») :

| UI label | CMake `juce_add_plugin` | v1.0 |
|----------|-------------------------|------|
| Plugin is a Synth | `IS_SYNTH` | ✅ (lié preset + override) |
| Plugin MIDI Input | `NEEDS_MIDI_INPUT` | ✅ |
| Plugin MIDI Output | `NEEDS_MIDI_OUTPUT` | ✅ **priorité** (cas Matrix-Control) |
| MIDI Effect Plugin | `IS_MIDI_EFFECT` | ✅ |
| Editor Requires Keyboard Focus | `EDITOR_WANTS_KEYBOARD_FOCUS` | ✅ |

**Règles validation UI :**

- `IS_SYNTH` + `IS_MIDI_EFFECT` → **incompatibles** (erreur inline)
- `IS_MIDI_EFFECT` actif → masquer/désactiver presets I/O audio (§5.3)
- Changer le preset radio **réinitialise** les toggles aux defaults du preset (avec confirmation si formulaire dirty — réutiliser dirty guard existant ou comportement documenté)

### 5.3 I/O audio — presets simples (pas le champ texte Projucer)

Remplacer la logique fixe du template `PluginProcessor.cpp` par des variantes selon preset sélectionné :

| Preset I/O | `createBusesProperties()` | Cas d'usage |
|------------|----------------------------|-------------|
| `stereo` (default) | in stereo + out stereo (effect) ; out stereo only (synth) | Majorité |
| `mono` | mono in/out ou out only | Effets mono |
| `synth_no_input` | pas d'entrée audio, sortie stereo | Synthé pur |
| `midi_effect` | `{}` (pas de bus audio) | MIDI Effect |

**Champ UI :** combo « Audio I/O » — pas de saisie `{2,2},{1,1}` style Projucer en v1.0.

### 5.4 MIDI VST channel counts

Si `NEEDS_MIDI_INPUT` → combo **1–16** → `VST_NUM_MIDI_INS` (default 16)  
Si `NEEDS_MIDI_OUTPUT` → combo **1–16** → `VST_NUM_MIDI_OUTS` (default 16)

### 5.5 Plugin Description

Nouveau champ texte → `DESCRIPTION` dans `juce_add_plugin`.

### 5.6 VST3 Category (optionnel v1.0 — PO : nice-to-have)

Si trivial : liste dérivée auto suffit ; sinon **dériver** depuis flags comme aujourd'hui (`au_and_vst3_categories`). Story 9.3 peut limiter à DESCRIPTION + flags si le temps manque.

### 5.7 Explicitement hors scope v1.0

AUv3, AAX (+ Disable AAX Bypass/Multi-Mono), LV2 URI, ARA, VST Legacy, Unity, IAA, GUI App standalone, BinaryData UI, channel configs texte libre, side-chain/bus custom, reopen, regenerate, merge CMake brownfield.

### 5.8 UI — couleur d'accent et connecteurs OS (Workspace & Artefacts)

#### 5.8.1 Couleur d'accent : Preferences uniquement

**Contexte :** Aujourd'hui, l'onglet **Project** expose `AccentColorSection` (`app/pages/project.py`) ; la couleur est aussi sérialisée dans `ProjectSpec.accent_color` → `.luthier.json`. Ce modèle supposait qu'on rouvrirait le projet et restaurerait son « look » Luthier — **plus pertinent** en scaffold-only.

**Décision PO :**

| Emplacement | v1.0 |
|-------------|------|
| Onglet **Project** | **Pas** de sélecteur de couleur |
| Onglet **Preferences** | **Conserver** `AccentColorSection` — l'utilisateur choisit le look **de Luthier** |
| `preferences.json` | **`accentColor`** persiste (auto-save Preferences) |
| `ProjectSpec` / `.luthier.json` | **Retirer `accentColor`** — le sidecar ne décrit que le projet JUCE, pas l'UI Luthier |
| Thème au changement d'onglet | **Simplifier** — toujours `prefs.accent_color` (plus de bascule Project vs Preferences) |

**Impact code attendu :**

- Retirer `AccentColorSection` de `app/pages/project.py`
- Retirer `accent_color` de `core/project_spec.py` (`to_dict` / `from_dict`)
- Simplifier `app/main_window.py` : supprimer `_accent_color_for_tab`, `_on_project_accent_changed`, wiring Project accent
- Mettre à jour manuels : une seule section « Luthier accent colour » sous **Preferences**

#### 5.8.2 Connecteurs visuels — arborescence Windows / macOS / Linux

**Objectif :** Habiller l'indentation existante (`OS_FIELD_LEFT_MARGIN = 28` dans `path_specs.py`) par de **vraies lignes** type arborescence, dans les sections **Workspace** et **Artefacts**, onglets **Project** et **Preferences**.

**Cibles (4 blocs identiques visuellement) :**

| Section | Parent (ancre du trait vertical) | Enfants (branches horizontales) |
|---------|----------------------------------|----------------------------------|
| **Workspace** | Label « Destination folder * » | Windows, macOS, Linux |
| **Workspace** | Label « JUCE directory » | Windows, macOS, Linux |
| **Artefacts** | Case « Copy to central artefacts folder » | Windows, macOS, Linux (si activée) |

**Schéma visuel cible :**

```
Destination folder *
│
├─ Windows     [________________]
├─ macOS       [________________]  [Choose…]
└─ Linux       [________________]

JUCE directory
│
├─ Windows     …
├─ macOS       …
└─ Linux       …

☑ Copy to central artefacts folder
│
├─ Windows     …
├─ macOS       …
└─ Linux       …
```

**Spécification dessin :**

- **Trait vertical** : démarre **sous** le label parent (sous le « D » de « Destination folder », sous la baseline de la checkbox « Copy to central artefacts folder »), s'arrête au niveau vertical du **dernier** enfant (Linux).
- **Traits horizontaux** : partent du vertical vers chaque label OS (Windows, macOS, Linux), avec **padding** (~6–8 px) avant le texte du label — les labels ne doivent **pas** toucher la ligne.
- **Dernier enfant (Linux)** : coin arrondi ou branche en « └ » (style tree view) ; branches intermédiaires en « ├ ».
- **Couleur** : ton discret du thème (ex. `#Palette.MID` / bordure QSS existante — **pas** la couleur d'accent, pour ne pas distraire).
- **Implémentation suggérée** : widget réutilisable `OsPathTreeGroup` (ou `TreeIndentedPathGroup`) dans `app/widgets/`, utilisé par `WorkspaceSection` et `ArtefactsSection` — **éviter** de dupliquer la logique paint dans deux fichiers.
- **Accessibilité** : lignes purement décoratives ; la structure reste dans l'ordre DOM/logique des champs (pas de régression clavier).

**Hors scope :** connecteurs sur d'autres sections ; animation ; lignes pour « Copy to system plugin folders » (pas d'enfants OS).

---

## 6. Garde-fou Generate — spécification

### 6.1 Règle

**Generate refusé** si le chemin cible `{destination}/{projectName}/` :

1. **Existe** et contient **au moins un fichier ou sous-dossier** (non vide), **OU**
2. Contient un marqueur projet Luthier : `.luthier.json` **ou** `CMakeLists.txt` avec signature Luthier (comment header template)

### 6.2 UX

- **Pas de dialog « Continue anyway »** en v1.0
- Message status bar + `QMessageBox.warning` explicite :
  - *« This folder already exists and is not empty. Luthier only creates new projects. Choose an empty folder or a different project name. »*
- `_confirm_overwrite` actuel → **retirer ou restreindre** au cas « dossier parent existe mais sous-dossier projet n'existe pas encore » uniquement

### 6.3 Cas autorisé

`destination/Matrix-Control/` **n'existe pas** → création OK (même si `destination/` existe).

---

## 7. Epic 9 proposé — stories et ordre

Le workflow **Correct Course** doit produire `sprint-change-proposal-2026-07-04-v1-scaffold-only.md` et patcher `epics.md` + `sprint-status.yaml` avec cette structure.

| Story | Slug | Dépend de | Résumé |
|-------|------|-----------|--------|
| **9.1** | `9-1-remove-open-project-scaffold-only-positioning` | — | Retirer Open Project (UI, `project_reader`, wiring) ; MAJ `project-context.md` / architecture ; `.luthier.json` write-only |
| **9.2** | `9-2-block-generate-non-empty-destination` | — | Garde-fou dossier non vide ; tests ; retirer overwrite confirm |
| **9.3** | `9-3-decoupled-plugin-characteristics-and-projectspec` | — | `ProjectSpec` + UI + `plugin_settings` refactor ; presets + toggles ; validation |
| **9.4** | `9-4-template-pipeline-audio-io-midi-description` | 9.3 | `CMakeLists.txt`, `PluginProcessor.cpp`, `render_context`, tokens |
| **9.5** | `9-5-documentation-v1-guide-manuals-readme` | 9.1, 9.7 | Guide, manuels EN/FR, README, CONTRIBUTING, QA checklists |
| **9.6** | `9-6-test-suite-scaffold-only-regression` | 9.1–9.4, 9.7 | Retirer tests open/round-trip reload ; ajouter tests guard + characteristics |
| **9.7** | `9-7-ui-accent-preferences-only-os-tree-connectors` | 9.1 | Retirer accent Project + `ProjectSpec` ; connecteurs OS Workspace/Artefacts |

**Ordre d'implémentation PO :** `9.1 → 9.7 → 9.2 → 9.3 → 9.4 → 9.6 → 9.5`  
(9.7 juste après 9.1 : même zone UI Project ; docs en dernier pour refléter l'UI finale)

**Epic 9 titre suggéré :** `v1.0 Scaffold-Only Release`

---

## 8. Acceptance Criteria détaillés (canoniques pour CE / CS)

### Story 9.1 — Remove Open Project

**Given** Luthier running  
**When** user views Project tab action bar  
**Then** buttons are **Create New Project** and **Generate Project** only — no **Open Project…**

**Given** codebase  
**Then** `core/project_reader.py` **deleted** (no app-layer imports, no legacy read path)  
**And** no menu item / shortcut / `_load_project` / `read_project_result` in `app/`  
**And** no backward-compatibility shim for older `.luthier.json` sidecars (§2.3)

**Given** successful Generate  
**Then** `.luthier.json` is still written (metadata snapshot for humans/AI — not read back by Luthier)

**Given** Epic 2 documentation in `epics.md` / architecture  
**Then** marked **superseded** by Epic 9 with brief note

**Given** Project tab  
**Then** no **Luthier Accent Color** / `AccentColorSection` — colour picker exists **only** on Preferences tab (§5.8.1)

**Given** successful Generate  
**Then** `.luthier.json` does **not** contain `accentColor`

---

### Story 9.7 — UI: accent Preferences-only + OS tree connectors

**Given** Project tab scroll content  
**Then** no accent colour picker ; Preferences tab still shows `AccentColorSection` with auto-save to `preferences.json`

**Given** user changes accent on Preferences  
**Then** Luthier theme updates immediately on **all** tabs (single source: `prefs.accent_color`)

**Given** `ProjectSpec.to_dict()` after Generate  
**Then** no `accentColor` key in `.luthier.json`

**Given** Workspace section (Project and Preferences tabs)  
**Then** each OS path group (Destination folder, JUCE directory) displays tree connector lines per §5.8.2

**Given** Artefacts section (Project and Preferences tabs)  
**When** « Copy to central artefacts folder » is visible  
**Then** the three OS path rows display the same tree connector pattern anchored to that checkbox

**Given** light/dark theme QSS  
**Then** connector lines use a subtle neutral colour (not accent) and remain visible

**Given** implementation  
**Then** prefer one reusable widget (`app/widgets/…`) shared by `workspace.py` and `artefacts.py`

---

### Story 9.2 — Block Generate on non-empty destination

**Given** target project directory exists and is non-empty  
**When** user clicks Generate  
**Then** generation does **not** start ; clear error message

**Given** target directory does not exist  
**When** Generate  
**Then** generation proceeds (current behavior)

**Given** target exists as empty directory  
**Then** PO decision: **allow** generate (empty is OK)

**Given** unit/integration tests  
**Then** cover non-empty block, empty allow, fresh path allow

---

### Story 9.3 — Decoupled plugin characteristics

**Given** Project tab  
**Then** user sees preset radios **and** characteristic checkboxes per §5.2

**Given** Instrument preset selected  
**Then** Synth + MIDI Input checked ; MIDI Output **unchecked** but user may enable (Matrix-Control case)

**Given** Synth + MIDI Effect both checked  
**Then** form invalid with inline error

**Given** `ProjectSpec.to_dict` / `from_dict`  
**Then** new fields persisted in `.luthier.json` (for reference only)

**Fields suggérés `ProjectSpec` :**

```python
# Existing: plugin_type (preset key)
needs_midi_input: bool
needs_midi_output: bool
is_synth: bool  # or derive — prefer explicit stored values synced from UI
is_midi_effect: bool
editor_wants_keyboard_focus: bool
plugin_description: str
audio_io_preset: str  # stereo | mono | synth_no_input | midi_effect
vst_num_midi_ins: int   # 1-16, default 16
vst_num_midi_outs: int  # 1-16, default 16
```

---

### Story 9.4 — Template pipeline

**Given** generated project  
**Then** `juce_add_plugin` reflects all characteristics flags, DESCRIPTION, VST_NUM_MIDI_*

**Given** `audio_io_preset`  
**Then** `PluginProcessor::createBusesProperties()` matches §5.3

**Given** `plugin_settings.flags_for_type`  
**Then** replaced or reduced to **preset defaults only** — not sole source of truth at generate time

---

### Story 9.5 — Documentation

**Given** `docs/user/guide-juce-cmake-et-luthier.md`  
**Then** linked from README, user-manual.md, manuel-utilisateur.md (section « Philosophy » ou équivalent)

**Given** manuels EN/FR  
**Then** all **Open Project…** sections removed or replaced by « after generation » workflow

**Given** accent colour documentation  
**Then** single source of truth: **Preferences only** ; remove `.luthier.json` accent / Project tab picker references

**Given** Workspace & Artefacts sections in manuals  
**Then** optional screenshot or ASCII note describing OS tree connectors (§5.8.2)

**Given** release clôturée (story 9.5)  
**Then** `app/version.py` a `VERSION == "1.0.0"` (inchangé) et `REVISION_DATE` à jour  
**And** l'onglet About affiche la nouvelle revision date sans changement de numéro de version

**Given** README / manuels  
**Then** positioning scaffold-only ; sponsor block unchanged ; features list updated

**Given** QA checklists in `docs/tests/`  
**Then** open/round-trip scenarios removed ; add empty-folder guard smoke step

---

### Story 9.6 — Test suite

**Remove or rewrite:**

- `tests/unit/test_project_reader.py` (if module removed)
- `tests/integration/test_round_trip.py` — regenerate/open scenarios
- References in `test_frozen_bundle.py`, `test_cmake_cross_platform.py`, `test_project_dirty_guard.py`

**Add:**

- Generate blocked on non-empty dir
- Characteristics validation matrix (synth+midi effect invalid ; instrument + midi out valid)
- Template emission spot-checks (CMake flags)
- Remove / update `test_project_spec` accent round-trip ; `test_project_dirty_guard` accent snapshot if field removed
- `ProjectSpec` / sidecar: assert no `accentColor` after generate

**CI :** `pytest` must pass (GitHub Actions workflow from Epic 7.1)

---

## 9. Inventaire fichiers — guide implémentation

### 9.1 Retrait Open Project (priorité)

| Fichier | Action |
|---------|--------|
| `app/main_window.py` | Remove `_open_btn`, `_on_open`, `_load_project`, open dialog constants, open status messages ; simplify accent theme (prefs only) |
| `app/pages/project.py` | Remove `AccentColorSection` and `accentColor` from `spec()` |
| `core/project_spec.py` | Remove `accent_color` field and JSON key |
| `core/project_reader.py` | **Delete** |
| `tests/unit/test_project_reader.py` | **Delete** |
| `tests/integration/test_round_trip.py` | Rewrite — generation-only assertions |
| `tests/unit/test_core_imports.py` | Remove `project_reader` import if present |
| `_bmad-output/project-context.md` | Update data flow — remove `_on_open` path |
| `_bmad-output/architecture.md` | Same |

### 9.2 Garde-fou Generate

| Fichier | Action |
|---------|--------|
| `app/main_window.py` | `_run_generation` / `_confirm_overwrite` — new `_destination_is_safe_for_generate()` |
| `core/project_generator.py` or `project_writer.py` | Optional defense-in-depth check before `write()` |
| `tests/unit/test_project_writer.py` | Keep ; add guard tests separately |

### 9.3 Characteristics + templates

| Fichier | Action |
|---------|--------|
| `core/project_spec.py` | New fields + serialization |
| `core/plugin_settings.py` | Preset defaults ; keep `bundle_id`, `au_and_vst3_categories` |
| `core/render_context.py` | Map new fields to context/tokens |
| `app/pages/plugin_type.py` | Extend UI (checkboxes, combos) — may rename/split page |
| `app/pages/project_info.py` | Plugin description field |
| `templates/CMakeLists.txt` | New placeholders |
| `templates/Source/PluginProcessor.cpp` | Conditional buses / `@TOKENS@` or separate template variants |

### 9.4 Documentation

| Fichier | Action |
|---------|--------|
| `README.md` | Scaffold-only positioning |
| `docs/user/user-manual.md` | Major update |
| `docs/user/manuel-utilisateur.md` | Major update |
| `docs/user/guide-juce-cmake-et-luthier.md` | Already OK — add cross-links; moved to `docs/user/` |
| `docs/user/juce-cmake-and-luthier-guide.md` | EN translation — add cross-links |
| `docs/tests/checklist-qa-*.md` | Update |
| `templates/README.md` | Post-generation workflow, no Luthier reopen |

### Inventaire — UI accent + connecteurs OS (story 9.7)

| Fichier | Action |
|---------|--------|
| `app/pages/project.py` | Remove accent section (if not done in 9.1) |
| `app/pages/preferences.py` | Keep `AccentColorSection` ; libellé explicite « Luthier appearance » si utile |
| `app/main_window.py` | Remove tab-based accent switching ; `_apply_accent_theme(prefs.accent_color)` only |
| `app/pages/workspace.py` | Wrap path groups in tree connector widget (×2 groups) |
| `app/pages/artefacts.py` | Tree connector on OS paths under artefacts checkbox |
| `app/pages/path_specs.py` | Possibly tune `OS_FIELD_LEFT_MARGIN` to align with connector geometry |
| `app/widgets/` | **New** — `os_path_tree_group.py` (or equivalent) |
| `app/theme.py` | Optional token for connector line colour |
| `tests/unit/test_project_spec.py` | Remove accent round-trip tests |
| `tests/unit/test_project_dirty_guard.py` | Remove accent from dirty snapshots |

---

## 10. Impacts PRD / FR — patches attendus (Correct Course)

Le workflow Correct Course doit proposer les révisions suivantes dans `prd.md` (ou addendum v1.0) :

| ID | Avant | Après (synthèse) |
|----|-------|------------------|
| **FR reload** | Reload project via Open… | **Removed** — Luthier does not reload projects |
| **FR8** | Action bar: Create, **Open**, Generate | Create, Generate only |
| **Product goal** | Create, reopen, configure | **Create initial skeleton only** |
| **NFR safety** | Overwrite confirm | **Hard block** on non-empty target |
| **Accent colour** | Project tab + sidecar | **Preferences only** — Luthier UI theme, not project metadata |
| **Backward compatibility** | Reload, sidecar read, migration | **None** — clean break; delete legacy paths (§2.3) |

**Architecture AD (spine) :**

- Remove « reload path » from data flow diagram
- Document `.luthier.json` as **write-only sidecar** (reference metadata, not app input) — **without** `accentColor`
- Document `accentColor` lives in `preferences.json` only
- Epic 2 marked superseded

**Versioning :**

- **`VERSION`** dans `app/version.py` : **conserver `1.0.0`** — ne pas modifier pour Epic 9.
- **`REVISION_DATE`** : mettre à jour à la date PO de clôture release (story 9.5 ou smoke final) ; reflétée dans l'onglet **About** uniquement.
- Tag git `v1.0.0` : **uniquement sur demande PO** (§12) — pas automatique agent ; peut coïncider avec la première publication publique du repo.

---

## 11. Hors scope Epic 9

- GUI App project type (`juce_add_gui_app`)
- AUv3, AAX, LV2, ARA
- PyInstaller rebuild / notarization (unless regression — existing bundles still valid)
- New features Templates beyond doc updates (accent stays Preferences-only — in scope 9.7)
- Matrix-Control or external project migration tools
- `.jucer` import script
- Migration of pre-refactor Luthier-generated projects or legacy `.luthier.json` sidecars (§2.3)

---

## 12. Critères de succès release v1.0.0

1. Aucun chemin UI/code pour Open Project
2. Generate impossible sur dossier non vide
3. Plugin Instrument + MIDI Output généra un projet qui compile (smoke : configure preset macOS si dispo)
4. Couleur d'accent **uniquement** dans Preferences ; absente de Project et de `.luthier.json`
5. Connecteurs OS visibles dans Workspace & Artefacts (Project + Preferences)
6. Manuels EN/FR + README alignés ; guide référencé
7. `pytest` vert en CI
8. PO smoke manuel : Create → Generate → ouvrir dans Cursor → build Standalone
9. About : **Version 1.0.0** inchangée ; **Revision date** à jour
10. Tag git `v1.0.0` **uniquement sur demande PO** (pas automatique agent)

---

## 13. Risques et mitigations

| Risque | Mitigation |
|--------|------------|
| Tests Epic 2/3 fortement couplés à reload | Story 9.6 dédiée ; grep `read_project`, `Open Project` |
| UI surcharge (trop de toggles) | Section « Plugin characteristics » repliable ou sous `Section` existante |
| `PluginProcessor.cpp` variants complexity | Max 4 branches `audio_io_preset` — pas de texte libre |
| Docs EN/FR divergence | Même structure de sections ; traduction en parallèle story 9.5 |
| Utilisateurs MVP habitués à Open | Notes de release + guide § limites volontaires |
| Connecteurs OS mal alignés (HiDPI / marges) | Widget dédié + constantes dans `path_specs.py` ; smoke visuel macOS + Windows |
| Régression accent au changement d'onglet | Tests manuels : une seule source `prefs.accent_color` |
| Tentative de compatibilité ascendante « au cas où » | Interdit PO §2.3 — supprimer, ne pas wrapper |

---

## 14. Enchaînement BMad — checklist PO

```
[ ] 1. Correct Course → proposal approuvée PO
[ ] 2. Create Epics → Epic 9 in epics.md + sprint-status.yaml
[ ] 3. Create Story 9.1 → Dev → Review → done
[ ] 4. … stories 9.2 – 9.7 (ordre §7)
[ ] 5. Epic 9 retrospective (optional)
[ ] 6. PO smoke + publication repo public (hors scope agent sauf demande)
```

---

## 15. Prompt prêt à coller — Correct Course

```
/bmad-correct-course

Passation PO : _bmad-output/planning-artifacts/correct-course-handoff-v1-scaffold-only.md
Référence vision : docs/user/guide-juce-cmake-et-luthier.md (FR), docs/user/juce-cmake-and-luthier-guide.md (EN)

Contexte : Pivot v1.0.0 scaffold-only — supprimer Open Project, bloquer Generate sur dossier non vide, enrichir characteristics plugin (§5), accent Preferences-only + connecteurs OS (§5.8), **aucune rétrocompatibilité** (§2.3), docs EN/FR + README. AUv3 exclu.

Produire :
1. sprint-change-proposal-2026-07-04-v1-scaffold-only.md
2. Patches proposés PRD + architecture-spine (FR reload removed, FR8 updated, accent scope)
3. Epic 9 + stories 9.1–9.7 dans epics.md (AC du handoff §8)
4. sprint-status.yaml — epic-9 backlog

Ne pas implémenter le code — proposal + planning only.

Français en conversation ; artefacts en anglais.
```

---

## 16. Prompt prêt à coller — Create Epics (après approval)

```
/bmad-create-epics-and-stories

Proposal approuvée : _bmad-output/planning-artifacts/sprint-change-proposal-2026-07-04-v1-scaffold-only.md
Passation : _bmad-output/planning-artifacts/correct-course-handoff-v1-scaffold-only.md

Mode : Epic 9 uniquement — ne pas modifier Epics 1–8 (marquer Epic 2 superseded note seulement).

Valider AC §8, ordre 9.1→9.7→9.2→9.3→9.4→9.6→9.5, slugs sprint-status.

Français en conversation ; epics.md en anglais.
```

---

## 17. Prompt prêt à coller — Create Story (exemple 9.1)

```
/bmad-create-story

Story : 9.1 — Remove Open Project (scaffold-only positioning)
Epic : 9 — v1.0 Scaffold-Only Release
Passation : _bmad-output/planning-artifacts/correct-course-handoff-v1-scaffold-only.md §8 Story 9.1
Inventaire fichiers : §9.1

Charger project-context.md et app/main_window.py avant d'écrire la story.
```

---

## 18. Prompt prêt à coller — Create Story (exemple 9.7)

```
/bmad-create-story

Story : 9.7 — UI: accent Preferences-only + OS tree connectors
Epic : 9 — v1.0 Scaffold-Only Release
Passation : _bmad-output/planning-artifacts/correct-course-handoff-v1-scaffold-only.md §5.8 et §8 Story 9.7
Inventaire fichiers : §9 « Inventaire — UI accent + connecteurs OS »

Charger app/pages/workspace.py, app/pages/artefacts.py, app/pages/project.py, app/widgets/accent_color_picker.py avant d'écrire la story.
```

---

*Fin de passation — Correct Course v1.0.0 Scaffold Only*
