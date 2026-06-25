# Correct Course — Passation (handoff)

**Project:** Luthier  
**Date:** 2026-06-24  
**Author:** Guillaume DUPONT (product owner) + design session with agent  
**Workflow:** `[CC] bmad-correct-course`  
**Mode recommandé:** **Batch** (vision déjà consolidée ; proposer les edits PRD / spine / epics en une passe pour relecture)

---

## 1. Comment utiliser ce document

Dans une **nouvelle conversation**, invoquer :

```
/bmad-correct-course
```

Puis coller ou référencer :

> Le change signal est entièrement décrit dans  
> `_bmad-output/planning-artifacts/correct-course-handoff-epic-5-workflows.md`  
> et validé fonctionnellement par  
> `Docs/USER-MANUAL.md` (vision cible produit).

**Ne pas redemander** « quel est le problème ? » — tout est ci-dessous. Enchaîner sur l’analyse d’impact (checklist) et la **Sprint Change Proposal** vers  
`_bmad-output/planning-artifacts/sprint-change-proposal-2026-06-24.md` (ou date du jour).

**Langue :** conversation en **français** ; documents produits (PRD, epics, spine, proposal) en **anglais** (NFR5).

---

## 2. État du sprint au moment de la passation

| Epic | Statut |
|------|--------|
| Epic 1 — Core Architecture & Project Generation | **done** |
| Epic 2 — Reliable Project Reload | **done** |
| Epic 3 — Test Suite | **done** (retro faite 2026-06-24) |
| Epic 4 — Cross-Platform Distribution (PyInstaller) | **backlog** |

Fichier de suivi : `_bmad-output/implementation-artifacts/sprint-status.yaml`

**Décision de priorité :** insérer un **nouvel Epic 5** *avant* Epic 4 — workflows Project / Preferences / UI — car la vision UX est validée et bloque la cohérence produit.

---

## 3. Déclencheur du Correct Course

### 3.1 Type de changement

- **Nouvelle exigence produit** émergée après clôture des Epics 1–3 (pas un bug d’implémentation isolé).
- **Incohérence structurelle** entre le comportement codé (Epics 1–2) et la vision UX cible :
  - Open / Generate **écrivent** `preferences.json` via `prefs.update(spec)` (AD-5 actuel).
  - `juce_dir` est **hors** `ProjectSpec` (AD-7 actuel) alors que l’utilisateur veut un JUCE **par projet**.
  - Boutons UI partiellement ajoutés hors BMad (Create New Project, Load Preferences) sans stories.
  - Schéma `preferences.json` **incomplet** (pas de plugin type, formats, compilation).

### 3.2 Problème en une phrase

> Luthier mélange aujourd’hui **projet courant** et **réglages globaux** ; la vision cible sépare strictement Project vs Preferences/Templates, étend le profil `preferences.json` comme unique source de defaults, et porte `juceDir` sur le projet pour le round-trip.

### 3.3 Preuves / références

| Référence | Rôle |
|-----------|------|
| **`Docs/USER-MANUAL.md`** | **Source de vérité UX** — vision cible validée par le PO |
| `_bmad-output/planning-artifacts/prds/prd-Luthier-2026-06-22/prd.md` | À mettre à jour (F7, F8) |
| `_bmad-output/planning-artifacts/epics.md` | À étendre (Epic 5) |
| `_bmad-output/planning-artifacts/architecture/.../ARCHITECTURE-SPINE.md` | AD-5, AD-7 à réviser |
| `app/main_window.py` | `prefs.update` + `save` sur Open et Generate (l.213–218, 237–242) |
| `core/project_spec.py` | Pas de `juce_dir` aujourd’hui |
| `core/preferences.py` | `_DEFAULTS` partiel ; pas type/formats/compilation |

**Pas de legacy utilisateur** — app jamais diffusée ; pas de compat projets anciens à préserver pour `juceDir` sidecar.

---

## 4. Vision produit cible (résumé exécutif)

### 4.1 Trois domaines

| Domaine | Onglet | Persistance |
|---------|--------|-------------|
| Projet en cours | **Project** | Formulaire + `.luthier.json` après Generate |
| Réglages globaux | **Preferences** | `preferences.json` |
| Modèles globaux | **Templates** | Overrides `AppConfigLocation` |

