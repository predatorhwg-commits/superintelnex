#!/usr/bin/env python3
"""Content-Agent Regressions-Schutz: site/ headless-Check (Playwright + SwiftShader).

Checks (entsprechend agent-content.md):
  - alle 3 Seiten: 0 pageerror, 0 console-errors
  - index: 4 Szenen (1–4) per Klick + Pfeiltasten umschaltbar, tab-titel pro Szene
  - keine toten Buttons (alle data-go führen zu gültiger Szene, prev/next korrekt)
  - 0 Overflow @390px (und @1280px) auf allen Seiten
  - Text-Check: „kein echtes Geld" in Devnet-Eintrag, keine „Anlage"-Zusage
  - canvas rendert (>0 helle Pixel)
Exit 0 = grün, 1 = rot.
"""
import glob, json, re, sys

from playwright.sync_api import sync_playwright

BASE = "http://localhost:8193"
CHROME = sorted(glob.glob(
    "/Users/haqmal/Library/Caches/ms-playwright/chromium-1223/chrome-mac-arm64/"
    "Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"))
SWIFT = ["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"]

results = []

def check(name, ok, detail=""):
    results.append((name, ok, detail))
    print(f"  {'PASS' if ok else 'FAIL'}  {name}" + (f"  [{detail}]" if detail and not ok else ""))

