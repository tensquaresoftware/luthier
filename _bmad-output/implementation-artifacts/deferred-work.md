# Deferred Work

Registre vivant de la dette technique ouverte. **Resynchronisé le 2026-06-28** avec la codebase (modifs hors BMad incluses).

Items **retirés** depuis la purge précédente : géométrie fenêtre (`app_state.json`), barre de statut dédiée (6-1), annonces lecteurs d’écran (`StatusCapsule`), logo README (`docs/luthier.png`), convention `docs/` unique, dialog dirty guard (bouton No accent), chemins Windows JSON (`normalize_portable_path`), validation JSON presets (tests 4-3), reset projet complet (5-5), `juceDir` sur ProjectSpec (5-3), `architecture-explained.md` AD-5/AD-7.

---

## Infrastructure

- ~~**Tests legacy** — Fichiers `tests/test_story_*.py` redondants avec la suite pytest ; fusion ou retrait à planifier.~~ *(Résolu — Story 7.4)*

## Deferred from: code review of 7-1-github-actions-ci-for-pytest (2026-06-28)

- No pip or apt caching in CI workflow — slower installs on every run; add `actions/cache` when CI latency becomes a concern.
- apt-get update has no retry on transient network failures — consider `nick-fields/retry` if flaky CI observed.
- Test helpers `make_spec` / `_make_spec` still allow backslash Windows path overrides via kwargs — normalize in helper if cross-platform test drift recurs.

## Deferred from: code review of 7-2-atomic-json-persistence-corrupt-file-feedback (2026-06-28)

- No `fsync` after temp write in `atomic_write_text` — same durability level as AD-4 `ProjectWriter`; add if crash/power-loss persistence becomes a requirement.
- Orphaned `.tmp` files after SIGKILL or power loss — inherent atomic-write limitation; no automatic recovery path beyond manual cleanup.

## Deferred from: code review of 7-4-test-hygiene-minor-ui-hardening (2026-06-28)

- No automated `PreferencesPage.import_from_file` UI rollback test — AD-6 no Qt widget tests; manual QA for widget refresh on import failure.
- Post-`save()` disk revert on import failure — out of scope; failure normally occurs before `save()` (Story 7.2 atomic write).
- In-process no-Qt import guard (`test_core_imports.py`) vs subprocess cold-import — weaker than subprocess but matches Story 7.4 migration sketch.
- MemoryError uncaught on Templates Load File (`read_text`) — edge case for very large files; catch alongside OSError if observed in QA.

## Deferred from: code review of 7-3-core-generation-reload-robustness (2026-06-28)

- `read_project()` still returns only `.spec` without `error` — pre-existing API; app layer uses `read_project_result()`.
- Module docstring not extended with error taxonomy — spec suggested AD-3 note in docstring only.
- Conflicting `set()` vs `juce_add_plugin` identity values — `_quoted_fields` prefers `set()` when both differ (rare legacy CMake).
- `_cmake_quoted` does not escape CMake control characters (newline/tab) — AC1 covers quotes/`$`/spaces only.

## Persistance JSON (prefs + app_state)

- ~~**Écriture non atomique** — Crash pendant `write_text` peut corrompre le fichier.~~ *(Résolu — Story 7.2, AD-10)*
- **Pas de champ version** — Migrations futures ad hoc si les clés changent.
- ~~**Chargement silencieux** — JSON corrompu → defaults sans message utilisateur.~~ *(Résolu — Story 7.2, `load_warning` + status bar)*

## Génération et rechargement (cas limites)

~~- **Chemins spéciaux dans CMake** — Guillemets / `$` dans `JUCE_DIR` (`_juce_dir_line`) ; guillemets et caractères de contrôle dans entrées JSON artefact au-delà de la normalisation backslash.~~ *(Story 7.3)*
~~- **Booléens mal typés** — `"ON"`, `"false"` (string) dans `from_dict` non convertis en bool.~~ *(Story 7.3)*
~~- **Sidecar édité à la main** — Types incorrects ou `null` acceptés sans validation.~~ *(Story 7.3)*
~~- **Cache CMake** — `CACHE BOOL` sans `FORCE` : regénération sans effet si cache existant.~~ *(Story 7.3)*
~~- **Type de plugin inconnu** — `KeyError` brut au lieu d’erreur explicite.~~ *(Story 7.3)*
~~- **Écriture projet** — Perte possible si `rename` échoue après suppression de l’ancien dossier (cas rare).~~ *(Story 7.3 — documenté + test)*
~~- **Lecture projets legacy** — Messages d’erreur peu discriminants ; regex CMake fragile (guillemets échappés) ; sidecar valide mais vide → defaults silencieux.~~ *(Story 7.3)*

## Interface (mineur)

- ~~**`null` dans prefs** — Peut apparaître comme `"None"` dans un champ dossier.~~ *(Résolu — Story 7.4)*
- ~~**Import profil** — Rollback incomplet sur certains `ValueError`.~~ *(Résolu — Story 7.4)*
- **Couplage widgets Préférences** — Accès aux attributs internes des sections ; refactor si signaux unifiés.
- ~~**Éditeur Templates** — Label d’état après Load File ; pas de validation de type de fichier ; erreurs lecture non gérées.~~ *(Résolu — Story 7.4)*

## Tests — durcissement optionnel

- Paramétrisation `plugin_type` (effect/midi) sur round-trip intégration.
- Cas limites validation, templates store, render_context, bundle PyInstaller (timeout, encoding, layout `_internal`).
- Pas de tests widget `MainWindow` (AD-6, volontaire).
- ~~Garde no-Qt au premier import (subprocess).~~ *(Résolu — Story 7.4, `test_core_imports.py`)*

## Référence

Détails historiques par story : fichiers `_*-*.md` dans ce dossier (sections `[Review][Defer]`). Ce registre ne liste que l’**ouvert** consolidé.
