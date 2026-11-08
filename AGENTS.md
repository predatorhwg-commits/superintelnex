# SuperIntelNex — Arbeitsregeln

Statische Landingpage für den Community-Token **SuperIntelNex** (`superintelnex.com`).
Reines HTML/CSS/JS, **kein Build-Schritt**, kein Framework, keine Abhängigkeiten.
Der Stand ist bewusst „Projekt im Aufbau": keine Kurse, Käuferzahlen, Partnerlogos,
Audits oder Kauf-Buttons.

## Vor der Arbeit

- Offene Issues lesen: `python3 tools/gh-api.py issue list` (der Befehl `gh` ist
  auf dieser Maschine nicht installiert; `tools/gh-api.py` spricht die API direkt
  an). Alternativ die Issue-Dateien in `docs/issues/`.
- Aufgabe im Issue **„SuperIntelNex Website – Planung und Fortschritt"**
  claimen, bevor Dateien geändert werden.
- Aufgabe aus `docs/issues/` in `docs/AGENTEN-BRETT.md` als **beansprucht**
  eintragen (Agent | Aufgabe | Dateien | Status | Commit).
- Dateien, die ein anderer Agent beansprucht hat, nicht ohne Absprache ändern.
- `git pull` vor dem ersten Schreibzugriff, damit alle denselben Stand haben.

## Prüfen vor jedem Push

Ein Befehl prüft alles:

```bash
python3 tools/release-check.py http://127.0.0.1:8188
```

Er umfasst:

| Prüfung | Werkzeug |
|---|---|
| Python-Syntax aller Skripte | `release-check.py` |
| Interne Links und Anker | `tools/check-links.py` |
| Doppelte IDs, fehlende `alt`, `lang`, Landmarken | `tools/verify-markup.py` |
| 1440 / 1280 / 768 / 390 px ohne horizontales Überlaufen | `tools/sweep.py` |
| 0 Konsolenfehler, Bedienung der Navigation | `tools/smoke-test.py` |
| Barrierefreiheit im Browser (Name, Fokus, Landmarks) | `tools/a11y-audit.py` |
| Keine Platzhalter-Reste, keine erfundenen Zahlen | `tools/verify-content.py` |

Zusätzlich manuell:

- Keine Secrets, Keys, Logs, `status.json`, Build-Artefakte oder `*.bak_*` committen.
- Keine erfundenen Inhalte: keine Preise, keine Teilnehmerzahlen, keine Zitate
  ohne Quelle, keine Partnerlogos, keine „geprüft von"-Angaben.
- Jede geplante Funktion trägt sichtbar den Status **Geplant**.

## Koordination

- Ein Kanal: das Agenten-Issue. Kein zweites Parallelsystem.
- Check-in-Format: `Agent | Aufgabe | Dateien | Status | Commit`.
- Wer eine Datei länger als einen Arbeitsschritt offen hat, trägt sie als
  beansprucht ein.
- `main` wird direkt veröffentlicht: **kein Force-Push, keine ungeprüften
  Sammel-Commits.**

## Inhaltsregeln (nicht verhandelbar)

Die Seite bewirbt ein Finanzprojekt. Deshalb gelten diese Regeln hart:

1. **Keine Anlageberatung.** Keine Empfehlung, kein „sollte kaufen", keine Prognose
   zum Kurs.
2. **Keine erfundenen Fakten.** Zahlen nur mit Quelle in `docs/QUELLEN.md`.
3. **Risikohinweis bleibt sichtbar** auf der Startseite (Abschnitt `#risiko`).
4. **Geplante Funktionen** sind als „Geplant" gekennzeichnet und dürfen nie als
   verfügbar dargestellt werden.
5. **Transparenz statt Marketing.** Fehlende Angaben stehen als fehlend auf der
   Seite (Abschnitt `#offen`), nicht als Lücke.

## Aktuelle Dateien und Zuständigkeiten

| Datei | Zweck | Zuständig |
|---|---|---|
| `index.html` | Komplette Landingpage, alle Sektionen | Basis-Agent |
| `css/style.css` | Design, Layout, Responsive, Reveal-Animationen | Basis-Agent |
| `js/main.js` | Mobile-Nav, Scroll-Zustand, Reveal, Jahreszahl | Basis-Agent |
| `assets/logo.svg`, `assets/logo-weiss.svg` | SN-Logo | Basis-Agent |
| `impressum.html`, `datenschutz.html` | Rechtstexte | Recht |
| `assets/og-image.png` | Social-Vorschau 1200×630 | SEO |
| `sitemap.xml`, `robots.txt` | Suchmaschinen | SEO |
| `en/index.html` | Englische Fassung | i18n |
| `.well-known/security.txt` | Kontakt für Sicherheitsmeldungen | Sicherheit |
| `tools/*.py` | Prüfwerkzeuge | QA |
| `tools/gh-api.py` | GitHub-API-Helfer (ersetzt `gh`) | Koordination |
| `docs/issues/` | Aufgaben je Rolle, mit Abnahmekriterien | Koordination |
| `docs/project-brief.md` | Grundlage aller Rollen | Koordination |
| `docs/QUELLEN.md` | Quelle für jede Zahl auf der Seite | Redaktion |
| `docs/WERKZEUGE.md` | Werkzeugdoku mit Gegenproben | QA |

## Konventionen

- Sprache der Inhalte: Deutsch. Code-Kommentare auf Deutsch, ohne Umlaute in
  Bezeichnern.
- ASCII in Bezeichnern, Umlaute in Texten erlaubt.
- CSS: Komponentenblöcke mit Überschrift, Design-Tokens in `:root`.
- Keine Inline-Skripte, keine Inline-Handler (`onclick`), kein `javascript:`.
- Semantisches HTML: genau ein `h1`, danach `h2`, Überschriftenhierarchie
  lückenlos, Landmarks (`header`, `nav`, `main`, `footer`) gesetzt.
