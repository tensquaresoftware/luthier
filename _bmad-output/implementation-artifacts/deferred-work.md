# Deferred Work

Registre vivant de la dette technique ouverte. **Resynchronisé le 2026-06-28** avec la codebase (modifs hors BMad incluses).

Items **retirés** depuis la purge précédente : géométrie fenêtre (`app_state.json`), barre de statut dédiée (6-1), annonces lecteurs d’écran (`StatusCapsule`), logo README (`docs/luthier.png`), convention `docs/` unique, dialog dirty guard (bouton No accent), chemins Windows JSON (`normalize_portable_path`), validation JSON presets (tests 4-3), reset projet complet (5-5), `juceDir` sur ProjectSpec (5-3), `architecture-explained.md` AD-5/AD-7.

---

## Infrastructure

- **Tests legacy** — Fichiers `tests/test_story_*.py` redondants avec la suite pytest ; fusion ou retrait à planifier.

## Deferred from: code review of 7-1-github-actions-ci-for-pytest (2026-06-28)

- No pip or apt caching in CI workflow — slower installs on every run; add `actions/cache` when CI latency becomes a concern.
- apt-get update has no retry on transient network failures — consider `nick-fields/retry` if flaky CI observed.
- Test helpers `make_spec` / `_make_spec` still allow backslash Windows path overrides via kwargs — normalize in helper if cross-platform test drift recurs.

## Persistance JSON (prefs + app_state)

- **Écriture non atomique** — Crash pendant `write_text` peut corrompre le fichier.
- **Pas de champ version** — Migrations futures ad hoc si les clés changent.
- **Chargement silencieux** — JSON corrompu → defaults sans message utilisateur.

## Génération et rechargement (cas limites)

- **Chemins spéciaux dans CMake** — Guillemets / `$` dans `JUCE_DIR` (`_juce_dir_line`) ; guillemets et caractères de contrôle dans entrées JSON artefact au-delà de la normalisation backslash.
- **Booléens mal typés** — `"ON"`, `"false"` (string) dans `from_dict` non convertis en bool.
- **Sidecar édité à la main** — Types incorrects ou `null` acceptés sans validation.
- **Cache CMake** — `CACHE BOOL` sans `FORCE` : regénération sans effet si cache existant.
- **Type de plugin inconnu** — `KeyError` brut au lieu d’erreur explicite.
- **Écriture projet** — Perte possible si `rename` échoue après suppression de l’ancien dossier (cas rare).
- **Lecture projets legacy** — Messages d’erreur peu discriminants ; regex CMake fragile (guillemets échappés) ; sidecar valide mais vide → defaults silencieux.

## Interface (mineur)

- **`null` dans prefs** — Peut apparaître comme `"None"` dans un champ dossier.
- **Import profil** — Rollback incomplet sur certains `ValueError`.
- **Couplage widgets Préférences** — Accès aux attributs internes des sections ; refactor si signaux unifiés.
- **Éditeur Templates** — Label d’état après Load File ; pas de validation de type de fichier ; erreurs lecture non gérées.

## Tests — durcissement optionnel

- Paramétrisation `plugin_type` (effect/midi) sur round-trip intégration.
- Cas limites validation, templates store, render_context, bundle PyInstaller (timeout, encoding, layout `_internal`).
- Pas de tests widget `MainWindow` (AD-6, volontaire).
- Garde no-Qt au premier import (subprocess).

## Référence

Détails historiques par story : fichiers `_*-*.md` dans ce dossier (sections `[Review][Defer]`). Ce registre ne liste que l’**ouvert** consolidé.
