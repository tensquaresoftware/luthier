# Luthier — Checklist QA manuelle

**Version produit visée :** 1.0.0  
**Public :** testeurs sans connaissance technique particulière  
**Langue de l’app :** l’interface Luthier est en **anglais** ; les libellés de boutons ci-dessous reprennent le texte exact à l’écran.

---

## Comment utiliser ce document

1. **Lisez d’abord** la section [Avant de commencer](#avant-de-commencer).
2. **Partie 1** — cochez les cases dans **chaque** bloc : [A — macOS](#a--macos), [B — Windows](#b--windows), [C — Linux](#c--linux).
3. **Partie 2** — une seule fois, avec **les trois machines** (ou deux machines + une VM), suivez le parcours « projet qui voyage » (Git, modifications, réouverture).
4. Cochez chaque case : `- [ ]` → `- [x]` quand c’est OK.
5. Notez les problèmes dans la [Grille de suivi](#grille-de-suivi-des-problèmes) en bas.

**Ce que vous testez :** Luthier crée et rouvre des **projets JUCE** (plugins VST/AU & apps audio/MIDI standalone). Luthier **ne compile pas** le plugin à votre place — vous vérifiez surtout l’application Luthier elle-même. Si vous voulez aller plus loin, un build CMake rapide sur chaque OS est un plus (étape optionnelle en fin de chaque bloc).

---

## Avant de commencer

### Sur chaque machine (macOS, Windows, Linux)

- [ ] Luthier est installé (application autonome **ou** version lancée depuis les sources — gardez la **même façon** sur les trois OS si possible).
- [ ] Vous avez une copie de **JUCE** quelque part sur le disque (dossier téléchargé ou cloné).
- [ ] Vous savez où vous mettez vos projets (Bureau, Documents, etc.).
- [ ] Pour la **Partie 2** : **Git** est installé et vous avez un dépôt vide (GitHub, GitLab, clé USB avec dépôt, etc.) pour synchroniser le projet entre machines.

### Conventions pour cette checklist

| Nom | Signification |
|-----|----------------|
| **Projet test local** | Nom suggéré : `TestLuthier` — un projet créé uniquement sur une machine |
| **Projet voyage** | Nom suggéré : `VoyageLuthier` — le projet partagé entre OS via Git |
| **Profil test** | Fichier exporté par OS : `profil-qa-macos.json`, `profil-qa-windows.json`, `profil-qa-linux.json` |
| **Barre de message** | La bandeau en bas de la fenêtre (au-dessus des boutons) : message couleur d'accent = OK, rouge = erreur |

---

# Partie 1 — Tests sur chaque système

Chaque système a **son propre bloc** (A, B ou C) avec les mêmes étapes numérotées de 1 à 9. Cochez les cases **dans les trois blocs** avant de passer à la Partie 2.

Les étapes sont identiques d’un OS à l’autre ; seules les notes spécifiques (installation, chemins, formats) changent.

---

## A — macOS

**Date :** _______________  
**Version Luthier (onglet About) :** _______________  
**Install :** ☐ application autonome (`Luthier.app`) ☐ depuis les sources

### A1 — Premier lancement et fenêtre

- [ ] Luthier s’ouvre sans plantage (si l’app n’est pas signée : autorisation dans **Réglages système** si macOS le demande).
- [ ] Vous voyez les quatre onglets : **Project**, **Preferences**, **Templates**, **About**.
- [ ] L’onglet **Project** est actif au démarrage.
- [ ] Redimensionnez la fenêtre, fermez Luthier, rouvrez : la taille et la position sont **à peu près** retrouvées (ou la fenêtre s’ouvre au centre si l’écran a changé — c’est acceptable).
- [ ] Onglet **About** : la version affichée correspond à celle que vous testez.

### A2 — Réglages par défaut (onglet Preferences)

**Identité et chemins**

- [ ] Onglet **Preferences** → section **Identity** : changez **Manufacturer** (ex. `QA Studio`).
- [ ] Cliquez **Generate** à côté des codes fabricant / plugin : des codes valides apparaissent.
- [ ] Section **Paths** : **Choose…** pour **Destination folder** → choisissez un dossier existant.
- [ ] **Choose…** pour **JUCE directory** → pointez vers votre installation JUCE.

**Sauvegarde automatique**

- [ ] Après une modification valide, un petit badge **Saved** clignote sur le champ.
- [ ] Fermez et rouvrez Luthier : vos valeurs **Preferences** sont toujours là.

**Couleur d’accent**

- [ ] En haut de **Preferences**, changez **Luthier Accent Color** : les onglets et boutons changent de couleur tout de suite (pendant que vous restez sur cet onglet).
- [ ] Passez sur l’onglet **Project** : le sélecteur peut encore afficher l’**ancienne** couleur — c’est normal (les deux onglets ne sont pas synchronisés en direct).
- [ ] Revenez sur **Preferences** : la nouvelle couleur y est bien sélectionnée.
- [ ] Fermez et rouvrez Luthier : la couleur choisie dans **Preferences** est toujours là ; les deux sélecteurs reprennent cette valeur au démarrage.
- [ ] **Create New Project** : le sélecteur **Project** reprend la couleur enregistrée dans **Preferences**.

**Export / import de profil**

- [ ] **Export Preferences…** → enregistrez `profil-qa-macos.json` (Bureau ou Documents).
- [ ] Message de succès dans la barre de message (type *Preferences exported to…*).
- [ ] Modifiez **Manufacturer** (ex. `Autre Nom`).
- [ ] **Import Preferences…** → choisissez `profil-qa-macos.json`.
- [ ] L’ancien profil revient (manufacturer, couleur, chemins).
- [ ] **Test fichier invalide :** importez un fichier texte renommé en `.json` → message d’erreur, **vos réglages précédents restent**.

### A3 — Créer un premier projet (onglet Project)

- [ ] **Create New Project** → message du type *New project — defaults from Preferences.*
- [ ] Les champs reprennent vos **Preferences** (fabricant, chemins, formats cochés).
- [ ] **Project name** : `TestLuthier`.
- [ ] **Display name** : `Test Luthier QA` (avec espaces — autorisé).
- [ ] Laissez ou ajustez **Version**, codes, **Destination folder**, **JUCE directory**.
- [ ] **Plugin Type** : **Instrument** (vous retesterez un autre type en A5).
- [ ] **Formats** : cochez **VST3** et **AU** (Audio Unit — spécifique Mac).
- [ ] **Generate Project** devient cliquable quand tout est valide.
- [ ] Cliquez **Generate Project** → message de succès avec le chemin du dossier créé.
- [ ] Dans le **Finder** : le dossier `TestLuthier` contient `CMakeLists.txt`, `Source/`, `.luthier.json`, `README.md`.

**Validations (le bouton reste grisé tant que c’est invalide)**

- [ ] **Project name** vide ou commençant par un chiffre → erreur affichée.
- [ ] Tous les formats décochés → **Generate Project** désactivé.
- [ ] **Manufacturer code** en minuscules partout → erreur (il faut une majuscule puis des minuscules).

### A4 — Rouvrir et modifier un projet

- [ ] Modifiez **Version** (ex. `1.0.1`) **sans** générer.
- [ ] **Create New Project** → boîte de confirmation → **No** : vos changements restent ; refaites → **Yes** : formulaire réinitialisé.
- [ ] **Open Project…** → dossier `TestLuthier`.
- [ ] Message *Loaded TestLuthier from…* et champs cohérents avec le projet.
- [ ] Changez **Display name** → **Generate Project** → confirmez l’écrasement si demandé → succès.
- [ ] Rouvrez le projet : **Display name** et **Version** reflètent vos changements.
- [ ] Déplacez `TestLuthier` ailleurs sur le disque → **Open Project…** au nouvel emplacement → **Destination folder** mis à jour.
- [ ] **Open Project…** sur un dossier qui n’est **pas** un projet Luthier → message d’erreur clair, pas de plantage.

### A5 — Variantes de projet

- [ ] **Create New Project** → **Plugin Type** : **Audio Effect** → `TestLuthierFX` → **Generate Project** → OK.
- [ ] **Create New Project** → **VST3** seul (décochez **Standalone**) → `TestLuthierVST3` → OK.
- [ ] **Compilation** → **Preprocessor defs** : `QA_FLAG=1` → projet `TestLuthierDefs` → rouvrez : la ligne est toujours là.
- [ ] Projet avec **AU** coché → génération OK.

### A6 — Dossier central des binaires (optionnel)

- [ ] Section **Artefacts** : cochez **Copy to central artefacts folder**.
- [ ] Chemin **macOS** : **Choose…** (ex. `~/Documents/ArtefactsQA`).
- [ ] Champs **Windows** et **Linux** : saisissez des chemins plausibles pour plus tard (ex. `D:/ArtefactsQA`, `/home/vous/ArtefactsQA`).
- [ ] Regénérez `TestLuthier` → pas d’erreur de validation.

### A7 — Modèles de code (onglet Templates)

- [ ] Liste des fichiers : `PluginProcessor.cpp`, `.gitignore`, etc.
- [ ] `PluginProcessor.cpp` → commentaire `// QA override macOS` → **Save override**.
- [ ] **Create New Project** → `TestLuthierTemplate` → **Generate Project** → commentaire visible dans `Source/PluginProcessor.cpp`.
- [ ] **Reset to default** → regénération : le commentaire disparaît des nouveaux projets.
- [ ] **Load from file…** → fichier `.cpp` externe → **Save override** pour conserver.
- [ ] Fichier illisible ou énorme → message d’erreur ou comportement propre, pas de plantage.

### A8 — Trois réglages ne se mélangent pas

- [ ] **Preferences** : `Manufacturer` = `Profil Global`.
- [ ] **Project** ouvert sur `TestLuthier` : le manufacturer du projet peut différer — c’est normal.
- [ ] Changez **Preferences** → **Project** inchangé.
- [ ] **Import Preferences…** (`Import Test`) → **Project** inchangé.
- [ ] **Create New Project** → formulaire reprend `Import Test`.
- [ ] Changements **Templates** visibles dans un projet existant seulement après **Generate Project**.

### A9 — Build CMake (optionnel)

> Seulement si Xcode ou CMake + compilateur sont installés.

- [ ] Ouvrez le dossier généré (Xcode, VS Code, etc.).
- [ ] Suivez le `README.md` du projet : configuration + build.
- [ ] Résultat : ☐ OK ☐ échec (toolchain) ☐ non testé

---

## B — Windows

**Date :** _______________  
**Version Luthier (onglet About) :** _______________  
**Install :** ☐ application autonome (`Luthier.exe`) ☐ depuis les sources

### B1 — Premier lancement et fenêtre

- [ ] Luthier s’ouvre sans plantage (SmartScreen possible : **Informations complémentaires** → exécuter pour un build local).
- [ ] Vous voyez les quatre onglets : **Project**, **Preferences**, **Templates**, **About**.
- [ ] L’onglet **Project** est actif au démarrage.
- [ ] Redimensionnez la fenêtre, fermez Luthier, rouvrez : la taille et la position sont **à peu près** retrouvées (ou la fenêtre s’ouvre au centre si l’écran a changé — c’est acceptable).
- [ ] Onglet **About** : la version affichée correspond à celle que vous testez.

### B2 — Réglages par défaut (onglet Preferences)

**Identité et chemins**

- [ ] Onglet **Preferences** → section **Identity** : changez **Manufacturer** (ex. `QA Studio`).
- [ ] Cliquez **Generate** à côté des codes fabricant / plugin : des codes valides apparaissent.
- [ ] Section **Paths** : **Choose…** pour **Destination folder** → choisissez un dossier existant.
- [ ] **Choose…** pour **JUCE directory** → pointez vers votre installation JUCE.
- [ ] En quittant un champ de chemin, les `\` deviennent des `/` à l’affichage (normal sur Windows).

**Sauvegarde automatique**

- [ ] Après une modification valide, un petit badge **Saved** clignote sur le champ.
- [ ] Fermez et rouvrez Luthier : vos valeurs **Preferences** sont toujours là.

**Couleur d’accent**

- [ ] En haut de **Preferences**, changez **Luthier Accent Color** : les onglets et boutons changent de couleur tout de suite (pendant que vous restez sur cet onglet).
- [ ] Passez sur l’onglet **Project** : le sélecteur peut encore afficher l’**ancienne** couleur — c’est normal (les deux onglets ne sont pas synchronisés en direct).
- [ ] Revenez sur **Preferences** : la nouvelle couleur y est bien sélectionnée.
- [ ] Fermez et rouvrez Luthier : la couleur choisie dans **Preferences** est toujours là ; les deux sélecteurs reprennent cette valeur au démarrage.
- [ ] **Create New Project** : le sélecteur **Project** reprend la couleur enregistrée dans **Preferences**.

**Export / import de profil**

- [ ] **Export Preferences…** → enregistrez `profil-qa-windows.json`.
- [ ] Message de succès dans la barre de message (type *Preferences exported to…*).
- [ ] Modifiez **Manufacturer** (ex. `Autre Nom`).
- [ ] **Import Preferences…** → choisissez `profil-qa-windows.json`.
- [ ] L’ancien profil revient (manufacturer, couleur, chemins).
- [ ] **Test fichier invalide :** importez un fichier texte renommé en `.json` → message d’erreur, **vos réglages précédents restent**.

### B3 — Créer un premier projet (onglet Project)

- [ ] **Create New Project** → message du type *New project — defaults from Preferences.*
- [ ] Les champs reprennent vos **Preferences** (fabricant, chemins, formats cochés).
- [ ] **Project name** : `TestLuthier`.
- [ ] **Display name** : `Test Luthier QA` (avec espaces — autorisé).
- [ ] Laissez ou ajustez **Version**, codes, **Destination folder**, **JUCE directory**.
- [ ] **Plugin Type** : **Instrument** (vous retesterez un autre type en B5).
- [ ] **Formats** : cochez **VST3** (et **Standalone** si vous voulez) ; **AU** peut rester coché pour un usage futur sur Mac — la génération ne doit **pas** échouer.
- [ ] **Generate Project** devient cliquable quand tout est valide.
- [ ] Cliquez **Generate Project** → message de succès avec le chemin du dossier créé.
- [ ] Dans l’**Explorateur de fichiers** : le dossier `TestLuthier` contient `CMakeLists.txt`, `Source/`, `.luthier.json`, `README.md`.

**Validations (le bouton reste grisé tant que c’est invalide)**

- [ ] **Project name** vide ou commençant par un chiffre → erreur affichée.
- [ ] Tous les formats décochés → **Generate Project** désactivé.
- [ ] **Manufacturer code** en minuscules partout → erreur (il faut une majuscule puis des minuscules).

### B4 — Rouvrir et modifier un projet

- [ ] Modifiez **Version** (ex. `1.0.1`) **sans** générer.
- [ ] **Create New Project** → boîte de confirmation → **No** : vos changements restent ; refaites → **Yes** : formulaire réinitialisé.
- [ ] **Open Project…** → dossier `TestLuthier`.
- [ ] Message *Loaded TestLuthier from…* et champs cohérents avec le projet.
- [ ] Changez **Display name** → **Generate Project** → confirmez l’écrasement si demandé → succès.
- [ ] Rouvrez le projet : **Display name** et **Version** reflètent vos changements.
- [ ] Déplacez `TestLuthier` ailleurs sur le disque → **Open Project…** au nouvel emplacement → **Destination folder** mis à jour.
- [ ] **Open Project…** sur un dossier qui n’est **pas** un projet Luthier → message d’erreur clair, pas de plantage.

### B5 — Variantes de projet

- [ ] **Create New Project** → **Plugin Type** : **Audio Effect** → `TestLuthierFX` → **Generate Project** → OK.
- [ ] **Create New Project** → **VST3** seul (décochez **Standalone**) → `TestLuthierVST3` → OK.
- [ ] **Compilation** → **Preprocessor defs** : `QA_FLAG=1` → projet `TestLuthierDefs` → rouvrez : la ligne est toujours là.
- [ ] **AU** coché (même si vous ne builderez pas sur Mac) → génération OK quand même.

### B6 — Dossier central des binaires (optionnel)

- [ ] Section **Artefacts** : cochez **Copy to central artefacts folder**.
- [ ] Chemin **Windows** : **Choose…** (ex. `C:/Users/Vous/Documents/ArtefactsQA`).
- [ ] Champs **macOS** et **Linux** : saisissez des chemins plausibles (ex. `/Users/vous/Documents/ArtefactsQA`, `/home/vous/ArtefactsQA`).
- [ ] Regénérez `TestLuthier` → pas d’erreur de validation.

### B7 — Modèles de code (onglet Templates)

- [ ] Liste des fichiers : `PluginProcessor.cpp`, `.gitignore`, etc.
- [ ] `PluginProcessor.cpp` → commentaire `// QA override Windows` → **Save override**.
- [ ] **Create New Project** → `TestLuthierTemplate` → **Generate Project** → commentaire visible dans `Source/PluginProcessor.cpp`.
- [ ] **Reset to default** → regénération : le commentaire disparaît des nouveaux projets.
- [ ] **Load from file…** → fichier `.cpp` externe → **Save override** pour conserver.
- [ ] Fichier illisible ou énorme → message d’erreur ou comportement propre, pas de plantage.

### B8 — Trois réglages ne se mélangent pas

- [ ] **Preferences** : `Manufacturer` = `Profil Global`.
- [ ] **Project** ouvert sur `TestLuthier` : le manufacturer du projet peut différer — c’est normal.
- [ ] Changez **Preferences** → **Project** inchangé.
- [ ] **Import Preferences…** (`Import Test`) → **Project** inchangé.
- [ ] **Create New Project** → formulaire reprend `Import Test`.
- [ ] Changements **Templates** visibles dans un projet existant seulement après **Generate Project**.

### B9 — Build CMake (optionnel)

> Seulement si Visual Studio, CMake ou Ninja sont installés.

- [ ] Ouvrez le dossier généré (Visual Studio, VS Code, etc.).
- [ ] Suivez le `README.md` du projet : configuration + build.
- [ ] Résultat : ☐ OK ☐ échec (toolchain) ☐ non testé

---

## C — Linux

**Date :** _______________  
**Version Luthier (onglet About) :** _______________  
**Install :** ☐ application autonome ☐ depuis les sources (`chmod +x` sur l’exécutable si besoin)

### C1 — Premier lancement et fenêtre

- [ ] Luthier s’ouvre sans plantage.
- [ ] Vous voyez les quatre onglets : **Project**, **Preferences**, **Templates**, **About**.
- [ ] L’onglet **Project** est actif au démarrage.
- [ ] Redimensionnez la fenêtre, fermez Luthier, rouvrez : la taille et la position sont **à peu près** retrouvées (ou la fenêtre s’ouvre au centre si l’écran a changé — c’est acceptable).
- [ ] Onglet **About** : la version affichée correspond à celle que vous testez.

### C2 — Réglages par défaut (onglet Preferences)

**Identité et chemins**

- [ ] Onglet **Preferences** → section **Identity** : changez **Manufacturer** (ex. `QA Studio`).
- [ ] Cliquez **Generate** à côté des codes fabricant / plugin : des codes valides apparaissent.
- [ ] Section **Paths** : **Choose…** pour **Destination folder** → choisissez un dossier existant.
- [ ] **Choose…** pour **JUCE directory** → pointez vers votre installation JUCE.

**Sauvegarde automatique**

- [ ] Après une modification valide, un petit badge **Saved** clignote sur le champ.
- [ ] Fermez et rouvrez Luthier : vos valeurs **Preferences** sont toujours là.

**Couleur d’accent**

- [ ] En haut de **Preferences**, changez **Luthier Accent Color** : les onglets et boutons changent de couleur tout de suite (pendant que vous restez sur cet onglet).
- [ ] Passez sur l’onglet **Project** : le sélecteur peut encore afficher l’**ancienne** couleur — c’est normal (les deux onglets ne sont pas synchronisés en direct).
- [ ] Revenez sur **Preferences** : la nouvelle couleur y est bien sélectionnée.
- [ ] Fermez et rouvrez Luthier : la couleur choisie dans **Preferences** est toujours là ; les deux sélecteurs reprennent cette valeur au démarrage.
- [ ] **Create New Project** : le sélecteur **Project** reprend la couleur enregistrée dans **Preferences**.

**Export / import de profil**

- [ ] **Export Preferences…** → enregistrez `profil-qa-linux.json`.
- [ ] Message de succès dans la barre de message (type *Preferences exported to…*).
- [ ] Modifiez **Manufacturer** (ex. `Autre Nom`).
- [ ] **Import Preferences…** → choisissez `profil-qa-linux.json`.
- [ ] L’ancien profil revient (manufacturer, couleur, chemins).
- [ ] **Test fichier invalide :** importez un fichier texte renommé en `.json` → message d’erreur, **vos réglages précédents restent**.

### C3 — Créer un premier projet (onglet Project)

- [ ] **Create New Project** → message du type *New project — defaults from Preferences.*
- [ ] Les champs reprennent vos **Preferences** (fabricant, chemins, formats cochés).
- [ ] **Project name** : `TestLuthier`.
- [ ] **Display name** : `Test Luthier QA` (avec espaces — autorisé).
- [ ] Laissez ou ajustez **Version**, codes, **Destination folder**, **JUCE directory**.
- [ ] **Plugin Type** : **Instrument** (vous retesterez un autre type en C5).
- [ ] **Formats** : cochez **VST3** (et **Standalone** si vous voulez) ; **AU** peut rester coché pour un usage futur sur Mac — la génération ne doit **pas** échouer.
- [ ] **Generate Project** devient cliquable quand tout est valide.
- [ ] Cliquez **Generate Project** → message de succès avec le chemin du dossier créé.
- [ ] Dans le **gestionnaire de fichiers** : le dossier `TestLuthier` contient `CMakeLists.txt`, `Source/`, `.luthier.json`, `README.md`.

**Validations (le bouton reste grisé tant que c’est invalide)**

- [ ] **Project name** vide ou commençant par un chiffre → erreur affichée.
- [ ] Tous les formats décochés → **Generate Project** désactivé.
- [ ] **Manufacturer code** en minuscules partout → erreur (il faut une majuscule puis des minuscules).

### C4 — Rouvrir et modifier un projet

- [ ] Modifiez **Version** (ex. `1.0.1`) **sans** générer.
- [ ] **Create New Project** → boîte de confirmation → **No** : vos changements restent ; refaites → **Yes** : formulaire réinitialisé.
- [ ] **Open Project…** → dossier `TestLuthier`.
- [ ] Message *Loaded TestLuthier from…* et champs cohérents avec le projet.
- [ ] Changez **Display name** → **Generate Project** → confirmez l’écrasement si demandé → succès.
- [ ] Rouvrez le projet : **Display name** et **Version** reflètent vos changements.
- [ ] Déplacez `TestLuthier` ailleurs sur le disque → **Open Project…** au nouvel emplacement → **Destination folder** mis à jour.
- [ ] **Open Project…** sur un dossier qui n’est **pas** un projet Luthier → message d’erreur clair, pas de plantage.

### C5 — Variantes de projet

- [ ] **Create New Project** → **Plugin Type** : **Audio Effect** → `TestLuthierFX` → **Generate Project** → OK.
- [ ] **Create New Project** → **VST3** seul (décochez **Standalone**) → `TestLuthierVST3` → OK.
- [ ] **Compilation** → **Preprocessor defs** : `QA_FLAG=1` → projet `TestLuthierDefs` → rouvrez : la ligne est toujours là.
- [ ] **AU** coché (même si vous ne builderez pas sur Mac) → génération OK quand même.

### C6 — Dossier central des binaires (optionnel)

- [ ] Section **Artefacts** : cochez **Copy to central artefacts folder**.
- [ ] Chemin **Linux** : **Choose…** (ex. `/home/vous/Documents/ArtefactsQA`).
- [ ] Champs **macOS** et **Windows** : saisissez des chemins plausibles (ex. `/Users/vous/Documents/ArtefactsQA`, `D:/ArtefactsQA`).
- [ ] Regénérez `TestLuthier` → pas d’erreur de validation.

### C7 — Modèles de code (onglet Templates)

- [ ] Liste des fichiers : `PluginProcessor.cpp`, `.gitignore`, etc.
- [ ] `PluginProcessor.cpp` → commentaire `// QA override Linux` → **Save override**.
- [ ] **Create New Project** → `TestLuthierTemplate` → **Generate Project** → commentaire visible dans `Source/PluginProcessor.cpp`.
- [ ] **Reset to default** → regénération : le commentaire disparaît des nouveaux projets.
- [ ] **Load from file…** → fichier `.cpp` externe → **Save override** pour conserver.
- [ ] Fichier illisible ou énorme → message d’erreur ou comportement propre, pas de plantage.

### C8 — Trois réglages ne se mélangent pas

- [ ] **Preferences** : `Manufacturer` = `Profil Global`.
- [ ] **Project** ouvert sur `TestLuthier` : le manufacturer du projet peut différer — c’est normal.
- [ ] Changez **Preferences** → **Project** inchangé.
- [ ] **Import Preferences…** (`Import Test`) → **Project** inchangé.
- [ ] **Create New Project** → formulaire reprend `Import Test`.
- [ ] Changements **Templates** visibles dans un projet existant seulement après **Generate Project**.

### C9 — Build CMake (optionnel)

> Seulement si CMake et un compilateur sont installés.

- [ ] Ouvrez le dossier généré (VS Code, CLion, etc.).
- [ ] Suivez le `README.md` du projet : configuration + build.
- [ ] Résultat : ☐ OK ☐ échec (toolchain) ☐ non testé

### Bilan Partie 1

| Bloc | Étapes 1–8 terminées | Étape 9 (optionnel) | Date |
|------|----------------------|---------------------|------|
| A — macOS | ☐ | ☐ | |
| B — Windows | ☐ | ☐ | |
| C — Linux | ☐ | ☐ | |

---

# Partie 2 — Parcours cross-plateforme

> **Objectif :** un même projet passe de macOS → Windows → Linux (ou autre ordre), via **Git** (commit, push, pull), avec des modifications Luthier sur chaque machine.  
> **Durée indicative :** 2 à 4 h selon vos installs.

## 2.1 — Préparation (une seule fois)

- [ ] Créez un dépôt Git **vide** en ligne (ou partagé sur clé USB réseau).
- [ ] Sur **chaque** machine, installez Luthier et JUCE (chemins **locaux** différents — c’est voulu).
- [ ] Décidez de l’ordre de travail, par exemple : **1. macOS → 2. Windows → 3. Linux**.

**Nom du projet partagé :** `VoyageLuthier`  
**Dépôt Git :** _______________________________________________

---

## 2.2 — Machine 1 (ex. macOS) — Création et premier commit

- [ ] Configurez **Preferences** (fabricant, destination, JUCE **local Mac**).
- [ ] **Create New Project**.
- [ ] **Project name** : `VoyageLuthier`.
- [ ] **Display name** : `Voyage Cross QA`.
- [ ] **Version** : `1.0.0`.
- [ ] Formats : **VST3** + **Standalone** ; **AU** aussi si machine 1 = Mac.
- [ ] **JUCE directory** : chemin JUCE **sur cette machine**.
- [ ] Section **Artefacts** : renseignez les **trois** chemins (Mac avec **Choose…**, Windows et Linux en saisie manuelle — chemins que vous utiliserez vraiment sur les autres OS).
- [ ] **Generate Project**.
- [ ] Vérifiez la présence de `.luthier.json` à la racine du projet.

### Git

- [ ] Dans le dossier `VoyageLuthier` : `git init` (si pas déjà fait).
- [ ] Vérifiez que `.gitignore` ignore les dossiers de build (contenu généré par Luthier).
- [ ] `git add .` → `git commit -m "Projet initial VoyageLuthier depuis macOS"` (message libre).
- [ ] Liez le dépôt distant → `git push`.

**Hash / note du commit :** _______________

---

## 2.3 — Machine 2 (ex. Windows) — Clone, réouverture, adaptation

- [ ] `git clone` (ou `git pull` si déjà cloné) du dépôt.
- [ ] Ouvrez Luthier → **Open Project…** → dossier `VoyageLuthier` cloné.
- [ ] **Destination folder** : parent correct sur Windows (mis à jour automatiquement à l’ouverture).
- [ ] **JUCE directory** : remplacez par le chemin JUCE **Windows** (obligatoire — le chemin Mac ne fonctionne pas ici).
- [ ] Vérifiez que **Project name**, **Display name**, **Version**, formats et options **Artefacts** sont bien revenus depuis `.luthier.json`.
- [ ] **Version** → `1.1.0`.
- [ ] **Display name** → `Voyage Cross QA Win`.
- [ ] **Generate Project** → succès (écrasement confirmé si demandé).

### Git

- [ ] `git status` : `.luthier.json` (et fichiers regénérés) modifiés.
- [ ] Commit : *« Version 1.1.0 — réglages Windows »*.
- [ ] Push vers le dépôt distant.

---

## 2.4 — Machine 3 (ex. Linux) — Pull, modification Templates + projet

- [ ] `git pull` — vous devez voir les changements de la machine 2.
- [ ] Luthier → **Open Project…** → `VoyageLuthier`.
- [ ] **JUCE directory** → chemin JUCE **Linux**.
- [ ] Onglet **Templates** → petit override (commentaire `// Linux QA` dans `PluginProcessor.h`) → **Save override** (reste **local** à cette installation Luthier — normal).
- [ ] **Project** → **Version** `1.2.0`, **Preprocessor defs** : ajoutez `LINUX_QA=1`.
- [ ] **Generate Project**.
- [ ] Vérifiez que le commentaire template apparaît dans `Source/PluginProcessor.h`.

### Git

- [ ] Commit **uniquement le projet** (pas les templates Luthier locaux) : `.luthier.json`, `CMakeLists.txt`, `Source/`, etc.
- [ ] Push.

---

## 2.5 — Retour machine 1 (ex. macOS) — Synchronisation finale

- [ ] `git pull`.
- [ ] **Open Project…** → `VoyageLuthier`.
- [ ] **Version** affichée : `1.2.0`.
- [ ] **Preprocessor defs** contient `LINUX_QA=1`.
- [ ] **JUCE directory** : remettez le chemin JUCE **Mac** (le chemin Linux/Windows ne doit pas rester si invalide sur Mac).
- [ ] **Generate Project** sans erreur.
- [ ] Changez **Display name** → `Voyage Cross QA Final` → générez → commit + push *« Finalisation Mac »*.

---

## 2.6 — Profils Preferences entre machines (hors Git)

Les réglages globaux Luthier **ne voyagent pas** avec le projet Git. Testez la procédure manuelle :

- [ ] Sur la machine 1 : **Export Preferences…** → `voyage-profil.json`.
- [ ] Transférez le fichier (cloud, clé USB, e-mail).
- [ ] Sur la machine 2 : **Import Preferences…** → le profil s’applique dans **Preferences** (couleur + chemins + fabricant) ; le sélecteur de l’onglet **Project** n’est pas mis à jour tant que vous ne faites pas **Create New Project**.
- [ ] Ajustez **JUCE directory** et **Destination folder** pour la machine 2 (chemins locaux).
- [ ] **Open Project…** sur `VoyageLuthier` : le **projet** n’a pas été écrasé par l’import (seul un **Create New Project** prendrait le profil entier).

---

## 2.7 — Cas limites cross-plateforme

- [ ] **Chemins dans `.luthier.json`** : ouvrez le fichier dans un éditeur de texte — les chemins utilisent des `/` même sur Windows.
- [ ] **Projet sans `.luthier.json`** (test archive) : copiez un vieux dossier ou renommez temporairement `.luthier.json` → **Open Project…** → Luthier tente de lire `CMakeLists.txt` (legacy) ou affiche une erreur claire si impossible.
- [ ] **Conflit Git** : sur deux machines, modifiez **Version** différemment sans pull → poussez/pull/remergez → rouvrez dans Luthier : le fichier `.luthier.json` final reflète l’état du dépôt.
- [ ] **Fichier prefs corrompu** (test avancé, une machine jetable) : sauvegardez `preferences.json`, remplacez son contenu par `{` → relancez Luthier → message d’avertissement dans la barre de message, valeurs par défaut ou secours — **pas** de plantage. Restaurez la sauvegarde après le test.

Emplacement des fichiers de config Luthier :

| Système | Dossier (approximatif) |
|---------|-------------------------|
| macOS | `~/Library/Preferences/Luthier/` |
| Windows | `%LOCALAPPDATA%\Luthier\` |
| Linux | `~/.config/Luthier/` |

---

## 2.8 — Récapitulatif cross-plateforme

| Étape | Machine | Version affichée | Display name | Git OK ? |
|-------|---------|------------------|--------------|----------|
| Création (2.2) | | 1.0.0 | Voyage Cross QA | |
| Après Windows (2.3) | | 1.1.0 | … Win | |
| Après Linux (2.4) | | 1.2.0 | (inchangé ou …) | |
| Final Mac (2.5) | | 1.2.0 | … Final | |

- [ ] Sur les **trois** OS, **Open Project…** sur la dernière révision Git donne un projet **cohérent** (même version, mêmes options — seuls les chemins JUCE/destination doivent être adaptés localement).
- [ ] Aucun plantage Luthier pendant tout le parcours de la Partie 2.

---

# Grille de suivi des problèmes

| # | OS | Section | Que faisiez-vous ? | Résultat attendu | Résultat obtenu | Gravité (bloquant / gênant / mineur) |
|---|----|---------|--------------------|------------------|-----------------|--------------------------------------|
| 1 | | | | | | |
| 2 | | | | | | |
| 3 | | | | | | |

**Gravité :**

- **Bloquant** — impossible de continuer le test.
- **Gênant** — contournement possible mais pénible.
- **Mineur** — cosmétique ou cas rare.

*Section :* indiquez par ex. `A3`, `B7`, `C2`, `2.4`, etc.

---

## Critères de fin de QA

La QA est **réussie** pour une release si :

- [ ] Les **trois** blocs de la Partie 1 sont entièrement cochés ([A — macOS](#a--macos), [B — Windows](#b--windows), [C — Linux](#c--linux)) sans bloquant.
- [ ] La Partie 2 (étapes 2.1 à 2.8) est complète sans bloquant (Git + réouverture sur au moins **deux** OS minimum ; idéal **trois**).
- [ ] Tous les bloquants documentés dans la grille ont un ticket ou une décision produit.

---

## Références

- [Manuel utilisateur (FR)](manuel-utilisateur.md)
- [User manual (EN)](user-manual.md)
