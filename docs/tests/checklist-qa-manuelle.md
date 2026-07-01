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

- [x] Luthier est installé (application autonome **ou** version lancée depuis les sources — gardez la **même façon** sur les trois OS si possible).
- [x] Vous avez une copie de **JUCE** quelque part sur le disque (dossier téléchargé ou cloné).
- [x] Vous savez où vous mettez vos projets (Bureau, Documents, etc.).
- [x] Pour la **Partie 2** : **Git** est installé et vous avez un dépôt vide (GitHub, GitLab, clé USB avec dépôt, etc.) pour synchroniser le projet entre machines.

### Conventions pour cette checklist

| Nom                   | Signification                                                                                           |
| --------------------- | ------------------------------------------------------------------------------------------------------- |
| **Projet test local** | Nom suggéré : `TestLuthier` — un projet créé uniquement sur une machine                                 |
| **Projet voyage**     | Nom suggéré : `VoyageLuthier` — le projet partagé entre OS via Git                                      |
| **Profil test**       | Fichier exporté par OS : `profil-qa-macos.json`, `profil-qa-windows.json`, `profil-qa-linux.json`       |
| **Barre de message**  | La bandeau en bas de la fenêtre (au-dessus des boutons) : message couleur d'accent = OK, rouge = erreur |

---

# Partie 1 — Tests sur chaque système

Chaque système a **son propre bloc** (A, B ou C) avec les mêmes étapes numérotées de 1 à 9. Cochez les cases **dans les trois blocs** avant de passer à la Partie 2.

Les étapes sont identiques d’un OS à l’autre ; seules les notes spécifiques (installation, chemins, formats) changent.

---

## A — macOS

**Date :** 2026-06-29
**Version Luthier (onglet About) :** 1.0.0
**Install :** ✅ application autonome (`Luthier.app`) ☐ depuis les sources

### A1 — Premier lancement et fenêtre

- [x] Luthier s’ouvre sans plantage (si l’app n’est pas signée : autorisation dans **Réglages système** si macOS le demande).
- [x] Vous voyez les quatre onglets : **Project**, **Preferences**, **Templates**, **About**.
- [x] L’onglet **Project** est actif au démarrage.
- [x] Redimensionnez la fenêtre, fermez Luthier, rouvrez : la taille et la position sont **à peu près** retrouvées (ou la fenêtre s’ouvre au centre si l’écran a changé — c’est acceptable).
- [x] Onglet **About** : la version affichée correspond à celle que vous testez.

### A2 — Réglages par défaut (onglet Preferences)

**Identité et chemins**

- [x] Onglet **Preferences** → section **Identity** : changez **Manufacturer** (ex. `QA Studio`).
- [x] Cliquez **Generate** à côté des codes fabricant / plugin : des codes valides apparaissent.
- [x] Section **Paths** : **Choose…** pour **Destination folder** → choisissez un dossier existant.
- [x] **Choose…** pour **JUCE directory** → pointez vers votre installation JUCE.

**Sauvegarde automatique**

- [x] Après une modification valide, un petit badge **Saved** clignote sur le champ.
- [x] Fermez et rouvrez Luthier : vos valeurs **Preferences** sont toujours là.

**Couleur d’accent**

- [x] En haut de **Preferences**, changez **Luthier Accent Color** : les onglets et boutons changent de couleur tout de suite (pendant que vous restez sur cet onglet).
- [x] Passez sur l’onglet **Project** : le sélecteur peut encore afficher l’**ancienne** couleur — c’est normal (les deux onglets ne sont pas synchronisés en direct).
- [x] Revenez sur **Preferences** : la nouvelle couleur y est bien sélectionnée.
- [x] Fermez et rouvrez Luthier : la couleur choisie dans **Preferences** est toujours là ; les deux sélecteurs reprennent cette valeur au démarrage.
- [x] **Create New Project** : le sélecteur **Project** reprend la couleur enregistrée dans **Preferences**.

**Export / import de profil**

- [x] **Export Preferences…** → enregistrez `profil-qa-macos.json` (Bureau ou Documents).
- [x] Message de succès dans la barre de message (type *Preferences exported to…*).

📌 **Note GD** : seul le nom du fichier JSON est mentionné dans le message, pas le chemin complet.

- [x] Modifiez **Manufacturer** (ex. `Autre Nom`).
- [x] **Import Preferences…** → choisissez `profil-qa-macos.json`.
- [x] L’ancien profil revient (manufacturer, couleur, chemins).
- [x] **Test fichier invalide :** importez un fichier texte renommé en `.json` → message d’erreur, **vos réglages précédents restent**.

### A3 — Créer un premier projet (onglet Project)

