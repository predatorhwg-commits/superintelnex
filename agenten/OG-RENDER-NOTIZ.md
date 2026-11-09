# OG-Image: Re-Render-Pfad (Offiziell)

**Kurz:** `site/og-image.png` (1200×630, 57.712 B) wird **deterministisch** aus
`agenten/og-render.html` gerendert. Das PNG ist ein statisches Artefakt — die
Render-Datei ist die alleinige Quelle (Playwright-Snippet, kein Build-Tool).

## Warum wichtig
- `agenten/render-og.swift` wurde vom CEO **bewusst entfernt** (KONFLIKT-4: untracked,
  nicht eigen, kompiliert nicht). **Playwright-Render ist der offizielle Weg.**
- Bei einer Bild-Änderung (z. B. neuer Eyebrow-Text, Design-Austausch):
  immer Re-Render aus `og-render.html`, **niemals** per Hand/extern ein PNG reinpacken.

## Determinismus
- LCG-Seed **349112** (identisch zum Site-Canvas-Seed, `site/index.html`) —
  Re-Render = identisches Punktmuster (Tiefen-Banding, weiße Rechteck-Partikel).
- Layout: Textblock links (Titel + Eyebrow + „FIG. 01 / RING — superintelnex.com"),
  Punktring rechts — asymmetrisch wie die Site bei Desktop, gleiche Arial/ui-monospace-
  Font-Familie wie die Site.

## Re-Render-Befehl (Playwright, System-Python 3.9)
```python
from playwright.sync_api import sync_playwright
import glob

CHROME = sorted(glob.glob(
    "/Users/haqmal/Library/Caches/ms-playwright/chromium-*/chrome-mac-arm64/"
    "Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"))[-1]

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME, headless=True,
        args=["--no-sandbox", "--use-gl=angle", "--use-angle=swiftshader",
              "--enable-unsafe-swiftshader"])
    pg = b.new_page(viewport={"width": 1200, "height": 630})
    pg.goto("file:///Users/haqmal/Desktop/Projekte/SuperIntelNex/agenten/og-render.html")
    pg.wait_for_timeout(500)  # Canvas-First-Frame wartbar
    pg.screenshot(path="site/og-image.png")
    b.close()
```
→ Überprüft danach: PNG-Größe (PIL), 1200×630, >10 KB; danach `run-gate.sh`
(Check C7: OG-Image 1200×630 + >10KB).

## Meta-Tag
`site/index.html` (1 Zeile, Task 3 Design):
```html
<meta property="og:image" content="https://superintelnex.com/og-image.png">
```
(wird vom QA-Gate C7 per Datei-Check + OG-Tag-Präsenz kontrolliert — Tag ist aktuell
vorhanden.)
