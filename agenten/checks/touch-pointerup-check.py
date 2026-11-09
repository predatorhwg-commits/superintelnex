#!/usr/bin/env python3
"""Engineering-Hilfe (Hinweis 3): Touch-pointerup-Verifikation per Headless-DISPATCH.

Prueft den pointerup-Fix (site/index.html:
  stage.addEventListener('pointerup', e => {if (e.pointerType !== 'mouse') releasePointer();}))
ohne echtes Touch-Device.

VORAUSSETZUNG (Engineering-Test-Hebel, 1 Zeile in index.html):
    window.__sinxPointer = () => ({inside: pointer.inside, strength: pointer.strength});
  (read-only Snapshot, null Verhaltensaenderung). Fehlt der Hebel -> Check 1-3 FAILen
  sichtbar mit 'CLOSURE-NOT-ACCESSIBLE' (nicht still).

WARUM dispatchEvent (nicht Playwright-API):
  - Playwright sendet Pointer-Events per Default mit pointerType='mouse' —
    der Fix ist im Maus-Pfad INKT aktiv (pointerup(mouse) wird ignoriert).
  - Der Check muss die Touch-Events selbst bauen (PointerEvent, pointerType:'touch').
  - pointer = IIFE-Local, nur ueber den Test-Hebel beobachtbar.

CHECKS:
  1) pointermove(touch)       -> inside === true
  2) pointerup(touch)         -> inside === false   (DER FIX: Finger-Release loescht)
  3) pointermove + pointerup(mouse) -> inside bleibt true (Maus-Pfad unveraendert:
     Wirbel bleibt aktiv bis pointerleave)
  4) 0 pageerror / 0 console-errors waehrend der Sequenz.

Exit: 0 = alle 4 PASS, 1 = mind. 1 FAIL, 2 = Umgebungsfehler.

Aufruf:
  cd /Users/haqmal/Desktop/Projekte/SuperIntelNex
  python3 -m http.server 8193 --directory site &
  python3 agenten/checks/touch-pointerup-check.py
"""
import glob, sys

from playwright.sync_api import sync_playwright

CHROME = glob.glob(
    "/Users/haqmal/Library/Caches/ms-playwright/chromium-*/chrome-mac-arm64/"
    "Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing")
BASE = "http://localhost:8193"

DISPATCH = """([type, pointerType]) => {
    const stage = document.querySelector('#stage');
    const r = stage.getBoundingClientRect();
    stage.dispatchEvent(new PointerEvent(type, {
        pointerType, bubbles: true,
        clientX: r.left + r.width / 2, clientY: r.top + r.height / 2
    }));
    if (typeof window.__sinxPointer !== 'function') return 'CLOSURE-NOT-ACCESSIBLE';
    return window.__sinxPointer().inside;
}"""

fails = []
def check(name, ok, detail):
    print(f"  {'PASS' if ok else 'FAIL'}  {name}" + (f"  [{detail}]" if not ok else ""))
    if not ok:
        fails.append(name)

def main():
    if not CHROME:
        print("FEHLER: Chromium-Bundle nicht gefunden")
        sys.exit(2)
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=sorted(CHROME)[-1], headless=True,
            args=["--no-sandbox", "--use-gl=angle", "--use-angle=swiftshader",
                  "--enable-unsafe-swiftshader"])
        page = browser.new_page(viewport={"width": 1280, "height": 800})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.goto(BASE + "/index.html", wait_until="networkidle")
        page.wait_for_timeout(500)

        v1 = page.evaluate(DISPATCH, ["pointermove", "touch"])
        check("1) pointermove(touch) -> inside=true", v1 is True, f"ist {v1!r}")

        v2 = page.evaluate(DISPATCH, ["pointerup", "touch"])
        check("2) pointerup(touch) -> inside=false (Fix aktiv)", v2 is False, f"ist {v2!r}")

        page.evaluate(DISPATCH, ["pointermove", "mouse"])
        v3 = page.evaluate(DISPATCH, ["pointerup", "mouse"])
        check("3) pointerup(mouse) -> inside bleibt true (Maus-Pfad unveraendert)",
              v3 is True, f"ist {v3!r}")

        check("4) 0 pageerror / 0 console-errors", not errors, "; ".join(errors[:3]))
        browser.close()

    print(f"\n==== ERFEGNIS: {4 - len(fails)}/4 PASS ({len(fails)} FAIL) ====")
    for f in fails:
        print(f"  FAIL: {f}")
    sys.exit(0 if not fails else 1)

if __name__ == "__main__":
    main()