- [x] **Create New Project** → message du type *New project — defaults from Preferences.*
- [x] Les champs reprennent vos **Preferences** (fabricant, chemins, formats cochés).
- [x] **Project name** : `TestLuthier`.
- [x] **Display name** : `Test Luthier QA` (avec espaces — autorisé).
- [x] Laissez ou ajustez **Version**, codes, **Destination folder**, **JUCE directory**.
- [x] **Plugin Type** : **Instrument** (vous retesterez un autre type en A5).
- [x] **Formats** : cochez **VST3** et **AU** (Audio Unit — spécifique Mac).
- [x] **Generate Project** devient cliquable quand tout est valide.
- [x] Cliquez **Generate Project** → message de succès avec le chemin du dossier créé.
- [x] Dans le **Finder** : le dossier `TestLuthier` contient `CMakeLists.txt`, `Source/`, `.luthier.json`, `README.md`.

**Validations (le bouton reste grisé tant que c’est invalide)**

- [x] **Project name** vide ou commençant par un chiffre → erreur affichée.
- [x] Tous les formats décochés → **Generate Project** désactivé.
- [x] **Manufacturer code** en minuscules partout → erreur (il faut une majuscule puis des minuscules).

### A4 — Rouvrir et modifier un projet

- [x] Modifiez **Version** (ex. `1.0.2`) **sans** générer.
- [x] **Create New Project** → boîte de confirmation → **No** : vos changements restent ; refaites → **Yes** : formulaire réinitialisé.
- [x] **Open Project…** → dossier `TestLuthier`.
- [x] Message *Loaded TestLuthier from…* et champs cohérents avec le projet.
- [x] Changez **Display name** → **Generate Project** → confirmez l’écrasement si demandé → succès.
- [x] Rouvrez le projet : **Display name** et **Version** reflètent vos changements.
- [x] Déplacez `TestLuthier` ailleurs sur le disque → **Open Project…** au nouvel emplacement → **Destination folder** mis à jour.

📌 **Note GD** : fonctionne en déplaçant le projet dans un dossier "été 2026", mais message rouge indiquant que les caractères sont interdits, or ils sont valides ici.

- [x] **Open Project…** sur un dossier qui n’est **pas** un projet Luthier → message d’erreur clair, pas de plantage.

📌 **Note GD** : la modale d'erreur indique que le dossier ne correspond pas à un projet de plugin JUCE, il faut changer cela en disant qu'il ne s'agit pas d'un projet Luthier.

### A5 — Variantes de projet

- [x] **Create New Project** → **Plugin Type** : **Audio Effect** → `TestLuthierFX` → **Generate Project** → OK.
- [x] **Create New Project** → **VST3** seul (décochez **Standalone**) → `TestLuthierVST3` → OK.
- [x] **Compilation** → **Preprocessor defs** : `QA_FLAG=1` → projet `TestLuthierDefs` → rouvrez : la ligne est toujours là.
- [x] Projet avec **AU** coché → génération OK.

### A6 — Dossier central des binaires (optionnel)

- [x] Section **Artefacts** : cochez **Copy to central artefacts folder**.
- [x] Chemin **macOS** : **Choose…** (ex. `~/Documents/ArtefactsQA`).
- [x] Champs **Windows** et **Linux** : saisissez des chemins plausibles pour plus tard (ex. `D:/ArtefactsQA`, `/home/vous/ArtefactsQA`).
- [x] Regénérez `TestLuthier` → pas d’erreur de validation.

### A7 — Modèles de code (onglet Templates)

- [x] Liste des fichiers : `PluginProcessor.cpp`, `.gitignore`, etc.
- [x] `PluginProcessor.cpp` → commentaire `// QA override macOS` → **Save override**.

📌 **Note GD** : Faudrait-il que le message "Override active — used for new projects" apparaisse plutôt dans la barre de messages, au lieu de sous l'éditeur de sources ?

- [x] **Create New Project** → `TestLuthierTemplate` → **Generate Project** → commentaire visible dans `Source/PluginProcessor.cpp`.
- [x] **Reset to default** → regénération : le commentaire disparaît des nouveaux projets.

📌 **Note GD** : est-ce que le clic sur **Reset to default** nécessite un clic sur **Save override** ?

- [x] **Load from file…** → fichier `.cpp` externe → **Save override** pour conserver.
- [x] Fichier illisible ou énorme → message d’erreur ou comportement propre, pas de plantage.

### A8 — Trois réglages ne se mélangent pas

- [x] **Preferences** : `Manufacturer` = `Profil Global`.
- [x] **Project** ouvert sur `TestLuthier` : le manufacturer du projet peut différer — c’est normal.
- [x] Changez **Preferences** → **Project** inchangé.
- [x] **Import Preferences…** (`Import Test`) → **Project** inchangé.
- [x] **Create New Project** → formulaire reprend `Import Test`.
- [x] Changements **Templates** visibles dans un projet existant seulement après **Generate Project**.

### A9 — Build CMake (optionnel)

