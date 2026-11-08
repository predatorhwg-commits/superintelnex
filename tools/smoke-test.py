#!/usr/bin/env python3
"""Funktionstest im Browser: prueft die Bedienung, nicht das Aussehen.

Geprueft werden auf der Startseite:
  1. Seite laedt ohne Konsolenfehler
  2. Mobile-Navigation oeffnet, schliesst per Escape und gibt den Fokus zurueck
  3. Sprunglink zielt auf #main
  4. Alle Anker der Navigation existieren
  5. Scroll-Reveal wird aktiviert (kein Element bleibt unsichtbar)
  6. Footer-Jahreszahl ist gesetzt
  7. Risikohinweis ist im sichtbaren Text vorhanden

Aufruf:
    python3 tools/smoke-test.py [basis-url]

Exit 0 = alles gruen, Exit 1 = mindestens ein Fehlschlag.
"""
from __future__ import annotations

import glob
import os
import sys

from playwright.sync_api import sync_playwright

DEFAULT_BASE = "http://127.0.0.1:8188"


def find_chrome() -> str | None:
    patterns = [
        os.path.expanduser(
            "~/Library/Caches/ms-playwright/chromium-*/chrome-mac-arm64/"
            "Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"
        ),
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
    ]
    for pat in patterns:
        hits = sorted(glob.glob(pat))
        if hits:
            return hits[-1]
    return None


class Checks:
    def __init__(self) -> None:
        self.results: list[tuple[bool, str]] = []

    def add(self, ok: bool, label: str, detail: str = "") -> None:
        self.results.append((ok, label if not detail else f"{label} — {detail}"))

    def report(self) -> int:
        passed = sum(1 for ok, _ in self.results if ok)
        print(f"Prüfungen: {passed}/{len(self.results)} grün\n")
        for ok, label in self.results:
            print(f"  {'[ok]' if ok else '[FEHLER]'} {label}")
        return 0 if passed == len(self.results) else 1


def main() -> int:
    base = (sys.argv[1] if len(sys.argv) > 1 else DEFAULT_BASE).rstrip("/")
    exe = find_chrome()
    if not exe:
        print("FEHLER: kein Chromium/Chrome gefunden.")
        return 1

    c = Checks()
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=exe)
        ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        errors: list[str] = []
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: errors.append(str(e)))

        page.goto(f"{base}/", wait_until="load")
        page.wait_for_timeout(400)

        # 1) Konsolenfehler
        c.add(not errors, "Keine Konsolenfehler", "; ".join(errors[:3]))

        # 2) Anker der Navigation
        anchors = page.eval_on_selector_all(
            ".site-nav a[href^='#']", "els => els.map(e => e.getAttribute('href'))"
        )
        missing = [
            a
            for a in anchors
            if not page.evaluate("h => !!document.querySelector(h)", a)
        ]
        c.add(bool(anchors) and not missing,
              f"Alle {len(anchors)} Navigationsanker existieren",
              ", ".join(missing))

        # 3) Sprunglink
        skip = page.evaluate(
            """() => {
                const a = document.querySelector('.skip-link');
                if (!a) return 'kein Sprunglink';
                const id = a.getAttribute('href').slice(1);
                return document.getElementById(id) ? null : 'Ziel fehlt: ' + id;
            }"""
        )
        c.add(skip is None, "Sprunglink zeigt auf existierendes Ziel", str(skip or ""))

        # 4) Risikohinweis sichtbar
        risk = page.evaluate(
            """() => {
                const el = document.querySelector('#risiko');
                if (!el) return false;
                const t = (el.innerText || '').toLowerCase();
                return t.includes('risiko') && t.includes('verlust');
            }"""
        )
        c.add(risk, "Risikohinweis vorhanden und sichtbar")

        # 5) Footer-Jahr
        year = page.evaluate("() => (document.getElementById('year')||{}).textContent")
        c.add(bool(year) and year.strip().isdigit(), "Jahreszahl im Footer gesetzt", str(year))

        # 6) Reveal-Elemente werden sichtbar
        total = page.evaluate("() => document.querySelectorAll('.reveal').length")
        # Die Seite abschnittsweise durchrollen, damit der IntersectionObserver
        # jedes Element erreicht. Ein Sprung ans Ende reicht nicht: Elemente
        # in der Bildschirmmitte werden dabei uebersprungen.
        height = page.evaluate("() => document.body.scrollHeight")
        step = 600
        y = 0
        while y < height:
            page.evaluate(f"() => window.scrollTo(0, {y})")
            page.wait_for_timeout(180)
            y += step
        page.wait_for_timeout(900)
        hidden = page.evaluate(
            "() => Array.from(document.querySelectorAll('.reveal'))"
            ".filter(e => !e.classList.contains('is-visible')).length"
        )
        c.add(total > 0 and hidden == 0,
              f"Alle {total} Reveal-Elemente werden aktiviert", f"{hidden} blieben unsichtbar")

        # 7) Mobile Navigation
        mctx = browser.new_context(viewport={"width": 390, "height": 844})
        mpage = mctx.new_page()
        mpage.goto(f"{base}/", wait_until="load")
        mpage.wait_for_timeout(300)

        toggle = mpage.query_selector(".nav-toggle")
        c.add(toggle is not None, "Mobile-Menü-Knopf vorhanden")
        if toggle:
            toggle.click()
            mpage.wait_for_timeout(400)
            opened = mpage.evaluate(
                "() => document.getElementById('site-nav').classList.contains('is-open')"
            )
            c.add(opened, "Mobile-Navigation öffnet")

            mpage.keyboard.press("Escape")
            mpage.wait_for_timeout(400)
            closed = mpage.evaluate(
                "() => !document.getElementById('site-nav').classList.contains('is-open')"
            )
            c.add(closed, "Escape schließt die Mobile-Navigation")

            focused = mpage.evaluate(
                "() => document.activeElement && document.activeElement.className"
            )
            c.add("nav-toggle" in str(focused),
                  "Fokus kehrt zum Menü-Knopf zurück", str(focused))

        mctx.close()
        ctx.close()
        browser.close()

    return c.report()


if __name__ == "__main__":
    sys.exit(main())
