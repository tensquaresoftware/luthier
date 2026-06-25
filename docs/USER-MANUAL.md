# Luthier — Manuel utilisateur

> **Statut de ce document** — Ce manuel décrit la **vision cible** de Luthier, incluant des comportements et des libellés **en cours de formalisation** (user stories à venir). Il sert de référence pour valider la cohérence du produit avant implémentation. L’interface de l’application est en **anglais** ; les libellés cités ci-dessous reprennent les intitulés prévus dans l’UI.

---

## 1. Qu’est-ce que Luthier ?

Luthier est une application de bureau qui permet de **créer**, **configurer** et **régénérer** des projets JUCE basés sur **CMake** (plugins AU, VST3, Standalone, ou combinaisons). Elle s’inspire de l’esprit de Projucer, orienté CMake portable et rechargement de projet.

En pratique, Luthier vous aide à :

- remplir un formulaire validé en direct ;
- générer un dossier de projet complet (`CMakeLists.txt`, `CMakeUserPresets.json`, sources, `.gitignore`, sidecar `.luthier.json`) ;
- rouvrir un projet déjà généré, modifier sa configuration et le régénérer ;
- conserver vos **habitudes de travail** (identité éditeur, chemins, templates) sans les mélanger avec un projet particulier.

---

## 2. Les trois domaines de réglages

Luthier organise l’interface autour de **trois périmètres distincts**. Les comprendre évite la plupart des ambiguïtés d’usage.

| Domaine | Onglet | Portée | Question à laquelle il répond |
|--------|--------|--------|-------------------------------|
| **Projet en cours** | **Project** | Un seul projet à la fois | *Comment est configuré **ce** plugin ?* |
| **Réglages globaux** | **Preferences** | Toute l’application, tous projets | *Quelles valeurs par défaut veux-je réutiliser ?* |
| **Modèles globaux** | **Templates** | Toute l’application, tous projets | *Quels fichiers sources modèle utiliser à la génération ?* |

**Project** correspond au travail du moment : noms, type, formats, compilation, chemins propres à **ce** projet.

**Preferences** et **Templates** se comportent comme des réglages d’application (comparable à un menu *Settings* sur macOS), partagés entre tous vos projets. Modifier les préférences **ne modifie pas** le projet ouvert tant que vous n’agissez pas explicitement sur l’onglet Project (par exemple via **Create New Project**).

---

## 3. Navigation

Quatre onglets en haut de la fenêtre :

- **Project** — formulaire du projet en cours et actions **Create New Project**, **Open Project…**, **Generate Project**.
- **Preferences** — valeurs par défaut réutilisables ; actions **Import Preferences…**, **Export Preferences…**.
- **Templates** — édition des modèles C++ et `.gitignore` ; actions **Load from file…**, **Reset to default**, **Save override**.
- **About** — crédits et version.

Une **barre d’actions** en bas change selon l’onglet actif. Une **ligne de statut** confirme les opérations réussies ou signale les erreurs.

Lors de l’enregistrement automatique des préférences, une **étiquette furtive** (couleur accent orange) apparaît brièvement à droite de la barre d’onglets pour confirmer que les changements ont bien été enregistrés.

---

## 4. Premier lancement et source des defaults

### 4.1 Principe : code → `preferences.json` → tout le reste

Luthier ne maintient **qu’une seule source de defaults** une fois l’application installée :

1. **À la toute première exécution**, le fichier `preferences.json` est **créé** à partir de valeurs **hardcodées dans le code** (usine).
2. **Ensuite**, tout ce qui seed l’onglet Project — au démarrage, via **Create New Project**, ou après **Import Preferences…** — provient **exclusivement** de `preferences.json`.

Les widgets de l’interface ne portent plus leurs propres defaults « métier » : ils affichent ce que contient le profil actif.

### 4.2 Valeurs usine (création initiale de `preferences.json`)

Au **tout premier démarrage**, Luthier écrit `preferences.json` avec :