> Seulement si Xcode ou CMake + compilateur sont installés.

- [x] Ouvrez le dossier généré (Xcode, VS Code, etc.).
- [x] Suivez le `README.md` du projet : configuration + build.
- [x] Résultat : ✅ OK ☐ échec (toolchain) ☐ non testé

---

## B — Windows

**Date :** 2026-06-29  
**Version Luthier (onglet About) :** 1.0.0  
**Install :** ✅ application autonome (`Luthier.exe`) ☐ depuis les sources

### B1 — Premier lancement et fenêtre

- [x] Luthier s’ouvre sans plantage (SmartScreen possible : **Informations complémentaires** → exécuter pour un build local).
- [x] Vous voyez les quatre onglets : **Project**, **Preferences**, **Templates**, **About**.
- [x] L’onglet **Project** est actif au démarrage.
- [x] Redimensionnez la fenêtre, fermez Luthier, rouvrez : la taille et la position sont **à peu près** retrouvées (ou la fenêtre s’ouvre au centre si l’écran a changé — c’est acceptable).
- [x] Onglet **About** : la version affichée correspond à celle que vous testez.

### B2 — Réglages par défaut (onglet Preferences)

**Identité et chemins**

- [x] Onglet **Preferences** → section **Identity** : changez **Manufacturer** (ex. `QA Studio`).
- [x] Cliquez **Generate** à côté des codes fabricant / plugin : des codes valides apparaissent.
- [x] Section **Paths** : **Choose…** pour **Destination folder** → choisissez un dossier existant.

📌 **Note GD** : j'ai pointé vers mon dossier Téléchargements, un message d'erreur m'indique que les accents sont interdits > il faut changer cela, les noms accentués de dossiers (et même fichiers) sont valides.

