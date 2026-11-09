#!/usr/bin/env python3
"""QA-Hilfe (BUG-01): rAF-Framerate auf echter GPU (ohne SwiftShader-Flags).

Neue Datei — release-gate.py bleibt unverändert.
Exit: 0 = >=50 fps, 1 = <50 fps, 2 = Umgebungsfehler.
Aufruf: python3 agenten/checks/gpu-perf-check.py [BASE_URL]
"""
import glob, sys

from playwright.sync_api import sync_playwright

CHROME = glob.glob(
    "/Users/haqmal/Library/Caches/ms-playwright/chromium-*/chrome-mac-arm64/"
    "Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing")

def main():
    base = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8193"
    if not CHROME:
        print("FEHLER: Chromium-Bundle nicht gefunden")
        sys.exit(2)
    with sync_playwright() as p:
        # bewusst KEINE SwiftShader-Flags -> echter GPU-Pfad
        browser = p.chromium.launch(
            executable_path=sorted(CHROME)[-1], headless=True,
            args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1280, "height": 800})
        try:
            page.goto(base + "/index.html", wait_until="networkidle", timeout=30000)
        except Exception as e:
            print(f"FEHLER: {base} nicht erreichbar: {e}")
            browser.close()
            sys.exit(2)
        page.wait_for_timeout(1000)
        r = page.evaluate("""() => new Promise(resolve => {
            let frames = 0;
            const t0 = performance.now();
            function loop() {
                frames++;
                if (performance.now() - t0 < 5000) requestAnimationFrame(loop);
                else resolve({fps: Math.round((frames / ((performance.now() - t0) / 1000)) * 10) / 10,
                              frames, seconds: Math.round((performance.now() - t0) / 10) / 100});
            }
            requestAnimationFrame(loop);
        })""")
        browser.close()
    fps = r["fps"]
    print(f"GPU-PERF: {fps} fps ({r['frames']} Frames in {r['seconds']}s) — echter GPU-Pfad (keine SwiftShader-Flags)")
    ok = fps >= 50
    print("ERGEBNIS: >=50 fps" if ok else "ERGEBNIS: <50 fps — Profil mit DevTools prüfen (nicht als SwiftShader vermuten)")
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