| Champ | Valeur initiale (code) |
|-------|------------------------|
| Manufacturer | `My Company` |
| Manufacturer code | `Myco` |
| Plugin code | `Mypl` |
| Copyright, Website, E-mail | vides |
| **Destination folder** | dossier **Bureau** (résolu via l’API OS, selon la plateforme) |
| **JUCE directory** | vide (placeholder adapté à l’OS, ex. `/Applications/JUCE` sur macOS) |
| Plugin type | Instrument (Synth) |
| Formats | AU, VST3 et Standalone cochés |
| C++ standard | C++17 |
| Preprocessor defs, Header search paths | vides |
| Copy to central artefacts folder | **décochée** |
| Chemins d’artefacts (Windows, macOS, Linux) | vides |
| Copy to system plugin folders | décochée |

L’onglet **Project** s’ouvre comme un **nouveau projet** : identité du plugin vide (noms, version `1.0.0`), **tous les autres champs** pré-remplis depuis `preferences.json`.

Vous pouvez ensuite adapter **Preferences** (auto-save), ou importer un profil client (voir § 8).

---

## 5. Onglet Project — le projet en cours

Texte d’introduction (en haut de la vue) :

> *Configure your JUCE project by entering the information below. Fields marked with an asterisk (\*) are mandatory. A new project is pre-configured based on the default settings entered in the Preferences tab.*

### 5.1 Project Info

Champs d’identité et de publication du plugin :

- **Project name** * — nom technique (dossier, cibles CMake).
- **Display name** — nom affiché ; si vide, le project name est utilisé.
- **Version** *
- **Manufacturer** *, **Manufacturer code** *, **Plugin code** *
- **Copyright**, **Website**, **E-mail**
- **Bundle ID** — calculé automatiquement à partir du manufacturer et du project name.

**Destination folder** * et **JUCE directory** (ordre prévu dans l’UI) :

- **Destination folder** * — dossier **parent** dans lequel Luthier crée (ou régénère) le sous-dossier portant le **Project name**.  
  Exemple : destination `~/Documents` + project name `MySynth` → projet dans `~/Documents/MySynth`.  
  Disposition : **label → bouton Choose… → champ texte**. **Choose…** ouvre le sélecteur de dossier natif de l’OS ; le champ reste éditable (collage, correction manuelle).

- **JUCE directory** — chemin vers le SDK JUCE **utilisé pour ce projet**. À la création d’un nouveau projet, il est pré-rempli depuis **Preferences** ; vous pouvez le remplacer pour épingler une version de JUCE **spécifique à ce projet** (plusieurs projets peuvent ainsi viser des versions différentes de JUCE).  
  Même disposition **label → Choose… → champ texte** que pour Destination folder.

### 5.2 Plugin Type

Choix exclusif :

- **Instrument** (Synth)
- **Audio Effect**
- **MIDI Effect**

### 5.3 Formats

Au moins un format requis :

- AU, VST3, Standalone

### 5.4 Compilation

- **C++ standard** (17, 20 ou 23)
- **Preprocessor defs** (une par ligne)
- **Header search paths** (une par ligne, relatives au projet)

### 5.5 Artefacts

Options de copie post-build :

- **Copy to system plugin folders**
- **Copy to central artefacts folder** — lorsque cochée, les trois champs **Windows**, **macOS** et **Linux** deviennent actifs.

Ces chemins décrivent où les binaires seront copiés **sur chaque OS au moment du build** (valeurs injectées dans CMake). Ils se saisissent **au clavier** — pas de bouton **Choose…** : depuis une machine donnée, un sélecteur local ne peut pas produire un chemin valide pour une autre plateforme (ex. `D:\Plugins` depuis macOS).

Ces réglages sont **propres au projet en cours**. Ils peuvent diverger des préférences globales après un **Create New Project** ou un **Open Project…**.

### 5.6 Actions (barre du bas)

#### Create New Project

Remet l’application dans l’état d’un **nouveau projet**, identique au démarrage à froid après chargement de `preferences.json` :

- **effacé** : identité propre au plugin (project name, display name vides ; version `1.0.0`) ;
- **re-seedé depuis `preferences.json`** : tout le reste — manufacturer, codes, copyright, destination folder, JUCE directory, plugin type, formats, compilation, artefacts.

Si le formulaire a été modifié depuis le dernier état « stable » (projet chargé ou dernier reset), Luthier demande confirmation avant d’abandonner les changements.

