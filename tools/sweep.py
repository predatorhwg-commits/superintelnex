#!/usr/bin/env python3
"""Misst horizontales Ueberlaufen in Chromium, ueber mehrere Breiten.

Aufruf:
    python3 tools/sweep.py [basis-url] [breiten]

Breiten sind per Komma getrennt (Standard: 1440 1280 768 390). Fuer jede Seite
und Breite wird documentElement.scrollWidth gegen clientWidth geprueft.
Zusaetzlich werden Konsolenfehler gezaehlt.
Exit 0 = kein Ueberlauf, Exit 1 = Ueberlauf gefunden.
"""
from __future__ import annotations

import sys

from playwright.sync_api import sync_playwright

DEFAULT_BASE = "http://127.0.0.1:8188"
DEFAULT_WIDTHS = "1440,1280,768,390"
PAGES = ["/", "/impressum.html", "/datenschutz.html", "/en/"]
# Seiten aus den Aufgaben 1 und 3, die noch nicht existieren. Sie werden
# als "noch nicht vorhanden" ausgewiesen und nicht als Fehler gewertet.
OPTIONAL_PAGES = {"/impressum.html", "/datenschutz.html", "/en/"}


def find_chrome() -> str | None:
    import glob
    import os

    patterns = [
        os.path.expanduser(
            "~/Library/Caches/ms-playwright/chromium-*/chrome-mac-arm64/"
            "Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"
        ),
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    ]
    for pat in patterns:
        hits = sorted(glob.glob(pat))
        if hits:
            return hits[-1]
    return None


def main() -> int:
    base = (sys.argv[1] if len(sys.argv) > 1 else DEFAULT_BASE).rstrip("/")
    widths = [
        int(w)
        for w in (sys.argv[2] if len(sys.argv) > 2 else DEFAULT_WIDTHS).split(",")
        if w.strip()
    ]

    exe = find_chrome()
    if not exe:
        print("FEHLER: kein Chromium/Chrome gefunden.")
        return 1

    problems: list[str] = []
    console_errors = 0
    checked = 0
    missing: set[str] = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=exe, args=["--hide-scrollbars"])
        for width in widths:
            ctx = browser.new_context(viewport={"width": width, "height": 900})
            page = ctx.new_page()

            for path in PAGES:
                url = f"{base}{path}"
                try:
                    resp = page.goto(url, wait_until="load", timeout=20000)
                except Exception as exc:
                    problems.append(f"{path}@{width}: Seite nicht ladbar ({exc}).")
                    continue

                # Noch nicht existierende Seiten aus den offenen Aufgaben:
                # ueberspringen, ohne die Konsole zu laden (der 404 selbst
                # wuerde sonst als Konsolenfehler gezaehlt).
                if resp and resp.status == 404 and path in OPTIONAL_PAGES:
                    missing.add(path)
                    continue

                errors: list[str] = []
                page.on(
                    "console",
                    lambda m: errors.append(m.text) if m.type == "error" else None,
                )
                page.on("pageerror", lambda e: errors.append(str(e)))
                page.reload(wait_until="load", timeout=20000)
                page.wait_for_timeout(400)

                inner = page.evaluate("window.innerWidth")
                client = page.evaluate("document.documentElement.clientWidth")
                scroll = page.evaluate("document.documentElement.scrollWidth")

                if inner != width:
                    problems.append(
                        f"{path}@{width}: innerWidth={inner} (Viewport wurde nicht uebernommen)."
                    )
                checked += 1
                if scroll > client:
                    problems.append(
                        f"{path}@{width}: horizontaler Ueberlauf {scroll - client} px "
                        f"(scrollWidth {scroll} > clientWidth {client})."
                    )

                console_errors += len(errors)
                for err in errors:
                    problems.append(f"Konsolenfehler@{width} ({path}): {err}")

            ctx.close()
        browser.close()

    print(f"Geprüfte Kombinationen (Seite × Breite): {checked}")
    print(f"Breiten: {', '.join(str(w) for w in widths)} px")
    print(f"Konsolenfehler: {console_errors}")
    if missing:
        print("Noch nicht vorhanden (offene Aufgaben, nicht gewertet):")
        for path in sorted(missing):
            print(f"  - {path}")
    if problems:
        print(f"\n{len(problems)} Befund(e):")
        for prob in problems:
            print(f"  ! {prob}")
        return 1
    print("\nKein horizontaler Ueberlauf, keine Konsolenfehler.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
