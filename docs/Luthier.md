## Projet "Luthier" — GUI pour JUCE Project Generator

### Contexte

Je dispose d'un générateur de projets JUCE en ligne de commande, écrit en Python, situé dans `/Volumes/Guillaume/Dev/SDKs/JUCE/Tools/Juce-Project-Generator/`. Il fonctionne sur macOS, Windows et Linux. Je souhaite lui créer une interface graphique baptisée **Luthier**, inspirée visuellement du Projucer de JUCE (voir screenshot : dark theme, panneau gauche avec sections, formulaire central). L'application doit être **distribuable** (packagée sans Python installé : `.app` macOS, `.exe` Windows, binaire Linux), construite avec **PySide6**.

------

### Structure du générateur existant

```
Juce-Project-Generator/
├── generate-new-juce-project.py      # Point d'entrée CLI
├── generator-configuration.py        # Constantes : paths JUCE, manufacturer defaults, artefacts dirs
├── Generator/
│   ├── project-data.py               # class ProjectData (tous les champs du projet)
│   ├── input-collector.py            # Collecte des inputs utilisateur (toute la logique de validation)
│   ├── file-generator.py             # Génère les fichiers à partir des templates
│   ├── template-loader.py            # Charge les templates Jinja2
│   ├── template-renderer.py          # Rend les templates
│   ├── plugin-categories.py          # Calcul AU main type, VST3 categories, bundle ID
│   ├── path-validation.py            # Validation chemins (pas de caractères accentués, etc.)
│   ├── path-error-messages.py        # Messages d'erreur chemins
│   ├── platform-info.py              # Détection OS
│   ├── project-config-parser.py      # Lit un project-configuration.cmake existant
│   ├── config-loader.py              # Charge generator-configuration.py
│   ├── summary-display.py            # Affiche récap terminal avant génération
│   ├── success-display.py            # Affiche message de succès terminal
│   ├── ui-constants.py               # Couleurs terminal, constantes de validation
│   └── utils.py                      # Helpers (getValidBooleanInput, getValidChoice)
└── Templates/
    ├── CMakeLists.txt                 # Template principal CMake (Jinja2)
    ├── CMakeUserPresets.json          # Template presets CMake
    ├── project-configuration.cmake   # Template config plugin (copy settings, artefacts dirs)
    ├── Source/
    │   ├── PluginProcessor.cpp/h     # Templates source C++
    │   └── PluginEditor.cpp/h
    └── README.md                     # Template README projet généré
```

------

### Champs collectés par `ProjectData`

| Champ                | Type | Notes                                                        |
| -------------------- | ---- | ------------------------------------------------------------ |
| `projectName`        | str  | Nom technique (regex `^[a-zA-Z][a-zA-Z0-9_-]*$`)             |
| `projectDisplayName` | str  | Nom affiché (lettres, chiffres, espaces, tirets, underscores) |
| `projectVersion`     | str  | Default `"1.0.0"`                                            |
| `manufacturerName`   | str  | Default depuis `generator-configuration.py`                  |
| `manufacturerCode`   | str  | 4 caractères alphabétiques exactement                        |
| `pluginCode`         | str  | 4 caractères alphanumériques exactement                      |
| `bundleId`           | str  | Auto-généré depuis manufacturerName + projectName            |
| `isSynth`            | str  | `"TRUE"` / `"FALSE"`                                         |
| `needsMidiInput`     | str  | `"TRUE"` / `"FALSE"`                                         |
| `needsMidiOutput`    | str  | `"TRUE"` / `"FALSE"`                                         |
| `isMidiEffect`       | str  | `"TRUE"` / `"FALSE"`                                         |
| `auMainType`         | str  | Calculé par `plugin-categories.py`                           |
| `vst3Categories`     | str  | Calculé par `plugin-categories.py`                           |
| `pluginFormats`      | str  | Ex : `"AU VST3 Standalone"`                                  |
| `destinationDir`     | str  | Chemin destination (sans accents)                            |
| `projectDir`         | Path | `destinationDir / projectName`                               |

