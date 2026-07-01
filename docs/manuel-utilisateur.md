---
Organization: Ten Square Software
Author: Guillaume DUPONT
Project: Luthier
Title: Luthier — Manuel utilisateur
Version: 1.0
Product-Version: 1.0.0
Created: 2026-06-26
Updated: 2026-07-02
References:
  - docs/user-manual.md
  - docs/architecture.md
  - CONTRIBUTING.md
  - README.md
---

# Luthier — Manuel utilisateur

Ce manuel vous guide dans l’utilisation de Luthier, une application de bureau pour **créer**, **rouvrir** et **régénérer** des projets JUCE basés sur CMake (plugins audio et/ou applications Standalone).

Un soin particulier a été apporté à ce document rédigé pour les personnes qui découvrent JUCE ou la chaîne de build d’un projet audio. Chaque section explique d’abord *à quoi sert* un réglage, puis *comment* l’utiliser dans l’interface. Les tableaux et listes restent là pour la consultation rapide. Les textes qui les accompagnent visent à vous éviter les fausses pistes les plus courantes.

> **Langue de l’interface** — Luthier s’affiche en **anglais**. Les libellés de boutons et de champs cités ci-dessous reprennent exactement le texte à l’écran. Ce document est la traduction française du [manuel anglais](user-manual.md), qui reste la référence officielle du produit.

---

## Table des matières

