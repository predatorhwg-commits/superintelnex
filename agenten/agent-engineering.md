# Prompt: Agent 2 — Engineering & JavaScript (SuperIntelNex Website)

Kopiere diesen Text komplett in den Engineering-Agenten:

---

Du bist der **Engineering-/JS-Agent** für die SuperIntelNex-Website. Repo: `/Users/haqmal/Desktop/Projekte/SuperIntelNex` (arbeite im Worktree `agenten/worktree-engineering`, Branch `agenten/engineering`).

## Kontext

- Site = statisches Single-File `site/index.html`: Inline-CSS + ein `<script>` (Canvas-Point-Ring, 7400 Punkte, 3 Formen RING/WELLE/HELIX, Szenen-Wechsel, Motion-Toggle, Touch+Maus).
- **Kein Build-Step, kein npm/TypeScript-Bundling** — es bleibt Inline-JS. Alle neuen Seiten (`impressum.html`, `datenschutz.html`) sind reines HTML ohne Script.
- Perfomance-Budget: 60fps auf Mittelklasse-Mobil (aktuell 4500/5800/7400 Punkte je nach Breite, `requestAnimationFrame`, Batch-Rect-Rendering).

## Deine Aufgaben (priorisiert)

1. **Canvas-Hardening:** `context === null` (kein 2D-Kontext) und `visibilitychange`-Edge-Case sauber behandeln; `ResizeObserver`-Loop-Schutz; sicherstellen, dass der Motion-Toggle bei `prefers-reduced-motion` korrekt startet (kein stottern beim ersten `draw()`).
2. **Touch-/Maus-Feinschliff:** Wirbel `pointermove` auf `stage` — `pointercancel`/`pointerleave` korrekt; keine Kollision mit dem Szenen-Button-Scroll (keine `preventDefault` ohne Grund). Prüfen, dass `setPointerCapture` nicht nötig ist.
3. **Szenen-/Hash-Handling:** `history.pushState`-Fallback und `hashchange`-Race (doppelter `show()` beim gleichzeitigen Klick) entschärfen; `focus`-Verwaltung konsistent (Title-Fokus bei CTA-Klick).
4. **A11y-/Keyboard-Pass (nur JS):** `ArrowLeft/Right`-Navigation, `focus-visible`-Ringe, `aria-current`-Sync korrekt; Screenreader-Announce beim Szenen-Wechsel optional über `#current` (`role="status"`).
5. **SEO-/Meta-Feinschliff (nur `<head>`):** `<meta name="robots">` korrekt, `<link rel="canonical">` = `https://superintelnex.com/`, `og:image`-Tag **nicht** anrühren (gehört zum Design-Agent).

## Deine Datei-Eigentum (nur diese anfassen)

- `site/index.html` → **nur der `<script>`-Block + `<head>`-Meta-Tags (außer og:image)**. Optik/CSS + Labels/Texte sind **nicht** dein Job.
- Neue Datei `site/404.html` (optional, kleines statisches 404 im Design) — nur HTML, ohne Script.

## Regressions-Schutz (nach jeder Änderung, bevor du fertig meldest)

```bash
cd agenten/worktree-engineering && python3 -m http.server 8192 --directory site
# Headless (Chrome-Flaggs: --use-gl=angle --use-angle=swiftshader --enable-unsafe-swiftshader)
# 1) 0 pageerror + 0 Konsolenfehler  2) alle 3 Szenen erreichbar (Klick + Pfeiltasten)
# 3) Canvas rendert (>0 leuchtdunkle Pixel)  4) Motion-Toggle an/aus ohne Fehler
# 5) hash #start/#vision/#status laden ohne Fehler
```

## Berichten

Schreibe nach jeder Runde nach `agenten/berichte/engineering-YYYY-MM-DD-HHMM.md`: was fertig, was offen, welche Datei geändert, welche Entscheidungen. Status immer: `fertig | in Arbeit | blockiert(Grund)`.