**Create New Project** ne modifie **pas** `preferences.json` : il **lit** le profil actif pour remplir Project.

#### Open Project…

Ouvre un dossier de projet **déjà généré par Luthier** (celui qui contient `.luthier.json` et `CMakeLists.txt`).

- Seul l’onglet **Project** est mis à jour.
- **Preferences** et **Templates** ne sont **pas** modifiés.

**Destination folder après déplacement du projet**

Si vous avez créé un projet sur le Bureau, fermé Luthier, puis **déplacé** le dossier du projet vers Documents avant de le rouvrir :

- vous sélectionnez le dossier du projet à son **nouvel emplacement** (ex. `~/Documents/MySynth`) ;
- **Destination folder** affiche le **parent** de ce dossier : `~/Documents` ;
- l’ancien chemin (Bureau) n’est **pas** conservé : **l’emplacement réel du dossier ouvert fait foi**.

Cela garantit qu’une régénération écrit au bon endroit.

#### Generate Project

Génère (ou régénère) le projet CMake à partir **uniquement** des réglages de l’onglet **Project** :

- écrit ou met à jour le dossier `Destination folder` / `Project name` ;
- injecte le **JUCE directory** du projet dans `CMakeLists.txt` lorsqu’il est renseigné ;
- applique les **Templates** globaux (overrides utilisateur s’il y en a) ;
- écrit le sidecar `.luthier.json` à la racine du projet.

**Generate Project** ne lit ni ne modifie **Preferences** (`preferences.json`).  
Les **Templates** sont lus au moment de la génération mais ne sont pas modifiés par cette action.

**Destination folder** reste un champ du formulaire (et non une modale systématique au clic sur Generate) afin de garder une **régénération en un clic** après **Open Project…**, et de laisser le chemin visible avant génération. Si le champ est vide ou pointe vers un dossier inexistant, Luthier peut proposer **Choose…** ou le sélecteur de dossier avant de continuer.

Après chaque génération réussie, Luthier mémorise le **dernier dossier parent** utilisé (confort pour les prochains **Choose…** et pour le dossier de départ de **Open Project…**). Si ce chemin n’est plus valide (dossier supprimé, autre machine), le **Bureau** (résolu via l’API OS) sert de repli.

Si un dossier du même nom existe déjà à l’emplacement cible, Luthier demande confirmation avant écrasement.

---

## 6. Onglet Preferences — valeurs par défaut globales

Texte d’introduction (en haut de la vue) :

> *These are reusable defaults: they pre-fill the matching fields when you create a new project, so you don't retype them each time. They are saved on this machine only and are never imposed on the projects you generate.*

### 6.1 Contenu

Les mêmes familles de champs que sur Project, **sans** identité propre au plugin (pas de project name, display name, version, bundle ID). Les libellés reprennent ceux de Project (**Destination folder**, pas « Default destination » — le texte d’introduction en haut de la vue porte déjà le concept de defaults).

- identité éditeur : Manufacturer, codes, Copyright, Website, E-mail ;
- **Destination folder** — **label → Choose… → champ** ;
- **JUCE directory** — **label → Choose… → champ** ;
- **Plugin type**, **Formats**, **Compilation** (C++ standard, preprocessor defs, header search paths) ;
- section artefacts : cases à cocher + champs **Windows**, **macOS**, **Linux** (saisie texte uniquement, sans **Choose…** — voir § 5.5).

Toutes ces valeurs sont persistées dans `preferences.json` et constituent le **seul** jeu de defaults pour **Create New Project** et le premier affichage de Project au lancement.

### 6.1.1 Boutons Choose… (chemins locaux)

| Champ | Choose… | Remarque |
|-------|---------|----------|
| Destination folder (Project et Preferences) | Oui | Dossier sur **cette** machine |
| JUCE directory (Project et Preferences) | Oui | Installation JUCE **locale** |
| Windows / macOS / Linux (artefacts) | **Non** | Chemins **cibles par OS** pour CMake ; saisie manuelle |

**Choose…** utilise le sélecteur de dossier natif (syntaxe correcte pour l’OS courant). Le champ texte associé reste modifiable. Quand la case **Copy to central artefacts folder** est décochée, les champs artefacts (et leurs validations) sont inactifs.

