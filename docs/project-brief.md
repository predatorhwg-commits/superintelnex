# Projekt-Brief — SuperIntelNex Website

Stand: 08.11.2026 · Grundlage für alle Aufgaben der Website `superintelnex.com`
Repository: `predatorhwg-commits/superintelnex` (privat, Branch `main`)

Dieser Brief beantwortet drei Fragen: Was ist heute bestätigt? Was ist offen?
Was umfasst die erste Version? Er ist bewusst kurz gehalten. Details zu
einzelnen Aufgaben stehen in `docs/AUFGABEN.md`, der Belegungsstand in
`docs/AGENTEN-BRETT.md`, jede belegte Angabe in `docs/QUELLEN.md`.

---

## 1. Bestätigte Fakten

Alle Angaben in diesem Abschnitt sind in `docs/QUELLEN.md` belegt.

**Das Projekt.** SuperIntelNex ist ein Community-Projekt für Menschen, die sich
für künstliche Intelligenz, Superintelligenz und die digitale Zukunft begeistern.
Geplant ist ein Community-Token, der langfristig digitale Zahlungen mit
KI-Anwendungen verbindet. Betreiber hat den Projektstatus „im Aufbau" am
08.11.2026 bestätigt.

**Der Stand der Seite.** Der Stand ist bewusst „Projekt im Aufbau". Es gibt
keine Kursangaben, keine Käuferzahlen, keine Partnerlogos, keine Audits und
keine Kauf-Buttons. Was noch nicht existiert, steht auch nicht auf der Seite.
Die Seite ist reines HTML/CSS/JS ohne Build-Schritt und läuft auf jedem
statischen Host.

**Der Entwicklungsplan.** Fünf Schritte in fester Reihenfolge, bewusst ohne
Termine: Marke und Community, Token-Konzept, technische Erprobung im Testnetz,
Vorbereitung der Veröffentlichung, weitere Anwendungen.

**Die Gestaltung.** Heller Hintergrund, Text in Schwarz und Anthrazit, Schrift
Inter mit System-Fallback, zwei Shadow-Stufen, Breakpoints bei 1080 px, 900 px
und 640 px. `prefers-reduced-motion` wird respektiert.

**Der Prüfstand.** Die Seite wurde in Chromium bei 1440 px und 390 px geprüft:
kein horizontales Überlaufen, null Konsolenfehler, alle Reveal-Elemente
werden aktiviert. Diese Messung bezieht sich auf den Stand vom 08.11.2026 und
wird mit jeder inhaltlichen Änderung neu geführt.

**Der Risikohinweis.** Der Wortlaut im Abschnitt `#risiko` wurde vom Betreiber
geliefert und ist nicht verändert. Er bleibt sichtbar auf der Startseite.

**Der Rechtsrahmen.** Die Seite bewirbt kein konkretes Finanzprodukt und
enthält keine Anlageberatung. Das ist kein Freifahrtschein: Impressum und
Datenschutzerklärung sind nach den offiziellen Konten zu ergänzen, je nach
Betreiberform und Sitzland.

---

## 2. Offene Entscheidungen

Diese Punkte sind nicht technisch, sondern inhaltlich. Sie brauchen eine
Entscheidung oder eine Angabe vom Betreiber. Bis dahin bleibt die Website
transparent und zeigt die Lücke offen, statt sie zu füllen.

