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
| **Windows (PowerShell)** | `.venv\Scripts\python.exe` |
| **macOS & Linux** | `.venv/bin/python` |

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
      Luthier-X.Y.Z-windows.zip
      Luthier-X.Y.Z-macos.zip
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

### 1. Sur **chaque** OS — build + pack de l'application

**Windows (PowerShell)**

```powershell
cd <chemin-vers-le-projet>

.venv\Scripts\python.exe publish/build-dist.py
.venv\Scripts\python.exe publish/prepare-release.py pack
```

**macOS & Linux**

```bash
cd <chemin-vers-le-projet>

.venv/bin/python publish/build-dist.py
.venv/bin/python publish/prepare-release.py pack
```

Résultat : une archive plateforme dans `_local/releases/X.Y.Z/` (version lue depuis `app/version.py`).

> Synchronisez ce dossier entre machines (Git n'est **pas** utilisé — `_local/` est gitignoré) : Copie réseau, clé USB, cloud perso, etc.

Écraser une archive existante : ajoutez `--force` (ex. `publish/prepare-release.py --force pack`).

### 2. Quand les **3** archives plateforme sont réunies — finaliser

Sur **une** machine (souvent celle qui a les 3 fichiers), depuis la racine du projet :

**Windows (PowerShell)**

```powershell
cd <chemin-vers-le-projet>

.venv\Scripts\python.exe publish/prepare-release.py finalize
```

**macOS & Linux**

```bash
cd <chemin-vers-le-projet>

# docs + notes + SHA256SUMS.txt (+ inventaire des assets à la fin)
.venv/bin/python publish/prepare-release.py finalize
```

> `finalize` affiche déjà l'inventaire des assets en fin d'exécution (comme `status`). Lancez `status` séparément seulement si vous voulez vérifier le dossier sans regénérer quoi que ce soit.

**Windows (PowerShell)**

```powershell
cd <chemin-vers-le-projet>

.venv\Scripts\python.exe publish/prepare-release.py status
```

**macOS & Linux**

```bash
cd <chemin-vers-le-projet>

.venv/bin/python publish/prepare-release.py status
```

**Compléter les notes de release** — `finalize` génère un brouillon ; **avant `publish`**, ouvrez `_local/releases/X.Y.Z/RELEASE_NOTES.md` et remplacez le paragraphe placeholder :

```markdown
<!-- Replace this paragraph with a summary of new features and fixes. -->
```

par un résumé concis des nouveautés et corrections de cette version (2–5 phrases, en anglais — le fichier sert de texte public GitHub Release).

- [ ] Le commentaire HTML ci-dessus a disparu
- [ ] Le résumé décrit bien ce qui change pour l'utilisateur

> Si vous relancez `finalize` sans `--force`, le fichier existant est conservé. Utilisez `--force` uniquement si vous voulez regénérer le modèle depuis zéro.

Puis vérifiez les archives :

**Windows (PowerShell)**

```powershell
cd <chemin-vers-le-projet>

.venv\Scripts\python.exe publish/prepare-release.py verify
```

**macOS & Linux**

```bash
cd <chemin-vers-le-projet>

.venv/bin/python publish/prepare-release.py verify
```

### 3. Publier sur GitHub

**Windows (PowerShell)**

```powershell
cd <chemin-vers-le-projet>
git status
git pull origin main

.venv\Scripts\python.exe publish/prepare-release.py publish
```

**macOS & Linux**

```bash
cd <chemin-vers-le-projet>
git status
git pull origin main

.venv/bin/python publish/prepare-release.py publish
```

Le script :

1. Vérifie archives + checksums  
2. Crée le tag annoté `X.Y.Z`  
3. Pousse le tag  
4. Crée la GitHub Release + upload des 5 assets via `gh`

Options :

**Windows (PowerShell)**

```powershell
.venv\Scripts\python.exe publish/prepare-release.py publish -y
.venv\Scripts\python.exe publish/prepare-release.py publish --prerelease
```

**macOS & Linux**

```bash
.venv/bin/python publish/prepare-release.py publish -y          # sans confirmation
.venv/bin/python publish/prepare-release.py publish --prerelease # bêta
```

### 4. Contrôle final

- https://github.com/tensquaresoftware/luthier/releases/latest  
- [ ] 5 assets téléchargeables  
- [ ] Notes de release OK (pas de `<!-- Replace this paragraph… -->` restant)  
- [ ] Tag = `X.Y.Z` (sans `v`)

---

## Commandes du script — référence

| Commande | Rôle |
|----------|------|
| `status` | Inventaire des assets (optionnel — aussi affiché à la fin de `finalize`) |
| `pack` | Archive `dist/` de l'OS courant + `README.txt` |
| `finalize` | Zip docs, brouillon `RELEASE_NOTES.md` (à compléter à la main), `SHA256SUMS.txt` |
| `verify` | Présence + checksums |
| `publish` | Tag Git + GitHub Release |

Version explicite (si différente de `app/version.py`) :

**Windows :** `.venv\Scripts\python.exe publish/prepare-release.py --version 1.0.1 status`  
**macOS & Linux :** `.venv/bin/python publish/prepare-release.py --version 1.0.1 status`

---

## Publication manuelle (secours)

Si `gh` ou `publish` échoue — depuis la racine du projet :

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
  Luthier-$VERSION-windows.zip `
  Luthier-$VERSION-macos.zip `
  Luthier-$VERSION-linux.zip `
  Luthier-$VERSION-docs.zip `
  SHA256SUMS.txt
```

**macOS & Linux**

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
  Luthier-${VERSION}-windows.zip \
  Luthier-${VERSION}-macos.zip \
  Luthier-${VERSION}-linux.zip \
  Luthier-${VERSION}-docs.zip \
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

**Windows (PowerShell)**

```text
cd <chemin-vers-le-projet>
.venv\Scripts\python.exe publish/build-dist.py          (×3 OS)
.venv\Scripts\python.exe publish/prepare-release.py pack
.venv\Scripts\python.exe publish/prepare-release.py finalize
compléter _local/releases/X.Y.Z/RELEASE_NOTES.md  (remplacer <!-- Replace this paragraph… -->)
.venv\Scripts\python.exe publish/prepare-release.py verify
.venv\Scripts\python.exe publish/prepare-release.py publish
```

**macOS & Linux**

```text
cd <chemin-vers-le-projet>
.venv/bin/python publish/build-dist.py          (×3 OS)
.venv/bin/python publish/prepare-release.py pack          (×3 OS, sync _local/releases/X.Y.Z/)
.venv/bin/python publish/prepare-release.py finalize
compléter _local/releases/X.Y.Z/RELEASE_NOTES.md  (remplacer <!-- Replace this paragraph… -->)
.venv/bin/python publish/prepare-release.py verify
.venv/bin/python publish/prepare-release.py publish
```

---

*Luthier — Ten Square Software*