Paramètres supplémentaires gérés séparément (dans `generator-configuration.py` + `project-configuration.cmake`) :

- `copyToSystemFolders` : bool, copie vers dossiers système DAW
- `copyToArtefactsDir` : bool, copie vers dossier central personnalisé
- `artefactsDirWindows/Macos/Linux` : chemins vers ce dossier central
- Chemins JUCE par OS (`JUCE_DIR_WINDOWS/MACOS/LINUX`)

------

### Ce que Luthier doit faire

1. **Créer un nouveau projet** : formulaire avec tous les champs de `ProjectData` + les paramètres de `generator-configuration.py`, validation en temps réel, bouton "Generate"
2. **Rouvrir / modifier un projet existant** : lire le `project-configuration.cmake` d'un projet généré (via `project-config-parser.py`) et permettre de régénérer
3. **Préférences persistantes** : stocker les valeurs par défaut (manufacturer, paths, etc.) dans un fichier de config utilisateur (JSON ou TOML), remplaçant l'édition manuelle de `generator-configuration.py`
4. **Distribution** : packager avec PyInstaller (`.app` macOS via `--windowed`, `.exe` Windows via NSIS ou simple exe, binaire Linux)

------

### Exigences UI (inspirées du Projucer)

- Dark theme (style Projucer : fond ~`#323e44`, accents violets/roses)
- Fenêtre principale ~900×650 px minimum
- Panneau gauche : navigation entre sections (Project Info, Plugin Type, Formats, Build Settings, Preferences)
- Zone centrale : formulaire de la section active
- Barre inférieure : bouton "Generate" prominent, statut/messages
- Validation inline : indicateur vert/rouge à côté de chaque champ
- Pas de boîtes de dialogue modales pour les erreurs courantes : inline uniquement

------

### Contraintes techniques

- **Pas de caractères accentués** dans les chemins (la validation existe déjà dans `path-validation.py`)
- Les templates utilisent **Jinja2** — dépendance à conserver
- Le code du générateur dans `Generator/` doit rester **fonctionnel en CLI** (Luthier l'encapsule, ne le remplace pas)
- PySide6 uniquement (pas PyQt6 pour des raisons de licence)
- Python 3.11+ cible

------

### Organisation suggérée du projet Luthier

À créer dans un nouveau dossier, par exemple `/Volumes/Guillaume/Dev/SDKs/JUCE/Tools/Luthier/` :

```
Luthier/
├── main.py                    # Point d'entrée
├── app/
│   ├── main_window.py         # QMainWindow principal
│   ├── sidebar.py             # Panneau navigation gauche
│   ├── pages/
│   │   ├── project_info.py    # Section Project Info
│   │   ├── plugin_type.py     # Section Plugin Type
│   │   ├── formats.py         # Section Formats
│   │   └── build_settings.py  # Section Build Settings
│   ├── theme.py               # Couleurs, QSS stylesheet
│   └── preferences.py         # Persistance des préférences utilisateur
├── core/
│   └── (symlink ou copie du dossier Generator/ existant)
├── resources/
│   └── icons/
├── build/
│   └── luthier.spec           # Spec PyInstaller
└── requirements.txt
```

------

### Première tâche suggérée

Commencer par :

1. Créer la structure du projet
2. Implémenter `theme.py` (dark theme QSS fidèle au style Projucer)
3. Implémenter `main_window.py` avec sidebar + zone centrale vide
4. Implémenter la page "Project Info" avec validation inline
5. Brancher le bouton Generate sur le `file-generator.py` existant

Le rendu visuel est à valider avec l'utilisateur (il tourne sur macOS, peut tester sur Windows/Linux ensuite).

------

**Note importante** : l'utilisateur est le développeur de ce générateur et connaît bien JUCE. Il préfère des réponses concises et directes. Les commits doivent être en anglais. Les commentaires dans le code sont à éviter sauf pour les *pourquoi* non-évidents.