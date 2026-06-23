# Deferred Work

## Deferred from: code review of 1-1-projectspec-dataclass (2026-06-23)

- **Bool coercion silencieux dans `from_dict`** — `d.get("copyToSystemFolders", False)` accepte n'importe quelle valeur truthy sans conversion vers `bool`. Les callers actuels fournissent tous des bools propres, mais un futur caller direct pourrait passer une string et casser `_on_off()` dans `render_context.py`. À surveiller lors de l'intégration story 1.2/1.3.
- **Defaults non liés entre champ dataclass et fallback `from_dict`** — Les defaults du champ (`copy_to_artefacts_dir: bool = True`) et du fallback `from_dict` (`d.get("copyToArtefactsDir", True)`) sont synchronisés manuellement. Un changement de l'un sans l'autre est un bug silencieux. Considérer une constante partagée lors d'un refactor futur.

## Deferred from: code review of 1-3-app-layer-uses-projectspec-via-spec (2026-06-23)

- **Key collision in `spec()` between sections unguarded** (`app/pages/project.py`) — `d.update(self._artefacts.values())` and other `.update()` calls can silently overwrite earlier keys. No current collision, but no assertion exists. Flag if a new section is added.
- **`spec()`/`load()` round-trip symmetry not covered by tests** — `spec()` assembles a dict from widgets; `load(spec)` routes through `to_dict()`. The pair must be inverses but there are no round-trip tests. The `from_dict`/`to_dict` pair was verified in story 1-1, but the widget layer is untested.
- **`Preferences → ProjectSpec` import coupling direction** (`core/preferences.py`) — `core/preferences.py` importing `core.project_spec` creates a one-way dependency within `core/`. If `ProjectSpec` ever needed `Preferences`, it would be circular. Currently safe per AD-8.
- **`Preferences.update()` field list must stay manually in sync with `ProjectSpec`** (`core/preferences.py`) — The 12 explicit attribute mappings must be updated whenever `ProjectSpec` fields are added, removed, or renamed. No compiler enforcement; the old filter approach was self-maintaining.

## Deferred from: code review of 1-2-core-generation-pipeline-accepts-projectspec (2026-06-23)

- **Perte de projet si `tmp.rename()` échoue après `rmtree`** (`core/project_writer.py:52-53`) — Le projet existant est supprimé avant le rename ; si le rename échoue (permission, cross-device inattendu), le projet est perdu sans récupération possible. Le design sibling atténue le risque (même filesystem), mais la séquence reste fragile.
- **`TestNoQtImport` — dépendance d'ordre d'import** (`tests/test_story_1_2.py`) — Si `core.project_generator` est importé par un test précédent dans le même process, `_qt_modules_before()` inclut déjà les modules Qt importés, masquant un vrai leak. Low-risk compte tenu de la structure du fichier de test.
- **`KeyboardInterrupt`/`SystemExit` laisse `.tmp` sur disque** (`core/project_writer.py:44-57`) — `except Exception` ne capture pas `BaseException` ; un Ctrl+C mid-write laisse le répertoire `.tmp`. Atténué par le `if tmp.exists(): shutil.rmtree(tmp)` en début de prochaine exécution.
- **`flags_for_type` crash KeyError sur `plugin_type` inconnu** (`core/render_context.py`) — Pré-existant, non introduit par cette story. Un `plugin_type` hors des valeurs connues (`synth`, `effect`, `midi`) lève `KeyError` sans message descriptif.
- **Lectures fichier non gardées dans `read_project`** (`core/project_reader.py:34-43`) — `cmake.read_text()` et `_parse_build_settings` lèvent sur `PermissionError` / `UnicodeDecodeError` au lieu de retourner `None`. Pré-existant, aucune logique de lecture modifiée par story 1.2.
- **Bool coercion dans `ProjectSpec.from_dict`** (`core/project_spec.py`) — `d.get("copyToSystemFolders", False)` accepte n'importe quelle valeur truthy sans cast vers `bool`. Si la string `"ON"` passe, `_on_off()` évalue `"ON" == True` → `False`, sortie toujours `"OFF"`. Reporté depuis story 1.1.
