# Luthier — QA essentielle pré-promo v1.0.0

**Version visée :** 1.0.0  
**Build à installer :** commit **`c893cec`** — onglet **About** : version **1.0.0**, revision date **2026-07-02**  
**Public :** testeur sans connaissance technique  
**Langue de l’app :** anglais (libellés cités tels qu’à l’écran)  
**Durée indicative :**

| Scénario | Durée |
| --- | --- |
| Une machine, régressions + nouveautés | ~45 min |
| Fumée Workspace sur les 3 OS | ~30 min (10 min/OS) |
| Fin parcours Git `VoyageLuthier` | ~30 min |

> **Objectif :** ne pas refaire la [checklist détaillée](checklist-qa-manuelle.md) ni la [passe unique](checklist-qa-passe-unique.md) en entier. Cette feuille couvre **uniquement** ce qui a changé depuis le 30/06 et ce qui restait **non coché** ou **en échec** à l’arrêt des tests.

---

## Déjà validé — ne pas refaire

Cochez mentalement ; passez directement aux parties suivantes si vous utilisez le **même build** ou un build **plus récent** que celui testé le 30/06.

| Domaine | Statut | Référence |
| --- | --- | --- |
| Parcours complet Partie 1 (A/B/C, étapes 1–9) | ✅ | [checklist-qa-manuelle.md](checklist-qa-manuelle.md) — 2026-06-29 |
| Régressions R1, R4, R5, R6 (accents, messages `/`, dirty form, rouge erreur, prefs corrompues) | ✅ | [checklist-qa-passe-unique.md](checklist-qa-passe-unique.md) |
| Parcours Git `VoyageLuthier` 2.2 → 2.4 (Mac → Win → Linux) | ✅ | checklist manuelle + passe unique |
| WinError 5 sur `.git` (Windows) | ✅ corrigé | commits `60dc52e`, **`c893cec`** |
| Export Preferences avec chemin complet | ✅ | R2 passe unique |
| Import / export profil, Templates, validations de base | ✅ | Partie 1 manuelle |

**À ne pas retester** sauf si un point ci-dessous échoue : codes fabricant, variantes Audio Effect / VST3 seul, preprocessor defs, builds CMake optionnels déjà OK.

---

## Correctifs et features à valider (depuis le 30/06)

Commits concernés : `78dcf03` (QA fixes), `e78bce6` (Workspace per-OS), `fc433ac` (sidecar obligatoire), `3213eb0` / `6888e19` (indentation UI), **`26dcd0d`** (couleur projet + message sidecar), **`c893cec`** (WinError `.git` Windows).

### Prérequis communs (chaque OS)

- [x] Build **1.0.0** du **2026-07-02** installé.
- [x] **About** : version **1.0.0**, revision **2026-07-02**.
- [x] JUCE local disponible ; les chemins effectifs sont les suivants :

| OS | JUCE (exemple) |
| --- | --- |
| macOS | `/Volumes/Guillaume/Dev/SDKs/JUCE` |
| Windows | `C:/Users/Guillaume/Dev/SDKs/JUCE` |
| Linux | `/home/guillaume/Dev/SDKs/JUCE` |

---

## Partie 1 — Workspace per-OS (Epic 8.1)

> **Changement majeur :** la section **Paths** devient **Workspace** avec **six champs** (destination + JUCE × Windows / macOS / Linux). Seule la ligne de **l’OS hôte** a un bouton **Choose…**.

### W1 — Preferences → Workspace (~5 min/OS)

- [x] Onglet **Preferences** → section **Workspace** visible (plus de section **Paths** unique).
- [x] Sous **Destination folder** : trois lignes **Windows**, **macOS**, **Linux** — légèrement **indentées** sous le titre.
- [x] Sous **JUCE directory** : même disposition à trois lignes, indentée.
- [x] Sur **votre OS hôte** uniquement : bouton **Choose…** à côté de destination et JUCE ; les deux autres OS = saisie manuelle.
- [x] **Choose…** destination → dossier avec **accents** (ex. `Téléchargements`, `été 2026`) → **aucune** erreur rouge ; badge **Saved** possible.
- [x] Renseignez le chemin JUCE **hôte** ; saisissez des chemins plausibles pour les **deux autres OS** (utilisés plus tard en cross-plateforme).
- [x] Fermez / rouvrez Luthier : les **six** valeurs sont conservées.
- [x] **Export Preferences…** → **Import Preferences…** : les six champs reviennent.

