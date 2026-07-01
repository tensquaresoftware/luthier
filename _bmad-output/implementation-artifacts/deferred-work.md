# Deferred Work

**Gel MVP — 2026-06-29.** Epic 7 terminée ; critères MUST/SHOULD du sprint change proposal satisfaits. Ce registre ne sert plus de backlog sprint : il distingue **limitations acceptées pour v1**, **pistes post-MVP**, et **items retirés** (décisions de design ou hors périmètre).

Détails historiques par story : fichiers `_*-*.md` dans ce dossier (sections `[Review][Defer]`).

---

## Accepté pour v1 — limitations connues

Pas de story planifiée. Réouvrir seulement si retour utilisateur ou QA manuelle contredit cette acceptation.

| Item | Raison de l'acceptation |
|------|-------------------------|
| Pas de `fsync` après écriture temp (`atomic_write_text`) | Même niveau de durabilité qu'AD-4 `ProjectWriter` ; trade-off documenté (AD-10). |
| Fichiers `.tmp` orphelins après SIGKILL / coupure | Limitation inhérente à l'écriture atomique ; nettoyage manuel suffisant pour v1. |
| Pas de tests widget Qt (rollback import prefs, `MainWindow`, etc.) | Invariant **AD-6** ; logique core couverte par tests unitaires ; UI vérifiée en QA manuelle. |
| Garde no-Qt in-process (`test_core_imports.py`) | Choix explicite Story 7.4 ; couvre l'intention sans cold-import subprocess. |
| `read_project()` sans champ `error` | API legacy ; couche app utilise `read_project_result()`. |
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

**Prochaine étape produit :** QA manuelle (semaine 2026-07-07). Pas d'Epic 8 « vider deferred-work » sans signal utilisateur.

---

## Deferred from: code review of 8-1-workspace-per-os-paths (2026-07-01)

- `project-context.md` still documents single `destination`/`juceDir` keys — stale agent context; update when convenient.
- `host_workspace_field_key` lives in `core/paths.py` not `app/pages/path_specs.py` as spec suggested — works via re-export; cosmetic spec alignment only.
