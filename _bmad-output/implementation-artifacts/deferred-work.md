# Deferred Work

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