### W2 — Project → Workspace (~5 min/OS)

- [x] **Create New Project** → les champs **Workspace** reprennent vos **Preferences** (six chemins).
- [x] **Project name** `TestLuthier` → **Generate Project** → succès **sans** dialogue de dossier intempestif (destination hôte déjà valide).
- [x] **Open Project…** → `TestLuthier` : les six chemins reviennent depuis `.luthier.json`.
- [x] Déplacez le dossier projet dans un parent accentué → **Open Project…** : la ligne **destination hôte** se met à jour ; **pas** d’erreur sur le chemin.
- [x] Les chemins **JUCE** et **destination** des **autres OS** restent ceux enregistrés (non écrasés par le déplacement).
- [x] **Choose…** sur une ligne hôte → badge **Saved** visible (comme dans **Preferences**).

### W3 — Migration anciens réglages (une machine suffit)

> Si vos `preferences.json` ont déjà été migrés lors d’un lancement précédent, cochez et passez.

- [x] *(Optionnel)* Avant le premier lancement du nouveau build : sauvegardez `preferences.json` (emplacements ci-dessous).
- [x] Premier lancement : pas de plantage ; section **Workspace** remplie (anciennes clés `destinationDir` / `juceDir` réparties sur l’OS hôte si migration nécessaire).
- [x] Identité (**Manufacturer**, couleur, etc.) **inchangée** après migration.

### W3b — Import cross-plateforme (Dropbox / clé USB) (~5 min)

> **Scénario clé :** exporter les prefs sur une machine, importer sur une autre, compléter les chemins **hôte** avec **Choose…**.

- [x] Machine A (ex. Linux) : personnalisez **Preferences** → **Export Preferences…** vers Dropbox.
- [x] Machine B (ex. macOS) : **Import Preferences…** → **succès** même si la ligne **destination macOS** est encore vide.
- [x] Les chemins de la machine A (ex. Linux) sont présents ; les lignes hôte de B sont vides ou à compléter.
- [x] **Choose…** sur destination et JUCE **hôte** → badge **Saved** → fermez / rouvrez Luthier : chemins hôte conservés.
- [x] **Create New Project** : les six chemins Workspace sont bien re-seedés depuis le profil importé.