| # | Offene Entscheidung | Was blockiert | Wo geführt |
|---|---|---|---|
| 1 | Betreiber, Rechtsform, Sitz, Kontaktadresse | Impressum, Datenschutz, Kontaktbereich | `#offen`, `docs/RECHT.md` |
| 2 | Hosting-Anbieter und Serverstandort | Datenschutzerklärung, HTTP-Header-Empfehlung | `#offen`, `docs/RECHT.md` |
| 3 | Geltendes Recht und zuständige Aufsichtsbehörde | Impressum | `docs/RECHT.md` |
| 4 | Sicherheitskontakt für Meldungen | `security.txt`, `SECURITY.md` | `#offen`, `docs/SICHERHEIT.md` |
| 5 | Token-Kürzel | Abschnitt `#offen`, Glossar | `#offen`, `docs/QUELLEN.md` |
| 6 | Blockchain | Abschnitt `#offen` | `#offen`, `docs/QUELLEN.md` |
| 7 | Gesamtmenge und Regeln zur weiteren Ausgabe | Abschnitt `#offen` | `#offen`, `docs/QUELLEN.md` |
| 8 | Verteilung und mögliche Sperrfristen | Abschnitt `#offen` | `#offen`, `docs/QUELLEN.md` |
| 9 | Offizielle Token-Adresse | Abschnitt `#offen` | `#offen`, `docs/QUELLEN.md` |
| 10 | Bestätigte Social-Media-Konten | `#community`, `#offen` | `#community`, `docs/QUELLEN.md` |
| 11 | Anredeform „Sie" oder „du" | gesamter Text | `docs/TEXTE.md` |
| 12 | Hosting-Ziel und endgültige Domain-Konfiguration | canonical, Sitemap, OG-URL | `docs/SEO.md` |
| 13 | Kontaktweg: Formular oder reine Adresse | Datenschutz, Kontaktbereich | `#kontakt`, `docs/RECHT.md` |

**Regel für alle Rollen:** Ein offener Punkt wird nicht durch eine Annahme
geschlossen. Er wird entweder vom Betreiber beantwortet oder bleibt sichtbar
als offen auf der Seite. Das gilt auch dann, wenn eine Aufgabe sonst
abgeschlossen werden könnte.

Zwei dieser Punkte sind **Produktentscheidungen** und nicht nur Datenlieferungen:
Punkt 11 (Anredeform) und Punkt 13 (Kontaktweg). Sie verändern, wie die Seite
wirkt, und gehören vor der Redaktion entschieden. Die übrigen sind Angaben,
die der Betreiber liefert.

---

## 3. Umfang der ersten Version

### 3.1 Seiten

| Seite | Zustand | Verantwortlich |
|---|---|---|
| `index.html` | existiert, Sektionen `#top`, `#projekt`, `#funktionen`, `#roadmap`, `#offen`, `#community`, `#kontakt`, `#risiko` | Redaktion, Design, QA |
| `impressum.html` | offen | Recht |
| `datenschutz.html` | offen | Recht |
| `en/index.html` | offen | i18n |

### 3.2 Technische Bestandteile

| Bestandteil | Zustand | Verantwortlich |
|---|---|---|
| `css/style.css` | existiert | Design, QA |
| `js/main.js` | existiert: Mobile-Nav, Scroll-Zustand, Reveal, Jahreszahl | Basis |
| `assets/logo.svg`, `assets/logo-weiss.svg` | existieren | Basis |
| `assets/og-image.png` | offen, 1200×630 | SEO |
| `sitemap.xml`, `robots.txt` | offen | SEO |
| `.well-known/security.txt`, `SECURITY.md` | offen | Sicherheit |
| `tools/*.py` | existieren, werden erweitert | QA |

### 3.3 Funktionaler Umfang

Die erste Version ist eine **Landingpage**. Sie ist vollständig statisch und
enthält keine Benutzerkonten, keine Transaktionen, keine Preisberechnung und
kein Kontaktformular mit Backend.

Die Seite beantwortet vier Fragen: Was ist SuperIntelNex? Warum gibt es das
Projekt? Was ist heute schon da? Was ist ausdrücklich noch nicht da?

Alle Token-Funktionen — Übertragen, Handeln, Bezahlen, KI-Anwendungen — sind
geplante Entwicklungsziele und tragen sichtbar den Status **Geplant**.

### 3.4 Bewusst nicht im Umfang

