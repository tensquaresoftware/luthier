================================================================================
LUTHIER {{VERSION}} — macOS
Ten Square Software
https://github.com/tensquaresoftware/luthier
================================================================================

A French version of this document is included below.
Une version française de ce fichier est disponible plus bas.


WHAT IS IN THIS ARCHIVE
-----------------------
This archive contains Luthier.app — a standalone desktop app to create
ready-to-build CMake-based JUCE starter projects (AU / VST3 / Standalone).
Fill in a form, generate once, then focus on development in your IDE.

Keep the entire Luthier.app bundle together. Do not move only the executable out
of the .app package.


INSTALLATION
------------
1. Unzip the archive.
2. Drag Luthier.app to Applications (or any folder you prefer).
3. Double-click Luthier.app to launch.


FIRST RUN (UNSIGNED BUILD — NOT NOTARIZED)
------------------------------------------
Luthier is not signed with an Apple Developer certificate. That is normal for
open-source community builds.

After you download and unzip the archive, macOS may block the first launch.
The message depends on how the file arrived on your Mac.

A) « Luthier.app is damaged and can't be opened » (French: « est endommagé »)
   Your browser (Safari, Firefox, Chrome, …) added a quarantine flag. The app
   is not actually damaged. Remove the flag once in Terminal (adjust the path):

     xattr -cr /Applications/Luthier.app

   Then double-click Luthier.app again.

B) « Apple cannot check … for malicious software » / unidentified developer
   • Right-click Luthier.app → Open → click Open in the dialog, or
   • System Settings → Privacy & Security → Open Anyway (may appear only after
     macOS blocked a launch attempt).

If double-click still fails, use Terminal — it bypasses Finder Gatekeeper:

  /Applications/Luthier.app/Contents/MacOS/Luthier

(Or run the --check command in VERIFY THE BUNDLE below — exit code 0 confirms
the bundle is fine.)


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
Cette archive contient Luthier.app — application autonome pour créer des
projets JUCE de démarrage prêts à compiler, basés sur CMake (plugins AU /
VST3 et Standalone). Remplissez un formulaire, générez une fois, puis
concentrez-vous sur le développement dans votre IDE.

Conservez le bundle Luthier.app entier. Ne déplacez pas uniquement l'exécutable
hors du paquet .app.


INSTALLATION
------------
1. Décompressez l'archive.
2. Glissez Luthier.app dans Applications (ou tout autre dossier).
3. Double-cliquez sur Luthier.app pour lancer l'application.


PREMIER LANCEMENT (BUILD NON SIGNÉ — NON NOTARISÉ)
--------------------------------------------------
Luthier n'est pas signé avec un certificat Apple Developer. C'est normal pour
un build open source communautaire.

Après téléchargement et décompression, macOS peut bloquer le premier lancement.
Le message dépend de la façon dont le fichier est arrivé sur votre Mac.

A) « Luthier.app est endommagé et ne peut pas être ouvert »
   Votre navigateur (Safari, Firefox, Chrome, …) a posé un marqueur de
   quarantaine. L'application n'est pas réellement endommagée. Retirez-le une
   fois dans le Terminal (adaptez le chemin) :

     xattr -cr /Applications/Luthier.app

   Puis double-cliquez à nouveau sur Luthier.app.

B) « Apple ne peut pas vérifier … logiciels malveillants » / développeur non
   identifié
   • Clic droit sur Luthier.app → Ouvrir → cliquer sur Ouvrir dans la boîte de
     dialogue, ou
   • Réglages système → Confidentialité et sécurité → Ouvrir quand même (peut
     n'apparaître qu'après une tentative bloquée).

Si le double-clic échoue encore, utilisez le Terminal — il contourne Gatekeeper
dans le Finder :

  /Applications/Luthier.app/Contents/MacOS/Luthier

(Ou la commande --check de la section VÉRIFIER LE BUNDLE ci-dessous — code 0 =
le bundle est sain.)


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
