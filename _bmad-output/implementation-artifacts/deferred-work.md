# Deferred Work

## Deferred from: manual smoke 5-5-create-new-project-full-reset-dirty-guard (2026-06-25)

- **Barre de statut / messages utilisateur** (`app/main_window.py`) — Message Create New Project à gauche des boutons, manque de place ; souhait : barre dédiée au-dessus de la barre d’actions (#262F34), texte centré orange (succès) / rouge (erreur) ; libellé « New project created — defaults from Preferences. »
- **Bouton No dialog dirty guard peu visible** (`MainWindow._on_create_new_project`) — Default `QMessageBox.No` non perceptible visuellement ; suggéré : style orange pour l’action par défaut.
- **Persistance géométrie fenêtre** — À l’ouverture, fenêtre en (0,0) ; taille/position non mémorisées (hors scope story 5.5).

## Deferred from: code review of 5-5-create-new-project-full-reset-dirty-guard (2026-06-25)

- **Manual smoke AC2 dialog not verified** — Five UI scenarios in story Tasks/Subtasks (dirty/clean dialog, No/Yes, prefs mtime) not run before merge; code in `MainWindow._on_create_new_project()` matches spec; AD-6 defers dialog UX to manual tier. *(Partially addressed 2026-06-25: scenarios 1/2/3/5 PASS on `Dist/Luthier.app`.)*

## Deferred from: code review of 5-4-decouple-open-generate-from-preferences-json (2026-06-25)

- **Tests AC6 simulés, pas de parcours MainWindow e2e** (`tests/unit/test_preferences_decouple.py`) — Test construit `ProjectSpec` et `AppState` directement ; ne pilote pas `MainWindow._load_project` / `_run_generation`. Pattern AD-6 (pas de tests widget Qt).
- **Prompt destination AC4 non couvert par tests automatisés** (`app/main_window.py:206`) — Aucun test pour le dialog pré-génération (vide/invalide, annulation, rebuild spec).
- **`AppState.load()` avale JSON/OSError silencieusement** (`core/app_state.py:36`) — Même pattern que `Preferences._read()` ; fichier corrompu → état par défaut sans feedback utilisateur.
- **Écriture JSON non-atomique** (`core/app_state.py:48`) — `write_text` direct ; crash mid-write peut corrompre le fichier. Même pattern que `Preferences.save()`.
- **Pas de champ version dans `app_state.json`** (`core/app_state.py`) — Même dette que `preferences.json` (déjà différée en revue 5-1).
- **`ARCHITECTURE-EXPLAINED.md` AD-5 obsolète** — Décrit encore l'ancien modèle `prefs.update` + `save` après Open/Generate ; `ARCHITECTURE-SPINE.md` et `project-context.md` sont à jour.

## Deferred from: code review of 5-2-project-ui-choose-buttons-layout (2026-06-25)

- **`reset()` ne reseed que `ProjectInfoPage`** (`app/pages/project.py:64-66`) — `reset()` appelle `_info.load()` seulement ; type/formats/compilation/artefacts restent inchangés. Pré-existant ; Story 5.5 couvrira le reset complet + dirty guard.
- **`prefs.get()` peut propager `None` vers `FolderField`** (`app/pages/preferences.py:46-59`) — JSON null survit `validate_optional_path` via `str(None)` ; pattern pré-existant avant extraction `path_specs`.
- **`reset()` incomplet si appelé après changement type/formats** (`app/pages/project.py:64-66`) — Même cause que ci-dessus ; Create New Project via `reset()` ne réinitialise pas les sections hors Project Info.
- **Rollback `import_from_file` sans garde sur `ValueError`** (`app/pages/preferences.py:107-109`) — Pré-existant ; hors hunks du diff 5.2.
- **Accès attributs privés `_artefacts._checks`** (`app/pages/preferences.py:169-172`) — Couplage widget pré-existant depuis 5.1 ; refactor quand sections exposent des signaux unifiés.


- **Generate UI sans injection prefs `juceDir`** (`app/main_window.py:256`) — Comportement attendu AD-7 révisé ; prefs ne sont plus lues à generate time jusqu'à Story 5.2 (Project tab FolderField).
- **Open → Generate perd `juceDir` côté UI** (`app/pages/project.py:43-49`) — `ProjectPage.spec()` reconstruit depuis les widgets sans champ JUCE ; `load()` ne préserve pas `juceDir` jusqu'à Story 5.2.
- **Regenerate après lecture CMake-only supprime ligne `JUCE_DIR`** (`core/project_generator.py:39`) — `project_reader` ne parse pas `JUCE_DIR` depuis CMake ; spec 5.3 accepte `juce_dir` vide pour projets legacy sans sidecar.
- **`from_dict` avec `juceDir: null` en JSON** (`core/project_spec.py:66`) — `d.get("juceDir", "")` retourne `None` si clé présente avec valeur null ; pattern pré-existant sur tous les champs depuis story 1-1.
- **Échappement chemins spéciaux dans `_juce_dir_line`** (`core/render_context.py:35`) — Guillemets/backslashes interpolés bruts dans `set(JUCE_DIR "...")` ; pré-existant depuis story 1-6.
- **Sidecar whitespace-only vs CMake vide** (`core/project_spec.py:66`) — `_juce_dir_line` strip pour CMake mais sidecar sérialise la valeur brute ; hors AC 5.3.

## Deferred from: code review of 5-1-preferences-model-profile-workflow (2026-06-25)

- **Private-widget coupling in auto-save wiring** (`app/pages/preferences.py:168-171`) — PreferencesPage reaches into `_artefacts._checks`, `_compilation._cxx._combo`, etc. Pre-existing pattern across section widgets; refactor when sections expose unified change signals.
- **No JSON schema version field** (`core/preferences.py`) — Profile import/export has no version key; future key renames require ad-hoc migration. Epic 5 sequencing defers until AD-5 lands in 5.4.
- **Method length exceeds 15-line guideline** (`core/preferences.py`, `app/pages/preferences.py`) — `validate_profile`, `seed_dict`, `_connect_auto_save` exceed clean-code limit; project-context documents conscious exceptions for data/orchestration blocks.
- **`test_import_validation_preserves_existing_on_failure` does not call `import_from_file`** (`tests/unit/test_preferences.py:85-94`) — AD-6 unit tier avoids Qt widget tests; test exercises `validate_profile` + manual rollback instead of the page import path.

## Deferred from: code review of 3-4-integration-tests-project-generation-round-trip (2026-06-24)

- **No `plugin_type` parametrization** (`tests/integration/test_round_trip.py`) — Spec marks `@pytest.mark.parametrize("plugin_type", …)` as optional high-value coverage; synth-only golden path satisfies AC.
- **Malformed sidecar test not ported** (`tests/integration/test_round_trip.py`) — Spec explicitly optional; `test_story_2_1::test_malformed_sidecar_returns_none_no_cmake_fallback` retains coverage in unittest tier.
- **`IS_SYNTH` / plugin-type CMake fallback variants** (`tests/integration/test_round_trip.py:96-108`) — Negative case uses `COMPANY_NAME` strip only; effect/midi inference on CMake fallback deferred to future hardening.
- **`test_partial_cmake` regex narrow** (`tests/integration/test_round_trip.py:103`) — Matches legacy `test_story_2_2` pattern; broader CMake formatting variants are Epic 3+ scope.
- **Legacy compat test regex coupled to template banner** (`tests/integration/test_round_trip.py:151-157`) — DOTALL block removal depends on `# PLUGIN COPY CONFIGURATION` section text; template refactor is separate from reader compat.
- **No `read_project` round-trip via `write_project`** (`tests/integration/test_round_trip.py`) — AC2 uses `generate_project`; writer-only read parity is optional hardening beyond epic AC.
- **Byte-identical tree comparison sensitivity** (`tests/conftest.py:49-52`) — Theoretical flakiness if templates emit non-deterministic bytes; same approach as legacy unittest round-trip tests.

## Deferred from: code review of 3-3-unit-tests-projectspec-and-templates-store (2026-06-23)

- **JSON string round-trip untested** (`tests/unit/test_project_spec.py:56-70`) — Tests call `json.dumps` only; no `json.loads` → `from_dict` path. AC2 satisfied; full sidecar persistence path is story 3-4 integration scope.
- **GITIGNORE reset contract untested** (`tests/unit/test_templates_store.py:39-45`) — Reset tested on `PluginProcessor.h` only; gitignore override path (`templates_root()/.gitignore`) uses same `_override_path` logic but is not exercised for reset.
- **`read_default` GITIGNORE bundled path untested** (`tests/unit/test_templates_store.py:59-61`) — Optional bundled match test covers `PluginProcessor.h` only; `_bundled_path` gitignore branch (`templates_dir() / .gitignore`) untested.
- **`from_dict` type/null/empty-string edge cases** (`tests/unit/test_project_spec.py:73-80`) — Partial dict with one key tested per AC; null values, wrong types, and empty strings overriding non-empty defaults are pre-existing `from_dict` behavior (tracked since story 1-1).
- **Empty override and idempotent `reset()` semantics** (`tests/unit/test_templates_store.py:25-45`) — Empty `save_override` content, double-save overwrite, and `reset()` when no file exists not tested; explicitly deferred in story dev notes.

## Deferred from: code review of 3-2-unit-tests-rendering-render-context (2026-06-23)

- **No-Qt import guard limited to re-import** (`tests/unit/test_rendering.py:36`, `tests/unit/test_render_context.py:140`) — Guard re-imports modules already loaded at file top; first-load Qt leak would not be detected. Same AD-8 pattern as story 3-1; shared subprocess/reload fixture deferred to story 3-4.
- **`render()` / `render_tokens()` edge cases beyond AC** (`tests/unit/test_rendering.py`) — Malformed `str.format`, positional `{}`, multi-distinct `@KEY@` in one string, nested token substitution order. AC satisfied; extra cases are Epic 3+ hardening.
- **Whitespace-only preprocessor/header lines** (`tests/unit/test_render_context.py:77`) — `_non_empty_lines` strips blank lines in production; whitespace-only input not explicitly tested.
- **Unknown `plugin_type` KeyError** (`tests/unit/test_render_context.py:100`) — Explicitly deferred in story dev notes; `flags_for_type` behavior pre-existing.
- **`copyToSystemFolders` / `copyToArtefactsDir` ON/OFF mapping** (`tests/unit/test_render_context.py:111`) — `_copy_config` bool→ON/OFF not asserted; outside epic AC.
- **Artefact entry generation** (`tests/unit/test_render_context.py:50`) — Recommended in dev notes, not epic AC; `_artefact_entries` wiring untested here.
- **`bundleId` sanitization** (`tests/unit/test_render_context.py`) — Covered in story 3-1 `test_plugin_settings.py`; render_context tests verify wiring only per spec.
- **`cxxStandard` C++→numeric strip** (`tests/unit/test_render_context.py:64`) — `_extra_fields` replaces `"C++"` prefix; not in story AC.
- **`juce_dir` paths with quotes/backslashes** (`tests/unit/test_render_context.py:125`) — Known deferred production issue since story 1-6; AD-7 empty/set cases covered.
- **Empty `project_name` / `project_display_name` in `build_tokens`** (`tests/unit/test_render_context.py:131`) — Edge case outside AC; only two production tokens exist.
- **`KeyError` test missing key name assertion** (`tests/unit/test_rendering.py:18`) — Asserts exception type only; minor hardening, not AC gap.

## Deferred from: code review of 3-1-test-infrastructure-unit-tests-validators-and-plugin-settings (2026-06-23)

- **Validation boundary coverage gaps** (`tests/unit/test_validation.py`) — Leading `_`/`-` project names, tab chars in display name, padded version/manufacturer strings, 5-char manufacturer code, underscore in plugin code, whitespace-only optional path not covered. Story dev matrix satisfied; extra cases are Epic 3+ hardening.
- **Plugin settings edge cases untested** (`tests/unit/test_plugin_settings.py`) — Unknown `type_key` KeyError, dual-TRUE flag precedence (`type_for_flags`, `au_and_vst3_categories`), lowercase/malformed flag strings, empty manufacturer/project segments after sanitization in `bundle_id`. AC3 met for the three known types.
- **No CI workflow for pytest** (project root) — Story spec explicitly excludes CI (no `.github/` yet). Tests run locally (67 pytest + 20 unittest verified green).
- **Shared test helpers not centralized** (`tests/unit/`) — `_assert_result` and no-Qt pattern duplicated across files; story notes `tests/conftest.py` deferred to story 3-4.

## Deferred from: code review of 2-2-cmake-regex-fallback-for-legacy-projects (2026-06-23)

- **Échec sidecar sans raison structurée** (`core/project_reader.py:74-75`) — `ProjectReadResult` ne distingue pas JSON invalide, permission refusée ou payload non-dict. Hors périmètre 2-2 (story 2-1).
- **Chemin sidecar sans gate de complétude** (`core/project_reader.py:83-91`) — Un sidecar syntaxiquement valide avec champs vides charge des defaults silencieux. Explicitement hors scope 2-2.
- **Validation `pluginFormats` divergente sidecar vs CMake** (`app/main_window.py:150-154`) — Même échec, messages différents selon le chemin de lecture. Chemin sidecar = story 2-1.
- **`project()` absent → diagnostics vides** (`core/project_reader.py:116-117`) — CMakeLists.txt présent mais sans ligne `project()` : `missing_fields=()` et message générique « Not a JUCE plugin » au lieu d'un message parse CMake.
- **`OSError`/`UnicodeDecodeError` non capturés dans `_parse_build_settings`** (`core/project_reader.py:199`) — Pré-existant depuis review 1-4 ; `_parse_build_settings` inchangé dans sa logique interne.
- **`OSError` sur lecture CMake classé « not a JUCE project »** (`core/project_reader.py:104-105`) — Fichier présent mais illisible : pas de message parse CMake distinct.
- **`UnicodeDecodeError` non capturé sur lecture CMake** (`core/project_reader.py:103`) — Sidecar le capture ; CMake non. Durcissement optionnel.
- **`ProjectReadResult` sans enum de type d'erreur** (`core/project_reader.py:66-69`) — UI infère le mode d'échec via heuristiques (`sidecar.exists()`, `missing_fields`). Amélioration design future.
- **Regex `_quoted_fields` plus faible que `_SET_RE`** (`core/project_reader.py:172`) — Guillemets échappés (`O\"Reilly`) non gérés ; faux positifs « Company Name » manquant. Pré-existant.
- **Tests manquants : `IS_SYNTH` absent, `CMAKE_CXX_STANDARD` absent** (`tests/test_story_2_2.py`) — Logique implémentée mais non exercée ; gap couverture non bloquant.
- **Tests manquants : chemin UI `MainWindow._load_project()`** (`tests/test_story_2_2.py`) — AC4 dialogues CMake non testés (core-only par design story).
- **Tests manquants : échec multi-champs, chemin générique CMake malformé** (`tests/test_story_2_2.py`) — Gate multi-label et `project()` absent non couverts.

## Deferred from: code review of 2-1-project-reload-via-luthier-json-sidecar (2026-06-23)

- **Valeurs non-string dans le sidecar passent à `from_dict` sans validation** (`core/project_spec.py:52-73`) — Un sidecar édité manuellement avec `"projectName": 123` stockerait un `int` dans le dataclass et pourrait faire échouer des opérations string en aval. Pré-existant depuis story 1-1 ; le writer Luthier produit toujours des types corrects.
- **`from_dict` non encapsulé dans `_read_sidecar`** (`core/project_reader.py:51`) — AC3 couvre JSON malformé → `None` ; la validation de schéma / types est hors périmètre. Pré-existant via `ProjectSpec.from_dict`.

## Deferred from: code review of 1-1-projectspec-dataclass (2026-06-23)

- **Bool coercion silencieux dans `from_dict`** — `d.get("copyToSystemFolders", False)` accepte n'importe quelle valeur truthy sans conversion vers `bool`. Les callers actuels fournissent tous des bools propres, mais un futur caller direct pourrait passer une string et casser `_on_off()` dans `render_context.py`. À surveiller lors de l'intégration story 1.2/1.3.
- **Defaults non liés entre champ dataclass et fallback `from_dict`** — Les defaults du champ (`copy_to_artefacts_dir: bool = True`) et du fallback `from_dict` (`d.get("copyToArtefactsDir", True)`) sont synchronisés manuellement. Un changement de l'un sans l'autre est un bug silencieux. Considérer une constante partagée lors d'un refactor futur.

## Deferred from: code review of 1-3-app-layer-uses-projectspec-via-spec (2026-06-23)

- **Key collision in `spec()` between sections unguarded** (`app/pages/project.py`) — `d.update(self._artefacts.values())` and other `.update()` calls can silently overwrite earlier keys. No current collision, but no assertion exists. Flag if a new section is added.
- **`spec()`/`load()` round-trip symmetry not covered by tests** — `spec()` assembles a dict from widgets; `load(spec)` routes through `to_dict()`. The pair must be inverses but there are no round-trip tests. The `from_dict`/`to_dict` pair was verified in story 1-1, but the widget layer is untested.
- **`Preferences → ProjectSpec` import coupling direction** (`core/preferences.py`) — `core/preferences.py` importing `core.project_spec` creates a one-way dependency within `core/`. If `ProjectSpec` ever needed `Preferences`, it would be circular. Currently safe per AD-8.
- **`Preferences.update()` field list must stay manually in sync with `ProjectSpec`** (`core/preferences.py`) — The 12 explicit attribute mappings must be updated whenever `ProjectSpec` fields are added, removed, or renamed. No compiler enforcement; the old filter approach was self-maintaining.

## Deferred from: code review of 1-4-cmakelists-txt-template-consolidation (2026-06-23)

- **`CACHE BOOL` sans `FORCE`** (`Templates/CMakeLists.txt`) — `set(COPY_TO_SYSTEM_FOLDERS ... CACHE BOOL ...)` sans FORCE signifie que si CMakeCache.txt existe déjà, une re-génération avec des valeurs différentes n'a aucun effet. Bug pré-existant copié inline depuis project-configuration.cmake.
- **Chemins Windows non échappés dans les placeholders artefact dir** (`Templates/CMakeLists.txt:65-67`) — `{artefactsDirWindows}` injecté directement dans un `set()` CMake. Un chemin contenant `\t`, `\n` (séquences CMake) serait interprété comme tabulation/newline. Pré-existant dans l'ancien project-configuration.cmake.
- **`OSError` non capturé sur `source.read_text()`** (`core/project_reader.py:114`) — Si le fichier existe mais est verrouillé ou illisible (permissions), l'exception se propage jusqu'à `read_project()` et n'est pas interceptée. Pré-existant ; aucune logique de lecture modifiée par cette story.
- **Aucun test couvrant le fallback du reader** (`core/project_reader.py:109-121`) — Le branch `source = config if config.exists() else CMakeLists.txt` n'est pas couvert. Épique 3 prévu pour l'infrastructure de test.

## Deferred from: code review of 1-2-core-generation-pipeline-accepts-projectspec (2026-06-23)

- **Perte de projet si `tmp.rename()` échoue après `rmtree`** (`core/project_writer.py:52-53`) — Le projet existant est supprimé avant le rename ; si le rename échoue (permission, cross-device inattendu), le projet est perdu sans récupération possible. Le design sibling atténue le risque (même filesystem), mais la séquence reste fragile.
- **`TestNoQtImport` — dépendance d'ordre d'import** (`tests/test_story_1_2.py`) — Si `core.project_generator` est importé par un test précédent dans le même process, `_qt_modules_before()` inclut déjà les modules Qt importés, masquant un vrai leak. Low-risk compte tenu de la structure du fichier de test.
- **`KeyboardInterrupt`/`SystemExit` laisse `.tmp` sur disque** (`core/project_writer.py:44-57`) — `except Exception` ne capture pas `BaseException` ; un Ctrl+C mid-write laisse le répertoire `.tmp`. Atténué par le `if tmp.exists(): shutil.rmtree(tmp)` en début de prochaine exécution.
- **`flags_for_type` crash KeyError sur `plugin_type` inconnu** (`core/render_context.py`) — Pré-existant, non introduit par cette story. Un `plugin_type` hors des valeurs connues (`synth`, `effect`, `midi`) lève `KeyError` sans message descriptif.
- **Lectures fichier non gardées dans `read_project`** (`core/project_reader.py:34-43`) — `cmake.read_text()` et `_parse_build_settings` lèvent sur `PermissionError` / `UnicodeDecodeError` au lieu de retourner `None`. Pré-existant, aucune logique de lecture modifiée par story 1.2.
- **Bool coercion dans `ProjectSpec.from_dict`** (`core/project_spec.py`) — `d.get("copyToSystemFolders", False)` accepte n'importe quelle valeur truthy sans cast vers `bool`. Si la string `"ON"` passe, `_on_off()` évalue `"ON" == True` → `False`, sortie toujours `"OFF"`. Reporté depuis story 1.1.

## Deferred from: code review of 1-5-cmakeuserpresets-json-full-multi-platform-preset-set (2026-06-23)

- **Windows path backslashes break rendered JSON** (`core/render_context.py:63`) — `_artefact_entry` interpolates paths raw into JSON strings; `C:\Plugins` produces invalid JSON escapes. Explicitly deferred in story spec; same class of issue as CMakeLists.txt artefact paths (story 1-4).
- **`from_dict` bool coercion amplified by `_artefact_entries`** (`core/project_spec.py:70`, `core/render_context.py:52`) — String `"false"` for `copyToArtefactsDir` is truthy; artefact cache vars inject when user intended off. Already tracked from stories 1-1/1-2; new code path makes consequence visible in presets.
- **`copyToArtefactsDir` ON with all empty artefact paths** (`core/render_context.py:51-57`) — Presets correctly omit `ARTEFACTS_DIR_*` per AC3, but CMakeLists.txt still renders `copyToArtefactsDir=ON`. Pre-existing cross-file inconsistency when checkbox on but paths unset.
- **No post-render JSON validation** (`core/rendering.py`) — CMakeUserPresets.json rendered via string interpolation with no `json.loads()` sanity check. Malformed output surfaces only at CMake configure time. Epic 3 test infrastructure planned.

## Deferred from: code review of 1-6-juce-directory-in-preferences (2026-06-23)

- **CMake path special characters not escaped in `_juce_dir_line`** (`core/render_context.py:35`) — Quotes, backslashes, and `$` in user paths are interpolated raw into `set(JUCE_DIR "...")`. Explicitly deferred in story spec §Known Deferred Issues (same class as CMakeLists artefact paths in stories 1-4/1-5).
- **No automated tests for juce_dir pipeline** — `_juce_dir_line`, `apply_form`, and end-to-end preference → CMake wiring untested. Epic 3 per story spec.

## Deferred from: code review of 1-7-gitignore-as-a-customizable-template (2026-06-23)

- **Override path resolution duplicated** (`core/project_writer.py:85-87`) — `templates_store._override_path` and `ProjectWriter._override_for` both encode gitignore layout; `_overrides.parent` assumes `overrides_dir()` is always `templates/Source`. Intentional per story spec AD-9; revisit if override injection changes.
- **Hardcoded `".gitignore"` in ProjectWriter** (`core/project_writer.py:85`) — Minor drift risk vs `templates_store.GITIGNORE_FILE`; spec documents literal string.
- **`.gitignore` special-cased across three modules** — Adding another non-Source template requires touching `templates_store`, `project_writer`, and `templates.py`. Accepted minimal-scope trade-off for story 1-7.
- **`_on_load_file` does not refresh status label** (`app/pages/templates.py:112-113`) — Editor content diverges from persisted override but status still shows previous state. Pre-existing for C++ templates.
- **No loaded-file type validation** (`app/pages/templates.py:111-113`) — User can load mismatched content via "All files (*)" without warning. Pre-existing pattern.
- **`read_text` errors unhandled in load-file handler** (`app/pages/templates.py:113`) — Invalid UTF-8 or permission errors propagate as exceptions. Pre-existing.
- **Split override directory layout** (`core/templates_store.py`) — Gitignore at `templates/.gitignore`, sources at `templates/Source/`. Required by AC2; document for backup/migration.
- **No automated tests for gitignore overrides** — Override paths, generation wiring, and Templates UI flows untested. Epic 3 story 3-3 per spec.
- **`read_default` unguarded `FileNotFoundError`** (`core/templates_store.py:51-52`) — Missing bundled asset crashes; pre-existing for source templates.
- **`save_override` no name allowlist** (`core/templates_store.py:60-63`) — Arbitrary `name` could write outside intended dirs if misused; internal callers only, pre-existing.