- [x] **Choose…** pour **JUCE directory** → pointez vers votre installation JUCE.
- [x] En quittant un champ de chemin, les `\` deviennent des `/` à l’affichage (normal sur Windows).

📌 **Note GD** : je vois en fait directement des `/`.

**Sauvegarde automatique**

- [x] Après une modification valide, un petit badge **Saved** clignote sur le champ.
- [x] Fermez et rouvrez Luthier : vos valeurs **Preferences** sont toujours là.

**Couleur d’accent**

- [x] En haut de **Preferences**, changez **Luthier Accent Color** : les onglets et boutons changent de couleur tout de suite (pendant que vous restez sur cet onglet).
- [x] Passez sur l’onglet **Project** : le sélecteur peut encore afficher l’**ancienne** couleur — c’est normal (les deux onglets ne sont pas synchronisés en direct).
- [x] Revenez sur **Preferences** : la nouvelle couleur y est bien sélectionnée.
- [x] Fermez et rouvrez Luthier : la couleur choisie dans **Preferences** est toujours là ; les deux sélecteurs reprennent cette valeur au démarrage.
- [x] **Create New Project** : le sélecteur **Project** reprend la couleur enregistrée dans **Preferences**.

**Export / import de profil**

- [x] **Export Preferences…** → enregistrez `profil-qa-windows.json`.
- [x] Message de succès dans la barre de message (type *Preferences exported to…*).

📌 **Note GD** : seul le nom du fichier JSON est mentionné dans le message, pas le chemin complet.

- [x] Modifiez **Manufacturer** (ex. `Autre Nom`).
- [x] **Import Preferences…** → choisissez `profil-qa-windows.json`.
- [x] L’ancien profil revient (manufacturer, couleur, chemins).
- [x] **Test fichier invalide :** importez un fichier texte renommé en `.json` → message d’erreur, **vos réglages précédents restent**.

### B3 — Créer un premier projet (onglet Project)

- [x] **Create New Project** → message du type *New project — defaults from Preferences.*
- [x] Les champs reprennent vos **Preferences** (fabricant, chemins, formats cochés).
- [x] **Project name** : `TestLuthier`.
- [x] **Display name** : `Test Luthier QA` (avec espaces — autorisé).
- [x] Laissez ou ajustez **Version**, codes, **Destination folder**, **JUCE directory**.
- [x] **Plugin Type** : **Instrument** (vous retesterez un autre type en B5).
- [x] **Formats** : cochez **VST3** (et **Standalone** si vous voulez) ; **AU** peut rester coché pour un usage futur sur Mac — la génération ne doit **pas** échouer.
- [x] **Generate Project** devient cliquable quand tout est valide.
- [x] Cliquez **Generate Project** → message de succès avec le chemin du dossier créé.
- [x] Dans l’**Explorateur de fichiers** : le dossier `TestLuthier` contient `CMakeLists.txt`, `Source/`, `.luthier.json`, `README.md`.

**Validations (le bouton reste grisé tant que c’est invalide)**

- [x] **Project name** vide ou commençant par un chiffre → erreur affichée.
- [x] Tous les formats décochés → **Generate Project** désactivé.
- [x] **Manufacturer code** en minuscules partout → erreur (il faut une majuscule puis des minuscules).

### B4 — Rouvrir et modifier un projet

- [x] Modifiez **Version** (ex. `1.0.2`) **sans** générer.
- [x] **Create New Project** → boîte de confirmation → **No** : vos changements restent ; refaites → **Yes** : formulaire réinitialisé.

📌 **Note GD** : le bouton Yes est à gauche et No à droite dans la modale, sous macOS c'est le contraire : je préfère l'ordre d'affichage macOS

- [x] **Open Project…** → dossier `TestLuthier`.

📌 **Note GD** : le chemin dans le message utilisateur utilise des anti-slashes au lieu de slashes, il faut corriger cela pour rester homogène avec le reste de l'app.

- [x] Message *Loaded TestLuthier from…* et champs cohérents avec le projet.
- [x] Changez **Display name** → **Generate Project** → confirmez l’écrasement si demandé → succès.

📌 **Note GD** : ici aussi l'ordre des boutons Yes et No doivent être inversés. Aucun bouton n'est pré-sélectionné par défaut.

- [x] Rouvrez le projet : **Display name** et **Version** reflètent vos changements.
- [x] Déplacez `TestLuthier` ailleurs sur le disque → **Open Project…** au nouvel emplacement → **Destination folder** mis à jour.

📌 **Note GD** : fonctionne en déplaçant le projet dans Téléchargements, mais message rouge indiquant que les caractères sont interdits, or ils sont valides ici.

- [x] **Open Project…** sur un dossier qui n’est **pas** un projet Luthier → message d’erreur clair, pas de plantage.

📌 **Note GD** : la modale d'erreur indique que le dossier ne correspond pas à un projet de plugin JUCE, il faut changer cela en disant qu'il ne s'agit pas d'un projet Luthier.

### B5 — Variantes de projet

- [x] **Create New Project** → **Plugin Type** : **Audio Effect** → `TestLuthierFX` → **Generate Project** → OK.
- [x] **Create New Project** → **VST3** seul (décochez **Standalone**) → `TestLuthierVST3` → OK.
- [x] **Compilation** → **Preprocessor defs** : `QA_FLAG=1` → projet `TestLuthierDefs` → rouvrez : la ligne est toujours là.
- [x] **AU** coché (même si vous ne builderez pas sur Mac) → génération OK quand même.

### B6 — Dossier central des binaires (optionnel)

- [x] Section **Artefacts** : cochez **Copy to central artefacts folder**.
- [x] Chemin **Windows** : **Choose…** (ex. `C:/Users/Vous/Documents/ArtefactsQA`).
- [x] Champs **macOS** et **Linux** : saisissez des chemins plausibles (ex. `/Users/vous/Documents/ArtefactsQA`, `/home/vous/ArtefactsQA`).
- [x] Regénérez `TestLuthier` → pas d’erreur de validation.

### B7 — Modèles de code (onglet Templates)

- [x] Liste des fichiers : `PluginProcessor.cpp`, `.gitignore`, etc.
- [x] `PluginProcessor.cpp` → commentaire `// QA override Windows` → **Save override**.

📌 **Note GD** : Faudrait-il que le message "Override active — used for new projects" apparaisse plutôt dans la barre de messages, au lieu de sous l'éditeur de sources ?

- [x] **Create New Project** → `TestLuthierTemplate` → **Generate Project** → commentaire visible dans `Source/PluginProcessor.cpp`.
- [x] **Reset to default** → regénération : le commentaire disparaît des nouveaux projets.

📌 **Note GD** : est-ce que le clic sur **Reset to default** nécessite un clic sur **Save override** ?

- [x] **Load from file…** → fichier `.cpp` externe → **Save override** pour conserver.
- [x] Fichier illisible ou énorme → message d’erreur ou comportement propre, pas de plantage.

### B8 — Trois réglages ne se mélangent pas

- [x] **Preferences** : `Manufacturer` = `Profil Global`.
- [x] **Project** ouvert sur `TestLuthier` : le manufacturer du projet peut différer — c’est normal.
- [x] Changez **Preferences** → **Project** inchangé.
- [x] **Import Preferences…** (`Import Test`) → **Project** inchangé.
- [x] **Create New Project** → formulaire reprend `Import Test`.
- [x] Changements **Templates** visibles dans un projet existant seulement après **Generate Project**.

### B9 — Build CMake (optionnel)

> Seulement si Visual Studio, CMake ou Ninja sont installés.

- [x] Ouvrez le dossier généré (Visual Studio, VS Code, etc.).
- [x] Suivez le `README.md` du projet : configuration + build.
- [x] Résultat : ✅ OK ☐ échec (toolchain) ☐ non testé

---

## C — Linux

