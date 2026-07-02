================================================================================
LUTHIER {{VERSION}} — Linux
Ten Square Software
https://github.com/tensquaresoftware/luthier
================================================================================

A French version of this document is included below.
Une version française de ce fichier est disponible plus bas.


WHAT IS IN THIS ARCHIVE
-----------------------
This archive contains a Luthier/ folder with:
  • Luthier              — the application executable
  • _internal/           — templates, Qt libraries, and other bundled files

Keep the entire Luthier/ folder together. The Luthier executable alone will not
work.


INSTALLATION
------------
1. Unzip the archive to a folder of your choice (e.g. ~/Apps/Luthier).
2. Make the binary executable if needed:
     chmod +x Luthier/Luthier
3. Launch from a file manager or terminal:
     ./Luthier/Luthier

A graphical session (X11 or Wayland) is required for the GUI.


REQUIREMENTS
------------
• Linux x86_64 with a recent distribution.
• A JUCE SDK installed on your machine — Luthier does not bundle JUCE.
  Download from https://juce.com or clone https://github.com/juce-framework/JUCE
  Then set JUCE directory in Preferences → Workspace.


DOCUMENTATION
-------------
Full user manuals (also available as Luthier-{{VERSION}}-docs.zip on the release page):

  English : https://github.com/tensquaresoftware/luthier/blob/{{VERSION}}/docs/user/user-manual.md
  French  : https://github.com/tensquaresoftware/luthier/blob/{{VERSION}}/docs/user/manuel-utilisateur.md

Release page : https://github.com/tensquaresoftware/luthier/releases/tag/{{VERSION}}


VERIFY THE BUNDLE (OPTIONAL)
----------------------------
In a terminal:

  ./Luthier/Luthier --check

Exit code 0 means bundled templates are reachable.


LICENSE
-------
Luthier source code: MIT License.
Packaged build includes Qt (PySide6) under LGPLv3.
See THIRD-PARTY-NOTICES in the GitHub repository.


================================================================================
LUTHIER {{VERSION}} — Linux
Ten Square Software
https://github.com/tensquaresoftware/luthier
FRANÇAIS
================================================================================

CONTENU DE CETTE ARCHIVE
------------------------
Cette archive contient un dossier Luthier/ avec :
  • Luthier              — l'exécutable de l'application
  • _internal/           — modèles, bibliothèques Qt et autres fichiers embarqués

Conservez le dossier Luthier/ entier. L'exécutable seul ne fonctionnera pas.


INSTALLATION
------------
1. Décompressez le fichier zip dans un dossier de votre choix (ex. ~/Apps/Luthier).
2. Rendez le binaire exécutable si nécessaire :
     chmod +x Luthier/Luthier
3. Lancez depuis le gestionnaire de fichiers ou le terminal :
     ./Luthier/Luthier

Une session graphique (X11 ou Wayland) est requise pour l'interface.


PRÉREQUIS
---------
• Linux x86_64 avec une distribution récente.
• Un SDK JUCE installé sur votre machine — Luthier n'inclut pas JUCE.
  Téléchargez-le sur https://juce.com ou clonez https://github.com/juce-framework/JUCE
  Puis renseignez JUCE directory dans Preferences → Workspace.


DOCUMENTATION
-------------
Manuels complets (également dans Luthier-{{VERSION}}-docs.zip sur la page de release) :

  Anglais : https://github.com/tensquaresoftware/luthier/blob/{{VERSION}}/docs/user/user-manual.md
  Français : https://github.com/tensquaresoftware/luthier/blob/{{VERSION}}/docs/user/manuel-utilisateur.md

Page de release : https://github.com/tensquaresoftware/luthier/releases/tag/{{VERSION}}


VÉRIFIER LE BUNDLE (OPTIONNEL)
------------------------------
Dans un terminal :

  ./Luthier/Luthier --check

Code de sortie 0 = les modèles embarqués sont accessibles.


LICENCE
-------
Code source Luthier : licence MIT.
Le build empaqueté inclut Qt (PySide6) sous LGPLv3.
Voir THIRD-PARTY-NOTICES dans le dépôt GitHub.
