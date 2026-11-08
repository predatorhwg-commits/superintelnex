# Agenten-Brett

Belegung und Status für die Website `superintelnex.com`.
Format: `Agent | Aufgabe | Dateien | Status | Commit`.

**Koordinationskanal:** das Tracking-Issue **„SuperIntelNex Website – Planung und
Fortschritt"** im Repository `predatorhwg-commits/superintelnex`. Dieses Brett
bleibt das lokale Belegungsprotokoll und wird bei jedem Check-in mitgezogen.
Kein zweites Parallelsystem.

**Grundlage aller Rollen:** `docs/project-brief.md` (bestätigte Fakten, offene
Entscheidungen, Umfang der ersten Version). Die Aufgaben stehen als Issues in
`docs/issues/` und werden per `tools/bootstrap-github.sh` auf GitHub angelegt.
`docs/QUELLEN.md` belegt jede Zahl.

## Regeln

1. Vor dem ersten Schreibzugriff die Datei hier eintragen.
2. Eine Datei gehört genau einem Agenten, solange er sie offen hat.
3. `git pull` vor dem ersten Schreibzugriff, `python3 -m py_compile` vor jedem
   Commit für geänderte Werkzeuge.
4. Kein Force-Push, keine Sammel-Commits, keine Secrets.
5. Was hier steht, ist der **aktuelle Stand** — nicht, was ein Agent plant.
6. Wer eine Aufgabe übernimmt, trägt sie unten mit dem Status **beansprucht**
   ein, nicht mit „wird gemacht".
7. Ein Issue gilt erst als erledigt, wenn die Abnahmekriterien einzeln
   nachgewiesen bestätigt sind. Der Nachweis gehört als Kommentar ins Issue.

## Belegung

| Agent | Aufgabe | Dateien | Status | Commit |
|---|---|---|---|---|
| Basis | Landingpage, Design, Responsive, Navigation | `index.html`, `css/style.css`, `js/main.js`, `assets/logo*.svg` | fertig, geprüft | `d415d0e` + `setup` |
| Basis | Quellenpflege, Regeln | `AGENTS.md`, `docs/QUELLEN.md` | fertig | `setup` |
| Basis | **Prüfwerkzeuge implementiert** | `tools/release-check.py`, `tools/verify-markup.py`, `tools/verify-content.py`, `tools/check-links.py`, `tools/sweep.py`, `tools/smoke-test.py`, `tools/a11y-audit.py`, `docs/WERKZEUGE.md` | fertig, 7/7 grün | `setup` |
| Koordination | Projekt-Brief, Issuesatz, GitHub-API-Helfer | `docs/project-brief.md`, `docs/issues/`, `docs/pr/`, `tools/gh-api.py` | **beansprucht** | — |
| Redaktion | Inhaltliche Qualität und Tonalität | `index.html` (Texte), `docs/TEXTE.md` | **offen** | — |
| Design | Struktur, Lesbarkeit, Responsive | `index.html`, `css/style.css`, `docs/DESIGN.md` | **offen** | — |
| Recht | Rechtstexte | `impressum.html`, `datenschutz.html`, `docs/RECHT.md` | **offen** | — |
| SEO | Social-Vorschau und Suchmaschinen | `assets/og-image.png`, `sitemap.xml`, `robots.txt`, `tools/og-image.py`, `docs/SEO.md` | **offen** | — |
| i18n | Englische Fassung | `en/index.html`, `en/css/style.css`, `docs/I18N.md` | **offen** | — |
| Sicherheit | Sicherheits-Meldeweg | `.well-known/security.txt`, `SECURITY.md`, `docs/SICHERHEIT.md` | **offen** | — |
| QA | Prüfwerkzeuge **erweitern** | `tools/verify-content.py`, `tools/check-links.py`, `tools/sweep.py`, `docs/WERKZEUGE.md` | **offen** (Basis-Arbeit abgeschlossen, Erweiterungen offen) | — |
| QA | Barrierefreiheit vertiefen | `index.html`, `css/style.css`, `docs/A11Y.md` | **offen** | — |

## Rollenzuordnung

Jeder Arbeitsbereich gehört genau einer Rolle. GitHub-Zuweisungen sind in
diesem privaten Repository bisher nicht möglich, weil es keine Teams mit
Schreibrecht gibt. Die Zuordnung ist deshalb hier und im Tracking-Issue
verbindlich dokumentiert.

| Rolle | Arbeitsbereich | Dateien |
|---|---|---|
| Koordination | Planung, Issues, Statuspflege, Freigabe | `docs/`, `tools/gh-api.py` |
| Redaktion | Sachtexte, Tonalität, Quellenpflege | `index.html` (Text), `docs/TEXTE.md`, `docs/QUELLEN.md` |
| Design | Struktur, Typografie, Breakpoints | `index.html`, `css/style.css`, `docs/DESIGN.md` |
| Recht | Impressum, Datenschutz | `impressum.html`, `datenschutz.html`, `docs/RECHT.md` |
| SEO | Social-Vorschau, Sitemap, Metadaten | `assets/og-image.png`, `sitemap.xml`, `robots.txt`, `tools/og-image.py`, `docs/SEO.md` |
| i18n | Englische Fassung, Sprachumschalter | `en/`, `docs/I18N.md` |
| Sicherheit | Meldeweg, Header-Empfehlung | `.well-known/security.txt`, `SECURITY.md`, `docs/SICHERHEIT.md` |
| QA | Prüfwerkzeuge, Barrierefreiheit | `tools/*.py`, `docs/WERKZEUGE.md`, `docs/A11Y.md` |

