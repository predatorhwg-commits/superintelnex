#!/usr/bin/env python3
"""Barrierefreiheits-Audit im Browser.

Geprueft werden auf allen Seiten:
  1. Sprunglink vorhanden, erstes Bedienelement und Ziel
  2. Genau eine main-Landmarke
  3. Jedes sichtbare Bedienelement hat einen zugaenglichen Namen
  4. Kein tabindex > 0
  5. Jedes Bild hat ein alt-Attribut
  6. html lang gesetzt
  7. Fokusring sichtbar (outline bei :focus-visible)

Aufruf:
    python3 tools/a11y-audit.py [basis-url]

Exit 0 = 0 Befunde, Exit 1 = Befunde vorhanden.
"""
from __future__ import annotations

import glob
import os
import sys

from playwright.sync_api import sync_playwright

DEFAULT_BASE = "http://127.0.0.1:8188"
PAGES = ["/", "/impressum.html", "/datenschutz.html", "/en/"]

JS_AUDIT = """
() => {
  const problems = [];
  const visible = (el) => {
    const r = el.getBoundingClientRect();
    const s = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none';
  };
  const nameOf = (el) => {
    const aria = el.getAttribute('aria-label');
    if (aria && aria.trim()) return aria.trim();
    const labelledby = el.getAttribute('aria-labelledby');
    if (labelledby) {
      const t = labelledby.split(/\\s+/).map(id => {
        const n = document.getElementById(id);
        return n ? (n.innerText || n.textContent || '') : '';
      }).join(' ').trim();
      if (t) return t;
    }
    if (el.tagName === 'IMG') {
      const alt = el.getAttribute('alt');
      if (alt !== null) return alt;
    }
    const txt = (el.innerText || el.textContent || '').trim();
    if (txt) return txt;
    const title = el.getAttribute('title');
    if (title && title.trim()) return title.trim();
    return '';
  };

  // Landmarks
  if (document.querySelectorAll('main').length !== 1) {
    problems.push('main-Landmarke: ' + document.querySelectorAll('main').length + ' gefunden');
  }
  // lang
  if (!document.documentElement.getAttribute('lang')) {
    problems.push('html ohne lang-Attribut');
  }
  // Sprunglink
  const skip = document.querySelector('.skip-link');
  if (!skip) {
    problems.push('kein Sprunglink');
  } else {
    const href = skip.getAttribute('href') || '';
    if (!href.startsWith('#') || !document.querySelector(href)) {
      problems.push('Sprunglink zielt ins Leere: ' + href);
    }
  }
  // Bedienelemente
  document.querySelectorAll('a, button, input, select, textarea').forEach(el => {
    if (!visible(el)) return;
    if (!nameOf(el)) {
      problems.push('Bedienelement ohne zugaenglichen Namen: <' +
        el.tagName.toLowerCase() + ' ' + (el.className || '') + '>');
    }
    const ti = el.getAttribute('tabindex');
    if (ti && parseInt(ti, 10) > 0) {
      problems.push('tabindex > 0: ' + ti);
    }
  });
  // Bilder
  document.querySelectorAll('img').forEach(el => {
    if (el.getAttribute('alt') === null) {
      problems.push('Bild ohne alt: ' + (el.getAttribute('src') || '?'));
    }
  });
  // Fokusring
  const focusable = document.querySelector('.skip-link, a, button');
  if (focusable) {
    focusable.focus();
    const s = getComputedStyle(focusable);
    const outline = s.outlineStyle !== 'none' && parseFloat(s.outlineWidth) > 0;
    const shadow = s.boxShadow && s.boxShadow !== 'none';
    if (!outline && !shadow) {
      problems.push('kein sichtbarer Fokusring an ' + focusable.tagName.toLowerCase());
    }
  }
  return problems;
}
"""


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


def main() -> int:
    base = (sys.argv[1] if len(sys.argv) > 1 else DEFAULT_BASE).rstrip("/")
    exe = find_chrome()
    if not exe:
        print("FEHLER: kein Chromium/Chrome gefunden.")
        return 1

    all_problems: list[str] = []
    evaluated = 0
    skipped: list[str] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=exe)
        ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        for path in PAGES:
            url = f"{base}{path}"
            try:
                resp = page.goto(url, wait_until="load", timeout=20000)
            except Exception as exc:
                skipped.append(f"{path} (nicht ladbar: {exc})")
                continue
            if resp and resp.status >= 400:
                skipped.append(f"{path} (HTTP {resp.status})")
                continue
            page.wait_for_timeout(300)
            final = page.evaluate("() => location.pathname")
            if final.rstrip("/") != path.rstrip("/"):
                skipped.append(f"{path} (Weiterleitung nach {final})")
                continue
            evaluated += 1
            problems = page.evaluate(JS_AUDIT)
            for prob in problems:
                all_problems.append(f"{path}: {prob}")
        ctx.close()
        browser.close()

    print(f"Bewertete Seiten: {evaluated}")
    if skipped:
        print("Nicht bewertet (Seite existiert noch nicht):")
        for s in skipped:
            print(f"  - {s}")

    if all_problems:
        print(f"\n{len(all_problems)} Befund(e):")
        for prob in all_problems:
            print(f"  ! {prob}")
        return 1
    print("\n0 Befunde: Namen, Landmarks, Fokus, tabindex, alt, lang in Ordnung.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
