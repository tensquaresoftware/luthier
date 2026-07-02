# Luthier — Guide de publication GitHub (toute version)

**Objectif :** publier une release `X.Y.Z` sur https://github.com/tensquaresoftware/luthier  
**Durée estimée :** 5–15 minutes avec `publish/prepare-release.py` (archives déjà testées)  
**Prérequis :** builds QA validés, `gh` connecté, repo Git propre.

---

## Invocation Python (lire en premier)

Toutes les commandes ci-dessous s'exécutent **depuis la racine du dépôt** (le dossier qui contient `main.py`, `publish/`, `app/`, etc.), avec le venv activé ou en appelant explicitement son interpréteur.

Placez-vous d'abord dans votre clone :

```text
cd <chemin-vers-le-projet>
```

| OS | Interpréteur du venv |
|----|----------------------|
| **macOS / Linux** | `.venv/bin/python` |
| **Windows (PowerShell)** | `.venv\Scripts\python.exe` |

> **Windows :** ne copiez pas les blocs `bash` contenant `.venv/bin/python` — ce chemin n'existe pas sous Windows. Utilisez les blocs **Windows (PowerShell)** de chaque section.

Alternative sous Windows après activation du venv :

```powershell
cd <chemin-vers-le-projet>
.venv\Scripts\activate
python publish/prepare-release.py pack
```

Les chemins **relatifs** du guide (`publish/…`, `_local/releases/…`, `dist/…`) sont toujours exprimés par rapport à cette racine.

---

## Convention de nommage

**`X.Y.Z` sans préfixe `v`** — tag Git, dossiers, archives, About, release GitHub.

| Élément | Format | Exemple |
|---------|--------|---------|
| Version produit (`app/version.py`) | `X.Y.Z` | `1.0.0` |
| Dossier local | `_local/releases/X.Y.Z` | `1.0.0` |
| Tag Git | `X.Y.Z` | `1.0.0` |
| Archives | `Luthier-X.Y.Z-<plateforme>.<ext>` | `Luthier-1.0.0-macos.zip` |
| Titre GitHub Release | `Luthier X.Y.Z` | `Luthier 1.0.0` |
| Onglet About | `X.Y.Z` | `1.0.0` |

### Arborescence

```text
<chemin-vers-le-projet>/
  _local/releases/
    X.Y.Z/
      Luthier-X.Y.Z-macos.zip
      Luthier-X.Y.Z-windows.zip
      Luthier-X.Y.Z-linux.zip
      Luthier-X.Y.Z-docs.zip
      SHA256SUMS.txt
      RELEASE_NOTES.md
```

Modèles README et notes : `publish/templates/*.template.*`  
Scripts d'automatisation : **`publish/`** (`build-dist.py`, `prepare-release.py`).

---

## Workflow automatisé (recommandé)

### 0. Avant la release

- [ ] Mettre à jour `app/version.py` (`VERSION`, `REVISION_DATE`)
- [ ] QA manuelle terminée
- [ ] `main` propre, poussé, CI verte

### 1. Sur **chaque** OS — build + pack

**macOS / Linux**

```bash
cd <chemin-vers-le-projet>

.venv/bin/python publish/build-dist.py
.venv/bin/python publish/prepare-release.py pack
```

**Windows (PowerShell)**

```powershell
cd <chemin-vers-le-projet>

.venv\Scripts\python.exe publish/build-dist.py
.venv\Scripts\python.exe publish/prepare-release.py pack
```

Résultat : une archive plateforme dans `_local/releases/X.Y.Z/` (version lue depuis `app/version.py`).

