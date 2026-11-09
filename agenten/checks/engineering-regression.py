#!/usr/bin/env python3
"""Engineering-Regression-Skript (SuperIntelNex, site/index.html).

Prueft exakt die Gates aus agent-engineering.md (Sektion "Regressions-Schutz"):
  1) 0 pageerror + 0 Konsolenfehler (error-level)
  2) alle 3 Szenen erreichbar (Klick + Pfeiltasten)
  3) Canvas rendert (>0 leuchtdunkle Pixel auf #dust)
  4) Motion-Toggle an/aus ohne Fehler
  5) hash #start/#vision/#status laden ohne Fehler

Voraussetzung: lokaler Server  http://localhost:8192  (python3 -m http.server 8192 --directory site)
Chrome: Google Chrome for Testing mit SwiftShader-Flaggs (kein GPU-Loellstand).

Exit 0 = alle Gates gruen, Exit 1 = rot (Fehlerliste am Ende).
"""
import sys, glob, time
from playwright.sync_api import sync_playwright

BASE = "http://localhost:8192"
SCENES = [("start", "SuperIntelNex | Start"), ("vision", "SuperIntelNex | Vision"), ("status", "SuperIntelNex | Projektstatus")]
failures = []

def chrome_bin():
    for pattern in [
        "/Users/haqmal/Library/Caches/ms-playwright/chromium-*/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing",
        "/Users/haqmal/Library/Caches/ms-playwright/chromium-*/chrome-mac-x64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing",
    ]:
        hits = sorted(glob.glob(pattern))
        if hits:
            return hits[0]
    return None  # Playwright-Default

def check(cond, label):
    print(("  [OK] " if cond else "  [FAIL] ") + label)
    if not cond:
        failures.append(label)

def collect_errors(page):
    errs = []
    page.on("pageerror", lambda e: errs.append("pageerror: %s" % e))
    page.on("console", lambda m: errs.append("console: %s" % m.text) if m.type == "error" else None)
    return errs

def canvas_lit_pixels(page):
    """Anzahl nicht-schwarzer (leuchtender) Pixel im Canvas-Backbuffer."""
    return page.evaluate(
        """() => {
            const c = document.querySelector('#dust');
            if (!c) return -1;
            const cx = c.getContext('2d', { alpha: true });
            const w = c.width, h = c.height;
            if (!w || !h) return -1;
            const d = cx.getImageData(0, 0, w, h).data;
            let n = 0;
            for (let i = 3; i < d.length; i += 4) if (d[i] > 0) n++;
            return n;
        }"""
    )

def run():
    binpath = chrome_bin()
    if binpath:
        print("Chrome:", binpath)
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path=binpath,
            args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"],
        )
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        errs = collect_errors(page)
        page.goto(BASE + "/index.html")
        page.wait_for_timeout(1200)  # erste Frames + resize-Callback

        # Gate 1: laeding ohne Fehler
        check(not errs, "Gate 1: Init-Lade ohne pageerror/Konsolenfehler (%s)" % len(errs))
        for e in errs: print("       ", e)

        # Gate 3: Canvas rendert
        n = canvas_lit_pixels(page)
        check(n > 0, "Gate 3: Canvas rendert, leuchtdunkle Pixel = %d" % n)

        # Gate 2: Szenen via Klick — pro Szene frische Lade, damit der Klick
        # immer eine echte Szenen-Wechsel triggert und der Hash-Write getestet wird.
        # Ausnahme: idx 0 (Start) ist bei einer frischen Lade die aktive Szene —
        # der Klick ist ein Early-Return ohne Hash-Write (Design-Entscheidung:
        # kein redundanter pushState). Der #start-Hash-Write wird unten separiert
        # von einer anderen Szene getestet.
        for idx, (sid, title) in enumerate(SCENES):
            page.goto(BASE + "/index.html"); page.wait_for_timeout(700)
            page.click("nav button[data-go='%d']" % idx)
            page.wait_for_timeout(400)
            ok_scene = page.evaluate("i => document.getElementById(i) && !document.getElementById(i).hidden", sid)
            ok_title = page.title() == title
            ok_hash = page.evaluate("() => location.hash") == "#" + sid
            check(ok_scene, "Gate 2 (Klick): Szene #"+sid+" sichtbar")
            check(ok_title, "Gate 2 (Klick): #"+sid+" Titel = '"+title+"' (ist '"+page.title()+"')")
            if idx == 0:
                check(page.evaluate("() => location.hash") == "", "Gate 2 (Klick): #start-Klick auf aktiver Szene = kein Hash-Write (Early-Return)")
            else:
                check(ok_hash, "Gate 2 (Klick): #"+sid+" Hash = '#"+sid+"' (ist '"+page.evaluate("() => location.hash")+"')")
        # #start-Hash-Write nach einem echten Wechsel
        page.goto(BASE + "/index.html#vision"); page.wait_for_timeout(700)
        page.click("nav button[data-go='0']"); page.wait_for_timeout(400)
        check(page.evaluate("() => location.hash") == "#start", "Gate 2 (Klick): #vision -> Start-Klick schreibt '#start' (ist '"+page.evaluate("() => location.hash")+"')")
        check(not errs, "Gate 2: Navigation per Klick ohne Fehler")

        # Gate 2 (b): Szenen via Pfeiltasten
        page.goto(BASE + "/index.html"); page.wait_for_timeout(800)
        for key in ["ArrowRight", "ArrowRight"]:
            page.keyboard.press(key); page.wait_for_timeout(400)
        check(page.evaluate("() => !document.getElementById('status').hidden"), "Gate 2 (Pfeil): ArrowRight x2 -> #status")
        for _ in range(2):
            page.keyboard.press("ArrowLeft"); page.wait_for_timeout(400)
        check(page.evaluate("() => !document.getElementById('start').hidden"), "Gate 2 (Pfeil): ArrowLeft x2 -> #start")
        check(not errs, "Gate 2: Pfeiltasten-Navigation ohne Fehler")

        # Gate 4: Motion-Toggle an/aus
        before = page.get_attribute("#motion", "aria-pressed")
        page.click("#motion"); page.wait_for_timeout(300)
        after = page.get_attribute("#motion", "aria-pressed")
        check(before != after, "Gate 4: Motion-Toggle wirft aria-pressed ('%s' -> '%s')" % (before, after))
        n2 = canvas_lit_pixels(page)
        check(n2 > 0, "Gate 4: Static-Frame rendert nach Toggle aus (Pixel = %d)" % n2)
        page.click("#motion"); page.wait_for_timeout(600)
        n3 = canvas_lit_pixels(page)
        check(n3 > 0, "Gate 4: Animation rendert wieder nach Toggle rein (Pixel = %d)" % n3)
        check(not errs, "Gate 4: Motion-Toggle ohne Fehler")

        # Gate 5: Hash-URLs laden
        for sid, _ in SCENES:
            page.goto(BASE + "/index.html#" + sid); page.wait_for_timeout(700)
            ok = page.evaluate("s => !document.getElementById(s).hidden", sid)
            check(ok, "Gate 5: /#%s laedt Szene #%s" % (sid, sid))
        check(not errs, "Gate 5: Hash-Ladungen ohne Fehler")

        browser.close()

    print()
    if failures:
        print("REGRESSION: ROT — %d Fehler" % len(failures))
        for f in failures: print("  -", f)
        sys.exit(1)
    print("REGRESSION: GRUEN — alle 5 Gates bestanden")

if __name__ == "__main__":
    run()
