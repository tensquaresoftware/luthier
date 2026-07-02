# Luthier — Guide de publication GitHub (toute version)

**Objectif :** publier une release `X.Y.Z` sur https://github.com/tensquaresoftware/luthier  
**Durée estimée :** 5–15 minutes avec `publish/prepare-release.py` (archives déjà testées)  
**Prérequis :** builds QA validés, `gh` connecté, repo Git propre.

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
_local/releases/
  release-guide.md              ← ce fichier
  1.0.0/
    Luthier-1.0.0-macos.zip
    Luthier-1.0.0-windows.zip
    Luthier-1.0.0-linux.zip
    Luthier-1.0.0-docs.zip
    SHA256SUMS.txt
    RELEASE_NOTES.md
  1.0.1/
    ...
```

Modèles README et notes : `publish/templates/*.template.*`  
Scripts d’automatisation : **`publish/`** (`publish/build-dist.py`, `publish/prepare-release.py`).

---

## Workflow automatisé (recommandé)

### 0. Avant la release

- [ ] Mettre à jour `app/version.py` (`VERSION`, `REVISION_DATE`)
- [ ] QA manuelle terminée
- [ ] `main` propre, poussé, CI verte

### 1. Sur **chaque** OS — build + pack

```bash
cd /Volumes/Guillaume/Dev/Projects/Apps/Luthier

.venv/bin/python publish/build-dist.py
.venv/bin/python publish/prepare-release.py pack
```

Windows (PowerShell, depuis la racine du dépôt) :

```powershell
.venv\Scripts\python.exe publish/build-dist.py
.venv\Scripts\python.exe publish/prepare-release.py pack
```

Résultat : une archive plateforme dans `_local/releases/1.0.0/` (version lue depuis `app/version.py`).

> Synchronisez ce dossier entre machines (Git n’est **pas** utilisé — `_local/` est gitignoré).  
> Copie réseau, clé USB, cloud perso, etc.

**Alternative** — importer une archive déjà créée ailleurs :

```bash
.venv/bin/python publish/prepare-release.py import macos /chemin/vers/Luthier-1.0.0-macos.zip
.venv/bin/python publish/prepare-release.py import windows /chemin/vers/Luthier-1.0.0-windows.zip
.venv/bin/python publish/prepare-release.py import linux /chemin/vers/Luthier-1.0.0-linux.zip
```

Windows : remplacez `.venv/bin/python` par `.venv\Scripts\python.exe` et les chemins par des chemins Windows (ex. `C:\...\Luthier-1.0.0-windows.zip`).

Écraser une archive existante : ajoutez `--force` (ex. `publish/prepare-release.py --force pack`).

### 2. Quand les **3** archives plateforme sont réunies — finaliser

Sur **une** machine (souvent celle qui a les 3 fichiers) :

```bash
.venv/bin/python publish/prepare-release.py status    # les 3 [OK] ?
.venv/bin/python publish/prepare-release.py finalize  # docs + notes + SHA256SUMS.txt
.venv/bin/python publish/prepare-release.py verify
```

Windows : `.venv\Scripts\python.exe publish/prepare-release.py status` (idem pour `finalize`, `verify`).

Éditez l’intro de `RELEASE_NOTES.md` (remplacez le commentaire HTML).

### 3. Publier sur GitHub

```bash
cd /Volumes/Guillaume/Dev/Projects/Apps/Luthier
git status          # doit être propre
git pull origin main

.venv/bin/python publish/prepare-release.py publish
```

Windows : `.venv\Scripts\python.exe publish/prepare-release.py publish`

Le script :

1. Vérifie archives + checksums  
2. Crée le tag annoté `1.0.0`  
3. Pousse le tag  
4. Crée la GitHub Release + upload des 5 assets via `gh`

Options :

```bash
.venv/bin/python publish/prepare-release.py publish -y          # sans confirmation
.venv/bin/python publish/prepare-release.py publish --prerelease # bêta
```

### 4. Contrôle final

- https://github.com/tensquaresoftware/luthier/releases/latest  
- [ ] 5 assets téléchargeables  
- [ ] Notes de release OK  
- [ ] Tag = `1.0.0` (sans `v`)

---

## Commandes du script — référence

| Commande | Rôle |
|----------|------|
| `status` | Inventaire des assets dans `_local/releases/X.Y.Z/` |
| `pack` | Archive `dist/` de l’OS courant + `README.txt` |
| `import <os> <fichier>` | Copie une archive externe au bon nom |
| `finalize` | Zip docs, `RELEASE_NOTES.md`, `SHA256SUMS.txt` |
| `verify` | Présence + checksums |
| `publish` | Tag Git + GitHub Release |

Version explicite (si différente de `app/version.py`) :

```bash
.venv/bin/python publish/prepare-release.py --version 1.0.1 status
```

---

## Publication manuelle (secours)

Si `gh` ou `publish` échoue :

```bash
export VERSION="1.0.0"
export RELEASE_DIR="/Volumes/Guillaume/Dev/Projects/Apps/Luthier/_local/releases/${VERSION}"

cd /Volumes/Guillaume/Dev/Projects/Apps/Luthier
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

---

## Après la publication (optionnel)

- Lien dans `README.md` : `[Download Luthier 1.0.0](https://github.com/tensquaresoftware/luthier/releases/latest)`
- Commit sur `main` **après** le tag (nouveau commit)

---

## En cas de problème

| Problème | Action |
|----------|--------|
| `dist/` introuvable au `pack` | Lancer `publish/build-dist.py` sur cette machine |
| Archive déjà existante | `--force` |
| `verify` échoue | `finalize` à nouveau après correction des zip |
| Tag déjà sur GitHub | Ne pas republier ; éditer la release ou supprimer le tag si non annoncée |
| `gh` non connecté | `gh auth login` |
| Dossier `v1.0.0` ancien | Renommer en `1.0.0` pour alignement Option B |

---

## Récapitulatif express

```text
publish/build-dist.py          (×3 OS)
publish/prepare-release.py pack          (×3 OS, sync dossier _local/releases/1.0.0/)
publish/prepare-release.py finalize
éditer RELEASE_NOTES.md
publish/prepare-release.py verify
publish/prepare-release.py publish
```

---

*Luthier — Ten Square Software*