**Open** et **Generate** ne modifient **jamais** `preferences.json`.  
**Import Preferences** ne modifie **pas** l’onglet Project ouvert.

### 4.2 Source des defaults

```
Code (factory defaults, once)
    → création initiale preferences.json
    → ensuite TOUT seed Project depuis preferences.json
```

Inclut : identité éditeur, destination folder, JUCE, **plugin type, formats, compilation**, artefacts.

**Create New Project** : efface project name / display name, version `1.0.0` ; re-seed **tout le reste** depuis `preferences.json` ; modale si formulaire modifié (dirty tracking à implémenter).

### 4.3 Preferences — workflow

| Action | Effet sur `preferences.json` |
|--------|------------------------------|
| Auto-save (champs valides) | Écrit |
| **Import Preferences…** | Remplace tout + écrit |
| **Export Preferences…** | Aucun (fichier externe) |
| Open / Generate | **Aucun** |

- Remplacer boutons actuels : Load → **Import**, Save → **Export**.
- Étiquette furtive orange dans la barre d’onglets après auto-save.

### 4.4 Factory defaults (premier lancement)

| Clé | Valeur usine |
|-----|----------------|
| manufacturer / codes | My Company, Myco, Mypl |
| copyright, website, email | vides |
| destination folder | **Desktop** (`QStandardPaths.DesktopLocation`) |
| juceDir | vide (placeholder OS) |
| plugin type | Instrument (synth) |
| formats | AU + VST3 + Standalone |
| cxxStandard | C++17 |
| preprocessor / headers | vides |
| copyToArtefactsDir | **false** |
| copyToSystemFolders | false |
| artefact paths | vides |

### 4.5 JUCE directory

- Champ sur **Preferences** (default) et **Project** (valeur du projet).
- **`juceDir` sur `ProjectSpec`** + sidecar `.luthier.json`.
- **Generate** lit `spec.juce_dir` — **supprimer** le paramètre séparé `juce_dir=` depuis Preferences dans le pipeline.
- **Révoquer AD-7** (Preferences-only) ; remplacer par règle du type : *juceDir is a ProjectSpec field; Preferences holds the default seed only.*

### 4.6 Destination folder

- Libellé : **Destination folder** * (Project et Preferences — pas « Default destination »).
- Sémantique : dossier **parent** ; à l’Open, `destinationDir = parent(project_dir)` (déjà en reader — conserver).
- **Pas** de modale systématique au Generate (régénération fluide) ; champ explicite documenté dans USER-MANUAL §5.6.
- Mémoriser **dernier dossier parent** après Generate réussi ; repli **Desktop** si invalide ; utiliser pour Choose… et dossier de départ Open Project….

### 4.7 UI — Choose…

Disposition : **label → Choose… → champ texte** (champ reste éditable).

| Emplacement | Choose… |
|-------------|---------|
| Project — Destination folder | Oui |
| Project — JUCE directory | Oui |
| Preferences — Destination folder | Oui |
| Preferences — JUCE directory | Oui |
| Artefacts Windows / macOS / Linux | **Non** (chemins cibles par OS pour CMake) |

Labels artefacts en Preferences : **Windows**, **macOS**, **Linux** (section artefacts).

**Project Info — ordre UI :** champs existants → Bundle ID → **Destination folder** → **JUCE directory**.

### 4.8 Templates

Inchangés — globaux, hors profils Import/Export.

---

## 5. Impact architecture — invariants à réviser

### AD-5 (REMPLACER)

**Ancien :** `prefs.update(spec)` + `save` sur generate/open success dans `MainWindow`.

**Nouveau (proposition) :**

- `preferences.json` est mis à jour **uniquement** par : création initiale, auto-save Preferences, Import Preferences.
- `MainWindow` appelle `prefs.save()` **seulement** après auto-save / import réussi (pas après Open/Generate).
- `Preferences.update(spec)` peut être **supprimé** ou réservé à un usage interne non lié Open/Generate — à trancher dans la proposal ; Open/Generate ne doivent plus synchroniser le profil global depuis le projet.