Diese Punkte sind **nicht** Teil der ersten Version. Sie sind nicht vergessen,
sondern bewusst ausgeschlossen:

- Keine Kauf-Buttons, kein Warteplatz, kein Countdown.
- Keine Preise, keine Kurse, keine Marktkapitalisierung.
- Keine Teilnehmer-, Halter- oder Mitgliederzahlen.
- Keine Partnerlogos, keine Kooperations- oder Händlerlisten.
- Keine Audit-, Prüf- oder Zertifizierungsangabe ohne benannten Prüfer.
- Keine Prognosen zu Kurs oder Rendite.
- Keine Anlageberatung in irgendeiner Form.
- Kein Kontaktformular mit Backend, keine Datenbank, kein Build-Schritt.
- Keine Analytics, keine Tracking-Pixel, keine Cookies, solange das nicht
  ausdrücklich entschieden und in der Datenschutzerklärung genannt wird.

### 3.5 Definition „fertig"

Die erste Version gilt als fertig, wenn:

1. alle neun Arbeits-Issues geschlossen sind und ihre Abnahmekriterien
   einzeln nachgewiesen bestätigt sind,
2. `python3 tools/release-check.py http://127.0.0.1:8188` vollständig grün
   läuft,
3. Impressum und Datenschutzerklärung mit echten Betreiberangaben gefüllt
   sind, oder der Betreiber bewusst entscheidet, mit sichtbaren Platzhaltern
   zu veröffentlichen,
4. die Domain eingerichtet ist, HTTPS aktiv ist und canonical, Sitemap sowie
   OG-URL auf die Live-Domain zeigen.

Punkt 3 ist eine Entscheidung des Betreibers, keine technische Hürde.

---

## 4. Arbeitsweise auf der Website

- **Ein Bereich, eine Rolle.** Jeder Arbeitsbereich gehört genau einer Rolle.
  Parallel-Arbeit an derselben Datei braucht Absprache über
  `docs/AGENTEN-BRETT.md`.
- **Ein Issue, ein Branch, ein PR.** Kein Sammel-Commit, kein Force-Push.
- **Abnahme über Messung.** Ein Kriterium gilt erst als erfüllt, wenn es
  geprüft und der Nachweis dokumentiert ist. „Sieht gut aus" ist kein Nachweis.
- **Transparenz statt Marketing.** Fehlende Angaben stehen als fehlend auf
  der Seite, nicht als Lücke im Layout.

Details zu den Arbeitsregeln stehen in `AGENTS.md`, die Aufgabenbeschreibung
mit Abnahmekriterien in `docs/AUFGABEN.md`.

---

## 5. Dokumentation

| Datei | Inhalt |
|---|---|
| `AGENTS.md` | Arbeitsregeln, Konventionen, Dateizuständigkeiten |
| `docs/project-brief.md` | dieser Brief |
| `docs/AUFGABEN.md` | Aufgabenbeschrieb mit Abnahmekriterien |
| `docs/AGENTEN-BRETT.md` | Belegung und Status je Agent |
| `docs/QUELLEN.md` | Quelle für jede Zahl und Tatsachenbehauptung |
| `docs/RECHT.md` | Rechtstexte: offene Angaben, Fristen |
| `docs/SEO.md` | Metadaten je Seite, Prüfschritte |
| `docs/I18N.md` | Übersetzungsleitfaden und Glossar |
| `docs/SICHERHEIT.md` | Meldeweg, Header-Empfehlung |
| `docs/A11Y.md` | Prüfprotokoll Barrierefreiheit, gemessene Kontraste |
| `docs/DESIGN.md` | Gestaltungsregeln, Tokens, Breakpoints |
| `docs/TEXTE.md` | Tonalität, Begründung, verbotene Formulierungen |
| `docs/WERKZEUGE.md` | Prüfwerkzeuge: Zweck, Aufruf, Exit-Codes, Gegenproben |