**Date :** 2026-06-29  
**Install :** ✅ application autonome ☐ depuis les sources (`chmod +x` sur l’exécutable si besoin)

### C1 — Premier lancement et fenêtre

- [x] Luthier s’ouvre sans plantage.

📌 **Note GD** : l'icône de l'app est générique, ce n'est pas celle de Luthier.

- [x] Vous voyez les quatre onglets : **Project**, **Preferences**, **Templates**, **About**.
- [x] L’onglet **Project** est actif au démarrage.
- [x] Redimensionnez la fenêtre, fermez Luthier, rouvrez : la taille et la position sont **à peu près** retrouvées (ou la fenêtre s’ouvre au centre si l’écran a changé — c’est acceptable).

📌 **Note GD** : sous Linux, la position et la taille sont assez approximatives au relancement de l'app...

- [x] Onglet **About** : la version affichée correspond à celle que vous testez.

### C2 — Réglages par défaut (onglet Preferences)

**Identité et chemins**

- [x] Onglet **Preferences** → section **Identity** : changez **Manufacturer** (ex. `QA Studio`).
- [x] Cliquez **Generate** à côté des codes fabricant / plugin : des codes valides apparaissent.
- [x] Section **Paths** : **Choose…** pour **Destination folder** → choisissez un dossier existant.

📌 **Note GD** : j'ai opté pour un dossier "Desktop/été 2026", mais message rouge indiquant que les caractères sont interdits, or ils sont valides ici.

- [x] **Choose…** pour **JUCE directory** → pointez vers votre installation JUCE.

**Sauvegarde automatique**

- [x] Après une modification valide, un petit badge **Saved** clignote sur le champ.
- [x] Fermez et rouvrez Luthier : vos valeurs **Preferences** sont toujours là.

**Couleur d’accent**

- [x] En haut de **Preferences**, changez **Luthier Accent Color** : les onglets et boutons changent de couleur tout de suite (pendant que vous restez sur cet onglet).
- [x] Passez sur l’onglet **Project** : le sélecteur peut encore afficher l’**ancienne** couleur — c’est normal (les deux onglets ne sont pas synchronisés en direct).
- [x] Revenez sur **Preferences** : la nouvelle couleur y est bien sélectionnée.
- [x] Fermez et rouvrez Luthier : la couleur choisie dans **Preferences** est toujours là ; les deux sélecteurs reprennent cette valeur au démarrage.
- [x] **Create New Project** : le sélecteur **Project** reprend la couleur enregistrée dans **Preferences**.

**Export / import de profil**

- [x] **Export Preferences…** → enregistrez `profil-qa-linux.json`.
- [x] Message de succès dans la barre de message (type *Preferences exported to…*).

📌 **Note GD** : le message indique le nom de fichier JSON mais pas le chemin complet.

- [x] Modifiez **Manufacturer** (ex. `Autre Nom`).
- [x] **Import Preferences…** → choisissez `profil-qa-linux.json`.
- [x] L’ancien profil revient (manufacturer, couleur, chemins).
- [x] **Test fichier invalide :** importez un fichier texte renommé en `.json` → message d’erreur, **vos réglages précédents restent**.

### C3 — Créer un premier projet (onglet Project)

- [x] **Create New Project** → message du type *New project — defaults from Preferences.*
- [x] Les champs reprennent vos **Preferences** (fabricant, chemins, formats cochés).
- [x] **Project name** : `TestLuthier`.
- [x] **Display name** : `Test Luthier QA` (avec espaces — autorisé).
- [x] Laissez ou ajustez **Version**, codes, **Destination folder**, **JUCE directory**.
- [x] **Plugin Type** : **Instrument** (vous retesterez un autre type en C5).
- [x] **Formats** : cochez **VST3** (et **Standalone** si vous voulez) ; **AU** peut rester coché pour un usage futur sur Mac — la génération ne doit **pas** échouer.
- [x] **Generate Project** devient cliquable quand tout est valide.
- [x] Cliquez **Generate Project** → message de succès avec le chemin du dossier créé.
- [x] Dans le **gestionnaire de fichiers** : le dossier `TestLuthier` contient `CMakeLists.txt`, `Source/`, `.luthier.json`, `README.md`.

**Validations (le bouton reste grisé tant que c’est invalide)**

- [x] **Project name** vide ou commençant par un chiffre → erreur affichée.
- [x] Tous les formats décochés → **Generate Project** désactivé.
- [x] **Manufacturer code** en minuscules partout → erreur (il faut une majuscule puis des minuscules).

### C4 — Rouvrir et modifier un projet

