---
id: design-struktur
titel: "Struktur, Lesbarkeit und Responsive-Verhalten"
status: offen
rolle: design
labels: bereich:design,rolle:design,status:offen
dateien: "index.html, css/style.css, docs/DESIGN.md"
---

# Struktur, Lesbarkeit und Responsive-Verhalten

## Ziel

Auf dem Handy muss die Seite in 30 Sekunden erfassbar sein. Der Text wird von
der Redaktion geliefert, die Aufgabe hier ist die Form: Reihenfolge, Typografie,
Abstände, das Verhalten über die Breiten.

## Konkrete Ergebnisse

- [ ] Über 1440 px sind alle Sektionen in einer Bildschirmhöhe lesbar.
- [ ] Der Fließtext hat maximal etwa 72 Zeichen Zeilenlänge.
- [ ] Die vier Funktionskarten stehen auf Desktop nebeneinander, auf Mobil
      untereinander, ohne Zwischenzustand.
- [ ] Die Roadmap ist auf dem Handy ohne Scrollen des Textes lesbar, die
      Nummern `01` bis `05` sind sichtbar.
- [ ] Zwischenüberschriften beschreiben den Inhalt, nicht die Optik.
- [ ] `docs/DESIGN.md` hält die Gestaltungsregeln fest.

## Abnahmekriterien

- [ ] Über 1440 px sind alle Sektionen in **einer** Bildschirmhöhe lesbar
      (kein Scroll-Sprung von 2 px bis 40 px).
- [ ] Fließtext max. etwa 72 Zeichen Zeilenlänge.
- [ ] Die vier Funktionskarten stehen nebeneinander auf Desktop, untereinander
      auf Mobil. Kein Zwischenzustand, in dem 2 + 2 stehen.
- [ ] Die Roadmap ist auf dem Handy auch ohne Scrollen des Textes lesbar
      (Zahlen `01`–`05` sichtbar).
- [ ] Zwischenüberschriften (`h2`) beschreiben den Inhalt, nicht die Optik
      („Funktionen" statt „Vier Karten nebeneinander").
- [ ] `tools/sweep.py` meldet bei 1440, 1280, 768 und 390 px keinen
      horizontalen Überlauf.
- [ ] `tools/smoke-test.py` meldet 0 Konsolenfehler.
- [ ] `python3 tools/release-check.py http://127.0.0.1:8188` ist grün.
- [ ] `docs/DESIGN.md` beschreibt Farbtokens, Typografie-Skala, Abstände,
      Breakpoints und die Regeln für Karten und Timeline.

## Abhängigkeiten

- **Setzt den Textbestand von #{{inhalt-redaktion}} voraus.** Die Messung
  gilt für den Endstand der Inhalte. Design und Redaktion arbeiten daher
  nacheinander, nicht gleichzeitig an `index.html`.
- **Berührt `index.html` und `css/style.css`:** Diese Dateien werden auch von
  #{{qa-barrierefreiheit}} und #{{seo-social}} angefasst. Reihenfolge:
  Redaktion, dann Design, dann Barrierefreiheit.
- **Berührt `css/style.css`:** Fokusringe und Kontrast sind Teil von
  #{{qa-barrierefreiheit}}. Der Fokusring wird hier nicht entfernt, nur
  gestaltet.

## Zuständige Rolle

Design. Für die Gestaltungsregeln in `css/style.css` ist diese Rolle allein
zuständig.

## Betroffene Dateien und Bereiche

| Datei | Art der Änderung |
|---|---|
| `index.html` | Sektionsreihenfolge, Überschriften, Klassenstruktur |
| `css/style.css` | Abstände, Typografie-Skala, Breakpoints, Grid |
| `docs/DESIGN.md` | neu: Gestaltungsregeln |

## Nicht tun

- Keine neue Abhängigkeit, kein Framework, kein Build-Schritt.
- Keine Inhalte umschreiben — das ist Aufgabe der Redaktion.
- Keine Änderungen am Risikohinweis, außer Layout.