### AD-7 (REMPLACER)

**Ancien :** `juce_dir` jamais sur `ProjectSpec` ; passé séparément à `build_context`.

**Nouveau (proposition) :**

- `ProjectSpec` inclut `juce_dir` (JSON key `juceDir`).
- Sidecar inclut `juceDir` ; round-trip tests utilisent la valeur du spec (plus `juce_dir=""` systématique).
- `build_context(spec)` lit `spec.juce_dir` — signature `juce_dir=` param optionnel **déprécié / supprimé**.
- Preferences conserve `juceDir` comme **default seed** uniquement.

### AD-2 (PRÉCISER)

ProjectSpec reste le modèle unique ; préciser que champs **projet** vs champs **defaults** sont les mêmes structurellement mais alimentés depuis sources différentes (projet ouvert vs prefs).

### Stories historiques affectées (documentation, pas rollback code)

- 1.3, 1.6, 2.1, 2.2 — AC mentionnant `prefs.update` sur open/generate et AD-7.
- 3.4 — intégration `juce_dir=""`.
- Epic 1 story 1.6 — partie « juceDir not on ProjectSpec ».

**Pas de rollback** des Epics 1–3 : **ajustement forward** via Epic 5 + révision docs.

---

## 6. Impact PRD (sections à éditer)

Fichier : `_bmad-output/planning-artifacts/prds/prd-Luthier-2026-06-22/prd.md`

| Section | Changement attendu |
|---------|-------------------|
| **F7 — Preferences** | Profil complet (type, formats, compilation) ; Import/Export ; auto-save ; `preferences.json` seule source de defaults après 1er lancement ; pas de sync depuis Open/Generate |
| **F8 — UI** | Create New Project ; Import/Export Preferences ; Choose… ; libellés Destination folder ; JUCE sur Project ; indicateur auto-save ; barre d’actions par onglet |
| **FR8** (epics inventory) | Aligner avec F8 |
| Optionnel | Courte note design : pourquoi destination en champ vs modale Generate |

---

## 7. Epic 5 proposé — découpage stories

**Titre suggéré :** Epic 5 — Project & Preferences Workflows

**FRs :** extension de F7, F8 (nouvelles capacités UX).

### Story 5.1 — Preferences model & profile workflow

- Étendre `_DEFAULTS` + schéma JSON : pluginType, pluginFormats, cxxStandard, preprocessorDefinitions, headerSearchPaths.
- Factory file creation on first launch (Desktop, etc.).
- UI Preferences : sections type, formats, compilation ; labels Destination folder, artefacts Windows/macOS/Linux.
- Choose… destination + JUCE (Preferences only for artefacts: no Choose).
- Auto-save on valid edit + tab-bar saved indicator.
- Import Preferences… / Export Preferences… (replace Load/Save).
- Validation + error messages on import failure.

### Story 5.2 — Project UI, Choose buttons, layout

- Rename Destination → Destination folder ; reorder under Bundle ID ; JUCE directory field on Project.
- Choose… on Project destination + JUCE.
- Artefact labels on Project if applicable (Windows/macOS/Linux).
- Wire seed from prefs at startup and after import (refresh `_form_defaults` / equivalent).

### Story 5.3 — juceDir on ProjectSpec & generation pipeline

- Add `juce_dir` to `ProjectSpec` to_dict/from_dict.
- Sidecar includes juceDir.
- `build_context` / `ProjectGenerator.generate(spec)` without separate juce_dir arg.
- Update unit + integration tests (remove AD-7 empty juce workaround where obsolete).

### Story 5.4 — Decouple Open/Generate from preferences.json

- Remove `prefs.update` + `save` from `_load_project` and `_run_generation`.
- Implement last-used parent folder + Desktop fallback.
- Optional: prompt Choose if destination empty/invalid before generate (new project path).
- Revise AD-5 in spine ; update project-context.md if needed.

### Story 5.5 — Create New Project (full reset + dirty guard)

- `ProjectPage.reset()` resets all sections from prefs snapshot.
- Dirty baseline tracking + confirmation dialog.
- Does not write preferences.json.