- [x] Modifiez **Version** (ex. `1.0.2`) **sans** générer.
- [x] **Create New Project** → boîte de confirmation → **No** : vos changements restent ; refaites → **Yes** : formulaire réinitialisé.
- [x] **Open Project…** → dossier `TestLuthier`.
- [x] Message *Loaded TestLuthier from…* et champs cohérents avec le projet.
- [x] Changez **Display name** → **Generate Project** → confirmez l’écrasement si demandé → succès.
- [x] Rouvrez le projet : **Display name** et **Version** reflètent vos changements.
- [x] Déplacez `TestLuthier` ailleurs sur le disque → **Open Project…** au nouvel emplacement → **Destination folder** mis à jour.
- [x] **Open Project…** sur un dossier qui n’est **pas** un projet Luthier → message d’erreur clair, pas de plantage.

### C5 — Variantes de projet

- [x] **Create New Project** → **Plugin Type** : **Audio Effect** → `TestLuthierFX` → **Generate Project** → OK.
- [x] **Create New Project** → **VST3** seul (décochez **Standalone**) → `TestLuthierVST3` → OK.
- [x] **Compilation** → **Preprocessor defs** : `QA_FLAG=1` → projet `TestLuthierDefs` → rouvrez : la ligne est toujours là.
- [x] **AU** coché (même si vous ne builderez pas sur Mac) → génération OK quand même.

### C6 — Dossier central des binaires (optionnel)

- [x] Section **Artefacts** : cochez **Copy to central artefacts folder**.
- [x] Chemin **Linux** : **Choose…** (ex. `/home/vous/Documents/ArtefactsQA`).
- [x] Champs **macOS** et **Windows** : saisissez des chemins plausibles (ex. `/Users/vous/Documents/ArtefactsQA`, `D:/ArtefactsQA`).
- [x] Regénérez `TestLuthier` → pas d’erreur de validation.

### C7 — Modèles de code (onglet Templates)

- [x] Liste des fichiers : `PluginProcessor.cpp`, `.gitignore`, etc.
- [x] `PluginProcessor.cpp` → commentaire `// QA override Linux` → **Save override**.
- [x] **Create New Project** → `TestLuthierTemplate` → **Generate Project** → commentaire visible dans `Source/PluginProcessor.cpp`.
- [x] **Reset to default** → regénération : le commentaire disparaît des nouveaux projets.
- [x] **Load from file…** → fichier `.cpp` externe → **Save override** pour conserver.
- [x] Fichier illisible ou énorme → message d’erreur ou comportement propre, pas de plantage.

### C8 — Trois réglages ne se mélangent pas

- [x] **Preferences** : `Manufacturer` = `Profil Global`.
- [x] **Project** ouvert sur `TestLuthier` : le manufacturer du projet peut différer — c’est normal.
- [x] Changez **Preferences** → **Project** inchangé.
- [x] **Import Preferences…** (`Import Test`) → **Project** inchangé.
- [x] **Create New Project** → formulaire reprend `Import Test`.
- [x] Changements **Templates** visibles dans un projet existant seulement après **Generate Project**.

### C9 — Build CMake (optionnel)

> Seulement si CMake et un compilateur sont installés.

📌 **Note GD** : j'ai d'abord créé un nouveau projet puis j'ai généré. Bien que le dossier destination folder soit renseigné (Desktop), une fenêtre apparaît automatiquement me demandant de sélectionner un dossier pour ceci. On dirait un bug spécifique à Linux, je n'ai rien constaté de tel sous macOS et Windows. 

- [x] Ouvrez le dossier généré (VS Code, CLion, etc.).
- [x] Suivez le `README.md` du projet : configuration + build.
- [x] Résultat : ✅ OK ☐ échec (toolchain) ☐ non testé

### Bilan Partie 1

| Bloc        | Étapes 1–8 terminées | Étape 9 (optionnel) | Date |
| ----------- | -------------------- | ------------------- | ---- |
| A — macOS   | ☐                    | ☐                   |      |
| B — Windows | ☐                    | ☐                   |      |
| C — Linux   | ☐                    | ☐                   |      |

---

# Partie 2 — Parcours cross-plateforme

> **Objectif :** un même projet passe de macOS → Windows → Linux (ou autre ordre), via **Git** (commit, push, pull), avec des modifications Luthier sur chaque machine.  
> **Durée indicative :** 2 à 4 h selon vos installs.

## 2.1 — Préparation (une seule fois)

- [x] Créez un dépôt Git **vide** en ligne (ou partagé sur clé USB réseau).
- [x] Sur **chaque** machine, installez Luthier et JUCE (chemins **locaux** différents — c’est voulu).
- [x] Décidez de l’ordre de travail, par exemple : **1. macOS → 2. Windows → 3. Linux**.

**Nom du projet partagé :** `VoyageLuthier`  
**Dépôt Git :** https://github.com/tensquaresoftware/voyage-luthier

---

## 2.2 — Machine 1 (ex. macOS) — Création et premier commit