1. [Qu’est-ce que Luthier ?](#1-quest-ce-que-luthier-)
2. [Avant de commencer](#2-avant-de-commencer)
3. [Installation et lancement de Luthier](#3-installation-et-lancement-de-luthier)
4. [Fenêtre principale](#4-fenêtre-principale)
5. [Trois types de réglages pour vos projets JUCE](#5-trois-types-de-réglages-pour-vos-projets-juce)
6. [Premier lancement de Luthier](#6-premier-lancement-de-luthier)
7. [Onglet Project](#7-onglet-project)
8. [Onglet Preferences](#8-onglet-preferences)
9. [Onglet Templates](#9-onglet-templates)
10. [Onglet About](#10-onglet-about)
11. [Parcours types](#11-parcours-types)
12. [Ce que Luthier génère](#12-ce-que-luthier-génère)
13. [Où sont stockées vos données](#13-où-sont-stockées-vos-données)
14. [Règles de validation des champs](#14-règles-de-validation-des-champs)
15. [Normalisation des chemins](#15-normalisation-des-chemins)
16. [Messages, erreurs et dépannage](#16-messages-erreurs-et-dépannage)
17. [Utiliser l’application Luthier autonome](#17-utiliser-lapplication-luthier-autonome)

---

## 1. Qu’est-ce que Luthier ?

Luthier vous aide à **créer des projets JUCE** (AU/VST3/Standalone) sans éditer les fichiers CMake à la main. Vous remplissez un formulaire dans l'éditeur de projet, Luthier valide vos saisies en direct. Lorsque vous cliquez sur **Generate Project**, Luthier écrit un dossier de projet complet, prêt à ouvrir dans votre IDE habituel et à compiler avec CMake.

En pratique, Luthier se place **en amont** de la compilation : il prépare l’ossature du projet JUCE (fichiers CMake, sources de départ, métadonnées du plugin). La phase suivante — configurer CMake, compiler, tester dans un DAW — se fait dans l’environnement de développement que vous choisissez (Visual Studio, Xcode, Cursor, Antigravity, Ninja, etc.).

Luthier peut aussi **rouvrir** un projet qu’il a créé auparavant, vous laisser modifier la configuration et **régénérer** les fichiers sur place. Vous n’avez donc pas à repartir de zéro à chaque changement de nom, de format ou de chemin JUCE.

On peut voir Luthier comme un workflow de type **Projucer**, le générateur de projet livré avec JUCE et dont Luthier est largement inspiré. Il est orienté vers des **projets CMake portables** et une **régénération reproductible**. Si vous avez déjà utilisé Projucer, vous retrouverez des notions familières (identité du plugin, formats, codes fabricant). Si ce n’est pas le cas, les sections suivantes les détaillent pas à pas.

### Ce que Luthier fait

- Génère des projets AU, VST3 et/ou Standalone à partir d’un seul formulaire dans l'éditeur de projet.
- Écrit `CMakeLists.txt`, `CMakeUserPresets.json`, les fichiers sources, des aides IDE optionnelles et le **fichier compagnon** `.luthier.json` (instantané de configuration pour rouvrir le projet).
- Enregistre vos **valeurs par défaut** (fabricant, chemins, type de plugin, couleur d’accent, etc.) dans un fichier de préférences sur votre machine (`preferences.json`).
- Permet de personnaliser les **modèles sources C++** utilisés pour chaque nouveau projet (`PluginProcessor.h/.cpp` et `PluginEditor.h/.cpp`).
- Rouvre les projets existants via `.luthier.json` (fichier compagnon requis).

### Ce que Luthier ne fait pas

- Il ne **compile pas** votre projet JUCE — vous utilisez toujours CMake et votre IDE ou toolchain (Visual Studio, Xcode, Cursor, Antigravity, Ninja, etc.).
- Il ne **télécharge ni n’installe** JUCE — vous indiquez un dossier JUCE déjà présent sur le disque.
- Il ne **synchronise pas** les réglages entre machines — utilisez **Export Preferences…** / **Import Preferences…** dans l'onglet **Preferences** pour déplacer vos profils manuellement. Ceci est pratique si vous êtes par exemple un développeur indépendant travaillant pour plusieurs clients en parallèle sur plusieurs projets.

Ces limites sont volontaires : Luthier reste un générateur léger et prévisible. Une fois le dossier de projet créé, vous gardez la main sur la toolchain, les mises à jour JUCE et le déploiement.

---

## 2. Avant de commencer

Avant d’ouvrir Luthier, assurez-vous d’avoir les éléments ci-dessous. Inutile de tout maîtriser d’emblée : la plupart des utilisateurs configurent d’abord **Preferences**, génèrent un premier projet test, puis affinent au fil des essais.

### Ce dont vous aurez besoin

- Un **SDK JUCE** installé quelque part sur votre ordinateur (ou un chemin que vous comptez utiliser).
- Un **dossier de destination** où créer les dossiers de projet (par exemple votre dossier Bureau, Documents, etc.).
- **CMake 3.22+** et une toolchain C++ adaptée à votre plateforme (détails dans le `README.md` de chaque projet généré).
- Une connaissance de base des **formats de plugin** sur votre plateforme (AU sur macOS, VST3 sur Windows/macOS/Linux, Standalone pour une application de bureau).

### JUCE en bref

**JUCE** est un framework C++ open source très répandu pour les plugins audio et les applications audio multiplateformes. C’est lui qui fournit l’API audio, les wrappers VST3/AU/Standalone et une grande partie du code de base d’un plugin.

Luthier génère des projets qui *utilisent* JUCE, mais ne l’inclut pas dans le dépôt : vous devez disposer du SDK sur votre machine. Téléchargez-le sur [juce.com](https://juce.com) ou clonez le [dépôt JUCE](https://github.com/juce-framework/JUCE), décompressez-le où vous voulez, puis indiquez ce dossier dans **JUCE directory**, section **Workspace** (voir [§7.5](#75-workspace)). Ce chemin sert de valeur par défaut pour que CMake sache où trouver JUCE lors de la génération.

Rien ne vous empêche d’utiliser une **copie de JUCE distincte par projet JUCE** : renseignez un **JUCE directory** propre à votre OS courant dans la section **Workspace** de l’onglet **Project** (voir [§11.2](#112-projet-avec-une-version-juce-spécifique)). Beaucoup d’équipes placent cette copie **dans le dossier du projet** (par exemple `MySynth/JUCE/`) pour figer la version du framework et éviter qu’une mise à jour globale de JUCE ne perturbe les autres projets.

Si vous compilez sur **plusieurs systèmes d’exploitation**, saisissez un **JUCE directory** (et un **Destination folder**) par plateforme dans **Workspace** — le même principe que les chemins d’artefacts. Exportez votre profil **Preferences** une fois ; chaque nouveau projet hérite des six chemins.

### Plateformes prises en charge

Luthier fonctionne sur **Windows**, **macOS** et **Linux**. Selon votre profil, vous pouvez l’exécuter depuis les sources (Python + PySide6), pratique pour les contributeurs, ou comme **application autonome** construite avec PyInstaller sur chaque plateforme. Les deux offrent la même interface. Seule l’installation diffère — voir [§17](#17-utiliser-lapplication-luthier-autonome).

---

## 3. Installation et lancement de Luthier

Choisissez la voie qui correspond à votre usage. Si vous débutez et recevez un installeur ou une archive, privilégiez l’application autonome. Si vous travaillez dans le dépôt Luthier lui-même, suivez la procédure développeur.

### Depuis les sources (développeurs)

Cette voie suppose Python 3.11+ et un environnement virtuel. Consultez [CONTRIBUTING.md](../CONTRIBUTING.md) dans le dépôt pour la procédure complète. En résumé :

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows : .venv\Scripts\activate
pip install -r requirements-dev.txt
.venv/bin/python main.py           # Windows : .venv\Scripts\python main.py
```

### Application autonome (utilisateurs finaux)

Téléchargez ou construisez le bundle pour votre système, puis lancez l’application comme toute application native : aucune installation Python n’est requise sur la machine. Les modèles de projet et les bibliothèques graphiques sont embarqués dans le dossier distribué — voir [§17](#17-utiliser-lapplication-luthier-autonome) pour les précisions par plateforme.

---

## 4. Fenêtre principale

L’interface de Luthier est volontairement simple : un onglet par grande tâche, un formulaire central, des boutons d’action en bas. Prenez un instant pour repérer les quatre zones ci-dessous. Elles reviendront dans tout le reste du manuel.

À l’ouverture de Luthier, vous voyez :

```
┌───────────────────────────────────────────────────┐
│  Project │ Preferences │ Templates │ About        │  ← Barre d’onglets
├───────────────────────────────────────────────────┤
│                                                   │
│            Contenu de l’onglet actif              │  ← Éditeur de projet
│                                                   │
├───────────────────────────────────────────────────┤
│     Message de statut (centré, pleine largeur)    │  ← Barre de statut
├───────────────────────────────────────────────────┤
│          [Boutons d’action de l’onglet]           │  ← Barre d’actions
└───────────────────────────────────────────────────┘
```

### Barre d’onglets

| Onglet | Rôle |
|--------|------|
| **Project** | Configurer le projet JUCE sur lequel vous travaillez. |
| **Preferences** | Modifier les valeurs par défaut globales qui pré-remplissent les nouveaux projets. |
| **Templates** | Voir et personnaliser les modèles C++ / `.gitignore` utilisés à la génération. |
| **About** | Crédits, version et liens. |

### Barre de statut

La barre de statut est votre retour principal après une action importante (génération, ouverture, import). Après la plupart des opérations, un court message s’affiche dans une **barre dédiée au-dessus des boutons d’action** :

- les messages de **succès** utilisent la **couleur d’accent** (personnalisable — magenta par défaut)
- les messages d’**erreur** sont en rouge

Exemples : *« Project generated at /Users/vous/Documents/MySynth »*, *« Loaded MySynth from … »*, *« Preferences imported from client-a.json »*.

L’enregistrement automatique dans **Preferences** affiche uniquement un badge **Saved** sur le champ modifié — il n’utilise pas cette barre de statut globale.

### Barre d’actions

Les boutons en bas **changent selon l’onglet actif** :

| Onglet | Boutons |
|--------|---------|
| **Project** | **Create New Project**, **Open Project…**, **Generate Project** |
| **Preferences** | **Import Preferences…**, **Export Preferences…** |
| **Templates** | **Load from file…**, **Reset to default**, **Save override** |
| **About** | *(aucun)* |

### Taille et position de la fenêtre

Luthier mémorise la taille et l’état maximisé de la fenêtre entre les sessions. Sous **macOS** et **Windows**, la position est également restaurée. Sous **Linux**, la taille est en général retrouvée ; la **position n’est pas garantie** (notamment sous Wayland, où le gestionnaire de fenêtres peut ignorer le placement demandé par l’application). Si la géométrie enregistrée n’est plus valide (par exemple après déconnexion d’un écran), la fenêtre s’ouvre centrée avec une taille par défaut confortable.

---

## 5. Trois types de réglages pour vos projets JUCE

La première source de confusion, pour un nouvel utilisateur, est de mélanger ce qui concerne **le projet JUCE en cours**, ce qui sert de **valeurs par défaut** et ce qui définit le **code source de départ**. Luthier sépare clairement ces trois domaines dans trois onglets. Le tableau ci-dessous résume la logique.

Comprendre cette distinction évite la plupart des questions du type « j’ai changé Preferences, pourquoi mon projet ouvert n’a pas bougé ? ».

| Domaine | Onglet | Portée | Répond à la question |
|---------|--------|--------|----------------------|
| **Projet en cours** | Project | Un projet JUCE à la fois | *Comment **ce** projet JUCE est-il configuré ?* |
| **Valeurs par défaut globales** | Preferences | Toute l’app, tous les futurs projets | *Quelles valeurs réutiliser à chaque fois ?* |
| **Modèles globaux** | Templates | Toute l’app, tous les projets générés | *Quel code source de départ pour les nouveaux projets JUCE ?* |

**Règles importantes :**

- Modifier **Preferences** ne change **pas** l’onglet **Project** tant que vous n’avez pas cliqué sur **Create New Project** (ou relancé l’app pour le peuplement initial).
- **Open Project…** et **Generate Project** n’écrivent **jamais** dans `preferences.json`.
- Les personnalisations de l’onglet **Templates** sont appliquées à chaque **Generate Project**. En revanche, **Export Preferences…** n’exporte que le profil de **Preferences**. Vos overrides de templates restent dans le dossier `templates/` de la configuration Luthier (voir [§13](#13-où-sont-stockées-vos-données)). Copiez-les séparément si vous changez de machine.

En résumé : **Preferences** et **Templates** préparent l’avenir. **Project** décrit le projet JUCE sur lequel vous travaillez *maintenant*. La génération lit uniquement **Project** (et les templates), jamais l’inverse.

---

## 6. Premier lancement de Luthier

Au tout premier démarrage, Luthier initialise un profil local avec des valeurs usine raisonnables. Vous pouvez générer un projet tout de suite, mais quelques minutes passées dans **Preferences** (fabricant, chemins, JUCE) vous feront gagner du temps sur chaque projet JUCE suivant.

### Ce qui se passe automatiquement

1. Luthier crée **`preferences.json`** dans le dossier de configuration applicative de votre OS (première exécution uniquement).
2. Les valeurs usine sont écrites — voir le tableau ci-dessous.
3. L’onglet **Project** s’ouvre comme **nouveau projet** : champs d’identité vides, tout le reste copié depuis les préférences.

### Valeurs usine (premier `preferences.json`)

| Réglage | Valeur initiale |
|---------|-----------------|
| Manufacturer | `My Company` |
| Manufacturer code | `Myco` |
| Plugin code | `Mypl` |
| Copyright, Website, E-mail | vides |
| Workspace — Destination folder (Windows / macOS / Linux) | OS hôte → votre **Bureau** ; autres plateformes → vide |
| Workspace — JUCE directory (Windows / macOS / Linux) | vides (placeholder selon l’OS sur la ligne hôte, ex. `/Applications/JUCE` sur macOS) |
| Plugin type | Instrument (Synth) |
| Formats | AU, VST3, Standalone — tous cochés |
| C++ standard | C++17 |
| Preprocessor defs, Header search paths | vides |
| Copy to system plugin folders | désactivé |
| Copy to central artefacts folder | désactivé |
| Chemins d’artefacts (Windows / macOS / Linux) | vides |
| **Couleur d’accent** (`accentColor`) | Magenta (`#A45C94`) — défaut inspiré de Projucer |

### Premiers pas recommandés

Voici un enchaînement simple pour valider que tout est en place — du formulaire Luthier jusqu’au premier dossier de projet JUCE sur le disque :

1. Ouvrez **Preferences** et renseignez **Manufacturer**, les codes, et les chemins **Workspace** (**Destination folder** et **JUCE directory** pour chaque OS que vous utilisez).
2. Passez à **Project**, saisissez un **Project name**, puis cliquez sur **Generate Project**.
3. Ouvrez le dossier généré dans votre IDE. Consultez le `README.md` du projet pour les prérequis et les commandes de build, puis lancez la configuration CMake et la compilation.

Si la génération réussit mais que la compilation échoue, le problème se situe en général côté toolchain (CMake, compilateur, chemin JUCE) : le `README.md` généré est le bon point de départ pour le diagnostic.

---

## 7. Onglet Project

C’est ici que vous décrivez **un** projet JUCE : son nom, son identité, ses formats, ses options de compilation et la destination des binaires après build. Pensez à cet onglet comme à la « fiche d’identité » du projet que Luthier va matérialiser sur le disque.

L’onglet est une page défilable divisée en six sections. Les champs marqués d’un astérisque (*) sont obligatoires. Luthier vous signale les erreurs au fil de la saisie et désactive **Generate Project** tant que le formulaire n’est pas valide.

### Luthier Accent Color

En haut de l’onglet **Project** — au-dessus de **Project Info** — la ligne **Luthier Accent Color** permet de choisir une couleur parmi **douze préréglages** pour l’interface de l’application. Tant que vous restez sur cet onglet, le changement s’applique **immédiatement** : onglet actif, boutons d’action, badges **Saved**, liens, coches de validation des champs et messages de succès dans la barre de statut.

Le même sélecteur apparaît en haut de l’onglet **Preferences** (au-dessus de **Identity**). Chaque onglet dispose de **son propre** sélecteur : ils ne se mettent pas à jour l’un l’autre en direct.

| Onglet | Effet d’un choix de couleur |
|--------|----------------------------|
| **Preferences** | Enregistrement **immédiat** dans `preferences.json` (sans badge **Saved**). L’apparence se met à jour tant que vous restez sur cet onglet. |
| **Project** | Mise à jour **immédiate** de l’apparence ; enregistrement dans `.luthier.json` au **Generate Project** ; restauration au **Open Project…**. |

En passant d’un onglet à l’autre, Luthier applique la couleur du sélecteur **de l’onglet actif**. Le sélecteur **Project** reprend la valeur enregistrée dans **Preferences** au **démarrage** de l’application et lors d’un **Create New Project**.

Deux niveaux de persistance coexistent :

- **`accentColor` dans `preferences.json`** — couleur par défaut pour les **nouveaux** projets et profils exportés via **Export Preferences…** / **Import Preferences…**. Pratique pour distinguer plusieurs clients ou marques avant de créer un projet.
- **`accentColor` dans `.luthier.json`** — couleur **propre au projet JUCE** ; écrite au **Generate Project**, relue au **Open Project…**, et transportée avec le dossier de projet (Git, clé USB, etc.).

Changer la couleur d’accent ne modifie **pas** les champs du projet, les templates ni les fichiers JUCE générés — seulement l’apparence de Luthier. Un changement dans **Preferences** met à jour `preferences.json` ; un changement dans **Project** ne l’écrit dans le sidecar qu’après **Generate Project**.

### 7.1 Project Info

Cette section regroupe l’**identité** du plugin : noms, version, fabricant et codes. Les codes fabricant et plugin peuient paraître cryptiques au début : ils servent surtout aux hôtes macOS (Audio Unit) et doivent respecter des règles strictes — d’où le bouton **Generate** et le tableau ci-dessous.

| Champ | Obligatoire | Description |
|-------|-------------|-------------|
| **Project name** * | Oui | Nom technique — nom du dossier et cible CMake. Doit commencer par une lettre. Lettres, chiffres, `-`, `_` uniquement. |
| **Display name** | Non | Nom affiché dans les hôtes (DAW, application Standalone). Lettres, chiffres, espaces, `-` et `_` autorisés (ex. `My Synth 1`). Si vide, le **Project name** est utilisé. |
| **Version** * | Oui | Chaîne de version (défaut `1.0.0` pour un nouveau projet). |
| **Manufacturer** * | Oui | Nom de votre société ou nom personnel. |
| **Copyright** | Non | Ligne de copyright dans les métadonnées générées. |
| **Website** | Non | URL optionnelle. |
| **E-mail** | Non | Contact optionnel. |
| **Manufacturer code** * | Oui | Code AU compatible GarageBand : première lettre **majuscule**, puis trois lettres **minuscules** (ex. `Myco`). Le bouton **Generate** remplit un code valide aléatoire. |
| **Plugin code** * | Oui | Code AU compatible GarageBand : première lettre **majuscule**, puis trois lettres minuscules ou chiffres (ex. `Mypl`, `Dem0`). `DEMO` est réservé par Apple. Même bouton **Generate** que pour le manufacturer code. |
| **Bundle ID** | — | Champ en lecture seule. Calculé à partir du manufacturer et du project name. |

L’emplacement de création du projet et le chemin JUCE se configurent dans [§7.5 Workspace](#75-workspace), pas ici.

### 7.2 Plugin Type

Le type de plugin détermine comment JUCE câble les entrées/sorties audio et MIDI dans le processeur généré. Vous ne pouvez en choisir qu’**un** à la fois. Changez-le avant la première génération si besoin, ou régénérez après modification.

Choix exclusif :

| Type | Signification |
|------|---------------|
| **Instrument** (Synth) | Reçoit du MIDI en entrée, produit de l’audio en sortie. |
| **Audio Effect** | Traite l’audio entrant et produit de l'audio sortant. |
| **MIDI Effect** | Traite le MIDI uniquement — pas d’entrée/sortie audio. |

### 7.3 Formats

Les formats définissent **sous quelle forme** votre projet JUCE sera compilé : module pour un DAW (AU, VST3) ou application autonome (Standalone). Cochez au moins celui que vous comptez tester en premier. Vous pourrez en ajouter d’autres plus tard en régénérant le projet.

Sélectionnez **au moins un** format :

- **AU** (*Audio Unit*, compatible macOS uniquement)
- **VST3** (*Virtual Studio Technology*, compatible Windows/macOS/Linux)
- **Standalone**

Si aucun n’est coché, **Generate Project** reste désactivé et une indication apparaît sous les cases à cocher.

**Note :** le format AU n’est compilé que sur macOS. Sous Windows et Linux, CMake ignore ce format au moment du build. Laisser la case cochée permet d’ouvrir le même projet sur un Mac plus tard sans régénérer.

### 7.4 Compilation

Ces réglages sont transmis tels quels au `CMakeLists.txt` généré. Pour un premier projet, les valeurs par défaut (C++17, champs vides) conviennent en général. Revenez-y lorsque vous aurez besoin de drapeaux de préprocesseur ou de chemins d’en-têtes supplémentaires.

| Champ | Description |
|-------|-------------|
| **C++ standard** | C++17, C++20 ou C++23. |
| **Preprocessor defs** | Une définition par ligne (ex. `MY_FLAG=1`). |
| **Header search paths** | Un chemin par ligne, relatif à la racine du projet. |

**Preprocessor defs** — macros C++ passées au compilateur (une par ligne). Utiles pour activer du code conditionnel (`MY_DEBUG=1`) sans retoucher le CMake à la main. Luthier les injecte dans le `CMakeLists.txt` sous forme de `target_compile_definitions`.

**Header search paths** — dossiers d’en-têtes supplémentaires que le compilateur doit connaître, **relatifs à la racine du projet** (ex. `libs/mon-sdk/include`). Luthier les injecte sous forme de `target_include_directories`.

### 7.5 Workspace

Avant de générer, Luthier doit savoir **où sur le disque** ce projet sera créé et **où JUCE est installé** — sur **chaque** système d’exploitation que vous utilisez. **Workspace** se trouve en bas du formulaire, juste au-dessus de **Artefacts** : d’abord vous configurez le plugin, puis vos dossiers locaux, puis éventuellement les cibles de copie d’artefacts.

| Groupe | Obligatoire | Description |
|--------|-------------|-------------|
| **Destination folder** * | OS hôte uniquement | Dossier **parent** où Luthier crée le sous-dossier nommé d’après **Project name**. Exemple sur macOS : `~/Documents` + `MySynth` → `~/Documents/MySynth`. Trois lignes : **Windows**, **macOS**, **Linux**. |
| **JUCE directory** | Non (hôte) | Chemin vers le SDK JUCE **pour ce projet** sur chaque OS. Pré-rempli depuis Preferences sur un nouveau projet. Peut différer d’un projet à l’autre. Trois lignes : **Windows**, **macOS**, **Linux**. |

La ligne correspondant à **votre OS actuel** dispose d’un bouton **Choose…** (sélecteur natif). Les deux autres se saisissent au clavier ou par collage — un sélecteur sur votre machine ne peut pas produire un chemin valide pour un autre OS. Disposition : **label → Choose… (hôte seulement) → champ texte**. Les chemins sont normalisés en slashs avant — voir [§15 Normalisation des chemins](#15-normalisation-des-chemins).

**Au moment de la génération**, seules les valeurs de l’**OS hôte** sont utilisées. Les autres chemins sont stockés dans `.luthier.json` pour qu’un projet partagé via Git s’ouvre prêt sur chaque machine — vous n’ajustez que le **JUCE directory** hôte si besoin.

**Après Open Project…** sur la machine courante, seul le **Destination folder** **hôte** est recalculé à partir du parent du dossier ouvert. Les chemins des autres OS restent inchangés.

#### Configuration multi-plateforme (exemple)

| OS | Destination folder | JUCE directory |
|----|-------------------|----------------|
| macOS | `/Users/vous/Documents/Plugins` | `/Users/vous/Dev/SDKs/JUCE` |
| Windows | `C:/Users/vous/Documents/Plugins` | `C:/Users/vous/Dev/SDKs/JUCE` |
| Linux | `/home/vous/Documents/Plugins` | `/home/vous/Dev/SDKs/JUCE` |

Configurez ces chemins une fois dans **Preferences → Workspace**, **Export Preferences…**, puis importez sur chaque machine. Les surcharges par projet vivent dans **Project → Workspace** et voyagent dans `.luthier.json`.

### 7.6 Artefacts

Après chaque compilation réussie, vous voudrez souvent **récupérer le binaire** (plugin ou Standalone) sans fouiller dans les dossiers `Builds/`. Cette section configure deux mécanismes complémentaires : copie vers les emplacements scannés par les DAW, et copie vers un dossier central que vous définissez.

Ce mécanisme centralise les binaires compilés de vos projets dans un dossier unique, organisé par plateforme et architecture, pour les retrouver, les archiver ou préparer une distribution sans parcourir chaque répertoire de build.

Les options ci-dessous sont injectées dans les variables cache CMake au moment de la génération. Le comportement effectif au build est détaillé dans le `README.md` du projet généré.

| Option | Description |
|--------|-------------|
| **Copy to system plugin folders** | Copie vers les emplacements standard scannés par les DAW — pratique pour tester le résultat juste après un build. |
| **Copy to central artefacts folder** | Une fois cochée, active les trois champs de répertoire ci-dessous. |

Lorsque **Copy to central artefacts folder** est activée :

| Champ | Description |
|-------|-------------|
| **Windows** | Chemin cible pour les builds Windows. |
| **macOS** | Chemin cible pour les builds macOS. |
| **Linux** | Chemin cible pour les builds Linux. |

Le chemin correspondant à **votre OS actuel** dispose d’un bouton **Choose…**. Les deux autres se saisissent au clavier (ou par collage), car un sélecteur sur votre machine ne peut pas produire un chemin valide pour un autre OS (par exemple `D:\Plugins` depuis macOS). C’est normal si vous développez sur une seule plateforme : vous pouvez laisser les autres champs vides pour l’instant.

#### Dossier dans le cloud (Dropbox, OneDrive, NAS…)

Un cas d’usage intéressant consiste à pointer chaque chemin vers le **même dossier logique** au sein d’un service cloud ou d’un partage réseau — par exemple `Dev/Artefacts/JUCE` dans votre Dropbox, OneDrive ou montage NAS. Il faut malgré tout renseigner **trois chemins** (un par OS), car chaque système exprime cet emplacement différemment :

| OS | Exemple de chemin |
|----|-------------------|
| macOS | `/Users/vous/Dropbox/Dev/Artefacts/JUCE` |
| Windows | `C:\Users\vous\Dropbox\Dev\Artefacts\JUCE` |
| Linux | `/home/vous/Dropbox/Dev/Artefacts/JUCE` |

Après chaque build, Luthier copie les binaires dans des **sous-dossiers par plateforme** sous cette racine : `macOS/` (avec un sous-dossier d’architecture tel que `ARM/` ou `Universal/`), `Windows/` et `Linux/`. Lorsque vous compilez le même projet sur plusieurs machines, la synchronisation fusionne ces branches en une arborescence unique — pratique pour archiver ou préparer une release sans tri manuel :

```
Dev/Artefacts/JUCE/
├── macOS/
│   ├── ARM/
│   │   ├── AU/
│   │   └── VST3/
│   └── Universal/
├── Windows/
│   └── VST3/
└── Linux/
    └── VST3/
```

Workflow typique : créer le projet sur une machine et définir le chemin d’artefacts avecle bouton  `Choose…`. Sur vos autres systèmes, clonez le dépôt, rouvrez le projet dans Luthier, puis saisissez le **chemin local équivalent** pour chaque OS avant d’y lancer un build.

Les réglages d’artefacts appartiennent à **ce projet**. Ils peuvent différer des defaults globaux de Preferences.

### 7.7 Actions du projet

Trois boutons structurent le cycle de vie d’un projet dans Luthier : repartir d’une feuille vierge, rouvrir un travail existant, ou écrire sur le disque la configuration affichée. Chacun a un rôle précis — les confondre est une autre source fréquente de confusion.

#### Create New Project

Utilisez cette action lorsque vous voulez **démarrer un autre projet JUCE** sans effacer vos defaults globaux. Elle remet le formulaire à zéro :

- **Effacé :** project name, display name (version remise à `1.0.0`).
- **Re-peuplé depuis `preferences.json` :** tout le reste — manufacturer, codes, chemins workspace, type, formats, compilation, artefacts.

Si vous avez modifié le formulaire depuis le dernier état stable (ouverture, reset ou démarrage à froid), Luthier demande :

> *The project form has unsaved changes. Discard them and start a new project?*

*(« Le formulaire projet contient des modifications non enregistrées. Les abandonner et démarrer un nouveau projet ? »)*

**No** conserve vos modifications. **Yes** réinitialise. Le bouton par défaut est **No**.

**Create New Project** ne modifie **pas** `preferences.json`.

#### Open Project…

Cette action recharge dans le formulaire un projet **déjà généré** par Luthier. Elle ne modifie ni vos préférences ni vos templates. Vous retrouvez exactement la configuration enregistrée dans le projet (idéalement via le fichier compagnon `.luthier.json`).

Ouvre un sélecteur de dossier. Choisissez un **dossier de projet** généré précédemment par Luthier (contient `CMakeLists.txt` et `.luthier.json`).

- Seul l’onglet **Project** est mis à jour.
- **Preferences** et **Templates** restent inchangés.

**Lecture du projet :**

Luthier charge la configuration complète depuis `.luthier.json`. Si le fichier compagnon est absent ou invalide, **Open Project…** affiche une erreur claire et n’analyse pas `CMakeLists.txt`.

**Après déplacement d’un dossier projet :** ouvrez-le à son **nouvel emplacement**. Le **Destination folder** **hôte** dans **Workspace** affiche le parent du dossier sélectionné. Les chemins de destination des autres OS ne sont pas modifiés.

#### Generate Project

C’est l’étape qui **écrit réellement les fichiers** sur le disque (CMake, sources, fichier compagnon, aides IDE optionnelles). Tant que vous n’avez pas cliqué sur ce bouton, les modifications du formulaire restent dans Luthier uniquement.

Crée ou régénère le projet à partir de l’onglet **Project** uniquement :

- écrit dans le **Destination folder** **hôte** / **Project name**.
- intègre le **JUCE directory** **hôte** dans `CMakeLists.txt` lorsqu’il est renseigné.
- applique vos overrides **Templates** le cas échéant.
- écrit `.luthier.json`, fichier compagnon avec un instantané complet de la configuration.

**Generate Project** ne lit ni n’écrit **Preferences**.

**Comportement de Destination folder :**

- la section **Workspace** reste visible pour permettre une régénération en un clic après **Open Project…**.
- si la destination **hôte** est vide ou pointe vers un dossier inexistant, Luthier ouvre un sélecteur avant de continuer.
- si un dossier du même nom existe déjà, Luthier demande confirmation avant écrasement.

Après une génération réussie, Luthier mémorise le dossier parent de destination **hôte** pour le prochain dialogue **Choose…**.

**Generate Project** n’est actif que lorsque tous les champs obligatoires sont valides et que les templates sont disponibles.

---

## 8. Onglet Preferences

L’onglet **Preferences** sert à éviter de ressaisir les mêmes informations pour chaque nouveau projet JUCE à générer : fabricant, codes par défaut, chemins **Workspace**, formats cochés par défaut, etc. Ce n’est **pas** l’endroit où vous nommez un projet précis. Cela reste dans **Project**.

### 8.1 Sections

En haut de l’onglet, **Luthier Accent Color** (voir [§7 Luthier Accent Color](#luthier-accent-color)) reprend le même sélecteur de douze couleurs que sur **Project**. **C’est ici** que le choix est **enregistré** dans `preferences.json` et inclus dans les profils exportés. Le sélecteur **Project** conserve sa **propre** couleur de projet (dans `.luthier.json` après génération) ; il est realigné sur **Preferences** au démarrage et via **Create New Project** uniquement.

| Section | Contenu |
|---------|---------|
| **Identity** | Manufacturer, codes (chacun avec **Generate**), Copyright, Website, E-mail |
| **Plugin Type** | Instrument / Audio Effect / MIDI Effect par défaut |
| **Formats** | Cases à cocher AU / VST3 / Standalone par défaut |
| **Compilation** | C++ standard, preprocessor defs, header paths par défaut |
| **Workspace** | **Destination folder** et **JUCE directory** par OS (**Choose…** pour l’OS hôte, saisie texte pour les deux autres) |
| **Artefacts** | Mêmes options de copie et chemins par OS que Project (**Choose…** pour l’OS hôte, saisie texte pour les deux autres) |

Il n’y a **pas** de champs propres au projet ici (pas de project name, version ou bundle ID). Si vous modifiez Preferences alors qu’un projet est déjà ouvert dans **Project**, c’est normal que l’écran Project ne change pas : cliquez sur **Create New Project** pour voir les nouveaux defaults sur un formulaire vierge.

### 8.2 Enregistrement automatique

Contrairement à de nombreuses applications, Luthier n’a pas de bouton **Save** dans Preferences : chaque champ valide est **enregistré immédiatement** dans `preferences.json`. Vous pouvez fermer l’application sans craindre d’oublier de sauvegarder, tant que le champ n’affiche pas d’erreur.

Lorsqu’un champ est sauvegardé, un badge **« Saved »** clignote brièvement sur ce champ (couleur d’accent courante).

Les champs invalides bloquent l’enregistrement tant qu’ils ne sont pas corrigés.

### 8.3 Import Preferences…

L’import permet de **remplacer** tout le profil local par un fichier JSON exporté auparavant — utile pour restaurer une sauvegarde ou basculer entre profils (clients, machines, studios).

1. Choisissez un fichier JSON (profil exporté, sauvegarde, autre machine).
2. S’il est valide, il **remplace** intégralement le profil de préférences actuel et met à jour `preferences.json` (y compris **`accentColor`** si présent dans le fichier).
3. L’onglet Preferences se recharge ; la couleur d’accent importée s’applique tout de suite **sur cet onglet**.

**L’import ne modifie pas l’onglet Project** (y compris le sélecteur de couleur). Utilisez **Create New Project** pour appliquer les nouveaux defaults — couleur comprise — à un formulaire vierge.

Si le fichier est invalide, une boîte de dialogue d’erreur s’affiche et votre profil précédent est conservé.

### 8.4 Export Preferences…

L’export crée une **copie** de vos préférences actuelles dans un fichier de votre choix. Le fichier `preferences.json` local n’est pas modifié. Vous pouvez exporter plusieurs profils nommés (`client-a.json`, `client-b.json`, `mes-prefs.json`, etc.) et les réimporter plus tard.

Le JSON exporté contient les mêmes champs que votre profil actif, y compris **`accentColor`**, de sorte que l’apparence et les valeurs par défaut voyagent ensemble lorsque vous changez de machine ou de profil.

Servez-vous-en pour sauvegarder des profils ou les partager entre machines (un fichier par client, par studio, etc.).

L’export est bloqué si un champ de préférences est actuellement invalide.

### 8.5 Parcours multi-clients

Si vous développez pour plusieurs marques ou clients, exportez un profil par contexte et importez-le avant chaque nouveau projet JUCE. Vous gardez codes fabricant, chemins, métadonnées et une **couleur d’accent distincte** cohérents sans tout retaper — et vous repérez le client actif d’un coup d’œil grâce aux couleurs de l’interface.

1. Configurez **Preferences** pour le **Client A** (valeurs par défaut + **Luthier Accent Color**) → **Export Preferences…** → `client-a.json`.
2. Répétez pour le **Client B** avec une autre couleur → `client-b.json`.
3. Avant de démarrer un projet JUCE pour un client → **Import Preferences…** → choisissez le bon fichier (couleur et champs mis à jour dans **Preferences**).
4. **Create New Project** → le formulaire correspond à ce profil.

Le projet que vous aviez ouvert reste inchangé jusqu’à ce que vous en créiez ou en ouvriez un autre.

---

## 9. Onglet Templates

Les templates sont les **fichiers sources modèles** que Luthier copie dans chaque nouveau projet : processeur audio (`PluginProcessor.h/.cpp`), éditeur graphique (`PluginEditor.h/.cpp`), `.gitignore`. Personnalisez-les une fois ici si vous voulez que tous vos futurs projets JUCE démarrent avec votre propre squelette de code (includes habituels, structure de classe, règles Git, etc.).

Les templates sont **globaux** : les mêmes fichiers sont utilisés pour **chaque** projet généré.

### Fichiers modifiables

| Fichier | Rôle |
|---------|------|
| `PluginProcessor.h` / `.cpp` | Squelette processeur audio/MIDI |
| `PluginEditor.h` / `.cpp` | Squelette interface éditeur |
| `.gitignore` | Règles Git ignore pour les nouveaux projets |

Sélectionnez un fichier dans la liste déroulante, modifiez-le dans l’éditeur avec coloration syntaxique, puis **Save override** pour persister votre version. Tant que vous n’avez pas sauvegardé l’override, vos changements ne seront pas utilisés à la génération. Pensez à **Save override** avant de quitter l’onglet.

### Actions

| Bouton | Effet |
|--------|--------|
| **Load from file…** | Charge un fichier externe dans l’éditeur **sans enregistrer**. Utilisez **Save override** pour persister. |
| **Reset to default** | Supprime votre override. Le modèle fourni avec Luthier est rétabli. |
| **Save override** | Enregistre le contenu de l’éditeur comme override personnel. |

Ligne de statut sous l’éditeur :

- *« Override active — used for new projects. »* lorsque vous avez une version personnalisée.
- *« Showing the built-in default. »* sinon.

Les overrides sont stockés dans le sous-dossier `templates/` du répertoire de configuration de Luthier, **séparément** de `preferences.json`. Importer des préférences n’importe **pas** les overrides de templates. Si vous changez de machine, exportez/importez les prefs et recopiez ou recréez vos overrides templates si nécessaire (voir [§13](#13-où-sont-stockées-vos-données)).

---

## 10. Onglet About

Onglet informatif : version de Luthier, crédits et liens utiles. Aucune action sur vos projets.

Utilisez les liens des lignes e-mail et GitHub pour contacter l’auteur et consulter sa page GitHub.

---

## 11. Parcours types

Les scénarios ci-dessous reprennent les usages les plus fréquents. Chacun suppose que Luthier est installé et que vous avez au minimum renseigné les chemins **Workspace** dans **Preferences** (**JUCE directory** hôte au minimum).

### 11.1 Nouveau projet JUCE (une seule installation JUCE)

Cas le plus courant : un SDK JUCE par machine, un dossier de destination, plusieurs projets à enchaîner avec les mêmes réglages de base :

1. Renseignez **Preferences** une fois (manufacturer, chemins **Workspace** pour votre OS).
2. Sur **Project**, saisissez **Project name** et ajustez les options (pensez à générer un **Plugin code** unique par projet).
3. Cliquez sur **Generate Project**.
4. Ouvrez le dossier de sortie dans votre IDE. Suivez le `README.md` généré pour configurer et compiler avec CMake.

Pour un autre projet JUCE : **Create New Project** → ajustez → **Generate Project**.

### 11.2 Projet avec une version JUCE spécifique

Utile lorsque ce projet doit rester sur une branche ou une version de JUCE différente de vos autres projets. Le chemin SDK est stocké **dans le projet** (par OS dans **Workspace**), pas seulement dans **Preferences** :

1. **Create New Project** (chemins JUCE **Workspace** peuplés depuis Preferences).
2. Modifiez la ligne **JUCE directory** **hôte** dans **Workspace** sur l’onglet **Project** pour pointer vers la branche ou la copie voulue du SDK.
3. **Generate Project** — le chemin du SDK est enregistré dans le projet et le fichier compagnon `.luthier.json`.

### 11.3 Reprendre et modifier un projet existant

Vous avez déjà généré un projet et souhaitez changer un nom, un format, un code ou un chemin : rouvrez-le, modifiez le formulaire, régénérez. Luthier réécrit les fichiers au même emplacement (sous réserve de confirmation si le dossier existe déjà) :

1. **Open Project…** → sélectionnez le dossier du projet.
2. Modifiez les champs sur **Project**.
3. **Generate Project** pour réécrire les fichiers sur place.

Si entre-temps vous aviez déplacé le dossier de votre projet, ouvrez-le d’abord à son nouvel emplacement. Le **Destination folder** **hôte** dans **Workspace** se met à jour automatiquement.

### 11.4 Changer de profil entre deux projets

Enchaînement typique pour un développeur freelance travaillant pour plusieurs clients, ou multi-marques : importer le bon profil JSON (valeurs par défaut **et couleur d’accent**), créer un nouveau projet puis générer, sans toucher au projet précédemment ouvert.

1. **Import Preferences…** → fichier JSON du client (champs et couleur d’accent mis à jour dans **Preferences**).
2. **Create New Project**.
3. Remplissez les champs d’identité → **Generate Project**.

Le projet précédemment ouvert n’est pas modifié.

### 11.5 Personnaliser le code source de départ

À faire une fois, avant une série de générations : vos overrides templates seront injectés dans **tous** les projets générés ensuite (nouveaux ou régénérés).

1. Ouvrez **Templates** → sélectionnez `PluginProcessor.cpp` (ou un autre fichier).
2. Modifiez → **Save override**.
3. **Generate Project** sur tout projet nouveau ou existant — votre override est utilisé.

### 11.6 Même projet sur macOS, Windows et Linux

Pour un projet partagé via Git et compilé sur plusieurs machines :

1. Sur votre machine principale, renseignez les six chemins **Workspace** dans **Preferences** (ou sur **Project** après **Create New Project**), puis **Export Preferences…** si vous réutilisez la même disposition pour plusieurs projets.
2. **Generate Project** et poussez le dépôt (`.luthier.json` transporte les six chemins).
3. Sur chaque autre OS : `git clone` → **Open Project…** → vérifiez le **JUCE directory** **hôte** (ajustez si votre SDK diffère) → **Generate Project** sans ressaisir les chemins des autres plateformes.
4. Optionnel : configurez les chemins **Artefacts** de la même façon (voir [§7.6](#76-artefacts)).

---

## 12. Ce que Luthier génère

Lorsque vous cliquez sur **Generate Project**, Luthier crée un dossier nommé comme le **Project name** à l’intérieur du **Destination folder** **hôte** défini dans **Workspace**. L’exemple ci-dessous illustre la structure typique. Les fichiers exacts dépendent des formats cochés et de la plateforme cible.

Avec un **Project name** valide intitulé `MySynth` et un **Destination folder** **hôte** pointant vers le dossier `Documents` de l'ordinateur, Luthier crée `~/Documents/MySynth/` contenant :

| Fichier / dossier | Description |
|-------------------|-------------|
| `CMakeLists.txt` | Projet CMake principal JUCE |
| `CMakeUserPresets.json` | Presets CMake multi-plateforme (debug/release par OS) |
| `Source/` | Fichiers `.h` / `.cpp` *PluginProcessor* et *PluginEditor* depuis les templates |
| `.luthier.json` | Fichier compagnon : instantané complet (formulaire, Workspace, **`accentColor`**, …) pour réouverture |
| `.gitignore` | Depuis le template (personnalisable) |
| `.vscode/` et `.cursorrules` | Aides **optionnelles** pour VS Code et Cursor (presets CMake, tâches de build, extensions suggérées). Inutiles si vous utilisez Xcode, Visual Studio ou un autre IDE — vous pouvez les ignorer ou les supprimer. |
| `CMake/CopyVst3Elevated.ps1` | Aide à la copie VST3 sous Windows |
| `README.md` | Readme du projet généré |

La génération utilise des écritures atomiques : les fichiers sont construits dans un dossier temporaire puis remplacés sur place, pour limiter le risque d’un projet à moitié écrit.

Le `README.md` généré dans le dossier du projet documente les prérequis (CMake, compilateur, Ninja), les presets CMake par plateforme et le comportement de copie des artefacts — commencez par ce fichier pour votre premier build.

---

## 13. Où sont stockées vos données

Luthier répartit les données entre la **configuration de l’application** (defaults, templates, état de la fenêtre) et le **dossier de chaque projet généré**. Savoir qui vit où vous aide à sauvegarder, migrer de machine ou comprendre pourquoi un réglage « revient » après une action.

| Emplacement | Contenu | Modifié par |
|-------------|---------|-------------|
| `preferences.json` | Profil de defaults globaux (`accentColor`, fabricant, chemins, …) | Premier lancement, auto-save Preferences, sélecteur d’accent (onglet **Preferences**), Import |
| `app_state.json` | Dernier dossier parent, dernier dossier import/export, géométrie fenêtre | Generate réussi, chemins Import/Export, redimensionnement/déplacement fenêtre |
| Fichiers `*.json` exportés | Copies de profils de préférences (y compris `accentColor`) | Export Preferences… (fichiers choisis manuellement) |
| Overrides Templates (`templates/`) | Contenu de templates personnalisé | Save override, Reset |
| Dossier de projet / `.luthier.json` | Projet CMake généré + sidecar (champs formulaire, Workspace, **`accentColor`**, …) | Generate Project |

Emplacements typiques du **répertoire de configuration** Luthier :

| Plateforme | Chemin |
|------------|--------|
| Windows | `%LOCALAPPDATA%\Luthier\` (ex. `C:/Users/Vous/AppData/Local/Luthier/`) |
| macOS | `~/Library/Preferences/Luthier/` |
| Linux | `~/.config/Luthier/` |

Vous y trouverez notamment `preferences.json`, `app_state.json`, et le sous-dossier `templates/` (overrides de l’onglet **Templates**).

**Idée clé :** les réglages globaux vivent dans ce répertoire de configuration sur votre machine. Les réglages propres à un projet JUCE vivent dans l’onglet **Project** pendant l’édition, puis dans le dossier du projet et le fichier compagnon `.luthier.json` après génération. Pour partager un projet avec un collègue, envoyez le **dossier de projet**. Pour partager vos habitudes de saisie, exportez les **Preferences**.

---

## 14. Règles de validation des champs

Luthier valide les champs **pendant** la saisie plutôt qu’au moment du clic sur **Generate** : les erreurs s’affichent à côté du champ concerné et **Generate Project** reste grisé tant que le formulaire n’est pas entièrement valide. C’est une aide, pas un blocage arbitraire. Corrigez le champ signalé et le bouton se réactive.

| Champ | Règle |
|-------|-------|
| Project name | Commence par une lettre. Lettres, chiffres, `-`, `_` uniquement. |
| Display name | Lettres, chiffres, espace, `-`, `_` uniquement (ex. `My Synth 1`). |
| Version | Non vide. |
| Manufacturer | Non vide. |
| Manufacturer code | Première lettre majuscule, puis 3 minuscules (GarageBand AU). |
| Plugin code | Première lettre majuscule, puis 3 minuscules ou chiffres (standard imposé pour compatibilité AU avec GarageBand). `DEMO` est réservé par Apple. |
| Destination folder (OS hôte) | Non vide sur la machine où vous générez. Pas de caractères accentués dans le chemin. |
| JUCE directory (OS hôte) | Optionnel. Si renseigné, pas de caractères accentués. |
| Chemins Workspace (OS non hôtes) | Optionnels. Si renseignés, pas de caractères accentués. |
| Formats | Au moins une case cochée. |
| Chemins d’artefacts | Lorsque la copie centrale est activée, pas de caractères accentués. |

Les champs texte optionnels (Copyright, Website, E-mail, preprocessor defs) acceptent tout contenu sauf indication contraire.

**Codes d’identité du plugin** — Luthier applique les règles de casse exigées par GarageBand 10.3 et recommandées par JUCE pour les plugins Audio Units. Cela évite un piège fréquent : le projet compile, mais le plugin AU n’apparaît pas dans GarageBand parce que les codes étaient mal cadrés (tout en minuscules, que des chiffres, etc.). Utilisez **Generate** à côté de chaque code pour obtenir une valeur conforme aléatoire.

---

## 15. Normalisation des chemins

Sur Windows, les chemins s’écrivent souvent avec des antislashs (`\`). Sur macOS et Linux, avec des slashs (`/`). Pour que vos projets et fichiers de config restent lisibles et copiables d’une machine à l’autre, Luthier **uniformise** l’affichage et l’enregistrement en slashs avant, sans modifier le sens du chemin sur votre disque.

Luthier enregistre et affiche les chemins de dossiers avec des **slashs avant** (`/`) sur toutes les plateformes. Cela garantit la cohérence de `preferences.json`, de `.luthier.json` et des réglages CMake générés, que vous travailliez sur Windows, macOS ou Linux — ou que vous copiez un projet d’une machine à l’autre.

**Champs concernés :** tous les chemins **Workspace** (destination et JUCE par OS) et les trois chemins d’artefacts centraux (Windows / macOS / Linux).

**Quand la normalisation s’applique :**

- lorsque vous **quittez** un champ de chemin (Tab ou clic ailleurs) — les antislashs deviennent des slashs avant et les espaces en début/fin sont supprimés.
- lorsque vous choisissez un dossier avec **Choose…**.
- lorsque Luthier **enregistre** les préférences, **génère** un projet, **ouvre** un projet ou **importe** un profil.

**Exemples** (ce que vous saisissez → ce que Luthier enregistre) :

| Saisie | Valeur enregistrée |
|--------|-------------------|
| `C:\Users\Dev\Projects` | `C:/Users/Dev/Projects` |
| `D:\Plugins\VST3` | `D:/Plugins/VST3` |
| `  /opt/juce  ` | `/opt/juce` |

Les chemins déjà au format Unix sont conservés tels quels (hors trim). La normalisation ne réécrit **pas** les lettres de lecteur et ne vérifie **pas** l’existence du chemin sur le disque.

---

## 16. Messages, erreurs et dépannage

Si quelque chose ne se passe pas comme prévu, commencez par regarder la **barre de statut** (message en couleur d’accent ou en rouge) et les indications à côté des champs du formulaire. La plupart des blocages viennent d’un champ obligatoire manquant, d’un chemin invalide ou d’un dossier qui n’est pas un projet Luthier.

Les retours d’opération globaux (Generate, Open, Create New Project, Import/Export Preferences) s’affichent dans la **barre de statut dédiée** au-dessus des boutons d’action — voir [§4 Barre de statut](#barre-de-statut). Le tableau ci-dessous liste les messages typiques.

### Messages de statut (succès)

| Action | Message typique |
|--------|-----------------|
| Generate | `Project generated at /chemin/vers/ProjectName` |
| Open | `Loaded ProjectName from /chemin/vers/dossier` |
| Create New Project | `New project — defaults from Preferences.` |
| Import preferences | `Preferences imported from filename.json.` |
| Export preferences | `Preferences exported to filename.json.` |

### Erreurs courantes

| Situation | Comportement |
|-----------|--------------|
| Ouverture d’un dossier non-Luthier ou sans `.luthier.json` | Dialogue : *Not a Luthier project or companion file .luthier.json is missing.* (ou message d’invalidité du sidecar). |
| `.luthier.json` invalide | Dialogue : fichier compagnon invalide ou illisible. |
| Aucun format dans le projet ouvert | Dialogue : aucun format détecté. |
| Import JSON invalide | Dialogue d’avertissement. Préférences précédentes conservées. |
| Export avec champs invalides | Message d’erreur. Fichier non écrit. |
| Templates manquants (installation cassée) | Generate désactivé. Erreur au démarrage dans la ligne de statut. |
| Écrasement d’un projet existant | Dialogue de confirmation avant remplacement du dossier. |
| Modifications Project non enregistrées + Create New Project | Dialogue de confirmation. Défaut **No**. |

### Conseils

Quelques pistes lorsque le comportement vous surprend. La plupart relèvent de la logique décrite au [§5](#5-trois-types-de-réglages-pour-vos-projets-juce) plutôt que d’un dysfonctionnement de l’application.

- **Plugin absent de GarageBand** — vérifiez que les codes manufacturer et plugin respectent les règles de casse GarageBand ([§14](#14-règles-de-validation-des-champs)). Utilisez **Generate** pour remplacer des codes invalides.
- **« Generate Project » est grisé** — vérifiez les champs obligatoires (*), les formats et les chemins d’artefacts si la copie centrale est activée.
- **Mauvaise destination après déplacement** — utilisez **Open Project…** au nouvel emplacement. Ne comptez pas sur un ancien chemin de destination.
- **Changement Preferences absent de l’onglet Project** — comportement normal pour les champs du formulaire. Cliquez sur **Create New Project** pour appliquer les nouveaux defaults (couleur incluse). Un projet **déjà ouvert** conserve sa couleur **Project** jusqu’au prochain **Open Project…** ou **Generate Project**.
- **Couleur différente après clone Git** — la couleur du projet vit dans `.luthier.json` ; régénérez ou rouvrez le projet après pull pour la retrouver.
- **Régénérer sans modification** — Open → **Generate Project** doit produire un projet cohérent. Le fichier compagnon préserve l’état complet.

---

## 17. Utiliser l’application Luthier autonome

Outre l’exécution depuis les sources Python, Luthier peut être distribué comme **application autonome**. C’est pratique pour les utilisateurs qui ne souhaitent pas installer Python ni cloner le dépôt. Le comportement de l’interface est identique. Seuls l’installation et le dossier d’installation diffèrent.

| Plateforme | Sortie typique |
|------------|----------------|
| Windows | `Luthier.exe` dans un dossier `Luthier/` avec son sous-dossier `_internal/` |
| macOS | `Luthier.app` |
| Linux | Exécutable `Luthier` dans un dossier `Luthier/` avec son sous-dossier `_internal/` |

**Important :** distribuez le **dossier entier**. L’exécutable seul ne suffit pas. Les templates et bibliothèques Qt sont à côté dans le sous-dossier `_internal`.

### Première exécution sous Windows (builds non signés)

SmartScreen peut avertir au premier lancement. Utilisez **More info** → **Run anyway** pour les builds locaux. Windows Defender peut analyser les fichiers au premier démarrage — cela peut ajouter un court délai, sans échec.

### Première exécution sous Linux

Si le binaire n’est pas exécutable : `chmod +x Luthier/Luthier`. Un serveur d’affichage X11 ou Wayland peut être nécessaire pour l’interface graphique.

### Vérification headless

Depuis un terminal (utile pour la CI ou vérifier un bundle) :

```bash
# Windows
dist\Luthier\Luthier.exe --check

# macOS
dist/Luthier.app/Contents/MacOS/Luthier --check

# Linux
dist/Luthier/Luthier --check
```

Un code de sortie `0` signifie que les templates embarqués sont accessibles.

---

## Aide-mémoire

Pour retrouver rapidement une action une fois les concepts ci-dessus lus :

| Je veux… | Faire ceci |
|----------|------------|
| Démarrer un nouveau projet JUCE | **Create New Project** → saisir le nom → **Generate Project** |
| Rouvrir un travail existant | **Open Project…** → modifier → **Generate Project** |
| Changer le manufacturer / les chemins workspace par défaut | **Preferences** (auto-save) |
| Appliquer les defaults sur un formulaire neuf | **Create New Project** après avoir modifié Preferences |
| Déplacer les prefs sur une autre machine | **Export Preferences…** / **Import Preferences…** |
| Attribuer une couleur par client ou marque | **Luthier Accent Color** dans **Preferences** → **Export Preferences…** |
| Personnaliser le boilerplate processeur | **Templates** → modifier → **Save override** |
| Épingler une version JUCE à un projet | Renseigner **JUCE directory** (ligne hôte) dans **Workspace** sur **Project** |
| Compiler le même dépôt sur trois OS | Renseigner les six chemins **Workspace** une fois → partage via `.luthier.json` + **Export Preferences…** |

---

*Luthier — Ten Square Software — Manuel utilisateur (traduction française)*