### 6.2 Enregistrement automatique

Toute modification **valide** dans Preferences est **enregistrée automatiquement** dans `preferences.json` sur votre machine. Une étiquette furtive dans la barre d’onglets confirme l’enregistrement.

Si un champ est invalide, l’enregistrement n’a pas lieu tant que la validation n’est pas corrigée.

### 6.3 Import Preferences…

Importe un fichier JSON (profil client, machine, etc.) et :

1. remplace **intégralement** le contenu actuel de Preferences ;
2. met à jour `preferences.json` ;
3. recharge l’affichage de l’onglet Preferences.

**Import Preferences…** ne modifie **pas** l’onglet Project ouvert. Les nouvelles valeurs s’appliqueront au prochain **Create New Project** (ou au prochain démarrage de l’app pour l’affichage des prefs).

### 6.4 Export Preferences…

Exporte les préférences **actuellement affichées** vers un fichier JSON au nom de votre choix.

- **Export** ne modifie **pas** `preferences.json`.
- sert à sauvegarder, partager ou versionner des profils (ex. un fichier par client).

### 6.5 Cas d’usage : plusieurs clients

1. Configurez Preferences pour le **Client A** → **Export Preferences…** → `client-a.json`.
2. Répétez pour le **Client B** → `client-b.json`.
3. Avant de démarrer un nouveau plugin pour un client → **Import Preferences…** → choisissez le bon fichier.
4. **Create New Project** → le formulaire Project est seedé avec ce profil.

Le projet déjà ouvert, le cas échéant, reste inchangé jusqu’à ce que vous créiez un nouveau projet ou en ouvriez un autre.

---

## 7. Onglet Templates — modèles globaux

Les templates sont **globaux** : les mêmes modèles s’appliquent à **tous** les projets générés.

Fichiers personnalisables :

- `Source/PluginProcessor.h` / `.cpp`
- `Source/PluginEditor.h` / `.cpp`
- `.gitignore`

Actions :

| Bouton | Effet |
|--------|--------|
| **Load from file…** | Charge un fichier externe dans l’éditeur (sans l’enregistrer tant que vous n’avez pas sauvé l’override). |
| **Reset to default** | Supprime votre override pour le fichier sélectionné ; le modèle fourni avec Luthier est rétabli. |
| **Save override** | Persiste le contenu de l’éditeur comme override utilisateur. |

Les overrides sont stockés dans le répertoire de configuration de l’application sur votre machine, **séparément** de `preferences.json`. Importer un profil de préférences **n’inclut pas** les overrides de templates.

---

## 8. Workflows typiques

### 8.1 Nouveau plugin, un seul JUCE sur la machine

1. Renseignez **Preferences** une fois (Destination folder, JUCE directory, identité).
2. Onglet **Project** → complétez Project name et options spécifiques.
3. **Generate Project**.
4. Pour un autre plugin : **Create New Project** → ajustez → **Generate Project**.

### 8.2 Nouveau plugin, version JUCE dédiée

1. **Create New Project** (JUCE directory seedé depuis Preferences).
2. Remplacez **JUCE directory** sur l’onglet **Project** par le chemin de la branche JUCE voulue.
3. **Generate Project** — le chemin est enregistré dans le projet (sidecar + `CMakeLists.txt`).

### 8.3 Reprendre un projet existant

1. **Open Project…** → sélectionnez le dossier du projet.
2. Modifiez les champs souhaités sur **Project**.
3. **Generate Project** pour régénérer sur place.

Si vous avez déplacé le projet, ouvrez-le à son **nouvel emplacement** : **Destination folder** reflétera le parent actuel.

### 8.4 Changer de client entre deux projets

1. **Import Preferences…** → profil du client.
2. **Create New Project**.
3. Complétez et **Generate Project**.

Le projet précédemment ouvert (autre client) n’est pas modifié tant que vous ne l’avez pas régénéré vous-même.

---

## 9. Fichiers et persistance — où est stocké quoi ?