- [x] Configurez **Preferences** (fabricant, destination, JUCE **local Mac**).
- [x] **Create New Project**.
- [x] **Project name** : `VoyageLuthier`.
- [x] **Display name** : `Voyage Cross QA macOS`.
- [x] **Version** : `1.0.0`.
- [x] Formats : **VST3** + **Standalone** ; **AU** aussi si machine 1 = Mac.
- [x] **JUCE directory** : chemin JUCE **sur cette machine**.
- [x] Section **Artefacts** : renseignez les **trois** chemins (Mac avec **Choose…**, Windows et Linux en saisie manuelle — chemins que vous utiliserez vraiment sur les autres OS).
- [x] Activer copie vers dossiers système & dossiers artefacts
- [x] **Generate Project**.
- [x] Vérifiez la présence de `.luthier.json` à la racine du projet.

### Git

- [x] Dans le dossier `VoyageLuthier` : `git init` (si pas déjà fait).
- [x] Vérifiez que `.gitignore` ignore les dossiers de build (contenu généré par Luthier).
- [x] `git add .` → `git commit -m "Projet initial VoyageLuthier depuis macOS"` (message libre).
- [x] Liez le dépôt distant → `git push`.

**Hash / note du commit :** 2787d45 / "Initial commit: VoyageLuthier JUCE audio plugin project."

### Cursor

- [x] Compiler le projet sans erreurs ni avertissements
- [x] Lancer l'app autonome depuis Cursor sans crash
- [x] Charger les versions VST3/AU sans crash dans un DAW ou AudioPluginHost depuis le dossier système
- [x] Charger les versions VST3/AU/Standalone sans crash dans un DAW ou AudioPluginHost depuis le dossier artefacts

---

## 2.3 — Machine 2 (ex. Windows) — Clone, réouverture, adaptation

