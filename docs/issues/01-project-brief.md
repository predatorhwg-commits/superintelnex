---
id: project-brief
titel: "Projekt-Brief und Dokumentationsbasis"
status: offen
rolle: koordination
labels: rolle:koordination,status:offen,dokumentation
dateien: "docs/project-brief.md, docs/AGENTEN-BRETT.md"
---

# Projekt-Brief und Dokumentationsbasis

## Ziel

Eine belastbare, kurze Grundlage schaffen, auf der alle weiteren Aufgaben
aufsetzen. Der Brief hält fest, was heute bestätigt ist, was offen ist und
was die erste Version umfasst. Er ersetzt keine Detaildokumentation, sondern
verweist darauf.

## Konkrete Ergebnisse

- [ ] `docs/project-brief.md` existiert mit drei Teilen: bestätigte Fakten,
      offene Entscheidungen, Umfang der ersten Version.
- [ ] Jede bestätigte Tatsache in `docs/project-brief.md` hat eine Quelle in
      `docs/QUELLEN.md`.
- [ ] Jede offene Entscheidung ist als Frage formuliert, mit der Angabe, was
      sie blockiert.
- [ ] Der Umfang der ersten Version ist als Liste konkreter Seiten und
      Funktionen beschrieben, inklusive der Angabe, was **nicht** enthalten ist.
- [ ] `docs/AGENTEN-BRETT.md` verweist auf den Brief und nennt ihn als
      verbindliche Grundlage für alle Rollen.
- [ ] Der Brief wird über einen kleinen Dokumentations-PR eingereicht
      (Branch `docs/project-brief`, Ziel `main`).

## Abnahmekriterien

- [ ] Der Brief ist auf Deutsch und in Prosa, keine Stichpunktsammlung
      ohne Kontext.
- [ ] Er behauptet nichts, was nicht in `docs/QUELLEN.md` belegt ist.
- [ ] Er nennt keine Preise, Teilnehmerzahlen oder Termine.
- [ ] Er widerspricht `AGENTS.md` nicht.
- [ ] Er enthält keine internen Zugangsdaten, Tokens oder Pfade, die nicht
      Teil des Projekts sind.
- [ ] `python3 tools/release-check.py http://127.0.0.1:8188` bleibt grün
      (die Änderung betrifft keine Webseite, das Ergebnis muss unverändert
      grün sein).

## Abhängigkeiten

- **Keine.** Dieser Brief ist die Grundlage aller anderen Aufgaben und
  sollte zuerst abgeschlossen sein.

## Zuständige Rolle

Koordination.

## Betroffene Dateien und Bereiche

| Datei | Art der Änderung |
|---|---|
| `docs/project-brief.md` | neu |
| `docs/AGENTEN-BRETT.md` | Verweis auf den Brief ergänzen |
| `README.md` | optional: Abschnitt „Dokumentation" |

## Nicht tun

- Keine Angaben ergänzen, die der Betreiber nicht geliefert hat.
- Keine Planung für Funktionen, die nicht in der Roadmap stehen.
- Keine Links auf noch nicht existierende Seiten.
