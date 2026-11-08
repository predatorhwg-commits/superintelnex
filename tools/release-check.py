#!/usr/bin/env python3
"""Freigabepruefung: buendelt alle Pruefungen in einem Lauf.

Aufruf:
    python3 tools/release-check.py [basis-url] [--fast]

  --fast   ueberspringt die Browserpruefungen (schneller, aber unvollstaendig)

Der Server muss laufen:
    python3 -m http.server 8188

Exit 0 = alle Pruefungen gruen, Exit 1 = mindestens eine rot.
"""
from __future__ import annotations

import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def run(label: str, cmd: list[str], optional: bool = False) -> tuple[bool, str, float]:
    start = time.time()
    print(f"\n>>> {label}")
    print(f"    {' '.join(cmd)}")
    try:
        proc = subprocess.run(
            cmd, cwd=ROOT, capture_output=True, text=True, timeout=300
        )
    except subprocess.TimeoutExpired:
        print("    ! Zeitueberschreitung")
        return False, "Zeitueberschreitung", time.time() - start

    out = (proc.stdout or "") + (proc.stderr or "")
    for line in out.strip().splitlines():
        print(f"    {line}")
    dur = time.time() - start
    ok = proc.returncode == 0
    if not ok and optional:
        print("    (optional, wird nicht gewertet)")
    return ok, out, dur


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    fast = "--fast" in sys.argv
    base = args[0] if args else "http://127.0.0.1:8188"

    print("=" * 68)
    print("SuperIntelNex — Freigabepruefung")
    print(f"Server: {base}   Modus: {'fast' if fast else 'voll'}")
    print("=" * 68)

    results: list[tuple[str, bool, float, bool]] = []

    # 1) Python-Syntax aller Werkzeuge
    scripts = sorted(
        os.path.join("tools", f)
        for f in os.listdir(os.path.join(ROOT, "tools"))
        if f.endswith(".py")
    )
    ok, out, dur = run(
        "Python-Syntax aller Werkzeuge",
        [sys.executable, "-m", "py_compile", *scripts],
    )
    results.append(("Python-Syntax", ok, dur, False))

    # 2) Markup
    ok, out, dur = run("Markup-Struktur", [sys.executable, "tools/verify-markup.py"])
    results.append(("Markup", ok, dur, False))

    # 3) Inhalt
    ok, out, dur = run("Inhaltsregeln", [sys.executable, "tools/verify-content.py"])
    results.append(("Inhalt", ok, dur, False))

    # 4) Links
    ok, out, dur = run(
        "Interne Links und Anker", [sys.executable, "tools/check-links.py", ".", base]
    )
    results.append(("Links", ok, dur, False))

    if not fast:
        # 5) Sweep
        ok, out, dur = run("Ueberlauf-Sweep", [sys.executable, "tools/sweep.py", base])
        results.append(("Sweep", ok, dur, False))

        # 6) Smoke
        ok, out, dur = run("Funktionstest", [sys.executable, "tools/smoke-test.py", base])
        results.append(("Funktionstest", ok, dur, False))

        # 7) A11y
        ok, out, dur = run("Barrierefreiheit", [sys.executable, "tools/a11y-audit.py", base])
        results.append(("Barrierefreiheit", ok, dur, False))

    print("\n" + "=" * 68)
    print("Ergebnis")
    print("=" * 68)
    for label, ok, dur, _ in results:
        print(f"  {'[ok]    ' if ok else '[FEHLER]'} {label:24} {dur:5.1f}s")

    failed = [label for label, ok, _, _ in results if not ok]
    print()
    if failed:
        print(f"{len(failed)} von {len(results)} Pruefungen rot: {', '.join(failed)}")
        return 1
    print(f"Alle {len(results)} Pruefungen gruen — bereit fuer den Push.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
