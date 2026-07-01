# Deferred Work

**Gel MVP — 2026-07-01.** Epic 8 terminée (8.1 Workspace + 8.2 legacy cleanup). Ce registre ne sert plus de backlog sprint : il distingue **limitations acceptées pour v1**, **pistes post-MVP**, et **items retirés** (décisions de design ou hors périmètre).

Détails historiques par story : fichiers `_*-*.md` dans ce dossier (sections `[Review][Defer]`).

---

## Accepté pour v1 — limitations connues

Pas de story planifiée. Réouvrir seulement si retour utilisateur ou QA manuelle contredit cette acceptation.

| Item | Raison de l'acceptation |
|------|-------------------------|
| Pas de `fsync` après écriture temp (`atomic_write_text`) | Même niveau de durabilité qu'AD-4 `ProjectWriter` ; trade-off documenté (AD-10). |
| Fichiers `.tmp` orphelins après SIGKILL / coupure | Limitation inhérente à l'écriture atomique ; nettoyage manuel suffisant pour v1. |
| Pas de tests widget Qt (rollback import prefs, `MainWindow`, etc.) | Invariant **AD-6** ; logique core couverte par tests unitaires ; UI vérifiée en QA manuelle. |
| Position fenêtre Linux non garantie (Wayland / WM) | Limitation plateforme acceptée v1.0.0 ; taille restaurée, placement laissé au gestionnaire de fenêtres. |
| Garde no-Qt in-process (`test_core_imports.py`) | Choix explicite Story 7.4 ; couvre l'intention sans cold-import subprocess. |
| `read_project()` supprimé (Story 8.2) | API unique : `read_project_result()` avec `error`. |
| Conflit `set()` vs `juce_add_plugin` dans `_quoted_fields` | CMake legacy rare ; `set()` privilégié de façon cohérente. |
| `_cmake_quoted` : pas d'échappement newline/tab | Périmètre AC Story 7.3 (guillemets, `$`, espaces) ; entrées utilisateur normales non concernées. |

---

## Post-MVP — déclencher si douleur réelle

Ne pas planifier proactivement. Créer une story ou un quick-dev **uniquement** si le déclencheur observé se produit.

| Item | Déclencheur suggéré |
|------|---------------------|
| Cache pip/apt dans CI | Latence CI gênante (> ~5 min) ou quota GitHub Actions. |
| Retry `apt-get update` en CI | Échecs réseau intermittents observés sur le workflow. |
| Normaliser backslash dans `make_spec` / `_make_spec` | Dérive de tests cross-platform Windows. |
| `MemoryError` sur Templates Load File | Fichier volumineux ou crash observé en QA. |
| Champ `version` dans prefs / app_state JSON | Changement de schéma clés nécessitant une migration. |
| Refactor couplage widgets Préférences | Modification UI prefs rend le couplage par attributs internes pénible. |
| Paramétrisation `plugin_type` (effect/midi) sur round-trip intégration | Régression plugin type non détectée en CI. |
| Cas limites tests (validation, templates store, render_context, bundle PyInstaller) | Bug production ou lacune CI identifiée sur un de ces modules. |
| Docstring `project_reader` avec taxonomie d'erreurs (AD-3) | Confusion développeur récurrente sur les codes d'erreur. |

---

## Retiré du registre

Ces entrées ne sont **plus** de la dette ouverte — décision de design, hors scope, ou déjà livré. Conservées ici pour traçabilité ; ne pas re-synchroniser depuis les CR Epic 7.

| Item | Motif de retrait |
|------|------------------|
| Revert disque post-`save()` en échec d'import prefs | Hors scope : échec normalement **avant** `save()` (Story 7.2). |
| Subprocess vs in-process pour garde no-Qt | Résolu par choix d'implémentation 7.4 — voir « Accepté pour v1 ». |
| Tests widget `MainWindow` | AD-6 : invariant architectural, pas dette différée. |
| Écriture JSON non atomique | Résolu — Story 7.2, AD-10. |
| Chargement silencieux JSON corrompu | Résolu — Story 7.2, `load_warning` + barre de statut. |
| Tests legacy `tests/test_story_*.py` | Résolu — Story 7.4. |
| Section « Génération et rechargement (cas limites) » (7 items) | Résolu — Story 7.3. |
| `null` prefs → `"None"`, rollback import, polish éditeur Templates | Résolu — Story 7.4. |
| Items exclus d'Epic 7 (géométrie fenêtre, 6-1 status bar, StatusCapsule, logo README, dirty guard dialog, chemins Windows JSON, presets 4-3, 5-3/5-5, rename doc AD) | Livré hors Epic 7 ou story dédiée — voir purge 2026-06-28. |

---

## Référence rapide Epic 7

| Story | Statut | Dette MUST/SHOULD fermée |
|-------|--------|--------------------------|
| 7.1 CI pytest | done | Infrastructure CI |
| 7.2 Persistance JSON | done | Écriture atomique + feedback corrupt |
| 7.3 Core robustness | done | Cas limites génération / reload |
| 7.4 Hygiène tests + UI mineur | done | Legacy tests, polish prefs/templates |

## Référence rapide Epic 8

| Story | Statut | Livrable |
|-------|--------|----------|
| 8.1 Workspace per-OS paths | done | Section **Workspace**, six clés |
| 8.2 Pre-release legacy cleanup | done | Sidecar-only Open, drop CMake/migration paths |

**Prochaine étape produit :** QA manuelle post-Epic 8 (checklists `docs/checklist-qa-*.md`, parcours Git cross-plateforme avec **Workspace**). Passage public v1.0.0 quand QA validée.

---

## Deferred from: code review of 8-2-pre-release-legacy-cleanup (2026-07-01)

- `architecture-spine.md` AD-3 still mandates CMake fallback — story scope excluded planning spine; `docs/architecture.md` is current.
- Shallow sidecar validation (3 required fields) allows partial spec load — pre-existing from Story 7.3; broader validation is a separate story.
- Unreachable `plugin_formats` guard in `MainWindow._load_project` — harmless defensive branch.
- `test_workspace_migration.py` filename misleading after migration removal — cosmetic rename only.
- No integration test asserting generated `README.md` references USER OPTIONS — templates correct; manual QA covers.

---

## Deferred from: code review of 8-1-workspace-per-os-paths (2026-07-01)

- `project-context.md` still documents single `destination`/`juceDir` keys — stale agent context; update when convenient.
- `host_workspace_field_key` lives in `core/paths.py` not `app/pages/path_specs.py` as spec suggested — works via re-export; cosmetic spec alignment only.