- [x] `git clone` (ou `git pull` si déjà cloné) du dépôt.
- [x] Ouvrez Luthier → **Open Project…** → dossier `VoyageLuthier` cloné.
- [x] **Destination folder** : parent correct sur Windows (mis à jour automatiquement à l’ouverture).
- [x] **JUCE directory** : remplacez par le chemin JUCE **Windows** (obligatoire — le chemin Mac ne fonctionne pas ici).
- [x] Vérifiez que **Project name**, **Display name**, **Version**, formats et options **Artefacts** sont bien revenus depuis `.luthier.json`.
- [x] **Version** → `1.1.0`.
- [x] **Display name** → `Voyage Cross QA Windows`.
- [x] **Generate Project** → succès (plus de message d'erreur WinError 5).

### Cursor

- [x] Compiler le projet sans erreurs ni avertissements
- [x] Lancer l'app autonome depuis Cursor sans crash
- [x] Charger la version VST3 sans crash dans un DAW ou AudioPluginHost depuis le dossier système
- [x] Charger les versions VST3/Standalone sans crash dans un DAW ou AudioPluginHost depuis le dossier artefacts

### Git

- [x] `git status` : `.luthier.json` (et fichiers regénérés) modifiés.
- [x] Commit : *« Version 1.1.0 — réglages Windows »*.
- [x] Push vers le dépôt distant.

---

## 2.4 — Machine 3 (ex. Linux) — Pull, modification Templates + projet

- [x] `git pull` — vous devez voir les changements de la machine 2.
- [x] Luthier → **Open Project…** → `VoyageLuthier`.
- [x] **JUCE directory** → chemin JUCE **Linux**.
- [x] Onglet **Templates** → petit override (commentaire `// Linux QA` dans `PluginProcessor.h`) → **Save override** (reste **local** à cette installation Luthier — normal).
- [x] **Project** → **Version** `1.2.0`, **Preprocessor defs** : ajoutez `LINUX_QA=1`.
- [x] **Generate Project**.
- [x] Vérifiez que le commentaire template apparaît dans `Source/PluginProcessor.h`.

### Cursor

- [x] Compiler le projet sans erreurs ni avertissements
- [x] Lancer l'app autonome depuis Cursor sans crash
- [x] Charger la version VST3 sans crash dans un DAW ou AudioPluginHost depuis le dossier système
- [x] Charger les versions VST3/Standalone sans crash dans un DAW ou AudioPluginHost depuis le dossier artefacts

### Git

- [x] Commit **uniquement le projet** (pas les templates Luthier locaux) : `.luthier.json`, `CMakeLists.txt`, `Source/`, etc.
- [x] Push.

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

- [x] Sur la machine 1 : **Export Preferences…** → `voyage-profil.json`.
- [x] Transférez le fichier (cloud, clé USB, e-mail).
- [x] Sur la machine 2 : **Import Preferences…** → le profil s’applique dans **Preferences** (couleur + chemins + fabricant) ; le sélecteur de l’onglet **Project** n’est pas mis à jour tant que vous ne faites pas **Create New Project**.
- [x] Ajustez **JUCE directory** et **Destination folder** pour la machine 2 (chemins locaux).
- [x] **Open Project…** sur `VoyageLuthier` : le **projet** n’a pas été écrasé par l’import (seul un **Create New Project** prendrait le profil entier).

---

## 2.7 — Cas limites cross-plateforme

- [x] **Chemins dans `.luthier.json`** : ouvrez le fichier dans un éditeur de texte — les chemins utilisent des `/` même sur Windows.
- [x] **Sidecar manquant** : générez un projet, renommez ou supprimez temporairement `.luthier.json` → **Open Project…** → message clair (fichier compagnon absent ou invalide), pas d’analyse CMake.
- [x] **Conflit Git** : sur deux machines, modifiez **Version** différemment sans pull → poussez/pull/remergez → rouvrez dans Luthier : le fichier `.luthier.json` final reflète l’état du dépôt.
- [ ] ❌ **Fichier prefs corrompu** (test avancé, une machine jetable) : sauvegardez `preferences.json`, remplacez son contenu par `{` → relancez Luthier → message d’avertissement dans la barre de message, valeurs par défaut ou secours — **pas** de plantage. Restaurez la sauvegarde après le test. GD : l'app plante sous macOS (pas testé sous Windows & Linux), au deuxième lancement elle se lance sans crash.

Emplacement des fichiers de config Luthier :

| Système | Dossier (approximatif)           |
| ------- | -------------------------------- |
| macOS   | `~/Library/Preferences/Luthier/` |
| Windows | `%LOCALAPPDATA%\Luthier\`        |
| Linux   | `~/.config/Luthier/`             |

---

## 2.8 — Récapitulatif cross-plateforme

| Étape               | Machine | Version affichée | Display name    | Git OK ? |
| ------------------- | ------- | ---------------- | --------------- | -------- |
| Création (2.2)      |         | 1.0.0            | Voyage Cross QA |          |
| Après Windows (2.3) |         | 1.1.0            | … Win           |          |
| Après Linux (2.4)   |         | 1.2.0            | (inchangé ou …) |          |
| Final Mac (2.5)     |         | 1.2.0            | … Final         |          |

- [x] Sur les **trois** OS, **Open Project…** sur la dernière révision Git donne un projet **cohérent** (même version, mêmes options — seuls les chemins JUCE/destination doivent être adaptés localement).
- [ ] ❌ Aucun plantage Luthier pendant tout le parcours de la Partie 2. GD : si, voir 2.7.

---

# Grille de suivi des problèmes

| #   | OS      | Section | Que faisiez-vous ? | Résultat attendu | Résultat obtenu | Gravité (bloquant / gênant / mineur) |
| --- | ------- | ------- | ------------------ | ---------------- | --------------- | ------------------------------------ |
| 1   | Windows | 2.3     | **Generate Project** sur `VoyageLuthier` cloné via Git | Régénération OK, `.git` intact | `[WinError 5] Accès refusé` sur `.git/objects/…` — Luthier tente de supprimer tout le dossier y compris `.git` ; objets Git en lecture seule sous Windows | **Bloquant** (fix en cours : `core/project_writer.py`) |
| 2   |         |         |                    |                  |                 |                                      |
| 3   |         |         |                    |                  |                 |                                      |

**Gravité :**

- **Bloquant** — impossible de continuer le test.
- **Gênant** — contournement possible mais pénible.
- **Mineur** — cosmétique ou cas rare.

*Section :* indiquez par ex. `A3`, `B7`, `C2`, `2.4`, etc.

---

## Critères de fin de QA

La QA est **réussie** pour une release si :

- [x] Les **trois** blocs de la Partie 1 sont entièrement cochés ([A — macOS](#a--macos), [B — Windows](#b--windows), [C — Linux](#c--linux)) sans bloquant.
- [x] La Partie 2 (étapes 2.1 à 2.8) est complète sans bloquant (Git + réouverture sur au moins **deux** OS minimum ; idéal **trois**).
- [x] Tous les bloquants documentés dans la grille ont un ticket ou une décision produit.

---

## Notes GD

### Partie 1

- Couleur rouge pour les erreurs : je souhaite un rouge plus vif / moins pastel.

- Lorsque je crée un nouveau projet valide, que je clique sur Generate Project puis que je clique sur Create New Project, une modale m'avertit que le projet n'a pas été sauvé, pour tant c'est ce Generate Project est censé faire, exact ?

- Dans les modales proposant des boutons Yes et No, je préfère les placer dans l'ordre No/Yes, pour les 3 OS. Il faudrait qu'il y ait toujours un bouton proposé par défaut, dans la couleur d'accent, défaut à adapter selon le contexte et le niveau de danger que représente l'opération.

---

## Références

- [Manuel utilisateur (FR)](../user/manuel-utilisateur.md)
- [User manual (EN)](../user/user-manual.md)
