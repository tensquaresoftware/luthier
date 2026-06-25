# Create Epics and Stories — Passation (handoff)

**Project:** Luthier  
**Date:** 2026-06-25  
**Author:** Guillaume DUPONT (PO)  
**Workflow:** `[CE] bmad-create-epics-and-stories`  
**Mode recommandé:** **Validation incrémentale** — ne pas réécrire Epics 1–4 ; **synchroniser et valider Epic 5**

---

## 1. Comment utiliser ce document

Nouvelle conversation :

```
/bmad-create-epics-and-stories
```

Puis :

> Passation CE : `_bmad-output/planning-artifacts/create-epics-handoff-epic-5.md`  
> Correct Course approuvé : `_bmad-output/planning-artifacts/sprint-change-proposal-2026-06-25.md`  
> Vision produit : `Docs/USER-MANUAL.md`  
> Mode : **validation incrémentale Epic 5** (pas de refonte Epics 1–4)

**Langue :** conversation **français** ; mises à jour `epics.md` en **anglais** (NFR5).

---

## 2. État actuel — ce qui est DÉJÀ fait

| Artefact | Statut |
|----------|--------|
| `sprint-change-proposal-2026-06-25.md` | **Approuvé** PO 2026-06-25 |
| `prd.md` F5/F7/F8 | **Mis à jour** (selon proposal §4.1–4.3) |
| `ARCHITECTURE-SPINE.md` AD-2/5/7 | **Mis à jour** (selon proposal §4.4–4.6) |
| `epics.md` Epic 5 + stories 5.1–5.5 | **Présent** (bloc complet avec AC) |
| `epics.md` AD-5/AD-7, FR map, supersession note | **Mis à jour** |
| `sprint-status.yaml` Epic 5 | **Présent** (5.1–5.5 en backlog) |
| `Docs/USER-MANUAL.md` | **Vision PO validée** |
| Fichiers `implementation-artifacts/5-*.md` | **Absents** — hors scope CE ; créés par `[CS] Create Story` |

**Frontmatter `epics.md` actuel :**

```yaml
stepsCompleted: ['step-01', 'step-02', 'step-03', 'step-04']
inputDocuments: [prd.md, ARCHITECTURE-SPINE.md]
```

→ Les 4 steps CE ont été marqués complets lors du Correct Course, mais l’**inventaire des exigences** (§ Requirements Inventory) n’a **pas** été resynchronisé avec le PRD révisé.

---

## 3. Objectif de CE dans ce contexte

**Ne pas** repartir de zéro sur tout `epics.md`.

**Faire :**

1. **Step 1 (ciblé)** — Resynchroniser l’inventaire FR7/FR8/UX avec PRD + USER-MANUAL ; enrichir `inputDocuments`.
2. **Step 2** — Confirmer structure Epic 5 dans Epic List (déjà OK) ; **N/A** pour Epics 1–4.
3. **Step 3** — **N/A réécriture** stories 5.1–5.5 si AC alignés proposal ; ajouter AC manquants seulement si gap trouvé.
4. **Step 4** — Exécuter checklist validation **Epic 5** ; documenter ordre d’implémentation et dépendances.

**Livrable CE :** `epics.md` à jour (inventaire + validation report en fin de doc ou commentaire) ; confirmation « Epic 5 ready for Create Story ».

**Pas CE :** fichiers story `implementation-artifacts/5-*.md` → workflow **`[CS] Create Story`** ensuite.

---

## 4. Documents à charger (ordre)

| Priorité | Fichier | Usage |
|----------|---------|-------|
| 1 | `create-epics-handoff-epic-5.md` | Ce handoff |
| 2 | `sprint-change-proposal-2026-06-25.md` | AC canoniques Epic 5 |
| 3 | `Docs/USER-MANUAL.md` | UX authoritative (pas de doc UX formelle) |
| 4 | `epics.md` | Cible à patcher |
| 5 | `prds/.../prd.md` | F7, F8, F5 révisés |
| 6 | `architecture/.../ARCHITECTURE-SPINE.md` | AD-2/5/7 |
| 7 | `implementation-artifacts/sprint-status.yaml` | Vérifier cohérence slugs |
| 8 | `correct-course-handoff-epic-5-workflows.md` | Contexte historique (optionnel) |

