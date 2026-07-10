# Luthier — GitHub Release Guide (any version)

**Goal:** publish release `X.Y.Z` on https://github.com/tensquaresoftware/luthier  
**Estimated time:** 5–15 minutes with `publish/prepare-release.py` (archives already tested)  
**Prerequisites:** QA builds validated, `gh` authenticated, clean Git repo.

---

## Python invocation (read first)

All commands below run **from the repository root** (the folder containing `main.py`, `publish/`, `app/`, etc.), with the venv activated or by calling its interpreter explicitly.

First `cd` into your clone:

```text
cd <path-to-project>
```

| OS | venv interpreter |
|----|------------------|
| **Windows (PowerShell)** | `.venv\Scripts\python.exe` |
| **macOS & Linux** | `.venv/bin/python` |

> **Windows:** do not copy `bash` blocks using `.venv/bin/python` — that path does not exist on Windows. Use the **Windows (PowerShell)** blocks in each section.

Alternative on Windows after activating the venv:

```powershell
cd <path-to-project>
.venv\Scripts\activate
python publish/prepare-release.py pack
```

**Relative paths** in this guide (`publish/…`, `_local/releases/…`, `dist/…`) are always relative to this root.

---

## Naming convention

**`X.Y.Z` without a `v` prefix** — Git tag, folders, archives, About tab, GitHub Release.

| Item | Format | Example |
|------|--------|---------|
| Product version (`app/version.py`) | `X.Y.Z` | `1.0.0` |
| Local folder | `_local/releases/X.Y.Z` | `1.0.0` |
| Git tag | `X.Y.Z` | `1.0.0` |
| Archives | `Luthier-X.Y.Z-<platform>.<ext>` | `Luthier-1.0.0-macos.zip` |
| GitHub Release title | `Luthier X.Y.Z` | `Luthier 1.0.0` |
| About tab | `X.Y.Z` | `1.0.0` |

### Layout

```text
<path-to-project>/
  _local/releases/
    X.Y.Z/
      Luthier-X.Y.Z-windows.zip
      Luthier-X.Y.Z-macos.zip
      Luthier-X.Y.Z-linux.zip
      Luthier-X.Y.Z-docs.zip
      SHA256SUMS.txt
      RELEASE_NOTES.md
```

README and notes templates: `publish/templates/*.template.*`  
Automation scripts: **`publish/`** (`build-dist.py`, `prepare-release.py`).

---

## Automated workflow (recommended)

### 0. Before release

- [ ] Update `app/version.py` (`VERSION`, `REVISION_DATE`)
- [ ] Manual QA complete
- [ ] Clean `main`, pushed, green CI

### 1. On **each** OS — build + pack the app

**Windows (PowerShell)**

```powershell
cd <path-to-project>

.venv\Scripts\python.exe publish/build-dist.py
.venv\Scripts\python.exe publish/prepare-release.py pack
```

**macOS & Linux**

```bash
cd <path-to-project>

.venv/bin/python publish/build-dist.py
.venv/bin/python publish/prepare-release.py pack
```

Result: one platform archive in `_local/releases/X.Y.Z/` (version read from `app/version.py`).

> Sync this folder across machines (Git is **not** used — `_local/` is gitignored): network copy, USB drive, personal cloud, etc.

Overwrite an existing archive: add `--force` (e.g. `publish/prepare-release.py --force pack`).

### 2. When all **3** platform archives are together — finalize

On **one** machine (often the one with all three files), from the project root:

**Windows (PowerShell)**

```powershell
cd <path-to-project>

.venv\Scripts\python.exe publish/prepare-release.py finalize
```

**macOS & Linux**

```bash
cd <path-to-project>

# docs + notes + SHA256SUMS.txt (+ asset inventory at the end)
.venv/bin/python publish/prepare-release.py finalize
```

> `finalize` already prints the asset inventory at the end (like `status`). Run `status` separately only if you want to inspect the folder without regenerating anything.

**Windows (PowerShell)**

```powershell
cd <path-to-project>

.venv\Scripts\python.exe publish/prepare-release.py status
```

**macOS & Linux**

```bash
cd <path-to-project>

.venv/bin/python publish/prepare-release.py status
```

**Complete release notes** — `finalize` generates a draft; **before `publish`**, open `_local/releases/X.Y.Z/RELEASE_NOTES.md` and replace the placeholder paragraph:

```markdown
<!-- Replace this paragraph with a summary of new features and fixes. -->
```

with a concise summary of what's new and fixed in this version (2–5 sentences in English — this file becomes the public GitHub Release text).

