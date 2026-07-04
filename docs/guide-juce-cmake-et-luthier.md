# JUCE, CMake et Luthier — comprendre les chemins pour créer un projet audio

> **Document de référence** — rédigé en juillet 2026 par Guillaume DUPONT, auteur de [Luthier](https://github.com/tensquaresoftware/luthier).  
> **Public visé :** développeur amateur ou débutant en JUCE et en CMake, souhaitant comprendre *pourquoi* et *comment* démarrer un projet audio multi-plateforme sans se perdre dans la jungle des outils.

**Voir aussi :** [README du dépôt](../../README.md) · [Manuel utilisateur (FR)](user/manuel-utilisateur.md) · [User manual (EN)](user/user-manual.md)

---

## Table des matières

1. [Introduction](#1-introduction)
2. [Ce que permet JUCE](#2-ce-que-permet-juce)
3. [Ce qu'il faut pour démarrer un projet JUCE](#3-ce-quil-faut-pour-démarrer-un-projet-juce)
4. [Deux grandes approches : Projucer ou CMake](#4-deux-grandes-approches--projucer-ou-cmake)
5. [Projucer : ce qu'il fait, ses contraintes, ses limites](#5-projucer--ce-quil-fait-ses-contraintes-ses-limites)
6. [Ce que recommande l'équipe JUCE aujourd'hui](#6-ce-que-recommande-léquipe-juce-aujourdhui)
7. [Gérer soi-même un projet JUCE / CMake](#7-gérer-soi-même-un-projet-juce--cmake)
8. [Luthier : un générateur de squelette pour gagner du temps](#8-luthier--un-générateur-de-squelette-pour-gagner-du-temps)
9. [Les limites volontaires de Luthier](#9-les-limites-volontaires-de-luthier)
10. [Synthèse : quel chemin choisir ?](#10-synthèse--quel-chemin-choisir-)
11. [Pour aller plus loin](#11-pour-aller-plus-loin)

---

## 1. Introduction

Si vous souhaitez créer un **plugin audio** (VST3, AU…) ou une **application standalone** orientée audio/MIDI pour Windows, macOS et Linux, vous tomberez tôt ou tard sur **[JUCE](https://juce.com/)** — un framework C++ open source conçu exactement pour cela.

Mais JUCE ne se contente pas de fournir des bibliothèques : il propose aussi des **outils** pour structurer et compiler vos projets. Et c'est là que les débutants se heurtent souvent à une question légitime :

> *Dois-je passer par **Projucer** (l'application fournie avec JUCE) ou par **CMake** (un système de build générique) ?*

Ce document retrace une réflexion menée sur plusieurs mois autour de ce choix, du rôle de **Projucer**, de la montée en puissance de **CMake**, et de la place de **Luthier** — un générateur de projet que j'ai développé pour simplifier le démarrage.

L'objectif n'est pas de vous transformer en expert CMake du jour au lendemain, mais de vous donner une **carte mentale durable** : une vision que vous pourrez relire dans un an et retrouver vos repères immédiatement.

---

## 2. Ce que permet JUCE

### En bref

**JUCE** (*Jules' Utility Class Extensions*) est un framework C++ qui abstrait les différences entre systèmes d'exploitation et formats de plugins. Vous écrivez votre code une fois ; JUCE s'occupe en grande partie de l'adaptation à chaque plateforme.

### Ce que nous visons ici (périmètre simplifié)

| Type de produit | Description | Formats typiques |
|-----------------|-------------|------------------|
| **Plugin audio** | Traitement ou génération de signal dans une DAW | **VST3**, **AU** (macOS), **Standalone** (version autonome du plugin) |
| **Application standalone GUI** | App audio/MIDI autonome avec interface graphique | Exécutable natif (.app, .exe…) |
| **Effet / instrument / effet MIDI** | Sous-types de plugins selon le rôle | Catégories VST3/AU adaptées automatiquement |

> **Note — CLAP et JUCE 9**  
> Le format **CLAP** gagne en adoption dans l'écosystème audio open source. Une **préversion de JUCE 9** est annoncée avec du travail en cours sur CLAP. À la date de rédaction de ce document (2026), CLAP n'est pas encore la voie « par défaut » pour un projet de production ; VST3 et AU restent les références. Surveillez les [releases JUCE](https://github.com/juce-framework/JUCE/releases) et le [forum JUCE](https://forum.juce.com/) pour l'évolution.

### Plateformes couvertes

Pour le périmètre visé par Luthier et par la plupart des projets indie :

- **Windows** (Visual Studio ou outils associés)
- **macOS** (Xcode ou Ninja + outils en ligne de commande)
- **Linux** (GCC/Clang, souvent via Ninja ou Makefiles)

JUCE couvre aussi iOS, Android et d'autres formats (AAX, LV2, AUv3…), mais ce document reste volontairement centré sur le trio **desktop + VST3/AU/Standalone**, qui correspond à la majorité des projets personnels et indépendants.

### Ce que JUCE vous évite de réinventer

- Connexion aux **APIs audio** de chaque OS (Core Audio, WASAPI, ALSA/JACK…)
- Encapsulation des **formats de plugins** (VST3, AU…)
- **Interface graphique** cross-platform (boutons, sliders, fenêtres…)
- Gestion **MIDI**, fichiers audio, DSP de base, etc.

En résumé : JUCE est le **moteur et la carrosserie** ; vous apportez la **logique métier** (votre synthé, votre effet, votre éditeur SysEx…).

---

## 3. Ce qu'il faut pour démarrer un projet JUCE

### Le socle commun : le SDK JUCE

Quel que soit le chemin choisi, il vous faut **JUCE lui-même** — le dossier SDK contenant les modules, les outils de build CMake internes, Projucer, les exemples, etc.

- Site officiel : [juce.com](https://juce.com/)
- Dépôt GitHub : [github.com/juce-framework/JUCE](https://github.com/juce-framework/JUCE)
- Licence : gratuite pour projets open source (AGPL) ou commerciale selon votre usage — voir [juce.com/legal](https://juce.com/legal)

### Chemin A — L'approche « classique » Projucer + IDE natif

C'est le workflow historique, encore très répandu :

| Élément | Rôle |
|---------|------|
| **JUCE SDK** | Framework et outils |
| **Projucer** | Application graphique pour créer/configurer le projet |
| **IDE natif** | Xcode (macOS), Visual Studio (Windows), Makefile (Linux) |

**Déroulé typique :**

1. Ouvrir Projucer → *New Project* → choisir « Audio Plug-in » ou « GUI Application »
2. Régler les options (nom, codes fabricant, formats VST3/AU…)
3. Cliquer **Save and Open in IDE**
4. Coder dans Xcode ou Visual Studio
5. Compiler et tester depuis l'IDE

### Chemin B — L'approche « moderne » CMake + IDE de votre choix

C'est la voie **recommandée par l'équipe JUCE** pour les nouveaux projets :

| Élément | Rôle |
|---------|------|
| **JUCE SDK** | Framework (référencé depuis CMake) |
| **CMake** (≥ 3.22) | Système qui *décrit* comment construire le projet |
| **CMake Presets** | Raccourcis pour configurer/builder selon l'OS et Debug/Release |
| **IDE ou Terminal** | Cursor, VS Code, CLion, ou simple éditeur + Terminal |

**Documentation officielle essentielle :**

- [CMake API — documentation JUCE](https://github.com/juce-framework/JUCE/blob/master/docs/CMake%20API.md)
- [Exemples CMake dans le dépôt JUCE](https://github.com/juce-framework/JUCE/tree/master/examples/CMake) (plugin audio, app GUI, app console)
- [Téléchargement CMake](https://cmake.org/download/)
- [Tutoriels JUCE](https://juce.com/learn/tutorials) et [documentation générale](https://juce.com/learn/documentation)

**Déroulé typique :**

1. Créer un dossier projet avec un `CMakeLists.txt` (à la main, en copiant un exemple, ou via un générateur comme Luthier)
2. Configurer : `cmake --preset macos-debug-arm64` (exemple)
3. Compiler : `cmake --build --preset macos-debug-arm64`
4. Coder dans l'IDE de votre choix ; reconfigurer CMake quand la description du build change

### Et l'éditeur de texte + Terminal seuls ?

**Oui, c'est possible.** CMake est conçu pour être piloté en ligne de commande. Un éditeur minimal + Terminal suffisent si vous acceptez :

- pas d'autocomplétion C++ avancée sans `compile_commands.json`
- pas de débogage visuel intégré (sauf via `lldb`/`gdb` en CLI)
- une courbe d'apprentissage plus raide

En pratique, la plupart des développeurs utilisent un IDE ou un éditeur enrichi (VS Code + CMake Tools, Cursor, CLion…) qui *consomme* les fichiers CMake sans imposer de format propriétaire.

---

## 4. Deux grandes approches : Projucer ou CMake

Avant d'entrer dans le détail, voici la distinction fondamentale :

```
┌──────────────────────────────────────────────────────────────────┐
│                        PROJUCER                                  │
│  SSOT = fichier .jucer (XML)                                     │
│  Sortie = projets IDE natifs (Builds/Xcode, Builds/VS…)          │
│  Régénération = écrase la vue IDE à chaque Save                  │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                         CMAKE                                    │
│  SSOT = CMakeLists.txt (+ éventuellement fichiers include)       │
│  Sortie = cache de build + binaires (Builds/…)                   │
│  Reconfigure = relit CMakeLists.txt, ne touche pas à vos sources │
└──────────────────────────────────────────────────────────────────┘
```

Les deux approches peuvent produire **le même plugin fonctionnel**. Ce qui change, c'est **qui tient la vérité** (SSOT : Single Source Of Truth) sur la configuration et la liste des fichiers — et **comment** l'IDE se resynchronise.

---

## 5. Projucer : ce qu'il fait, ses contraintes, ses limites

### Ce que Projucer fait concrètement

Projucer est une **application de bureau** livrée avec JUCE. C'est avant tout un **formulaire de configuration** et un **explorateur de fichiers de projet**, pas un IDE.

Quand vous cliquez **Save** ou **Save and Open in IDE**, Projucer :

1. **Enregistre** le fichier `.jucer` (XML) — c'est la **source de vérité** du projet côté Projucer
2. **Régénère** les fichiers de projet natifs dans le dossier `Builds/` :
   - `.xcodeproj` pour Xcode
   - `.sln` / `.vcxproj` pour Visual Studio
   - Makefile pour Linux
3. **Ouvre** l'IDE sur ce projet généré (si demandé)

> **Point important :** Projucer ne génère **pas** de `CMakeLists.txt`. Il injecte directement la configuration (fichiers sources, modules, defines…) dans le format Xcode ou Visual Studio.

### La règle d'or que tout utilisateur Projucer finit par apprendre

> **Créez et organisez vos fichiers sources depuis Projucer** (File Explorer dans la barre latérale), **pas depuis Xcode ou Visual Studio directement**.

**Pourquoi ?**

Le `.jucer` contient l'arborescence des fichiers (`MAINGROUP`). À chaque sauvegarde, Projucer **réécrit** le projet IDE à partir de cette arborescence. Si vous ajoutez un `.cpp` uniquement dans Xcode, il sera absent du `.jucer` : au prochain Save Projucer, il **disparaît du build**.

Ce n'est pas Xcode qui « oublie » votre fichier — c'est Projucer qui **resynchronise l'IDE depuis sa propre base**, en écrasant la configuration IDE précédente.

### Ce que Projucer gère bien

- Formulaire complet pour les **métadonnées** (nom, version, société, codes plugin…)
- Choix des **formats** (VST3, AU, Standalone, AAX…)
- **Modules JUCE** à lier, options de compilation
- **Explorateur de fichiers** intégré avec resync automatique vers l'IDE
- Export vers les **IDE officiellement supportés**

### Les limites structurelles

| Limite | Explication |
|--------|-------------|
| **Pas d'export CMake natif** | Les exporteurs Projucer ciblent Xcode, VS, Makefile, Android — pas CMake |
| **SSOT unique (.jucer)** | Toute resync repose sur ce fichier ; difficile de mélanger avec un workflow « IDE-first » |
| **Régénération destructive côté IDE** | Chaque Save peut écraser les changements faits uniquement dans l'IDE |
| **Deux responsabilités fusionnées** | Métadonnées projet **et** arborescence sources dans le même outil |
| **IDE agentiques non ciblés** | Cursor, Antigravity, etc. ne consomment pas de `.xcodeproj` ; ils veulent CMake + `compile_commands.json` |

Projucer reste **excellent** pour qui travaille en mode « Xcode + Projucer » et accepte ses règles. Il devient **contraignant** dès qu'on veut un workflow centré sur un éditeur moderne, l'IA, ou CMake multi-IDE.

---

## 6. Ce que recommande l'équipe JUCE aujourd'hui

La direction officielle est claire depuis plusieurs versions majeures :

> **Pour les nouveaux projets, privilégier CMake.**

Indices concrets :

- Documentation dédiée : [CMake API](https://github.com/juce-framework/JUCE/blob/master/docs/CMake%20API.md)
- Exemples officiels dans `examples/CMake/` (plugin, GUI app, console app)
- Fonctions CMake de haut niveau : `juce_add_plugin`, `juce_add_gui_app`, `juce_add_console_app`
- Projucer **n'a pas été retiré** et reste maintenu — mais ce n'est plus le chemin privilégié pour démarrer

### Pourquoi CMake ?

| Avantage | Détail |
|----------|--------|
| **IDE-agnostique** | Même projet ouvert dans Cursor, VS Code, CLion, ou Terminal |
| **Standard de l'industrie** | Compétence réutilisable hors JUCE |
| **Pas de régénération IDE opaque** | Vous éditez la description du build ; CMake reconfigure |
| **CI/CD facilité** | GitHub Actions, builds croisés, matrices OS/architecture |
| **Agentic coding** | L'IA peut lire et modifier `CMakeLists.txt` comme n'importe quel texte |

Projucer et CMake ne sont pas ennemis : ce sont deux **philosophies de gestion de projet**. JUCE supporte les deux, mais pousse les nouveaux venus vers CMake.

---

## 7. Gérer soi-même un projet JUCE / CMake

Si vous créez un projet CMake « à la main » (en copiant les exemples JUCE ou en suivant le [CMake API](https://github.com/juce-framework/JUCE/blob/master/docs/CMake%20API.md)), voici ce que cela implique au quotidien.

### Les deux fichiers que vous croiserez le plus

#### `CMakeLists.txt`

C'est le **plan de construction** de votre projet. Il répond aux questions :

- Quel est le nom du projet et sa version ?
- Où se trouve JUCE ?
- Quels fichiers `.cpp` compiler ?
- Quel type de plugin (instrument, effet…) et quels formats (VST3, AU, Standalone) ?
- Quels modules JUCE lier ?
- Quelles options de compilation (`C++20`, defines…) ?

**Ce fichier vit et grandit avec votre projet.** Ce n'est pas un fichier « généré une fois pour toutes ».

#### `CMakeUserPresets.json`

Ce sont des **raccourcis** pour invoquer CMake sans retaper les options :

```json
{
  "configurePresets": [
    {
      "name": "macos-debug-arm64",
      "generator": "Ninja",
      "binaryDir": "Builds/macOS/ARM/Debug",
      "cacheVariables": {
        "CMAKE_BUILD_TYPE": "Debug",
        "CMAKE_OSX_ARCHITECTURES": "arm64"
      }
    }
  ]
}
```

En pratique :

```bash
cmake --preset macos-debug-arm64    # configure
cmake --build --preset macos-debug-arm64   # compile
```

Les presets encapsulent les différences **macOS arm64 / macOS x86_64 / Windows / Linux**, Debug vs Release.

### Ce que vous devrez faire vous-même (ou déléguer à l'IA)

Une fois le squelette initial posé, le développement courant implique :

| Situation | Action typique dans CMake |
|-----------|---------------------------|
| Nouvelle classe / nouveau `.cpp` | Ajouter le fichier à la liste `PLUGIN_SOURCES` (ou équivalent) |
| Nouvelle ressource (police, image) | Ajouter un bloc `juce_add_binary_data` ou mettre à jour les sources existantes |
| Nouveau module JUCE | Ajouter `juce::juce_xxx` dans `target_link_libraries` |
| Tests unitaires | Créer une cible `add_executable` / `juce_add_console_app` dédiée |
| Option de build custom | Ajouter des `option()` ou des `set()` avec commentaires clairs |

Puis **reconfigurer** CMake (souvent automatique dans les IDE avec l'extension CMake Tools).

### Resynchroniser l'IDE

Contrairement à Projucer, il n'y a pas de bouton magique « Save and Open ». La resync, c'est :

```bash
cmake --preset <votre-preset>
```

L'IDE relit `compile_commands.json` et met à jour l'indexation. **Vos fichiers sources ne sont jamais écrasés** par cette opération.

### Deux profils de développeurs

| Profil | Qui maintient CMake au fil de l'eau ? |
|--------|---------------------------------------|
| **IDE agentique** (Cursor, etc.) | L'IA, sur demande (« ajoute cette classe au build ») — **approche recommandée par l'auteur de Luthier** |
| **IDE classique** (VS Code + CMake Tools, CLion…) | Vous-même, en éditant `CMakeLists.txt` — c'est le workflow standard de la communauté JUCE/CMake |

Les deux profils sont valides. La différence est *qui* tape les modifications, pas *si* elles sont nécessaires.

---

## 8. Luthier : un générateur de squelette pour gagner du temps

### Qu'est-ce que Luthier ?

**Luthier** est une application de bureau (Python + PySide6) que j'ai créée pour répondre à une frustration personnelle : démarrer un projet JUCE/CMake **correctement configuré** demande beaucoup de decisions techniques dès la première minute (codes plugin, presets multi-OS, formats, copie vers les dossiers système…).

Luthier propose un **formulaire** inspiré de Projucer — mais produit directement un **projet CMake natif JUCE**, prêt à ouvrir dans Cursor ou tout autre IDE.

Site / dépôt : [github.com/tensquaresoftware/luthier](https://github.com/tensquaresoftware/luthier)

### Ce que Luthier génère

Pour un nouveau projet, Luthier crée notamment :

| Fichier / dossier | Contenu |
|-------------------|---------|
| `CMakeLists.txt` | Description complète du build (JUCE, plugin, sources de base) |
| `CMakeUserPresets.json` | Presets Debug/Release pour macOS (arm64 + x86_64), Windows, Linux |
| `Source/` | Squelette `PluginProcessor` / `PluginEditor` (ou équivalent app) |
| `.luthier.json` | Sidecar JSON en **écriture seule** : photographie des métadonnées saisies au Generate — Luthier **ne le relit jamais** |
| `.vscode/`, `.cursorrules` | Aide à l'ouverture dans un IDE moderne |

### Ce que vous obtenez concrètement

- **Gain de temps immédiat** : pas besoin de copier-coller et adapter manuellement les exemples CMake JUCE
- **Squelette opérationnel** : configurable, compilable, testable dès la génération
- **Multi-plateforme** : presets prêts pour les 3 OS desktop
- **Formats plugin** : AU, VST3, Standalone (selon vos choix dans le formulaire)
- **Options avancées de départ** : copie automatique vers les dossiers de plugins système, dossier d'artefacts centralisé, standard C++, defines de base…

En quelques minutes, vous passez de « rien » à un projet qui build — et vous pouvez vous concentrer sur **votre code métier**.

---

## 9. Les limites volontaires de Luthier

C'est ici le cœur de la **vision actuelle** de Luthier, affinée après des mois de développement et d'usage réel (notamment sur [Matrix-Control](https://github.com/tensquaresoftware/matrix-control), un éditeur SysEx pour Oberheim Matrix-1000).

### Luthier n'est pas un « Projucer CMake » complet

Construire un outil capable de :

- rouvrir un projet existant,
- modifier ses caractéristiques (type instrument → effet, ajout MIDI out…),
- resynchroniser l'environnement IDE,

**sans rien casser**, demande des mécanismes de fusion, de zones protégées dans CMake, et de migration de configuration — un investissement considérable, comparable à des outils communautaires matures comme [FRUT](https://github.com/McMartin/FRUT) (conversion `.jucer` → CMake), mais avec une couche supplémentaire de GUI et de sécurité brownfield.

Pour mon usage personnel — et pour la majorité des utilisateurs d'IDE agentiques — **ce n'est pas le bon rapport effort/bénéfice**.

### Ce que Luthier fait (et ne fait pas)

| ✅ Luthier fait | ❌ Luthier ne fait pas |
|----------------|----------------------|
| Générer le **squelette initial** une seule fois | Rouvrir et reconfigurer un projet existant |
| Poser CMake + presets + sources de base | Gérer l'arborescence sources au fil du développement |
| Écrire `.luthier.json` comme **archive des métadonnées initiales** | Fusionner proprement un `CMakeLists.txt` devenu complexe |
| Accélérer le **jour 0** du projet | Remplacer Projucer pour tous les scénarios |

Luthier retrouve ainsi l'esprit de mon premier outil en ligne de commande — le **JUCE-Project-Generator** — : des questions, des defaults intelligents, un projet généré, **terminé**.

### Que se passe-t-il après la génération ?

Une fois le projet créé et le développement amorcé :

1. **Vos sources** vivent dans `Source/` (et ailleurs) — créées et organisées **depuis votre IDE**, librement
2. **Votre `CMakeLists.txt` évolue** — par vous, ou par l'IA si vous utilisez par exemple Cursor
3. **Ne relancez pas une génération Luthier par-dessus le projet** — cela écraserait le travail accumulé
4. **Reconfigurez CMake** quand vous modifiez la description du build :
   ```bash
   cmake --preset macos-debug-arm64
   cmake --build --preset macos-debug-arm64
   ```

Le fichier `.luthier.json` reste une **photographie** des choix initiaux (nom, codes, formats…). Il peut servir de référence pour vous ou pour l'IA, mais Luthier n'a pas vocation à le relire pour modifier le projet.

### Pourquoi l'IA est un bon « mainteneur CMake »

Dans un IDE agentique, demander :

> *« Crée la classe `FooBar` dans `Source/Core/` et ajoute-la au build »*

…provoque typiquement :

- création des fichiers `.h` / `.cpp`
- mise à jour de la liste des sources dans `CMakeLists.txt`
- éventuellement reconfiguration du projet

C'est **plus fluide** que de retourner dans un formulaire de générateur — surtout quand le projet a accumulé des centaines de fichiers et des blocs CMake très spécifiques (BinaryData, tests, hooks post-build…).

**C'est l'approche que je recommande** en tant qu'auteur de Luthier et développeur de plugins JUCE au quotidien.

---

## 10. Synthèse : quel chemin choisir ?

### Tableau comparatif

| Critère | Projucer + IDE natif | CMake manuel | **Luthier → CMake** |
|---------|---------------------|--------------|---------------------|
| Courbe d'apprentissage initiale | Faible | Élevée | **Faible** |
| Compatible Cursor / IDE agentique | Non (nativement) | Oui | **Oui** |
| Multi-IDE / CI | Limité | Oui | **Oui** |
| Gestion sources au fil du temps | Depuis Projucer uniquement | Depuis l'IDE | **Depuis l'IDE** |
| Reconfigurer le projet après coup | Via Projucer (avec contraintes) | Édition CMake | **Édition CMake / IA** |
| Recommandation JUCE 2026 | Legacy maintenu | ✅ Référence | ✅ **Accélérateur de démarrage** |

### Arbre de décision simplifié

```
Vous démarrez un NOUVEAU projet JUCE desktop (plugin ou app audio)
│
├─ Vous voulez rester 100 % dans Xcode/VS + Projucer ?
│  └─► Projucer (workflow classique, règles strictes sur les fichiers)
│
├─ Vous maîtrisez CMake et aimez tout configurer à la main ?
│  └─► Copier examples/CMake + CMake API JUCE
│
└─ Vous voulez CMake moderne + IDE libre (Cursor…) + démarrage rapide ?
   └─► Luthier (génération initiale) → puis développement normal + IA
```

### La phrase à retenir

> **Luthier vous évite la montagne du jour 0.**  
> **CMake et votre IDE vous accompagnent tous les jours suivants.**

---

## 11. Pour aller plus loin

### Documentation officielle JUCE

- [Documentation JUCE](https://juce.com/learn/documentation)
- [Tutoriels JUCE](https://juce.com/learn/tutorials)
- [CMake API (GitHub)](https://github.com/juce-framework/JUCE/blob/master/docs/CMake%20API.md)
- [Exemples CMake](https://github.com/juce-framework/JUCE/tree/master/examples/CMake)

### Outils et projets connexes

- [Luthier](https://github.com/tensquaresoftware/luthier) — générateur de squelette (ce document)
- [Matrix-Control](https://github.com/tensquaresoftware/matrix-control) — exemple de plugin JUCE/CMake complexe, développé avec un IDE agentique
- [FRUT / Jucer2CMake](https://github.com/McMartin/FRUT) — conversion `.jucer` → CMake (approche différente, communautaire)
- [CMake — site officiel](https://cmake.org/)

### Glossaire express

| Terme | Signification courte |
|-------|---------------------|
| **SSOT** | *Single Source of Truth* — la référence unique qui fait foi |
| **DAW** | *Digital Audio Workstation* — Logic Pro, Reaper, Ableton… |
| **VST3 / AU** | Formats de plugins audio (Steinberg / Apple) |
| **Standalone** | Version du plugin qui tourne comme une application autonome |
| **Preset (CMake)** | Raccourci nommé pour configurer/compiler avec un jeu d'options |
| **SDK** | *Software Development Kit* — ici, le dossier JUCE complet |
| **Sidecar** | Fichier auxiliaire (`.luthier.json`) stocké à côté du projet |

---

*Dernière mise à jour : 04/07/2026 — Ten Square Software / Guillaume DUPONT*