**Exclure de l’analyse :** réécriture des stories Epic 1–3 (done).

---

## 5. Gaps connus à corriger dans `epics.md`

### 5.1 Requirements Inventory — FR7 (STALE)

**Actuel (l.24) :**
> FR7: Preferences persist default values for all company identity fields and default artefact configuration…

**Remplacer par** (synthèse PRD F7 révisé) :

```
FR7: Preferences hold a complete global profile in preferences.json (identity, destination folder, JUCE default seed, plugin type, formats, compilation, artefacts). Factory defaults on first launch only; thereafter all Project seeding reads preferences.json. Auto-save on valid edit; Import replaces profile; Export copies without touching preferences.json. Open and Generate never write preferences.json.
```

### 5.2 Requirements Inventory — FR8 (STALE)

**Actuel (l.25) :**
> FR8: … bottom bar with "Open Project…" and "Generate Project" only…

**Remplacer par** (synthèse PRD F8 révisé) :

```
FR8: Tab bar (Project, Preferences, Templates, About) with per-tab action bar: Project — Create New Project, Open Project…, Generate Project; Preferences — Import Preferences…, Export Preferences…; Templates — Load from file…, Reset to default, Save override. Project form sections with Destination folder and JUCE directory (label → Choose… → field); Preferences mirrors defaults with same labels; auto-save indicator in tab bar. Dark theme, orange accent.
```

### 5.3 UX Design Requirements (STALE)

**Actuel (l.49–51) :** `N/A — No formal UX design contract`

**Remplacer par :**

```
UX-DR1: Authoritative UX reference is Docs/USER-MANUAL.md (PO-validated target, 2026-06-24+). No separate Figma/wireframe. Epic 5 implements USER-MANUAL §3–§9 and §12 checklist.
UX-DR2: Choose… on local paths only (destination, JUCE); not on cross-OS artefact path fields.
UX-DR3: Destination folder = parent directory; Open recalculates from filesystem.
```

### 5.4 inputDocuments (frontmatter)

**Ajouter :**

```yaml
inputDocuments:
  - _bmad-output/planning-artifacts/prds/prd-Luthier-2026-06-22/prd.md
  - _bmad-output/planning-artifacts/architecture/architecture-Luthier-2026-06-22/ARCHITECTURE-SPINE.md
  - Docs/USER-MANUAL.md
  - _bmad-output/planning-artifacts/sprint-change-proposal-2026-06-25.md
```

### 5.5 Epic 5 header — FR references

**Actuel :** `**FRs covered:** F7 (extended), F8 (extended)`

**Corriger en :** `**FRs covered:** FR7 (extended), FR8 (extended)`

### 5.6 FR5 line (optionnel)

FR map l.59 : `FR5: Epic 1 — Artefacts…` — ajouter note : *defaults in Preferences, values at generate from Project tab (PRD F5 clarification)*.

---

## 6. Epic 5 — stories (référence AC, ne pas dupliquer sauf gap)

Les AC ci-dessous sont **déjà** dans `epics.md` — la CE doit **valider**, pas réinventer.

| Story | Slug sprint-status | Dépend de |
|-------|-------------------|-----------|
| 5.1 Preferences Model & Profile Workflow | `5-1-preferences-model-profile-workflow` | — |
| 5.2 Project UI, Choose Buttons & Layout | `5-2-project-ui-choose-buttons-layout` | 5.1 (seed), 5.3 (JUCE on Project field) |
| 5.3 juceDir on ProjectSpec & Pipeline | `5-3-jucedir-on-projectspec-generation-pipeline` | 5.1 |
| 5.4 Decouple Open/Generate from prefs | `5-4-decouple-open-generate-from-preferences-json` | 5.3 |
| 5.5 Create New Project + dirty guard | `5-5-create-new-project-full-reset-dirty-guard` | 5.1, 5.2 |

**Ordre d’implémentation PO (proposal §3.4) :** `5.1 → 5.3 → 5.2 → 5.4 → 5.5`

### 6.1 AC additionnels à vérifier (proposer si absents)