def main():
    fails = []
    with sync_playwright() as p:
        exe = CHROME[0] if CHROME else None
        browser = p.chromium.launch(
            executable_path=exe, headless=True,
            args=SWIFT + ["--no-sandbox"])
        page = browser.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=2)

        # ---------- 1) alle 3 Seiten: 0 pageerror / console-error + Overflow @390 ----------
        for f in ["index.html", "impressum.html", "datenschutz.html"]:
            errors, console_err = [], []
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.on("console", lambda m: console_err.append(m.text) if m.type == "error" else None)
            page.goto(BASE + "/" + f, wait_until="networkidle")
            page.wait_for_timeout(400)
            overflow = page.evaluate(
                "document.documentElement.scrollWidth - document.documentElement.clientWidth")
            check(f"{f}: 0 pageerror", not errors, "; ".join(errors[:3]))
            check(f"{f}: 0 console-errors", not console_err, "; ".join(console_err[:3]))
            check(f"{f}: 0 Overflow @390px", overflow == 0, f"overflow={overflow}")
            page.evaluate("() => { window.__h = null; }")

        # ---------- 2) index: Szenen 1–4 per Klick + Pfeiltasten, Titel pro Szene ----------
        page.goto(BASE + "/index.html", wait_until="networkidle")
        page.wait_for_timeout(400)
        n_scenes = page.evaluate("document.querySelectorAll('.scene').length")
        check("index: 4 Szenen vorhanden", n_scenes == 4, f"scenes={n_scenes}")

        titles = []
        for i in range(4):
            page.evaluate(
                f"Array.from(document.querySelectorAll('nav button[data-go]'))"
                f"[{i}].click()")
            page.wait_for_timeout(350)
            visible = page.evaluate(
                f"(() => {{ const s = document.querySelectorAll('.scene')[{i}]; "
                f"return s && !s.hidden && s.querySelector('h1,h2').getBoundingClientRect().width > 0; }})()")
            aria = page.evaluate(
                f"Array.from(document.querySelectorAll('nav button[data-go]'))"
                f"[{i}].getAttribute('aria-current')")
            title = page.evaluate("document.title")
            titles.append(title)
            check(f"Szene {i+1}: sichtbar + nav aria-current", visible and aria == "page",
                  f"visible={visible} aria={aria}")
        expected_titles = [
            "SuperIntelNex | Start",
            "SuperIntelNex | Vision",
            "SuperIntelNex | Projektstatus",
            "SuperIntelNex | Fragen",
        ]
        for i, t in enumerate(expected_titles):
            check(f"Szene {i+1}: Tab-Titel = {t!r}", titles[i] == t, f"ist {titles[i]!r}")

        # Pfeiltasten: von Szene 1 nach rechts -> 4, nach links -> 1
        page.evaluate("Array.from(document.querySelectorAll('nav button[data-go]'))[0].click()")
        page.wait_for_timeout(200)
        for _ in range(3):
            page.keyboard.press("ArrowRight")
            page.wait_for_timeout(150)
        t_end = page.evaluate("document.title")
        check("Pfeiltasten: 3x ArrowRight lands auf Szene 4", t_end == "SuperIntelNex | Fragen",
              f"title={t_end!r}")
        for _ in range(3):
            page.keyboard.press("ArrowLeft")
            page.wait_for_timeout(150)
        check("Pfeiltasten: 3x ArrowLeft zurück auf Szene 1", page.evaluate("document.title") == "SuperIntelNex | Start")

        # ---------- 3) keine toten Buttons (prev/next + alle data-go) ----------
        page.evaluate("Array.from(document.querySelectorAll('nav button[data-go]'))[0].click()")
        page.wait_for_timeout(200)
        prev_disabled = page.evaluate("document.querySelector('#prev').disabled")
        check("Button-Check: prev auf Szene 1 disabled", prev_disabled is True)
        for i in range(4):
            if i > 0:
                page.evaluate("document.querySelector('#next').click()")
                page.wait_for_timeout(150)
            cur = page.evaluate("document.querySelector('#current').textContent")
            ok = cur == f"{i+1:02d}"
            check(f"Button-Check: next -> Zähler zeigt {i+1:02d}", ok, f"ist {cur}")
        next_disabled_last = page.evaluate("document.querySelector('#next').disabled")
        check("Button-Check: next auf Szene 4 disabled", next_disabled_last is True)

        # CTA-Buttons der Szenen: alle data-go existieren in validem Bereich
        invalid = page.evaluate("""Array.from(document.querySelectorAll('[data-go]'))
            .filter(b => {
                const t = Number(b.dataset.go);
                const scenes = document.querySelectorAll('.scene').length;
                return !Number.isInteger(t) || t < 0 || t >= scenes;
            }).length""")
        check("Button-Check: 0 Buttons mit ungültigem data-go", invalid == 0, f"invalid={invalid}")

        # ---------- 4) Text-Check (index) ----------
        # Alle Szenen lesen (auch die versteckten, via textContent), nicht nur innerText
        all_text = page.evaluate(
            "Array.from(document.querySelectorAll('.scene')).map(s => s.textContent).join('\\n')")
        check("Text-Check: Devnet-Eintrag enthält 'kein echtes Geld'",
              "kein echtes Geld" in all_text)
        page.evaluate("Array.from(document.querySelectorAll('nav button[data-go]'))[2].click()")
        page.wait_for_timeout(250)
        status_text = page.evaluate("document.body.innerText")
        has_anlage = any(w in status_text.lower() for w in
                         ["anlage", "gewinn", "profit", "kurs:"]) and "keine anlage" not in status_text.lower()
        check("Text-Check: keine 'Anlage'-Zusage in Status-Szene", not has_anlage)
        check("Text-Check: 'Emissionsverteuerung' (Tippfehler) nicht mehr vorhanden",
              "Emissionsverteuerung" not in all_text + status_text)
        check("Text-Check: 55/20/15/10 als Emissionsverteilung benannt",
              "Emissionsverteilung" in status_text and "55/20/15/10" in status_text)
        check("Text-Check: 'Prüfung der Rechtslage' bleibt",
              "Prüfung der Rechtslage" in status_text)

        # ---------- 5) canvas rendert (>0 helle Pixel) @1280 ----------
        page.set_viewport_size({"width": 1280, "height": 800})
        page.evaluate("Array.from(document.querySelectorAll('nav button[data-go]'))[0].click()")
        page.wait_for_timeout(1500)
        bright = page.evaluate("""() => {
            const c = document.querySelector('#dust');
            const ctx = c.getContext('2d');
            const d = ctx.getImageData(0, 0, c.width, c.height).data;
            let n = 0;
            for (let i = 0; i < d.length; i += 4) { if (d[i] > 40) n++; }
            return n;
        }""")
        check("Canvas: rendert (>0 helle Pixel @1280)", bright > 0, f"bright={bright}")
        overflow_1280 = page.evaluate(
            "document.documentElement.scrollWidth - document.documentElement.clientWidth")
        check("index: 0 Overflow @1280px", overflow_1280 == 0, f"overflow={overflow_1280}")

        # Impressum/Datenschutz @1280 Overflow
        for f in ["impressum.html", "datenschutz.html"]:
            page.goto(BASE + "/" + f, wait_until="networkidle")
            page.wait_for_timeout(200)
            ov = page.evaluate(
                "document.documentElement.scrollWidth - document.documentElement.clientWidth")
            check(f"{f}: 0 Overflow @1280px", ov == 0, f"overflow={ov}")

        browser.close()

    failed = [r for r in results if not r[1]]
    print(f"\n==== ERFEGNIS: {len(results) - len(failed)}/{len(results)} PASS "
          f"({len(failed)} FAIL) ====")
    if failed:
        for name, _, detail in failed:
            print(f"  FAIL: {name} {detail}")
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()
