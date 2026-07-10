#!/usr/bin/env python3
"""Strip filled results from archived smoke-test reports → reusable QA procedures."""

from __future__ import annotations

import re
import sys
from pathlib import Path


def blank_three_os(text: str) -> str:
    text = re.sub(
        r"\| \*\*Tester\*\* \| .+ \|",
        "| **Tester** | _name_ |",
        text,
    )
    text = re.sub(
        r"\| \*\*Start date\*\* \| .+ \|",
        "| **Start date** | _YYYY-MM-DD_ |",
        text,
    )
    text = re.sub(
        r"\| \*\*Commit / tag tested\*\* \| .+ \|",
        "| **Commit / tag tested** | _tag or commit SHA_ |",
        text,
    )
    text = re.sub(
        r"\| \*\*Smoke test end date\*\* \| .+ \|",
        "| **Smoke test end date** | _YYYY-MM-DD_ |",
        text,
    )
    text = re.sub(
        r"\| \*\*GitHub CI\*\* .+ \|",
        "| **GitHub CI** (pytest 3 OS) | ☐ green on tested commit ☐ not verified |",
        text,
    )
    text = re.sub(
        r"\| \*\*DAW used\*\* \| .+ \|",
        "| **DAW used** | ☐ Ableton Live ☐ JUCE AudioPluginHost ☐ both |",
        text,
    )
    text = re.sub(
        r"\| \*\*Cursor / VS Code\*\* \| .+ \|",
        "| **Cursor / VS Code** | Version: _…_ |",
        text,
    )
    text = re.sub(
        r"\| \*\*Dev machine\*\* \| .+ \|",
        "| **Dev machine** | _model / OS version_ |",
        text,
    )
    text = re.sub(
        r"\| \*\*Shared prefs file\*\* \| .+ \|",
        "| **Shared prefs file** | _path to exported luthier-smoke-prefs.json_ |",
        text,
    )

    # Phase progress rows: clear Done / Date / blockers
    text = re.sub(
        r"(\| \*\*[PABCD]\*\* \| .+ \| .+ min \|) ✅ ( \| .+ \| .+ \|)",
        r"\1 ☐ \2",
        text,
    )
    text = re.sub(
        r"(\| \*\*[PABCD]\*\* \| .+ \| .+ min \| ☐ \|) .+ ( \| .+ \|)",
        r"\1 _date_ \2",
        text,
    )
    for phase in "PABCD":
        text = re.sub(
            rf"(\| \*\*{phase}\*\* \| .+ \| .+ min \| ☐ \| _date_ \|) .+ \|",
            r"\1 — |",
            text,
        )

    # Per-phase build headers
    text = re.sub(r"^\*\*Build tested:\*\* .+$", "", text, flags=re.MULTILINE)

    # Table OK/KO columns
    text = re.sub(r"\| ✅ \| ☐ \|", "| ☐ | ☐ |", text)
    text = re.sub(r"\| ✅ \| ✅ \|", "| ☐ | ☐ |", text)

    # Success criteria verdict banner
    text = re.sub(
        r"\*\*Smoke test verdict .+\*\*\n\n",
        "",
        text,
    )

    # Accepted minors list (filled run only)
    text = re.sub(
        r"\n\*\*Accepted minors without release failure:\*\*\n\n(?:- .+\n)+",
        "\n",
        text,
    )

    # Issue grid: keep header + one empty template row
    text = re.sub(
        r"(\| # \| Step ID \| OS \| Summary .+\n\| --- .+\n)(?:\| .+\n)+",
        r"\1| _ | _ | _ | _ | _ | _ | _ | _ |\n",
        text,
    )

    # References (procedure paths)
    text = text.replace(
        "[rc4 Windows smoke test (condensed)](./smoke-test-rc4-windows.md)",
        "[Windows smoke test add-on](./smoke-test-windows-addon.md)",
    )
    text = text.replace(
        " — Phase B build/regen + D2 (✅ 10/07/2026)",
        " — optional Windows supplement for Phase B build/regen + D2",
    )
    text = text.replace(
        "../1.0.0-beta/checklist-qa-pre-release-v1.md",
        "./archive/v1.0.0-beta/checklist-qa-pre-release-v1.md",
    )

    return text


def blank_windows_addon(text: str) -> str:
    text = re.sub(
        r"\*\*Tag tested:\*\* `.+`",
        "**Tag tested:** _enter tag (e.g. `1.0.0-rc1`)_",
        text,
    )
    text = re.sub(
        r"\*\*Date:\*\* .+",
        "**Date:** _YYYY-MM-DD_",
        text,
    )
    text = re.sub(
        r"\*\*Tester:\*\* .+",
        "**Tester:** _name_",
        text,
    )
    text = re.sub(
        r"\*\*Actual duration:\*\* .+",
        "**Actual duration:** _…_",
        text,
    )
    text = re.sub(
        r"\*\*Result:\*\* .+",
        "**Result:** _pending / success / failed_",
        text,
    )
    text = text.replace(
        "./smoke-test-v1-three-os.md",
        "./smoke-test-three-os.md",
    )
    text = re.sub(r"\| ✅ \| ☐ \|", "| ☐ | ☐ |", text)
    text = re.sub(r"\| ✅ \| ✅ \|", "| ☐ | ☐ |", text)

    # Remove filled verdict paragraph
    text = re.sub(
        r"\n\*\*Verdict:\*\* all three criteria are ✅.+$",
        "",
        text,
        flags=re.MULTILINE,
    )

    return text


def main() -> int:
    if len(sys.argv) != 4:
        print("usage: blanken-qa-procedure.py <three-os|windows> <src> <dst>")
        return 1

    kind, src, dst = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    text = src.read_text(encoding="utf-8")
    if kind == "three-os":
        out = blank_three_os(text)
    elif kind == "windows":
        out = blank_windows_addon(text)
    else:
        print(f"unknown kind: {kind}")
        return 1

    dst.write_text(out, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
