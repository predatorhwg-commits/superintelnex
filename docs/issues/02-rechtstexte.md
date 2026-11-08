---
id: rechtstexte
titel: "Rechtstexte: Impressum und Datenschutzerklärung"
status: offen
rolle: recht
labels: bereich:inhalte,rolle:recht,status:offen
dateien: "impressum.html, datenschutz.html, docs/RECHT.md, index.html"
---

# Rechtstexte: Impressum und Datenschutzerklärung

## Ziel

Die Seite ist in Deutschland und der EU ohne Impressum und
Datenschutzerklärung nicht veröffentlichungsfähig. Die Seite bewirbt ein
Finanzprojekt, das erhöht die Anforderungen. Beide Rechtstexte entstehen
mit sichtbar markierten Platzhaltern, damit nichts erfunden wird und die
Lücke später gezielt geschlossen werden kann.

## Konkrete Ergebnisse

- [ ] `impressum.html` mit den Pflichtangaben, soweit sie vorliegen.
- [ ] `datenschutz.html` mit den Angaben zu den tatsächlich eingesetzten
      Diensten.
- [ ] `docs/RECHT.md` sammelt alle noch zu liefernden Angaben des Betreibers
      mit Priorität und Begründung.
- [ ] Beide Seiten sind aus `index.html` und untereinander verlinkt.
- [ ] Die offenen Betreiber-Angaben sind im Abschnitt `#offen` der Startseite
      sichtbar als offen geführt.

## Abnahmekriterien

- [ ] Beide Seiten nutzen dieselbe Kopf-/Fußzeilenstruktur wie `index.html`:
      dieselbe CSS-Datei, keine Duplikate, kein zweites Stylesheet.
- [ ] Je ein `<h1>`, lückenlose Überschriftenhierarchie, `lang="de"`.
- [ ] Sprunglink auf `#main` vorhanden, `main` hat `id="main"`.
- [ ] In der Navigation und im Footer verlinkt, in `index.html`,
      `impressum.html` und `datenschutz.html` konsistent.
- [ ] Platzhalter für Betreiber-Angaben sind **sichtbar markiert** und
      zentral in `docs/RECHT.md` als „noch zu liefern" gelistet.
- [ ] Keine erfundenen Angaben: keine Anschrift, kein Telefon, keine
      Registernummer, kein Geschäftsführer, keine Steuernummer.
- [ ] Die Datenschutzerklärung nennt **jeden** tatsächlich eingesetzten
      Dienst: Hosting (Anbieter und Ort), GitHub (Seiten-Statistik),
      Kontaktformular, Schriftarten, Cookies. Was nicht eingesetzt wird,
      wird nicht genannt.
- [ ] Falls ein Kontaktformular eingeführt wird: `action` zeigt auf einen
      echten Endpunkt oder ist als Platzhalter sichtbar gekennzeichnet.
- [ ] `python3 tools/release-check.py http://127.0.0.1:8188` ist grün.
- [ ] `tools/check-links.py` meldet keine toten Verweise auf die neuen Seiten.

## Abhängigkeiten

- **Blockiert:** Der Livegang. Ohne Impressum und Datenschutz nicht
  veröffentlichungsfähig.
- **Benötigt vom Betreiber:** Rechtsform, Sitz, Betreiber, Kontaktadresse,
  Hosting-Anbieter. Diese Angaben sind derzeit offen. Die Aufgabe wird
  trotzdem angefangen: die Struktur und die Platzhalter entstehen jetzt, die
  Inhalte folgen, sobald die Angaben geliefert sind.
- **Berührt `index.html`:** Koordination mit #{{design-struktur}} und
  #{{inhalt-redaktion}} absprechen. Empfohlen: nur Navigation und Footer
  anfassen, keine Textarbeit in den Sektionen.

## Zuständige Rolle

Recht. Keine andere Rolle ändert `impressum.html` oder `datenschutz.html`.

## Betroffene Dateien und Bereiche

| Datei | Art der Änderung |
|---|---|
| `impressum.html` | neu |
| `datenschutz.html` | neu |
| `docs/RECHT.md` | neu: Notizen, offene Fragen, Fristen |
| `index.html` | Navigation und Footer: Links auf die Rechtstexte |
| `impressum.html`, `datenschutz.html` | gegenseitige Verlinkung, Footer |

## Nicht tun

- Keine Muster-Impressumsdaten aus dem Internet kopieren.
- Keine Muster-AGB erfinden.
- Keine Datenschutzerklärung „nach Muster" mit Platzhaltern stehen lassen,
  die wie fertig aussehen.