> Synchronisez ce dossier entre machines (Git n'est **pas** utilisé — `_local/` est gitignoré).  
> Copie réseau, clé USB, cloud perso, etc.

**Alternative** — importer une archive déjà créée ailleurs (chemins **absolus ou relatifs** acceptés pour le fichier source) :

**macOS / Linux**

```bash
cd <chemin-vers-le-projet>

.venv/bin/python publish/prepare-release.py import macos <chemin-vers-l-archive-macos>
.venv/bin/python publish/prepare-release.py import windows <chemin-vers-l-archive-windows>
.venv/bin/python publish/prepare-release.py import linux <chemin-vers-l-archive-linux>
```

**Windows (PowerShell)**

```powershell
cd <chemin-vers-le-projet>

.venv\Scripts\python.exe publish/prepare-release.py import macos <chemin-vers-l-archive-macos>
.venv\Scripts\python.exe publish/prepare-release.py import windows <chemin-vers-l-archive-windows>
.venv\Scripts\python.exe publish/prepare-release.py import linux <chemin-vers-l-archive-linux>
```

Exemples de chemins d'archive : `~/Downloads/Luthier-1.0.0-macos.zip`, `./Luthier-1.0.0-windows.zip`, `D:\releases\Luthier-1.0.0-linux.zip`.

Écraser une archive existante : ajoutez `--force` (ex. `publish/prepare-release.py --force pack`).

### 2. Quand les **3** archives plateforme sont réunies — finaliser

Sur **une** machine (souvent celle qui a les 3 fichiers), depuis la racine du projet :

**macOS / Linux**

```bash
cd <chemin-vers-le-projet>

.venv/bin/python publish/prepare-release.py status    # les 3 [OK] ?
.venv/bin/python publish/prepare-release.py finalize  # docs + notes + SHA256SUMS.txt
.venv/bin/python publish/prepare-release.py verify
```

**Windows (PowerShell)**

```powershell
cd <chemin-vers-le-projet>

.venv\Scripts\python.exe publish/prepare-release.py status
.venv\Scripts\python.exe publish/prepare-release.py finalize
.venv\Scripts\python.exe publish/prepare-release.py verify
```

Éditez l'intro de `_local/releases/X.Y.Z/RELEASE_NOTES.md` (remplacez le commentaire HTML).

### 3. Publier sur GitHub

**macOS / Linux**

```bash
cd <chemin-vers-le-projet>
git status          # doit être propre
git pull origin main

.venv/bin/python publish/prepare-release.py publish
```

**Windows (PowerShell)**

```powershell
cd <chemin-vers-le-projet>
git status
git pull origin main

.venv\Scripts\python.exe publish/prepare-release.py publish
```

Le script :

1. Vérifie archives + checksums  
2. Crée le tag annoté `X.Y.Z`  
3. Pousse le tag  
4. Crée la GitHub Release + upload des 5 assets via `gh`

Options :

**macOS / Linux**

```bash
.venv/bin/python publish/prepare-release.py publish -y          # sans confirmation
.venv/bin/python publish/prepare-release.py publish --prerelease # bêta
```

**Windows (PowerShell)**

```powershell
.venv\Scripts\python.exe publish/prepare-release.py publish -y
.venv\Scripts\python.exe publish/prepare-release.py publish --prerelease
```

### 4. Contrôle final

- https://github.com/tensquaresoftware/luthier/releases/latest  
- [ ] 5 assets téléchargeables  
- [ ] Notes de release OK  
- [ ] Tag = `X.Y.Z` (sans `v`)

---

## Commandes du script — référence

| Commande | Rôle |
|----------|------|
| `status` | Inventaire des assets dans `_local/releases/X.Y.Z/` |
| `pack` | Archive `dist/` de l'OS courant + `README.txt` |
| `import <os> <fichier>` | Copie une archive externe au bon nom |
| `finalize` | Zip docs, `RELEASE_NOTES.md`, `SHA256SUMS.txt` |
| `verify` | Présence + checksums |
| `publish` | Tag Git + GitHub Release |

Version explicite (si différente de `app/version.py`) :

**macOS / Linux :** `.venv/bin/python publish/prepare-release.py --version 1.0.1 status`  
**Windows :** `.venv\Scripts\python.exe publish/prepare-release.py --version 1.0.1 status`

---

## Publication manuelle (secours)

Si `gh` ou `publish` échoue — depuis la racine du projet :

**macOS / Linux**

```bash
cd <chemin-vers-le-projet>

export VERSION="1.0.0"
export RELEASE_DIR="_local/releases/${VERSION}"

git tag -a "$VERSION" -m "Luthier ${VERSION}"
git push origin "$VERSION"

cd "$RELEASE_DIR"
gh release create "$VERSION" \
  --repo tensquaresoftware/luthier \
  --title "Luthier ${VERSION}" \
  --notes-file RELEASE_NOTES.md \
  Luthier-${VERSION}-macos.zip \
  Luthier-${VERSION}-windows.zip \
  Luthier-${VERSION}-linux.zip \
  Luthier-${VERSION}-docs.zip \
  SHA256SUMS.txt
```

**Windows (PowerShell)**

```powershell
cd <chemin-vers-le-projet>

$VERSION = "1.0.0"
$RELEASE_DIR = "_local/releases/$VERSION"

git tag -a $VERSION -m "Luthier $VERSION"
git push origin $VERSION

cd $RELEASE_DIR
gh release create $VERSION `
  --repo tensquaresoftware/luthier `
  --title "Luthier $VERSION" `
  --notes-file RELEASE_NOTES.md `
  Luthier-$VERSION-macos.zip `
  Luthier-$VERSION-windows.zip `
  Luthier-$VERSION-linux.zip `
  Luthier-$VERSION-docs.zip `
  SHA256SUMS.txt
```

---

## Après la publication (optionnel)

- Lien dans `README.md` : `[Download Luthier X.Y.Z](https://github.com/tensquaresoftware/luthier/releases/latest)`
- Commit sur `main` **après** le tag (nouveau commit)

---

## En cas de problème

| Problème | Action |
|----------|--------|
| `.venv/bin/python` introuvable (Windows) | Utiliser `.venv\Scripts\python.exe` — voir section *Invocation Python* |
| `dist/` introuvable au `pack` | Lancer `publish/build-dist.py` sur cette machine (depuis la racine du projet) |
| Archive déjà existante | `--force` |
| `verify` échoue | `finalize` à nouveau après correction des zip |
| Tag déjà sur GitHub | Ne pas republier ; éditer la release ou supprimer le tag si non annoncée |
| `gh` non connecté | `gh auth login` |
| Dossier `v1.0.0` ancien | Renommer en `1.0.0` pour alignement Option B |

---

## Récapitulatif express

**macOS / Linux**

```text
cd <chemin-vers-le-projet>
.venv/bin/python publish/build-dist.py          (×3 OS)
.venv/bin/python publish/prepare-release.py pack          (×3 OS, sync _local/releases/X.Y.Z/)
.venv/bin/python publish/prepare-release.py finalize
éditer _local/releases/X.Y.Z/RELEASE_NOTES.md
.venv/bin/python publish/prepare-release.py verify
.venv/bin/python publish/prepare-release.py publish
```

**Windows (PowerShell)**

```text
cd <chemin-vers-le-projet>
.venv\Scripts\python.exe publish/build-dist.py          (×3 OS)
.venv\Scripts\python.exe publish/prepare-release.py pack
.venv\Scripts\python.exe publish/prepare-release.py finalize
éditer _local/releases/X.Y.Z/RELEASE_NOTES.md
.venv\Scripts\python.exe publish/prepare-release.py verify
.venv\Scripts\python.exe publish/prepare-release.py publish
```

---

*Luthier — Ten Square Software*