| OS | Dossier config |
| --- | --- |
| macOS | `~/Library/Preferences/Luthier/` |
| Windows | `%LOCALAPPDATA%\Luthier\` |
| Linux | `~/.config/Luthier/` |

### W4 — Indentation Workspace + Artefacts (cosmétique, ~1 min/OS)

- [x] **Preferences** → **Workspace** et section **Artefacts** : labels **Windows / macOS / Linux** alignés visuellement avec le texte des **checkboxes** (même marge à gauche).
- [x] **Project** → sections **Workspace** et **Artefacts** : même alignement.

---

## Partie 2 — Sidecar obligatoire (Epic 8.2)

> **Changement breaking v1.0.0 :** plus de rechargement depuis `CMakeLists.txt` seul. Sans `.luthier.json`, **Open Project…** échoue proprement.

### S1 — Sidecar absent ou invalide (~3 min, une machine suffit ; refaire sur un second OS si doute)

- [x] Projet existant `TestLuthier` : renommez temporairement `.luthier.json` (ex. `.luthier.json.bak`).
- [x] **Open Project…** → modale ou barre de message : fichier compagnon **manquant** ou **Not a Luthier project** — message **clair**.
- [x] Le formulaire **ne** se remplit **pas** partiellement depuis CMake (pas de champs « à moitié » chargés).
- [x] Restaurez `.luthier.json` → **Open Project…** → chargement normal.
- [x] **Open Project…** sur un dossier **vide** ou non-Luthier → message *Not a Luthier project or companion file .luthier.json is missing.* — **pas de plantage**.

### S2 — `.luthier.json` cross-plateforme (si vous reprenez `VoyageLuthier`)

- [x] Ouvrez `.luthier.json` dans un éditeur : clés `destinationDirWindows`, `destinationDirMacos`, `destinationDirLinux`, `juceDirWindows`, etc. présentes ; chemins en **`/`** même sous Windows.
- [x] Clé **`accentColor`** présente après **Generate Project** ; couleur retrouvée au **Open Project…** sur une autre machine (commit `26dcd0d`).

---

## Partie 3 — Points en suspens de la passe unique

> Cases laissées vides ou marquées ❌ dans [checklist-qa-passe-unique.md](checklist-qa-passe-unique.md).

### P1 — Modales Windows (R3) — Windows uniquement

- [x] **Create New Project** après modification sans générer → **No** par défaut (ordre No/Yes cosmétique — accepté mineur).
- [x] **Generate Project** sur dossier existant → même comportement.

*(Ordre boutons : mineur Qt Windows — non bloquant pour la promo.)*

### P2 — Linux : icône et géométrie fenêtre (R7) — Linux uniquement

- [x] Lanceur / barre des tâches : icône Luthier visible.
- [x] Redimensionnez et déplacez la fenêtre → fermez → rouvrez : taille **sensiblement** retrouvée ; **position non garantie** (limitation v1 acceptée, surtout Wayland).

### P3 — Fumée rapide post-Workspace

> Non applicable — W1 + W2 déjà validés sur les **trois** OS.

| OS | Statut |
| --- | --- |
| macOS | [x] W1 + W2 validés |
| Windows | [x] W1 + W2 + **Generate** sur clone Git sans WinError (`c893cec`) |
| Linux | [x] W1 + W2 validés |

---

## Partie 4 — Fin du parcours Git `VoyageLuthier`

**Dépôt :** https://github.com/tensquaresoftware/voyage-luthier

### 4.1 — Retour macOS (finalisation)

- [x] `git pull` — dernière révision Linux (`1.2.0`, `LINUX_QA=1`).
- [x] **Open Project…** → `VoyageLuthier`.
- [x] **Version** : `1.2.0` ; **Preprocessor defs** contient `LINUX_QA=1`.
- [x] **Couleur Project** transportée via `.luthier.json` après régénération (build `26dcd0d`+).
- [x] Section **Workspace** : **JUCE directory** ligne **macOS** → chemin JUCE Mac ; destination Mac cohérente.
- [x] **Generate Project** → succès.
- [x] **Display name** → `Voyage Cross QA Final` → **Generate Project** → commit + push (*« Finalisation Mac »*).

### 4.2 — Vérifications finales (3 OS, ~10 min/OS ou 1 OS + spot-check)

- [x] **Open Project…** dernière révision Git → projet **cohérent** (même version, defs, options Artefacts ; seuls chemins **Workspace hôte** à adapter si besoin).
- [x] **Import Preferences…** depuis un JSON d’une autre machine → **Preferences** mis à jour ; projet ouvert **inchangé**.
- [x] **Aucun plantage** Luthier pendant 4.1–4.2.

### Récapitulatif VoyageLuthier

| Étape | Machine | Version | Display name |
| --- | --- | --- | --- |
| Création | macOS | 1.0.0 | Voyage Cross QA macOS |
| Windows | Windows | 1.1.0 | … Windows |
| Linux | Linux | 1.2.0 | (inchangé ou …) |
| **Final Mac** | **macOS** | **1.2.0** | **… Final** |

---

## Critères de réussite (go promo)

La QA pré-release est **réussie** :

- [x] **Partie 1 (W1–W4)** OK sur **macOS, Windows et Linux**.
- [x] **Partie 2 (S1–S2)** OK — sidecar obligatoire confirmé.
- [x] **Partie 4** terminée (final Mac + cohérence Git sur les 3 OS).
- [x] **Aucun bloquant** ouvert.
- [x] Points **mineurs** connus acceptés pour v1.0.0 :
  - ordre boutons modales sous Windows (P1) ;
  - position fenêtre Linux non garantie (P2).

**Décision : go promo v1.0.0** — build **`c893cec`**, révision **2026-07-02**.

---

## Grille de suivi

| # | OS | Section | Que faisiez-vous ? | Attendu | Obtenu | Gravité |
| --- | --- | --- | --- | --- | --- | --- |
| — | — | — | *(aucun item ouvert)* | — | — | — |

**Gravité :** **bloquant** = impossible de continuer ou risque perte de données ; **gênant** = contournement pénible ; **mineur** = cosmétique ou cas rare.

---

## Références

- [Checklist QA détaillée (archive)](checklist-qa-manuelle.md)
- [Passe QA unique Workspace (archive)](checklist-qa-passe-unique.md)
- [Manuel utilisateur (FR)](manuel-utilisateur.md)
- [User manual (EN)](user-manual.md)