**Ordre d’implémentation suggéré :** 5.1 → 5.3 → 5.2 → 5.4 → 5.5 (5.3 avant 5.4 car Generate lit spec.juce_dir). Le CC peut affiner.

---

## 8. Fichiers code — carte rapide

| Fichier | Changement attendu |
|---------|-------------------|
| `core/preferences.py` | Schéma étendu ; factory create ; last-used parent key (?); remove or narrow `update(spec)` |
| `core/project_spec.py` | `juce_dir` field |
| `core/render_context.py` | `build_context(spec)` only |
| `core/project_generator.py` | drop `juce_dir` param |
| `app/main_window.py` | Open/Generate decouple ; Import/Export ; indicator ; Create New Project |
| `app/pages/preferences.py` | UI expansion, auto-save, import/export |
| `app/pages/project.py` | full reset, sections from prefs |
| `app/pages/project_info.py` | layout, Choose, labels |
| `app/pages/plugin_type.py`, `formats.py`, `compilation.py` | remove hardcoded defaults as source of truth — read from prefs for seed |
| `tests/integration/test_round_trip.py` | juceDir in spec/sidecar |
| `tests/unit/test_render_context.py` | adjust juce tests |
| `Docs/USER-MANUAL.md` | déjà à jour — référence PO ; optionnel sync mineure post-CC |

---

## 9. Hors scope Epic 5

- Epic 4 PyInstaller (reste backlog après Epic 5).
- Template overrides per profile (templates stay global).
- Modale Choose obligatoire à chaque Generate sur projet ouvert.
- Choose… sur chemins d’artefacts multi-OS.
- Parser `set(JUCE_DIR)` depuis CMake pour Open (carte blanche sidecar — pas nécessaire).

---

## 10. Classification du changement

| Critère | Valeur |
|---------|--------|
| **Scope** | **Moderate** — nouveau epic, révision invariants, pas de rewrite total |
| **Rollback** | Non — forward fix |
| **Risque** | Moyen — tests round-trip + régression prefs |
| **Handoff post-CC** | `[CE] Create Epics and Stories` → `[CS]` / `[DS]` par story |

---

## 11. Critères de succès (acceptation Epic 5)

1. `Docs/USER-MANUAL.md` et comportement app **alignés** (checklist §12 du manuel).
2. Open puis Generate **ne modifient pas** `preferences.json` (test ou scénario manuel documenté).
3. Import profil → Create New Project → tous les champs seedés depuis profil (y compris type, formats, compilation).
4. `juceDir` round-trip dans `.luthier.json` après generate → open → regenerate (empty diff sur sidecar fields).
5. Choose… remplit destination et JUCE avec chemins OS-valides ; artefacts sans Choose.
6. Déplacement projet + Open → destination folder = nouveau parent.
7. Suite pytest verte ; adapter tests cassés par AD-5/AD-7.

---

## 12. Instructions explicites pour l’agent Correct Course

1. Charger PRD, epics.md, ARCHITECTURE-SPINE.md, sprint-status.yaml, **ce handoff**, **USER-MANUAL.md**.
2. Mode **Batch** : produire la Sprint Change Proposal complète avec edits OLD→NEW pour AD-5, AD-7, F7, F8, nouvel Epic 5 + stories.
3. **Ne pas** réécrire l’historique des Epics 1–3 comme « non done » — ajouter note de supersession / Epic 5 amends.
4. Proposer mise à jour `sprint-status.yaml` (epic-5 backlog, stories 5.1–5.5).
5. Recommander **Epic 5 avant Epic 4** dans la proposal.
6. Après approbation PO : handoff vers `[CE]` puis implémentation story par story.

---

## 13. Prompt prêt à coller

```
/bmad-correct-course

Change signal : _bmad-output/planning-artifacts/correct-course-handoff-epic-5-workflows.md
Vision produit validée : Docs/USER-MANUAL.md
Mode : Batch
Objectif : produire sprint-change-proposal avec révisions AD-5, AD-7, PRD F7/F8, Epic 5 (stories 5.1–5.5), sprint-status.
Priorité : Epic 5 avant Epic 4.
Conversation en français ; livrables planning en anglais.
```

---

*Fin de passation — Correct Course Epic 5 Workflows*