- [ ] The HTML comment above is gone
- [ ] The summary accurately describes user-facing changes

> If you rerun `finalize` without `--force`, the existing file is kept. Use `--force` only to regenerate the template from scratch.

Then verify archives:

**Windows (PowerShell)**

```powershell
cd <path-to-project>

.venv\Scripts\python.exe publish/prepare-release.py verify
```

**macOS & Linux**

```bash
cd <path-to-project>

.venv/bin/python publish/prepare-release.py verify
```

### 3. Publish to GitHub

**Windows (PowerShell)**

```powershell
cd <path-to-project>

# Repo must be clean before publishing
git status
git pull origin main

.venv\Scripts\python.exe publish/prepare-release.py publish
```

**macOS & Linux**

```bash
cd <path-to-project>

# Repo must be clean before publishing
git status
git pull origin main

.venv/bin/python publish/prepare-release.py publish
```

The script:

1. Verifies archives + checksums  
2. Creates annotated tag `X.Y.Z`  
3. Pushes the tag  
4. Creates the GitHub Release + uploads 5 assets via `gh`

Options:

**Windows (PowerShell)**

```powershell
.venv\Scripts\python.exe publish/prepare-release.py publish -y
.venv\Scripts\python.exe publish/prepare-release.py publish --prerelease
```

**macOS & Linux**

```bash
.venv/bin/python publish/prepare-release.py publish -y          # skip confirmation
.venv/bin/python publish/prepare-release.py publish --prerelease # beta
```

### 4. Final check

- https://github.com/tensquaresoftware/luthier/releases/latest  
- [ ] 5 downloadable assets  
- [ ] Release notes OK (no remaining `<!-- Replace this paragraph… -->`)  
- [ ] Tag = `X.Y.Z` (no `v`)

---

## Script commands — reference

| Command | Role |
|---------|------|
| `status` | Asset inventory (optional — also shown at end of `finalize`) |
| `pack` | Archive current OS `dist/` + `README.txt` |
| `finalize` | Docs zip, draft `RELEASE_NOTES.md` (complete by hand), `SHA256SUMS.txt` |
| `verify` | Presence + checksums |
| `publish` | Git tag + GitHub Release |

Explicit version (if different from `app/version.py`):

**Windows:** `.venv\Scripts\python.exe publish/prepare-release.py --version 1.0.1 status`  
**macOS & Linux:** `.venv/bin/python publish/prepare-release.py --version 1.0.1 status`

---

## Manual publication (fallback)

If `gh` or `publish` fails — from the project root:

**Windows (PowerShell)**

```powershell
cd <path-to-project>

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
cd <path-to-project>

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

## After publication (optional)

- Link in `README.md`: `[Download Luthier X.Y.Z](https://github.com/tensquaresoftware/luthier/releases/latest)`
- Commit on `main` **after** the tag (new commit)

---

## Troubleshooting

| Problem | Action |
|---------|--------|
| `.venv/bin/python` not found (Windows) | Use `.venv\Scripts\python.exe` — see *Python invocation* |
| `dist/` missing at `pack` | Run `publish/build-dist.py` on this machine (from project root) |
| Archive already exists | `--force` |
| `verify` fails | Run `finalize` again after fixing zips |
| Tag already on GitHub | Do not republish; edit the release or delete the tag if not announced |
| `gh` not authenticated | `gh auth login` |
| Old folder `v1.0.0` | Rename to `1.0.0` for Option B alignment |

---

## Quick recap

**Windows (PowerShell)**

```text
cd <path-to-project>
.venv\Scripts\python.exe publish/build-dist.py          (×3 OS)
.venv\Scripts\python.exe publish/prepare-release.py pack
.venv\Scripts\python.exe publish/prepare-release.py finalize
complete _local/releases/X.Y.Z/RELEASE_NOTES.md  (replace <!-- Replace this paragraph… -->)
.venv\Scripts\python.exe publish/prepare-release.py verify
.venv\Scripts\python.exe publish/prepare-release.py publish
```

**macOS & Linux**

```text
cd <path-to-project>
.venv/bin/python publish/build-dist.py          (×3 OS)
.venv/bin/python publish/prepare-release.py pack          (×3 OS, sync _local/releases/X.Y.Z/)
.venv/bin/python publish/prepare-release.py finalize
complete _local/releases/X.Y.Z/RELEASE_NOTES.md  (replace <!-- Replace this paragraph… -->)
.venv/bin/python publish/prepare-release.py verify
.venv/bin/python publish/prepare-release.py publish
```

---

*Luthier — Ten Square Software*