## Issue-Nummern

Nach dem Anlegen der Issues wird diese Spalte gefüllt. Vorher gilt die
Zuordnung über `docs/issues/`:

| Rolle | Issue-Datei | GitHub-Nummer |
|---|---|---|
| Koordination | `docs/issues/00-tracking.md` | — |
| Koordination | `docs/issues/01-project-brief.md` | — |
| Recht | `docs/issues/02-rechtstexte.md` | — |
| SEO | `docs/issues/03-seo-social.md` | — |
| Sicherheit | `docs/issues/04-sicherheit-meldeweg.md` | — |
| QA | `docs/issues/05-qa-werkzeuge.md` | — |
| Redaktion | `docs/issues/06-inhalt-redaktion.md` | — |
| Design | `docs/issues/07-design-struktur.md` | — |
| i18n | `docs/issues/08-i18n-en.md` | — |
| QA | `docs/issues/09-qa-barrierefreiheit.md` | — |

## Überschneidungen — bitte beachten

- **Redaktion, Design und QA** fassen alle `index.html` an. Sie **müssen**
  abgestimmt werden: entweder nacheinander arbeiten (Brett-Eintrag abwarten)
  oder arbeitsteilig nach Sektion (Hero / `#projekt` / `#funktionen` /
  `#roadmap` / `#community` / `#kontakt`).
- **SEO und QA** fassen beide `index.html` an. Reihenfolge einhalten oder
  Teile direkt zuweisen.
- **`css/style.css`** gehört Design und QA. Nur eine Rolle zur selben Zeit.
- **`tools/`** gehört QA. Wer in SEO `tools/og-image.py` anlegt, trägt das
  Datei-Feld in Zeile „Prüfwerkzeuge erweitern" mit.
- **`tools/gh-api.py`** gehört Koordination und wird nur bei Anpassungen am
  GitHub-API-Helfer angefasst.

Empfohlene Reihenfolge: **Brief → Recht → SEO → Sicherheit → Werkzeuge →
Redaktion → Design → i18n → Barrierefreiheit**.
Design und Barrierefreiheit zuletzt, weil sie auf dem Endstand der Inhalte
messen. i18n nach Redaktion, weil die Übersetzung sonst ungültig wird.

## Offene Punkte für den Betreiber

Diese Angaben fehlen und werden von der Website **nicht** erfunden. Sie sind
zusätzlich in `docs/QUELLEN.md`, in `docs/project-brief.md` und im Abschnitt
`#offen` der Seite geführt.

- [ ] Betreiber, Rechtsform, Sitz, Kontaktadresse
- [ ] Hosting-Anbieter und Serverstandort
- [ ] Sicherheitskontakt für Meldungen
- [ ] Token-Kürzel
- [ ] Blockchain
- [ ] Gesamtmenge
- [ ] Regeln zur weiteren Ausgabe
- [ ] Verteilung und Sperrfristen
- [ ] Offizielle Token-Adresse
- [ ] Bestätigte Social-Media-Links
- [ ] Anredeform „Sie" oder „du"
- [ ] Kontaktweg: Formular oder Adresse

## Koordinationskanal

Das Repository ist privat: `predatorhwg-commits/superintelnex`.
`gh` ist auf dieser Maschine nicht installiert. Der Helfer `tools/gh-api.py`
spricht die GitHub-API direkt an.

```bash
# Token bereitstellen (einmalig, nicht in Dateien speichern)
security add-generic-password -s github.com -a predatorhwg-commits -w <token>

python3 tools/gh-api.py check
python3 tools/gh-api.py issue create-batch --dir docs/issues
python3 tools/gh-api.py issue update-tracking <NUMMER> --dir docs/issues
```

Nach dem Merge des Dokumentations-PRs wird hier die Nummer des
Tracking-Issues eingetragen. Bis dahin gilt dieses Brett als einzige
Koordinationsstelle.

## Stand 08.11.2026

- Landingpage steht: Hero, `#projekt`, `#funktionen`, `#roadmap`, `#offen`,
  `#community`, `#kontakt`, `#risiko`.
- **Prüfwerkzeuge implementiert** (`tools/`): `release-check.py` bündelt sieben
  Prüfungen, alle grün. Werkzeuge: `verify-markup.py`, `verify-content.py`,
  `check-links.py`, `sweep.py`, `smoke-test.py`, `a11y-audit.py`.
- **Gegenproben ausgeführt:** Markup-Befunde, Inhalts-Befunde (Preis, Rendite,
  Kauf-Button), toter Link/Anker, horizontaler Überlauf — alle vier werden
  zuverlässig erkannt (Exit 1). Protokoll in `docs/WERKZEUGE.md`.
- Geprüft in Chromium: 1440, 1280, 768 und 390 px ohne horizontales Überlaufen,
  0 Konsolenfehler, 0 nicht aktivierte Reveal-Elemente, 0 A11y-Befunde.
- Repo angelegt und leer gepusht (`main`).
- Neu: Projekt-Brief, Issuesatz in `docs/issues/`, GitHub-API-Helfer
  `tools/gh-api.py`. Token liegt als generic-password im Schlüsselbund.
