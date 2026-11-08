# SuperIntelNex — Website

Statische Landingpage für den Community-Token **SuperIntelNex**.
Domain: `superintelnex.com` · Repository: `predatorhwg-commits/superintelnex` (privat)

**Stand:** Projektphase „Im Aufbau" — bewusst ohne Kursangaben, Käuferzahlen,
Partnerlogos, Audits oder Kauf-Buttons. Fehlende Angaben stehen als fehlend auf
der Seite, nicht als Lücke.

---

## Schnellstart

```bash
cd "/Users/haqmal/Desktop/Projekte/SuperIntelNex"
python3 -m http.server 8188
# → http://127.0.0.1:8188
```

Die Seite ist reines HTML/CSS/JS und läuft ohne Build-Schritt auf jedem statischen
Host (Netlify, Vercel, Cloudflare Pages, GitHub Pages, nginx, S3).

## Struktur

```
SuperIntelNex/
├── index.html            # Landingpage, alle Sektionen
├── css/style.css         # Design, Layout, Responsive, Reveal-Animationen
├── js/main.js            # Mobile-Nav, Scroll-Zustand, Reveal, Jahreszahl
├── assets/
│   ├── logo.svg          # SN-Logo, anthrazit (für helle Flächen)
│   └── logo-weiss.svg    # SN-Logo, weiß (für dunkle Flächen)
├── tools/                # Prüfwerkzeuge (Python 3.9, kein Build)
├── docs/                 # Projektunterlagen
│   ├── project-brief.md  # Grundlage aller Rollen
│   ├── issues/           # Aufgaben je Rolle mit Abnahmekriterien
│   ├── QUELLEN.md        # Quelle für jede Zahl und Tatsachenbehauptung
│   ├── AGENTEN-BRETT.md  # Belegung und Status
│   └── WERKZEUGE.md      # Werkzeugdoku mit Gegenproben
├── AGENTS.md             # Arbeitsregeln für alle Agenten
└── README.md
```

## Sektionen der Seite

| # | Abschnitt | Anker | Inhalt |
|---|---|---|---|
| 1 | Hero | `#top` | Claim, Einstiegstext, „Projekt im Aufbau"-Status, zwei CTAs |
| 2 | Über das Projekt | `#projekt` | Verbindung, Vision, nächste Schritte, ehrliche Abgrenzung |
| 3 | Geplante Funktionen | `#funktionen` | Übertragen, Handeln, Bezahlen, KI-Anwendungen — je mit „Geplant"-Tag |
| 4 | Entwicklungsplan | `#roadmap` | 5 Schritte als Timeline, bewusst ohne Termine |
| 5 | Offene Punkte | `#offen` | 7 noch fehlende Angaben als Platzhalter |
| 6 | Community | `#community` | Dunkles Panel, Kanal-Übersicht (noch „wird angekündigt") |
| 7 | Kontakt | `#kontakt` | 3 Kontaktarten als Platzhalter |
| 8 | Risikohinweis | `#risiko` | Pflichtinhalt zur Risikokommunikation |
| — | Footer | — | Navigation, Jahreszahl, Hinweis „keine Anlageberatung" |

## Design

- Hintergrund weiß, Flächen `#f5f6f6`, Text Schwarz `#08090a` / Anthrazit `#1c1d1e`
- Schrift: Inter (System-Fallback auf Helvetica Neue / SF)
- Radius 10 / 16 / 24 px, großzügige Abstände (Sections 112 px Desktop)
- Breakpoints: 1080 px (Hero stapelt), 900 px (Mobile-Nav), 640 px (einspaltig)
- `prefers-reduced-motion` wird respektiert

## Prüfen

```bash
python3 -m http.server 8188 &                    # Server starten
python3 tools/release-check.py http://127.0.0.1:8188
```

Sieben Prüfungen in einem Lauf: Markup, Inhaltsregeln, Links, Überlauf-Sweep,
Funktionstest, Barrierefreiheit, Syntax. Details und Gegenproben in
`docs/WERKZEUGE.md`.

## Mitwirken

Die Arbeitsregeln stehen in `AGENTS.md`. Kurzfassung:

1. Aufgabe aus `docs/issues/` in `docs/AGENTEN-BRETT.md` als beansprucht eintragen.
2. `git pull` vor dem ersten Schreibzugriff.
3. `python3 tools/release-check.py` vor jedem Push — muss grün sein.
4. Keine erfundenen Inhalte: jede Zahl braucht einen Eintrag in `docs/QUELLEN.md`.

## Noch einzutragen, sobald feststeht

- [ ] Token-Kürzel und Blockchain
- [ ] Gesamtmenge und Regeln zur weiteren Ausgabe
- [ ] Verteilung und mögliche Sperrfristen
- [ ] Offizielle Token-Adresse
- [ ] Verantwortlicher Betreiber und Kontaktadresse
- [ ] Bestätigte Social-Media-Links
- [ ] Impressum, Datenschutzerklärung und rechtliche Hinweise
- [ ] Offizielle Kanäle als echte Links statt Platzhalter

## Domain einrichten

```bash
dig +short NS superintelnex.com
```

Für den Livegang: DNS-A-Record auf den Hosting-Anbieter setzen, `www` per
CNAME auf die Apex-Domain, HTTPS/TLS aktivieren, danach die URLs in
`index.html` (`og:url`, `canonical`) prüfen.

## Hinweis zur Rechtslage

Die Seite bewirbt kein konkretes Finanzprodukt und enthält keine Anlageberatung.
Der Risikohinweis auf der Seite ist Pflichtbestandteil. Impressum und
Datenschutzerklärung sind nach den offiziellen Konten zu ergänzen — je nach
Betreiberform und Sitzland.

---

© SuperIntelNex — Projekt im Aufbau.
