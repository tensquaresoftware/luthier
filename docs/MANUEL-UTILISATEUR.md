---
Organization: Ten Square Software
Author: Guillaume DUPONT
Project: Luthier
Title: Luthier — Manuel utilisateur
Version: 1.0
Product-Version: 1.0.0
Created: 2026-06-26
Updated: 2026-06-26
References:
  - docs/USER-MANUAL.md
  - docs/ARCHITECTURE.md
  - CONTRIBUTING.md
  - README.md
---

# Luthier — Manuel utilisateur

Ce manuel vous guide dans l’utilisation de Luthier, une application de bureau pour **créer**, **rouvrir** et **régénérer** des projets de plugins audio JUCE basés sur CMake.

> **Langue de l’interface** — Luthier s’affiche en **anglais**. Les libellés de boutons et de champs cités ci-dessous reprennent exactement le texte à l’écran. Ce document est la traduction française du [manuel anglais](USER-MANUAL.md), qui reste la référence officielle du produit.

---

## Table des matières

1. [Qu’est-ce que Luthier ?](#1-quest-ce-que-luthier-)
2. [Avant de commencer](#2-avant-de-commencer)
3. [Installation et lancement](#3-installation-et-lancement)
4. [La fenêtre principale](#4-la-fenêtre-principale)
5. [Trois types de réglages](#5-trois-types-de-réglages)
6. [Premier lancement](#6-premier-lancement)
7. [Onglet Project](#7-onglet-project)
8. [Onglet Preferences](#8-onglet-preferences)
9. [Onglet Templates](#9-onglet-templates)
10. [Onglet About](#10-onglet-about)
11. [Parcours types](#11-parcours-types)
12. [Ce que Luthier génère](#12-ce-que-luthier-génère)
13. [Où sont stockées vos données](#13-où-sont-stockées-vos-données)
14. [Règles de validation des champs](#14-règles-de-validation-des-champs)
15. [Messages, erreurs et dépannage](#15-messages-erreurs-et-dépannage)
16. [Utiliser l’application autonome](#16-utiliser-lapplication-autonome)

---

## 1. Qu’est-ce que Luthier ?

Luthier vous aide à **créer des projets de plugins JUCE** sans éditer les fichiers CMake à la main. Vous remplissez un formulaire, Luthier valide vos saisies en direct, et lorsque vous cliquez sur **Generate Project**, il écrit un dossier de projet complet, prêt à ouvrir dans votre IDE et à compiler avec CMake.

Luthier peut aussi **rouvrir** un projet qu’il a créé auparavant, vous laisser modifier la configuration et **régénérer** les fichiers sur place.

On peut le voir comme un workflow de type Projucer (dont il est largement inspiré), orienté vers des **projets CMake portables** et une **régénération reproductible**.

### Ce que Luthier fait

- Génère des projets AU, VST3 et/ou Standalone à partir d’un seul formulaire.
- Écrit `CMakeLists.txt`, `CMakeUserPresets.json`, les fichiers sources, des aides IDE et un sidecar `.luthier.json`.
- Enregistre vos **valeurs par défaut** (fabricant, chemins, type de plugin, etc.) dans un fichier de préférences sur votre machine.
- Permet de personnaliser les **modèles sources C++** utilisés pour chaque nouveau projet.
- Rouvre les projets existants via `.luthier.json`, ou en lisant un `CMakeLists.txt` legacy lorsqu’il n’y a pas de sidecar.

### Ce que Luthier ne fait pas

- Il ne **compile pas** votre plugin — vous utilisez toujours CMake et votre IDE ou toolchain (Cursor, Xcode, Visual Studio, Ninja, etc.).
- Il ne **télécharge ni n’installe** JUCE — vous indiquez un dossier JUCE déjà présent sur le disque.
- Il ne **synchronise pas** les réglages entre machines — utilisez **Export Preferences…** / **Import Preferences…** pour déplacer vos profils manuellement.

---

## 2. Avant de commencer

### Ce dont vous aurez besoin

- Un **SDK JUCE** installé quelque part sur votre ordinateur (ou un chemin que vous comptez utiliser).
- Un **dossier de destination** où créer les dossiers de projet (par exemple Documents ou le Bureau).
- Une connaissance de base des **formats de plugin** sur votre plateforme (AU sur macOS, VST3 partout, Standalone pour une application de bureau).

### Plateformes prises en charge

Luthier fonctionne sur **macOS**, **Windows** et **Linux**. Vous pouvez l’exécuter depuis les sources (Python + PySide6) ou comme **application autonome** construite avec PyInstaller sur chaque plateforme — voir [§16](#16-utiliser-lapplication-autonome).

---

## 3. Installation et lancement

### Depuis les sources (développeurs)

Consultez [CONTRIBUTING.md](../CONTRIBUTING.md) dans le dépôt pour la procédure complète. En résumé :

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows : .venv\Scripts\activate
pip install -r requirements-dev.txt
.venv/bin/python main.py           # Windows : .venv\Scripts\python main.py
```

### Application autonome (utilisateurs finaux)

Téléchargez ou construisez le bundle pour votre système. Lancez l’application comme toute application native — aucune installation Python requise. Voir [§16](#16-utiliser-lapplication-autonome).

---

## 4. La fenêtre principale

À l’ouverture de Luthier, vous voyez quatre zones :

```
┌───────────────────────────────────────────────────┐
│  Project │ Preferences │ Templates │ About        │  ← Barre d’onglets
├───────────────────────────────────────────────────┤
│                                                   │
│            Contenu de l’onglet actif              │  ← Formulaire ou éditeur défilable
│                                                   │
├───────────────────────────────────────────────────┤
│     Message de statut (centré, pleine largeur)    │  ← Barre de statut dédiée
├───────────────────────────────────────────────────┤
│          [Boutons d’action de l’onglet]           │  ← Barre d’actions
└───────────────────────────────────────────────────┘
```

### Barre d’onglets

| Onglet | Rôle |
|--------|------|
| **Project** | Configurer le plugin sur lequel vous travaillez. |
| **Preferences** | Modifier les valeurs par défaut globales qui pré-remplissent les nouveaux projets. |
| **Templates** | Voir et personnaliser les modèles C++ / `.gitignore` utilisés à la génération. |
| **About** | Crédits, version et liens. |

### Barre d’actions (en bas)

Les boutons en bas **changent selon l’onglet actif** :

| Onglet | Boutons |
|--------|---------|
| **Project** | **Create New Project**, **Open Project…**, **Generate Project** |
| **Preferences** | **Import Preferences…**, **Export Preferences…** |
| **Templates** | **Load from file…**, **Reset to default**, **Save override** |
| **About** | *(aucun)* |

### Ligne de statut

Après la plupart des opérations, un court message s’affiche dans une **barre dédiée au-dessus des boutons d’action**, centrée sur toute la largeur de la fenêtre :

- les messages de **succès** utilisent la couleur d’accent (magenta) ;
- les messages d’**erreur** sont en rouge ;
- les longs chemins passent sur plusieurs lignes au lieu de chevaucher les boutons.

Exemples : *« Project generated at /Users/vous/Documents/MySynth »*, *« Loaded MySynth from … »*, *« Preferences imported from client-a.json »*.

L’enregistrement automatique dans **Preferences** affiche uniquement un badge **Saved** sur le champ modifié — il n’utilise pas cette barre de statut globale.

### Taille et position de la fenêtre

Luthier mémorise la taille, la position et l’état maximisé de la fenêtre entre les sessions. Si la position enregistrée n’est plus valide (par exemple après déconnexion d’un écran), la fenêtre s’ouvre centrée avec une taille par défaut confortable.

---

## 5. Trois types de réglages

Comprendre ces trois domaines évite la plupart des confusions.

| Domaine | Onglet | Portée | Répond à la question |
|---------|--------|--------|----------------------|
| **Projet en cours** | Project | Un plugin à la fois | *Comment **ce** plugin est-il configuré ?* |
| **Valeurs par défaut globales** | Preferences | Toute l’app, tous les futurs projets | *Quelles valeurs réutiliser à chaque fois ?* |
| **Modèles globaux** | Templates | Toute l’app, tous les projets générés | *Quel code source de départ pour les nouveaux projets ?* |

**Règles importantes :**

- Modifier **Preferences** ne change **pas** l’onglet **Project** tant que vous n’avez pas cliqué sur **Create New Project** (ou relancé l’app pour le seed initial).
- **Open Project…** et **Generate Project** n’écrivent **jamais** dans `preferences.json`.
- Les overrides **Templates** s’appliquent à chaque génération, mais ne sont **pas** inclus dans un export de préférences.

---

## 6. Premier lancement

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
| Destination folder | votre **Bureau** (via l’API OS) |
| JUCE directory | vide (placeholder selon l’OS, ex. `/Applications/JUCE` sur macOS) |
| Plugin type | Instrument (Synth) |
| Formats | AU, VST3, Standalone — tous cochés |
| C++ standard | C++17 |
| Preprocessor defs, Header search paths | vides |
| Copy to system plugin folders | désactivé |
| Copy to central artefacts folder | désactivé |
| Chemins d’artefacts (Windows / macOS / Linux) | vides |

### Premiers pas recommandés

1. Ouvrez **Preferences** et renseignez **Manufacturer**, les codes, **Destination folder** et **JUCE directory**.
2. Passez à **Project**, saisissez un **Project name**, puis cliquez sur **Generate Project**.
3. Ouvrez le dossier généré dans votre IDE et lancez la configuration CMake + compilation.

---

## 7. Onglet Project

Texte d’introduction en haut de la vue :

> *Configure your JUCE project by entering the information below. Fields marked with an asterisk (\*) are mandatory. A new project is pre-configured based on the default settings entered in the Preferences tab.*

*(« Configurez votre projet JUCE en remplissant les informations ci-dessous. Les champs marqués d’un astérisque (\*) sont obligatoires. Un nouveau projet est pré-configuré à partir des réglages par défaut de l’onglet Preferences. »)*

L’onglet est une page défilable divisée en cinq sections.

### 7.1 Project Info

Identité et chemins pour **ce** plugin.

| Champ | Obligatoire | Description |
|-------|-------------|-------------|
| **Project name** * | Oui | Nom technique — nom du dossier et cible CMake. Doit commencer par une lettre ; lettres, chiffres, `-`, `_` uniquement. |
| **Display name** | Non | Nom affiché dans les hôtes. Si vide, le project name est utilisé. |
| **Version** * | Oui | Chaîne de version (défaut `1.0.0` pour un nouveau projet). |
| **Manufacturer** * | Oui | Nom de votre société ou nom personnel. |
| **Copyright** | Non | Ligne de copyright dans les métadonnées générées. |
| **Website** | Non | URL optionnelle. |
| **E-mail** | Non | Contact optionnel. |
| **Manufacturer code** * | Oui | Exactement 4 lettres (code JUCE). |
| **Plugin code** * | Oui | Exactement 4 caractères alphanumériques. |
| **Bundle ID** | — | Lecture seule. Calculé à partir du manufacturer et du project name. |
| **Destination folder** * | Oui | Dossier **parent** où Luthier crée le sous-dossier nommé d’après **Project name**. Exemple : `~/Documents` + `MySynth` → `~/Documents/MySynth`. |
| **JUCE directory** | Non | Chemin vers le SDK JUCE **pour ce projet**. Pré-rempli depuis Preferences sur un nouveau projet ; peut différer d’un projet à l’autre (plusieurs versions de JUCE). |

Chaque ligne de chemin est disposée ainsi : **label → Choose… → champ texte**. **Choose…** ouvre le sélecteur de dossier natif. Vous pouvez aussi saisir ou coller un chemin à la main.

### 7.2 Plugin Type

Choix exclusif :

| Type | Signification |
|------|---------------|
| **Instrument** (Synth) | Reçoit du MIDI, produit de l’audio. |
| **Audio Effect** | Traite l’audio entrant. |
| **MIDI Effect** | Traite le MIDI uniquement — pas d’E/S audio. |

### 7.3 Formats

Sélectionnez **au moins un** format :

- **AU** (Audio Unit macOS)
- **VST3**
- **Standalone**

Si aucun n’est coché, **Generate Project** reste désactivé et une indication apparaît sous les cases.

### 7.4 Compilation

| Champ | Description |
|-------|-------------|
| **C++ standard** | C++17, C++20 ou C++23. |
| **Preprocessor defs** | Une définition par ligne (ex. `MY_FLAG=1`). |
| **Header search paths** | Un chemin par ligne, relatif à la racine du projet. |

### 7.5 Artefacts

Contrôle où les plugins compilés sont **copiés après chaque build** (injecté dans les variables cache CMake).

| Option | Description |
|--------|-------------|
| **Copy to system plugin folders** | Copie de type installation vers les emplacements standard de l’OS, si activé dans CMake. |
| **Copy to central artefacts folder** | Une fois cochée, active les trois champs de répertoire ci-dessous. |

Lorsque **Copy to central artefacts folder** est activée :

| Champ | Description |
|-------|-------------|
| **Windows** | Chemin cible pour les builds Windows. |
| **macOS** | Chemin cible pour les builds macOS. |
| **Linux** | Chemin cible pour les builds Linux. |

Ces chemins se saisissent **manuellement** — pas de bouton **Choose…**, car un sélecteur sur votre machine actuelle ne peut pas produire un chemin valide pour un autre OS (par exemple `D:\Plugins` depuis macOS).

Les réglages d’artefacts appartiennent à **ce projet**. Ils peuvent différer des defaults globaux de Preferences.

### 7.6 Actions du projet

#### Create New Project

Remet le formulaire à zéro :

- **Effacé :** project name, display name (version remise à `1.0.0`).
- **Re-seedé depuis `preferences.json` :** tout le reste — manufacturer, codes, destination, JUCE directory, type, formats, compilation, artefacts.

Si vous avez modifié le formulaire depuis le dernier état stable (ouverture, reset ou démarrage à froid), Luthier demande :

> *The project form has unsaved changes. Discard them and start a new project?*

*(« Le formulaire projet contient des modifications non enregistrées. Les abandonner et démarrer un nouveau projet ? »)*

**No** conserve vos modifications ; **Yes** réinitialise. Le bouton par défaut est **No**.

**Create New Project** ne modifie **pas** `preferences.json`.

#### Open Project…

Ouvre un sélecteur de dossier. Choisissez un **dossier de projet** généré précédemment par Luthier (contient `CMakeLists.txt` et idéalement `.luthier.json`).

- Seul l’onglet **Project** est mis à jour.
- **Preferences** et **Templates** restent inchangés.

**Lecture du projet :**

1. Si `.luthier.json` existe et est valide, Luthier charge la configuration complète depuis ce fichier.
2. Sinon, Luthier tente d’analyser `CMakeLists.txt` (projets legacy).

**Après déplacement d’un dossier projet :** ouvrez-le à son **nouvel emplacement**. **Destination folder** affiche le parent du dossier sélectionné — l’ancien chemin n’est pas conservé.

#### Generate Project

Crée ou régénère le projet à partir de l’onglet **Project** uniquement :

- écrit dans `Destination folder` / `Project name` ;
- intègre **JUCE directory** dans `CMakeLists.txt` lorsqu’il est renseigné ;
- applique vos overrides **Templates** le cas échéant ;
- écrit `.luthier.json` avec un instantané complet de la configuration.

**Generate Project** ne lit ni n’écrit **Preferences**.

**Comportement de Destination folder :**

- le champ reste visible pour permettre une régénération en un clic après **Open Project…** ;
- s’il est vide ou pointe vers un dossier inexistant, Luthier ouvre un sélecteur avant de continuer ;
- si un dossier du même nom existe déjà, Luthier demande confirmation avant écrasement.

Après une génération réussie, Luthier mémorise le dossier parent de destination pour le prochain dialogue **Choose…**.

**Generate Project** n’est actif que lorsque tous les champs obligatoires sont valides et que les templates sont disponibles.

---

## 8. Onglet Preferences

Texte d’introduction :

> *These are reusable defaults: they pre-fill the matching fields when you create a new project, so you don't retype them each time. They are saved on this machine only and are never imposed on the projects you generate.*

*(« Ce sont des valeurs par défaut réutilisables : elles pré-remplissent les champs correspondants lorsque vous créez un nouveau projet. Elles sont enregistrées sur cette machine uniquement et ne sont jamais imposées aux projets que vous générez. »)*

### 8.1 Sections

| Section | Contenu |
|---------|---------|
| **Identity** | Manufacturer, codes, Copyright, Website, E-mail |
| **Paths** | Destination folder, JUCE directory — tous deux avec **Choose…** |
| **Plugin Type** | Synth / effect / MIDI par défaut |
| **Formats** | Cases AU / VST3 / Standalone par défaut |
| **Compilation** | C++ standard, preprocessor defs, header paths par défaut |
| **Artefacts** | Mêmes options de copie et chemins par OS que Project (saisie texte pour les chemins d’artefacts) |

Il n’y a **pas** de champs propres au projet ici (pas de project name, version ou bundle ID).

### 8.2 Enregistrement automatique

Toute modification **valide** est **enregistrée immédiatement** dans `preferences.json`. Aucun bouton Save.

Lorsqu’un champ est sauvegardé, un badge **« Saved »** clignote brièvement sur ce champ (accent orange).

Les champs invalides bloquent l’enregistrement tant qu’ils ne sont pas corrigés.

### 8.3 Import Preferences…

1. Choisissez un fichier JSON (profil exporté, sauvegarde, autre machine).
2. S’il est valide, il **remplace** intégralement le profil de préférences actuel et met à jour `preferences.json`.
3. L’onglet Preferences se recharge.

**L’import ne modifie pas l’onglet Project.** Utilisez **Create New Project** pour appliquer les nouveaux defaults à un formulaire vierge.

Si le fichier est invalide, une boîte de dialogue d’erreur s’affiche et votre profil précédent est conservé.

### 8.4 Export Preferences…

Enregistre les préférences **actuelles** dans un fichier JSON de votre choix. Ne modifie **pas** `preferences.json` sur le disque.

Servez-vous-en pour sauvegarder des profils ou les partager entre machines (un fichier par client, par studio, etc.).

L’export est bloqué si un champ de préférences est actuellement invalide.

### 8.5 Parcours multi-clients

1. Configurez Preferences pour le **Client A** → **Export Preferences…** → `client-a.json`.
2. Répétez pour le **Client B** → `client-b.json`.
3. Avant de démarrer un plugin pour un client → **Import Preferences…** → choisissez le bon fichier.
4. **Create New Project** → le formulaire correspond à ce profil.

Le projet que vous aviez ouvert reste inchangé jusqu’à ce que vous en créiez ou en ouvriez un autre.

---

## 9. Onglet Templates

Les templates sont **globaux** : les mêmes fichiers sont utilisés pour **chaque** projet généré.

### Fichiers modifiables

| Fichier | Rôle |
|---------|------|
| `PluginProcessor.h` / `.cpp` | Squelette processeur audio/MIDI |
| `PluginEditor.h` / `.cpp` | Squelette interface éditeur |
| `.gitignore` | Règles Git ignore pour les nouveaux projets |

Sélectionnez un fichier dans la liste, modifiez-le dans l’éditeur avec coloration syntaxique, puis **Save override** pour persister votre version.

### Actions

| Bouton | Effet |
|--------|--------|
| **Load from file…** | Charge un fichier externe dans l’éditeur **sans enregistrer**. Utilisez **Save override** pour persister. |
| **Reset to default** | Supprime votre override ; le modèle fourni avec Luthier est rétabli. |
| **Save override** | Enregistre le contenu de l’éditeur comme override personnel. |

Ligne de statut sous l’éditeur :

- *« Override active — used for new projects. »* lorsque vous avez une version personnalisée.
- *« Showing the built-in default. »* sinon.

Les overrides sont stockés dans le répertoire de configuration de l’application, **séparément** de `preferences.json`. Importer des préférences n’importe **pas** les overrides de templates.

---

## 10. Onglet About

Affiche le logo Luthier, l’organisation (**Ten Square Software**), l’auteur, l’e-mail de contact, le lien GitHub, la version et la date de révision.

Cliquez sur la ligne e-mail ou GitHub pour ouvrir votre client mail ou navigateur.

---

## 11. Parcours types

### 11.1 Nouveau plugin (une seule installation JUCE)

1. Renseignez **Preferences** une fois (manufacturer, destination, chemin JUCE).
2. Sur **Project**, saisissez **Project name** et ajustez les options.
3. Cliquez sur **Generate Project**.
4. Ouvrez le dossier de sortie dans votre IDE ; configurez et compilez avec CMake.

Pour un autre plugin : **Create New Project** → ajustez → **Generate Project**.

### 11.2 Plugin avec une version JUCE spécifique

1. **Create New Project** (JUCE directory seedé depuis Preferences).
2. Modifiez **JUCE directory** sur l’onglet **Project** pour pointer vers la branche ou la copie voulue.
3. **Generate Project** — le chemin est enregistré dans le projet et le sidecar.

### 11.3 Reprendre et modifier un projet existant

1. **Open Project…** → sélectionnez le dossier du projet.
2. Modifiez les champs sur **Project**.
3. **Generate Project** pour réécrire les fichiers sur place.

Si vous avez déplacé le dossier, ouvrez-le d’abord à son nouveau chemin.

### 11.4 Changer de profil client entre deux projets

1. **Import Preferences…** → fichier JSON du client.
2. **Create New Project**.
3. Remplissez les champs d’identité → **Generate Project**.

Le projet précédemment ouvert n’est pas modifié.

### 11.5 Personnaliser le code source de départ

1. Ouvrez **Templates** → sélectionnez `PluginProcessor.cpp` (ou un autre fichier).
2. Modifiez → **Save override**.
3. **Generate Project** sur tout projet nouveau ou existant — votre override est utilisé.

---

## 12. Ce que Luthier génère

Avec un **Project name** valide `MySynth` et un **Destination folder** `~/Documents`, Luthier crée `~/Documents/MySynth/` contenant :

| Fichier / dossier | Description |
|-------------------|-------------|
| `CMakeLists.txt` | Projet CMake principal du plugin JUCE |
| `CMakeUserPresets.json` | Presets CMake multi-plateforme (debug/release par OS) |
| `Source/` | Fichiers `.h` / `.cpp` processeur et éditeur depuis les templates |
| `.luthier.json` | Instantané complet de la configuration pour réouverture |
| `.gitignore` | Depuis le template (personnalisable) |
| `.vscode/` | Réglages, tâches et configurations de lancement VS Code |
| `.cursorrules` | Indications pour l’IDE Cursor |
| `CMake/CopyVst3Elevated.ps1` | Aide à la copie VST3 sous Windows |
| `README.md` | Readme du projet généré |

La génération utilise des écritures atomiques : les fichiers sont construits dans un dossier temporaire puis remplacés sur place, pour limiter le risque d’un projet à moitié écrit.

---

## 13. Où sont stockées vos données

| Emplacement | Contenu | Modifié par |
|-------------|---------|-------------|
| `preferences.json` | Profil de defaults globaux | Premier lancement, auto-save Preferences, Import |
| `app_state.json` | Dernier dossier parent, dernier dossier import/export, géométrie fenêtre | Generate réussi, chemins Import/Export, redimensionnement/déplacement fenêtre |
| Fichiers `*.json` exportés | Copies de profils de préférences | Export Preferences… (fichiers choisis manuellement) |
| Overrides Templates (dossier config) | Contenu de templates personnalisé | Save override, Reset |
| Dossier de projet généré | Projet CMake + `.luthier.json` | Generate Project |

Les chemins des fichiers de configuration dépendent de votre OS (emplacement standard de configuration applicative pour Luthier).

**Idée clé :** les réglages globaux vivent dans la config Luthier. Les réglages par projet vivent dans l’onglet **Project** et, après génération, dans le dossier du projet et `.luthier.json`.

---

## 14. Règles de validation des champs

Luthier valide les champs pendant la saisie. Les champs invalides affichent une indication d’erreur ; **Generate Project** reste désactivé tant que tout le obligatoire n’est pas valide.

| Champ | Règle |
|-------|-------|
| Project name | Commence par une lettre ; lettres, chiffres, `-`, `_` uniquement. |
| Display name | Lettres, chiffres, espace, `-`, `_` uniquement. |
| Version | Non vide. |
| Manufacturer | Non vide. |
| Manufacturer code | Exactement 4 lettres. |
| Plugin code | Exactement 4 caractères alphanumériques. |
| Destination folder | Non vide ; pas de caractères accentués dans le chemin. |
| JUCE directory | Optionnel ; si renseigné, pas de caractères accentués. |
| Formats | Au moins une case cochée. |
| Chemins d’artefacts | Lorsque la copie centrale est activée, pas de caractères accentués. |

Les champs texte optionnels (Copyright, Website, E-mail, preprocessor defs) acceptent tout contenu sauf indication contraire.

---

## 15. Messages, erreurs et dépannage

Les retours d’opération globaux (Generate, Open, Create New Project, Import/Export Preferences) s’affichent dans la **barre de statut dédiée** au-dessus des boutons d’action — voir [§4 Ligne de statut](#ligne-de-statut). Le tableau ci-dessous liste les messages typiques.

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
| Ouverture d’un dossier non-Luthier | Dialogue : *Not a JUCE plugin project* ou erreur d’analyse avec champs manquants listés. |
| `.luthier.json` invalide | Dialogue : sidecar invalide ou illisible. |
| Aucun format dans le projet ouvert | Dialogue : aucun format détecté. |
| Import JSON invalide | Dialogue d’avertissement ; préférences précédentes conservées. |
| Export avec champs invalides | Message d’erreur ; fichier non écrit. |
| Templates manquants (installation cassée) | Generate désactivé ; erreur au démarrage dans la ligne de statut. |
| Écrasement d’un projet existant | Dialogue de confirmation avant remplacement du dossier. |
| Modifications Project non enregistrées + Create New Project | Dialogue de confirmation ; défaut **No**. |

### Conseils

- **« Generate Project » est grisé** — vérifiez les champs obligatoires (*), les formats et les chemins d’artefacts si la copie centrale est activée.
- **Mauvaise destination après déplacement** — utilisez **Open Project…** au nouvel emplacement ; ne comptez pas sur un ancien chemin de destination.
- **Changement Preferences absent de l’onglet Project** — comportement normal ; cliquez sur **Create New Project** pour appliquer.
- **Régénérer sans modification** — Open → **Generate Project** doit produire un projet cohérent ; le sidecar préserve l’état complet.

---

## 16. Utiliser l’application autonome

Luthier peut être empaqueté en application autonome (sans Python sur la machine cible).

| Plateforme | Sortie typique |
|------------|----------------|
| macOS | `Luthier.app` |
| Windows | `Luthier.exe` dans un dossier `Luthier/` avec `_internal/` |
| Linux | Exécutable `Luthier` dans un dossier `Luthier/` avec `_internal/` |

**Important :** distribuez le **dossier entier** — l’exécutable seul ne suffit pas ; templates et bibliothèques Qt sont à côté.

### Première exécution sous Windows (builds non signés)

SmartScreen peut avertir au premier lancement. Utilisez **More info** → **Run anyway** pour les builds locaux. Windows Defender peut analyser les fichiers au premier démarrage — cela peut ajouter un court délai, sans échec.

### Première exécution sous Linux

Si le binaire n’est pas exécutable : `chmod +x Luthier/Luthier`. Un serveur d’affichage X11 ou Wayland peut être nécessaire pour l’interface graphique.

### Vérification headless

Depuis un terminal (utile pour la CI ou vérifier un bundle) :

```bash
# macOS
Dist/Luthier.app/Contents/MacOS/Luthier --check

# Windows
Dist\Luthier\Luthier.exe --check

# Linux
Dist/Luthier/Luthier --check
```

Un code de sortie `0` signifie que les templates embarqués sont accessibles.

---

## Aide-mémoire

| Je veux… | Faire ceci |
|----------|------------|
| Démarrer un nouveau plugin | **Create New Project** → saisir le nom → **Generate Project** |
| Rouvrir un travail existant | **Open Project…** → modifier → **Generate Project** |
| Changer le manufacturer / les chemins par défaut | **Preferences** (auto-save) |
| Appliquer les defaults sur un formulaire neuf | **Create New Project** après avoir modifié Preferences |
| Déplacer les prefs sur une autre machine | **Export Preferences…** / **Import Preferences…** |
| Personnaliser le boilerplate processeur | **Templates** → modifier → **Save override** |
| Épingler une version JUCE à un projet | Renseigner **JUCE directory** sur l’onglet **Project** |

---

*Luthier — Ten Square Software — Manuel utilisateur (traduction française)*
