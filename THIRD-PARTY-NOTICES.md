# Third-Party Notices

Luthier's own source code is licensed under the MIT License (see [LICENSE](LICENSE)).

Distributed binaries — such as the packaged macOS `.app` — include the following third-party components.

## Qt (via PySide6)

- **Component:** Qt for Python (PySide6) and the underlying Qt libraries
- **License:** GNU Lesser General Public License, version 3 (LGPLv3)
- **Homepage:** https://www.qt.io — https://doc.qt.io/qtforpython/
- **Source:** https://download.qt.io/official_releases/qt/

The Qt libraries are used under the terms of the LGPLv3. They are **dynamically linked**: in packaged builds the Qt frameworks ship as separate shared libraries (for example under `Contents/Frameworks` on macOS), so an end user can replace them with a compatible version, as required by the LGPL. The corresponding Qt source is available from the Qt download site listed above.

Luthier's own code remains under the MIT License and may be used, modified, and redistributed accordingly.

## Logo fonts

The Luthier logo (`resources/luthier.svg`) embeds vector outlines derived from two fonts under the SIL Open Font License 1.1:

- **Orbitron** — © The Orbitron Project Authors (the "LUTHIER" wordmark)
- **Montserrat** — © The Montserrat Project Authors (the "JUCE PROJECT GENERATOR" subtitle)

Only the resulting glyph outlines are embedded; the font files themselves are not redistributed. SIL OFL: https://openfontlicense.org