| Fichier / emplacement | Contenu | Modifié par |
|----------------------|---------|-------------|
| `preferences.json` (config OS) | Profil actif : **tous** les defaults qui seed Project (identité éditeur, chemins, type, formats, compilation, artefacts, JUCE) | Création initiale (valeurs usine du code), auto-save Preferences, Import |
| Dernier dossier parent utilisé (dans la config app) | Raccourci pour **Choose…** et dossier de départ de **Open Project…** ; repli Bureau si invalide | Generate Project réussi |
| Fichiers exportés (`*.json`) | Copies de profils | Export Preferences… (lecture seule côté app) |
| Overrides Templates (config OS) | Sources / `.gitignore` personnalisés | Save override, Reset |
| Dossier généré du projet | CMake, sources, `.luthier.json` | Generate Project |
| `.luthier.json` (dans le projet) | Snapshot du **ProjectSpec** (config complète du projet, incl. JUCE directory et destination folder au moment de la génération) | Generate Project ; **Destination folder** recalculé à l’Open depuis l’emplacement du dossier |

**Principe clé :** ce qui est **global** vit dans la config Luthier (Preferences, Templates). Ce qui est **par projet** vit dans le formulaire Project et, après génération, dans le dossier du projet et son sidecar.

---

## 10. Validation et messages d’erreur

- Les champs obligatoires (*) doivent être valides pour activer **Generate Project**.
- Les erreurs de validation sont signalées inline sur les champs concernés.
- **Open Project…** échoue avec un message explicite si le dossier n’est pas un projet Luthier lisible (sidecar invalide, CMake illisible, champs manquants, etc.).
- **Import Preferences…** signale un JSON invalide ou des valeurs rejetées par la validation ; en cas d’échec, le profil précédent est conservé.

---

## 11. Rappels utiles

- **Destination folder** = dossier **parent**, pas le chemin complet du dossier du projet. Le nom du sous-dossier vient du **Project name**. Un champ explicite (plutôt qu’une modale à chaque Generate) privilégie la **régénération** et les **profils Import/Export** par client.
- **Choose…** pour les chemins **locaux** (destination, JUCE) ; saisie manuelle pour les chemins d’**artefacts par OS cible**.
- **`preferences.json`** est la **seule** source de defaults après le premier lancement ; les valeurs usine ne vivent que dans le code pour **créer** ce fichier une fois.
- **Preferences** seedent un **nouveau** projet ; elles ne « poussent » pas leurs changements vers un projet déjà ouvert.
- **Open** et **Generate** n’écrivent **pas** dans `preferences.json`.
- **JUCE directory** existe à deux niveaux : default global (Preferences) et chemin **par projet** (Project), utile pour travailler avec plusieurs versions de JUCE.
- Les **Templates** sont partagés entre tous les projets ; les profils Import/Export ne les incluent pas.

---

## 12. Évolutions prévues (non encore toutes implémentées)

Ce manuel anticipe les changements suivants, discutés et validés conceptuellement :

- Libellés : **Destination folder** (Project et Preferences) ; **JUCE directory** sur Project ; artefacts **Windows** / **macOS** / **Linux**.
- Boutons **Choose…** : Destination folder et JUCE directory (Project + Preferences) ; **pas** sur les chemins d’artefacts.
- **Import Preferences…** / **Export Preferences…** (remplacement de Load / Save).
- Auto-save des Preferences avec étiquette furtive (accent orange) dans la barre d’onglets.
- **Create New Project** : reset complet seedé **intégralement** depuis `preferences.json` + modale si formulaire modifié.
- Extension de `preferences.json` et de l’onglet Preferences : plugin type, formats, compilation.
- `juceDir` sur **ProjectSpec** / sidecar (révision AD-7) ; Generate lit le JUCE du projet, pas un paramètre séparé depuis prefs.
- Découplage Open / Generate ↔ `preferences.json` (révision AD-5).
- Defaults usine à la création initiale de `preferences.json` ; mémorisation du **dernier dossier parent** après Generate.
- Réorganisation UI Project Info : Destination folder et JUCE directory sous Bundle ID.

Lors de la relecture, comparez votre usage réel à ce document : toute friction restante indique probablement une user story ou une phrase d’introduction à ajuster.

---

*Luthier — Ten Square Software — Manuel utilisateur (brouillon de vision produit)*
