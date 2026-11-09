---
id: seo-social
titel: "Social-Vorschau und Suchmaschinen"
status: offen
rolle: seo
labels: bereich:design,rolle:seo,status:offen
dateien: "assets/og-image.png, sitemap.xml, robots.txt, tools/og-image.py, docs/SEO.md, index.html"
---

# Social-Vorschau und Suchmaschinen

## Ziel

Ohne eigenes OG-Bild zeigen X, WhatsApp, Telegram und Slack nur ein leeres
Bild. `og:image` muss existieren, bevor die Community teilt. Sitemap und
`robots.txt` sorgen dafür, dass die Seite auffindbar wird, ohne dass
Seiten indexiert werden, die es noch nicht gibt.

## Konkrete Ergebnisse

- [ ] `assets/og-image.png` in exakt 1200×630 px.
- [ ] `tools/og-image.py` erzeugt das Bild reproduzierbar.
- [ ] `sitemap.xml` listet alle real existierenden Seiten.
- [ ] `robots.txt` erlaubt das Crawlen und zeigt auf die Sitemap.
- [ ] `index.html` trägt die vollständigen Open-Graph- und Twitter-Metadaten.
- [ ] `docs/SEO.md` dokumentiert die Angaben je Seite und die Prüfschritte.

## Abnahmekriterien

- [ ] `assets/og-image.png` existiert und ist **exakt 1200×630 px**.
- [ ] `<meta property="og:image">` in `index.html` zeigt auf diese Datei.
- [ ] `<meta property="og:image:width">` = 1200, `og:image:height` = 630.
- [ ] `og:image:alt` beschreibt das Bild sinnvoll.
- [ ] `twitter:card` = `summary_large_image`.
- [ ] `twitter:title` und `twitter:description` sind gesetzt.
- [ ] `og:url` zeigt auf `https://superintelnex.com/`.
- [ ] `og:site_name` = `SuperIntelNex`, `og:locale` = `de_DE`.
- [ ] `<link rel="canonical" href="https://superintelnex.com/">` in `index.html`.
- [ ] `sitemap.xml` listet alle real existierenden Seiten mit `lastmod`.
- [ ] `robots.txt` erlaubt das Crawlen und zeigt auf die Sitemap.
- [ ] Keine URL in `sitemap.xml`, die es nicht gibt.
- [ ] Das OG-Bild ist dunkel (Anthrazit `#08090a`), mit weißem SN-Logo,
      Schrift „SuperIntelNex" und der Unterzeile „Gemeinsam die intelligente
      Zukunft gestalten."
- [ ] `python3 tools/release-check.py http://127.0.0.1:8188` ist grün.

## Abhängigkeiten

- **Keine harte Abhängigkeit.** Startet sofort.
- **Berührt `index.html`:** Koordination mit #10,
  #9 und #12 absprechen. Empfohlen:
  nur den `<head>`-Bereich anfassen.
- **Abhängig vom Hosting-Ziel:** Die canonical-URL und der Sitemap-Eintrag
  setzen `superintelnex.com` voraus. Falls das Hosting abweichend gewählt
  wird, müssen beide Stellen zusammen angepasst werden.
- **Aufgabe 8 (`#8`) und dieses Issue teilen sich `tools/`**:
  `tools/og-image.py` wird hier angelegt, `tools/verify-content.py` dort
  erweitert. Der Datei-Eintrag im Agenten-Brett nennt beide.

## Zuständige Rolle

SEO. Nur diese Rolle ändert `assets/og-image.png`, `sitemap.xml`,
`robots.txt` und `tools/og-image.py`.

## Betroffene Dateien und Bereiche

| Datei | Art der Änderung |
|---|---|
| `assets/og-image.png` | neu: 1200×630 |
| `tools/og-image.py` | neu: reproduzierbare Erzeugung |
| `sitemap.xml` | neu |
| `robots.txt` | neu |
| `docs/SEO.md` | neu |
| `index.html` | `<head>`: OG-, Twitter- und Canonical-Metadaten |

## Nicht tun

- Keine URLs für Seiten eintragen, die noch nicht existieren.
- Kein Keyword-Spam.
- Keine Seiten für „Token kaufen" anlegen.
- Keine externen Schriften oder Dienste für das OG-Bild einbinden, die
  nicht ohnehin Teil der Seite sind.
