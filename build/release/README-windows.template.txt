================================================================================
LUTHIER {{VERSION}} — Windows
Ten Square Software
https://github.com/tensquaresoftware/luthier
================================================================================

A French version of this document is included below.
Une version française de ce fichier est disponible plus bas.


WHAT IS IN THIS ARCHIVE
-----------------------
This archive contains a Luthier\ folder with:
  • Luthier.exe          — the application
  • _internal\           — templates, Qt libraries, and other bundled files

Keep the entire Luthier\ folder together. Luthier.exe alone will not work.


INSTALLATION
------------
1. Unzip the archive to a folder of your choice (e.g. C:\Apps\Luthier).
2. Run Luthier\Luthier.exe.
3. Optional: pin Luthier.exe to the taskbar or create a desktop shortcut.


FIRST RUN (UNSIGNED BUILD)
--------------------------
Windows SmartScreen may warn on first launch for an unsigned build.

If you see a blue warning screen:
  More info → Run anyway

Windows Defender may scan files on first start — a short delay is normal, not
a failure.


REQUIREMENTS
------------
• Windows 10 or later (64-bit).
• A JUCE SDK installed on your PC — Luthier does not bundle JUCE.
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
In Command Prompt or PowerShell:

  Luthier\Luthier.exe --check

Exit code 0 means bundled templates are reachable.


LICENSE
-------
Luthier source code: MIT License.
Packaged build includes Qt (PySide6) under LGPLv3.
See THIRD-PARTY-NOTICES in the GitHub repository.


================================================================================
LUTHIER {{VERSION}} — Windows
Ten Square Software
https://github.com/tensquaresoftware/luthier
FRANÇAIS
================================================================================

CONTENU DE CETTE ARCHIVE
------------------------
Cette archive contient un dossier Luthier\ avec :
  • Luthier.exe          — l'application
  • _internal\           — modèles, bibliothèques Qt et autres fichiers embarqués

Conservez le dossier Luthier\ entier. Luthier.exe seul ne fonctionnera pas.


INSTALLATION
------------
1. Décompressez l'archive dans un dossier de votre choix (ex. C:\Apps\Luthier).
2. Lancez Luthier\Luthier.exe.
3. Optionnel : épingler Luthier.exe à la barre des tâches ou créer un raccourci.


PREMIER LANCEMENT (BUILD NON SIGNÉ)
-----------------------------------
Windows SmartScreen peut afficher un avertissement au premier lancement.

Si un écran bleu d'avertissement s'affiche :
  Informations complémentaires → Exécuter quand même

Windows Defender peut analyser les fichiers au premier démarrage — un court
délai est normal, ce n'est pas une erreur.


PRÉREQUIS
---------
• Windows 10 ou ultérieur (64 bits).
• Un SDK JUCE installé sur votre PC — Luthier n'inclut pas JUCE.
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
Dans l'invite de commandes ou PowerShell :

  Luthier\Luthier.exe --check

Code de sortie 0 = les modèles embarqués sont accessibles.


LICENCE
-------
Code source Luthier : licence MIT.
Le build empaqueté inclut Qt (PySide6) sous LGPLv3.
Voir THIRD-PARTY-NOTICES dans le dépôt GitHub.
