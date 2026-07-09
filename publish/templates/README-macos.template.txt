================================================================================
LUTHIER {{VERSION}} — macOS
Ten Square Software
https://github.com/tensquaresoftware/luthier
================================================================================

A French version of this document is included below.
Une version française de ce fichier est disponible plus bas.


WHAT IS IN THIS ARCHIVE
-----------------------
This archive contains Luthier.app — a standalone desktop app to create new
CMake-based JUCE audio plugin project skeletons (AU / VST3 / Standalone).

Keep the entire Luthier.app bundle together. Do not move only the executable out
of the .app package.


INSTALLATION
------------
1. Unzip the archive.
2. Drag Luthier.app to Applications (or any folder you prefer).
3. Double-click Luthier.app to launch.


FIRST RUN (UNSIGNED BUILD)
--------------------------
macOS may block an app that is not signed with an Apple Developer certificate.

If you see a security warning:
  • Right-click Luthier.app → Open → Open again, or
  • System Settings → Privacy & Security → allow Luthier to run.

This is expected for community/open-source builds.


REQUIREMENTS
------------
• macOS on Apple Silicon (M1 or later). Intel-based Macs are not supported for
  the Luthier app.
• Generated JUCE projects produced by Luthier can still be built for Mac Intel
  (CMake presets macos-debug-x86_64 / macos-release-x86_64).
• A JUCE SDK installed on your Mac — Luthier does not bundle JUCE.
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
In Terminal:

  /path/to/Luthier.app/Contents/MacOS/Luthier --check

Exit code 0 means bundled templates are reachable.


LICENSE
-------
Luthier source code: MIT License.
Packaged build includes Qt (PySide6) under LGPLv3.
See THIRD-PARTY-NOTICES in the GitHub repository.


================================================================================
LUTHIER {{VERSION}} — macOS
Ten Square Software
https://github.com/tensquaresoftware/luthier
FRANÇAIS
================================================================================

CONTENU DE CETTE ARCHIVE
------------------------
Cette archive contient Luthier.app — application autonome pour créer de nouveaux
squelettes de projets JUCE basés sur CMake (AU / VST3 / Standalone).

Conservez le bundle Luthier.app entier. Ne déplacez pas uniquement l'exécutable
hors du paquet .app.


INSTALLATION
------------
1. Décompressez l'archive.
2. Glissez Luthier.app dans Applications (ou tout autre dossier).
3. Double-cliquez sur Luthier.app pour lancer l'application.


PREMIER LANCEMENT (BUILD NON SIGNÉ)
-----------------------------------
macOS peut bloquer une application non signée avec un certificat Apple Developer.

En cas d'avertissement de sécurité :
  • Clic droit sur Luthier.app → Ouvrir → Ouvrir à nouveau, ou
  • Réglages système → Confidentialité et sécurité → autoriser Luthier.

C'est normal pour des builds open source non signés.


PRÉREQUIS
---------
• macOS sur Apple Silicon (M1 ou ultérieur). Les Mac Intel ne sont pas pris en
  charge pour l'application Luthier.
• Les projets JUCE générés par Luthier restent compilables pour Mac Intel
  (presets CMake macos-debug-x86_64 / macos-release-x86_64).
• Un SDK JUCE installé sur votre Mac — Luthier n'inclut pas JUCE.
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
Dans le Terminal :

  /chemin/vers/Luthier.app/Contents/MacOS/Luthier --check

Code de sortie 0 = les modèles embarqués sont accessibles.


LICENCE
-------
Code source Luthier : licence MIT.
Le build empaqueté inclut Qt (PySide6) sous LGPLv3.
Voir THIRD-PARTY-NOTICES dans le dépôt GitHub.