| Story | AC suggéré si manquant |
|-------|------------------------|
| 5.1 | After Import, refresh in-memory seed cache used by Project (`_form_defaults` or equivalent) even though Project tab UI unchanged |
| 5.1 | `Preferences.update(ProjectSpec)` removed or unused for Open/Generate paths |
| 5.2 | JUCE directory field on Project wired to `ProjectSpec.juce_dir` (after 5.3) |
| 5.3 | `ProjectSpec.to_dict` / `from_dict` round-trip includes `juceDir` in unit tests |
| 5.4 | Test or documented scenario: open project → generate → `preferences.json` mtime/content unchanged |
| 5.5 | Dirty baseline updates on: cold start seed, Open success, Create New Project success |

---

## 7. Checklist Step 4 — Epic 5 seulement

Cocher et rapporter dans la conversation :

- [ ] FR7 extended requirements → stories 5.1, 5.4, 5.5
- [ ] FR8 extended requirements → stories 5.1, 5.2, 5.5
- [ ] AD-5 revised → story 5.4
- [ ] AD-7 revised → story 5.3
- [ ] USER-MANUAL §12 items mappés 1:1 vers une story
- [ ] Aucune story Epic 5 ne dépend d’une story **future** du même epic (5.2 après 5.3 OK au niveau dev order, pas AC bloquant)
- [ ] Chaque story = une session dev agent réaliste
- [ ] Slugs `sprint-status.yaml` alignés titres epics.md

### Mapping USER-MANUAL §12 → stories

| §12 item | Story |
|----------|-------|
| Destination folder, JUCE on Project, layout | 5.2 |
| Import/Export, auto-save, indicator | 5.1 |
| Create New Project reset | 5.5 |
| Extended preferences.json | 5.1 |
| juceDir on ProjectSpec | 5.3 |
| Decouple Open/Generate | 5.4 |
| Factory defaults, last parent, Desktop fallback | 5.1 + 5.4 |
| Choose… rules | 5.1 + 5.2 |

---

## 8. Hors scope CE

- Implémentation code (`[DS]`)
- Fichiers story `implementation-artifacts/5-*.md` (`[CS]` — **prochaine** étape après CE)
- Epic 4 stories (inchangées, backlog après Epic 5)
- Modification des stories Epic 1–3 marquées done

---

## 9. Après CE — enchaînement PO

```
1. [CE]  ← cette session (validation + sync epics.md)
2. [CS] Create Story — story 5.1 (contexte frais)
3. [DS] Dev Story 5.1
4. [CR] Code Review
5. Répéter CS → DS → CR pour 5.3, 5.2, 5.4, 5.5 (ordre dev ci-dessus)
6. Epic 4 quand Epic 5 done
```

---

## 10. Critères de succès CE

1. `epics.md` Requirements Inventory FR7/FR8/UX alignés PRD + USER-MANUAL.
2. `inputDocuments` frontmatter complet.
3. Rapport validation Step 4 Epic 5 sans gap bloquant.
4. PO confirme : **« Epic 5 ready for Create Story 5.1 »**.

---

## 11. Prompt prêt à coller

```
/bmad-create-epics-and-stories

Passation : _bmad-output/planning-artifacts/create-epics-handoff-epic-5.md
Proposal approuvée : _bmad-output/planning-artifacts/sprint-change-proposal-2026-06-25.md
UX : Docs/USER-MANUAL.md

Mode : validation incrémentale Epic 5 uniquement.
Ne pas réécrire Epics 1–4 ni leurs stories.

Tâches :
1. Resynchroniser FR7, FR8, UX-DR dans epics.md Requirements Inventory (§5 du handoff).
2. Mettre à jour inputDocuments frontmatter.
3. Valider stories 5.1–5.5 vs proposal ; ajouter AC manquants §6.1 si besoin.
4. Exécuter checklist Step 4 Epic 5 ; confirmer ordre 5.1→5.3→5.2→5.4→5.5.
5. Confirmer prêt pour [CS] story 5.1.

Français en conversation ; epics.md en anglais.
```

---

*Fin de passation — Create Epics and Stories Epic 5*
