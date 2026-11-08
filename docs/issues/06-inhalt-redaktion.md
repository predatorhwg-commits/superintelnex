---
id: inhalt-redaktion
titel: "Inhaltsqualität und Redaktion"
status: offen
rolle: redaktion
labels: bereich:inhalte,rolle:redaktion,status:offen
dateien: "index.html, docs/TEXTE.md, docs/QUELLEN.md"
---

# Inhaltsqualität und Redaktion

## Ziel

Die Seite wirkt schnell wie Werbe-Spam, wenn die Texte nur aus Schlagworten
bestehen. Guter, sachlicher Text ist der stärkste Vertrauensbeweis. Inhalt und
Darstellung sind getrennte Aufgaben, damit beide parallel bearbeitbar bleiben.

## Konkrete Ergebnisse

- [ ] Jeder Abschnitt beantwortet: Was ist das? Warum gibt es das? Was ist
      heute schon da und was noch nicht?
- [ ] Der Token ist an einer Stelle so erklärt, dass ein Laie ihn versteht.
- [ ] `docs/TEXTE.md` hält Tonalität, Begründung je Abschnitt und verbotene
      Formulierungen fest.
- [ ] Die Anredeform ist entschieden und dokumentiert.

## Abnahmekriterien

- [ ] Jeder Abschnitt beantwortet: Was ist das? Warum gibt es das? Was ist
      heute schon da und was noch nicht?
- [ ] Keine Superlative ohne Beleg. „Revolutionär", „bahnbrechend",
      „unsere revolutionäre Plattform" sind verboten.
- [ ] Keine Passiv-Konstruktionen, wo Aktiv klarer ist.
- [ ] Es gibt genau eine Stelle, an der das Token-Konzept für Laien erklärt
      wird: Was ist ein Token? Was macht er? Was macht er *nicht*?
- [ ] Der Abschnitt „Was wir bewusst noch nicht zeigen" bleibt bestehen und ist
      nicht weggerationalisiert.
- [ ] Keine konkreten Zahlen ohne Eintrag in `docs/QUELLEN.md`.
- [ ] Die Anredeform ist einheitlich („Sie" oder „du"). Die Entscheidung ist
      in `docs/TEXTE.md` begründet.
- [ ] `tools/verify-content.py` meldet 0 Befunde.
- [ ] `python3 tools/release-check.py http://127.0.0.1:8188` ist grün.

## Abhängigkeiten

- **Berührt `index.html`:** Koordination mit #{{design-struktur}},
  #{{qa-barrierefreiheit}} und #{{rechtstexte}} absprechen. Empfohlene
  Arbeitsteilung: Redaktion ändert nur den Textinhalt, Design ändert nur
  Struktur und Klassen. Reihenfolge: Redaktion vor Design.
- **Keine Abhängigkeit zu den Rechtstexten.** Die Rechtstexte werden parallel
  bearbeitet.
- **Benötigt vom Betreiber:** Token-Kürzel, Blockchain, Gesamtmenge,
  Verteilung, Sperrfristen, offizielle Token-Adresse, bestätigte
  Social-Media-Links, Entscheidung zur Anredeform. Diese Angaben sind offen
  und werden im Abschnitt `#offen` als fehlend geführt, nicht erfunden.

## Zuständige Rolle

Redaktion. Für den Textinhalt von `index.html` ist diese Rolle allein zuständig.

## Betroffene Dateien und Bereiche

| Datei | Art der Änderung |
|---|---|
| `index.html` | Text in Hero, `#projekt`, `#funktionen`, `#community` |
| `docs/TEXTE.md` | neu: Tonalität, Begründung, verbotene Formulierungen |
| `docs/QUELLEN.md` | Ergänzung nur für belegte Angaben |

## Nicht tun

- Keine Trading-Signale, keine „Signale folgen"-Hinweise.
- Keine Aussagen über erwartete Renditen.
- Keine Dringlichkeits-Tricks („Nur heute!", „Limitierte Plätze!").
- Keine Inhalte erfinden, die nicht vom Betreiber geliefert wurden.
