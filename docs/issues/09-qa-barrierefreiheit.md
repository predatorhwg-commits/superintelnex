---
id: qa-barrierefreiheit
titel: "Barrierefreiheit vertiefen"
status: offen
rolle: qa
labels: bereich:qualitaet,rolle:qa,status:offen
dateien: "index.html, css/style.css, docs/A11Y.md, impressum.html, datenschutz.html, en/index.html"
---

# Barrierefreiheit vertiefen

## Ziel

Die Zielgruppe umfasst Menschen, die mit Screenreader arbeiten. Die
Barrierefreiheit wird an der **fertigen** Seite gemessen, nicht an einer
Zwischenstufe, weil Fokusreihenfolge und Kontrast vom Textumbau abhängen.

## Konkrete Ergebnisse

- [ ] `tools/a11y-audit.py` meldet 0 Befunde auf allen Seiten.
- [ ] Alle interaktiven Elemente haben einen zugänglichen Namen.
- [ ] Der Fokusring ist auf hellem und dunklem Grund sichtbar.
- [ ] Die gemessenen Kontrastwerte stehen in `docs/A11Y.md`.

## Abnahmekriterien

- [ ] `tools/a11y-audit.py` meldet **0 Befunde** auf allen Seiten.
- [ ] Alle interaktiven Elemente haben einen zugänglichen Namen.
- [ ] Der Fokusring ist auf hellem **und** dunklem Grund sichtbar
      (Mindestkontrast 3:1 gegen beide Flächen).
- [ ] Textkontrast durchgehend ≥ 4.5:1, große Schrift ≥ 3:1. Die Werte werden
      **gemessen**, nicht geschätzt, und je Element in `docs/A11Y.md`
      notiert.
- [ ] Die Mobile-Navigation ist mit der Tastatur bedienbar, `Escape` schließt
      sie, der Fokus kehrt zum Knopf zurück.
- [ ] `prefers-reduced-motion: reduce` schaltet alle Animationen ab. Geprüft.
- [ ] Die Seite ist ohne JavaScript nutzbar: Inhalt vollständig lesbar,
      Navigation erreichbar. Geprüft und in `docs/A11Y.md` protokolliert.
- [ ] Kein ARIA-Attribut, das nur dekorativ wirkt (`aria-label` an einem
      `<div>` ohne Rolle).
- [ ] `python3 tools/release-check.py http://127.0.0.1:8188` ist grün.

## Abhängigkeiten

- **Kommt zuletzt.** Setzt die Endstände von #9,
  #10, #11 und #5 voraus, weil alle
  vier Aufgaben `index.html` bzw. die Unterseiten verändern.
- **Berührt `css/style.css`:** Koordination mit #10. Empfohlen:
  Design liefert die Fokusring- und Kontrastbasis, QA misst und korrigiert.
- **Berührt `index.html`:** Letzte Rolle an dieser Datei.

## Zuständige Rolle

Qualitätssicherung. Dieselbe Rolle wie #8, aber ein anderer
Arbeitsbereich: hier die Seite, dort die Werkzeuge.

## Betroffene Dateien und Bereiche

| Datei | Art der Änderung |
|---|---|
| `index.html` | ARIA, Landmarks, Fokusreihenfolge |
| `css/style.css` | Fokusringe, Kontrast |
| `docs/A11Y.md` | neu: Prüfprotokoll, gemessene Werte, verbleibende Lücken |
| `impressum.html`, `datenschutz.html`, `en/index.html` | geprüft, bei Bedarf korrigiert |

## Nicht tun

- Keine ARIA-Attribute setzen, die nur dekorativ aussehen.
- Keine Kontrastwerte schätzen; ohne Messung gilt das Kriterium als nicht
  erfüllt.
