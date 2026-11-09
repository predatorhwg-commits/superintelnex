---
id: qa-werkzeuge
titel: "Prüfwerkzeuge erweitern und Gegenproben dokumentieren"
status: offen
rolle: qa
labels: bereich:qualitaet,rolle:qa,status:offen
dateien: "tools/*.py, docs/WERKZEUGE.md"
---

# Prüfwerkzeuge erweitern und Gegenproben dokumentieren

## Ziel

Die Werkzeuge in `tools/` sind die Grundlage jeder Abnahme. Je besser sie
messen, desto weniger Diskussion. Jede Prüfung braucht ihre Gegenprobe: ein
absichtlich fehlerhafter Zustand, der zuverlässig erkannt wird. Eine Prüfung,
die immer grün ist, ist wertlos.

## Konkrete Ergebnisse

- [ ] `tools/verify-content.py` prüft zusätzlich die Content-Regeln.
- [ ] `tools/check-links.py` prüft externe Links erreichbar, ohne harte
      CI-Abhängigkeit.
- [ ] `tools/sweep.py` prüft zusätzlich 1920 px und 320 px.
- [ ] Jedes Werkzeug hat `--help`, sprechende Fehlermeldungen, Exit 0 oder 1
      und eine lesbare Textausgabe.
- [ ] `docs/WERKZEUGE.md` beschreibt Zweck, Aufruf, Exit-Codes und
      Gegenprobe je Werkzeug.

## Abnahmekriterien

- [ ] `tools/verify-content.py` meldet zusätzlich: keine Preise in `$`/`€`,
      keine Prozentangaben ohne Kontext, keine „geprüft"/„zertifiziert"-
      Behauptung, jede Zahl mit Quelle in `docs/QUELLEN.md`.
- [ ] `tools/check-links.py` prüft **externe** Links auf Erreichbarkeit, mit
      Timeout. Ein Netzwerkfehler ist ein **Hinweis**, kein Fehlschlag für
      CI; das Verhalten ist in der Ausgabe erkennbar.
- [ ] `tools/sweep.py` prüft zusätzlich 1920 px und 320 px.
- [ ] Jedes Werkzeug unterstützt `--help`.
- [ ] Fehlermeldungen nennen die konkrete Datei und den konkreten Fehler.
- [ ] Die Ausgabe ist als lesbarer Text formuliert, nicht nur als Zahlen.
- [ ] `docs/WERKZEUGE.md` nennt für jedes Werkzeug eine **Gegenprobe**: wie
      sieht ein absichtlich fehlerhafter Zustand aus, und wird er erkannt?
- [ ] Für jede neue Prüfung ist die Gegenprobe einmal ausgeführt und das
      Ergebnis in `docs/WERKZEUGE.md` oder im Issue protokolliert.
- [ ] `python3 tools/release-check.py http://127.0.0.1:8188` ist grün.

## Abhängigkeiten

- **Keine harte Abhängigkeit.** Startet sofort.
- **Teilt `tools/` mit #6:** `tools/og-image.py` wird dort
  angelegt. Der Eintrag in `docs/AGENTEN-BRETT.md` nennt beide Dateien, damit
  kein Konflikt entsteht.
- **Berührt `index.html` nicht.**

## Zuständige Rolle

Qualitätssicherung. Nur diese Rolle erweitert `tools/*.py`.

## Betroffene Dateien und Bereiche

| Datei | Art der Änderung |
|---|---|
| `tools/verify-content.py` | erweitern |
| `tools/check-links.py` | erweitern |
| `tools/sweep.py` | erweitern |
| `tools/release-check.py` | nur wenn eine neue Prüfung dazukommt |
| `docs/WERKZEUGE.md` | neu |

## Nicht tun

- Keine Prüfung hinzufügen, die immer grün ist.
- Keine Prüfung, die ohne Gegenprobe eingeführt wird.
- Keine harte Netzwerkabhängigkeit in CI.
