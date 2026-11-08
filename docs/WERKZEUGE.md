# Werkzeuge

Alle Prüfwerkzeuge liegen in `tools/` und laufen mit **Python 3.9** (Standard auf
diesem Rechner). Kein `node` nötig, kein Build-Schritt, keine Abhängigkeiten
außer `playwright` (für die Browserprüfungen).

## Gesamtlauf

```bash
cd "/Users/haqmal/Desktop/Projekte/SuperIntelNex"
python3 -m http.server 8188 &          # Server starten
python3 tools/release-check.py http://127.0.0.1:8188
```

`--fast` überspringt die drei Browserprüfungen (Sweep, Smoke-Test, A11y) und
läuft in unter einer Sekunde.

## Übersicht

| Werkzeug | Prüft | Exit 1 wenn |
|---|---|---|
| `release-check.py` | bündelt alle folgenden | eine Prüfung rot |
| `verify-markup.py` | Überschriften, IDs, Landmarks, Sprunglink, `lang`, Bildattribute, Inline-Handler | ein Befund |
| `verify-content.py` | erfundene Angaben, Kauf-Buttons, fehlender Risikohinweis, fehlender „Geplant"-Status | ein Befund |
| `check-links.py` | interne Links, Anker, `alt`-Attribute | toter Verweis |
| `sweep.py` | horizontaler Überlauf, Konsolenfehler | Überlauf oder Fehler |
| `smoke-test.py` | Bedienung: Navigation, Sprunglink, Reveal, Mobile-Menü, Escape, Fokusrückkehr | ein Fehlschlag |
| `a11y-audit.py` | zugängliche Namen, Landmarks, Fokusring, `tabindex`, `lang` | ein Befund |
| `gh-api.py` | GitHub-API ohne `gh` (Issues, PRs, Repo) | API-Fehler |

## Gegenproben

Eine Prüfung, die nie rot wird, ist wertlos. Zu jedem Werkzeug gehört ein
absichtlich fehlerhafter Zustand, der erkannt werden muss.

### `verify-markup.py`

Gegenprobe: eine Datei `test-h1.html` mit zwei `<h1>` und einer doppelten ID
anlegen.

```bash
cat > /tmp/gegenprobe/index.html <<'EOF'
<!doctype html><html lang="de"><body>
<h1 id="a">Eins</h1><h1 id="a">Zwei</h1>
<h4>Sprung</h4>
<img src="x.png">
</body></html>
EOF
python3 tools/verify-markup.py /tmp/gegenprobe
```

Erwartet: Exit 1 mit Befunden zu `h1`, doppelter ID, Überschriftensprung und
fehlendem `alt`.

### `verify-content.py`

Gegenprobe: eine Seite mit einer Kursangabe und einem Kauf-Button.

```bash
cat > /tmp/gegenprobe2/index.html <<'EOF'
<!doctype html><html lang="de"><body><main id="main">
<h1>Test</h1><p>Der Token kostet 0,50 USD und wird bei 12 % Rendite gehandelt.</p>
<p>Risiko: Verlust moeglich. Geplant.</p>
<button>Jetzt kaufen</button>
</main></body></html>
EOF
python3 tools/verify-content.py /tmp/gegenprobe2
```

Erwartet: Exit 1 mit Befunden für Preisangabe, Renditeversprechen, Kauf-Button
und fehlenden Risikohinweis.

Gegenprobe zur Negations-Ausnahme: `Keine „Jetzt kaufen"-Schaltflächen` darf
**kein** Befund sein. Der aktuelle Text auf der Startseite belegt das.

### `check-links.py`

Gegenprobe: in `index.html` einen Link auf `#gibtsnicht` setzen und einen auf
eine nicht existierende Datei `fehlt.html`.

Erwartet: Exit 1 mit beiden Meldungen.

### `sweep.py`

Gegenprobe: in `css/style.css` eine Regel `body { width: 3000px; }` ergänzen.

Erwartet: Exit 1 mit „horizontaler Ueberlauf" bei allen Breiten.

### `smoke-test.py`

Gegenprobe: in `js/main.js` den Block `setNav(false)` beim Escape entfernen.

Erwartet: Exit 1 bei „Escape schließt die Mobile-Navigation".

### `a11y-audit.py`

Gegenprobe: einem Button den Text entfernen (`<button aria-label=""></button>`).

Erwartet: Exit 1 mit „Bedienelement ohne zugaenglichen Namen".

## Konventionen für neue Prüfungen

1. Sprechende Fehlermeldung mit **Seitenname** und **konkretem Ort**.
2. Exit 0 bei Erfolg, Exit 1 bei Befund — keine Exit-Code-Sonderfälle.
3. Ausgabe als lesbarer Text, nicht nur Zahlen.
4. Kein Prüfungsschritt, der sich nicht mit einer Datei im Repository belegen
   lässt.
5. Jede neue Prüfung bekommt eine Gegenprobe, die hier dokumentiert wird.

## Bekannte Grenzen

- `check-links.py` prüft externe Links **nicht** — sie sammelt sie nur und gibt
  sie aus. Aufgabe 8 erweitert das.
- `sweep.py` und `a11y-audit.py` messen nur die Seiten, die unter
  `http://127.0.0.1:8188` erreichbar sind. Noch nicht existierende Seiten
  werden als solche ausgewiesen, nicht stillschweigend übersprungen.
- Die Browserprüfungen brauchen Chromium. Gefunden wird zuerst die
  Playwright-Installation, dann Google Chrome, Chromium und Edge. Fehlt alle
  vier, bricht das Werkzeug mit einer klaren Meldung ab.
