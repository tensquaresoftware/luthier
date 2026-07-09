## Luthier {{VERSION}}

<!-- Replace this paragraph with a summary of new features and fixes. -->

### Downloads

| Platform | File | Instructions |
|----------|------|----------------|
| Windows | `Luthier-{{VERSION}}-windows.zip` | Unzip → run `Luthier\Luthier.exe` (SmartScreen: More info → Run anyway) |
| macOS | `Luthier-{{VERSION}}-macos.zip` | Unzip → open `Luthier.app` on **Apple Silicon** (see README.txt inside) |
| Linux | `Luthier-{{VERSION}}-linux.zip` | Unzip -> `chmod +x Luthier/Luthier` if needed |
| Documentation | `Luthier-{{VERSION}}-docs.zip` | User manuals (EN + FR) |

Verify downloads with `SHA256SUMS.txt` included in this release.

### Documentation (online)

- [User Manual (EN)](https://github.com/tensquaresoftware/luthier/blob/{{VERSION}}/docs/user/user-manual.md)
- [Manuel utilisateur (FR)](https://github.com/tensquaresoftware/luthier/blob/{{VERSION}}/docs/user/manuel-utilisateur.md)

### Requirements

- JUCE SDK on disk (not bundled with Luthier)
- Windows 10+ (64-bit) / **macOS Apple Silicon (M1+)** / Linux x86_64

**Note:** The standalone Luthier app does not run on Intel-based Macs. Generated JUCE projects can still target Mac Intel via CMake presets.

### License

MIT — packaged builds include Qt (PySide6) under LGPLv3. See [THIRD-PARTY-NOTICES.md](https://github.com/tensquaresoftware/luthier/blob/{{VERSION}}/THIRD-PARTY-NOTICES.md).
