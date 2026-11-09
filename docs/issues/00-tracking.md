---
id: tracking
titel: "SuperIntelNex Website – Planung und Fortschritt"
status: offen
rolle: koordination
labels: rolle:koordination,status:offen,dokumentation
dateien: "docs/issues/, docs/project-brief.md, docs/AGENTEN-BRETT.md"
---

# SuperIntelNex Website – Planung und Fortschritt

Zentrales Koordinations-Issue für die Website `superintelnex.com`
(Repository `predatorhwg-commits/superintelnex`, privat, Standardbranch `main`).

Dieses Issue ist der einzige Koordinationskanal. Es hält die Aufgabenliste,
die Statusübersicht und die Rollenverteilung. `docs/AGENTEN-BRETT.md` bleibt
das lokale Belegungsprotokoll und wird bei jedem Check-in mitgezogen.

## Zweck des Projekts

Statische Landingpage für den Community-Token **SuperIntelNex**. Kein Build-Schritt,
kein Framework, keine Abhängigkeiten. Reines HTML/CSS/JS.

Der Stand ist bewusst **„Projekt im Aufbau"**: keine Kurse, keine Käuferzahlen,
keine Partnerlogos, keine Audits, keine Kauf-Buttons. Fehlende Angaben stehen
als fehlend auf der Seite (Abschnitt `#offen`), nicht als Lücke.

## Ziele der ersten Version

1. Rechtlich veröffentlichungsfähig in DE und EU (Impressum, Datenschutz).
2. Inhaltlich belastbar und frei von erfundenen Fakten.
3. Technisch sauber: keine Konsolenfehler, kein Überlaufen, kein toter Link.
4. Barrierefrei nach WCAG-AA für die geprüften Kriterien.
5. Suchmaschinen- und Social-Media-tauglich.
6. Für eine internationale KI-Community zweisprachig erreichbar.

## Wie gearbeitet wird

- **Ein Issue pro Arbeitsbereich.** Jede Aufgabe bekommt einen eigenen Branch
  und einen eigenen PR. Kein Sammel-Commit.
- **Ein Bereich, eine Rolle.** Jeder Arbeitsbereich ist genau einer Rolle
  zugewiesen. Parallel-Arbeit an derselben Datei braucht Absprache im Brett.
- **Abnahme über Messung.** Eine Aufgabe gilt erst als erfüllt, wenn ihre
  Abnahmekriterien nachgewiesen geprüft sind. Der Nachweis gehört als Kommentar
  oder Prüfprotokoll ins Issue.
- **Vor jedem Push** läuft der vollständige Prüflauf:
  ```bash
  python3 tools/release-check.py http://127.0.0.1:8188
  ```
  Der Server läuft separat: `python3 -m http.server 8188`.
- **`main` wird direkt veröffentlicht.** Kein Force-Push, keine ungeprüften
  Sammel-Commits.

## Rollen und Arbeitsbereiche

| Rolle | Arbeitsbereich | Issues |
|---|---|---|
| Koordination | Planung, Aufgabenverteilung, Statuspflege, Freigabe | dieses Issue, #4 |
| Redaktion | Sachtexte, Tonalität, Quellenpflege | #9 |
| Design | Struktur, Lesbarkeit, Typografie, Responsive | #10 |
| Recht | Impressum, Datenschutz, Rechtshinweise | #5 |
| SEO | Social-Vorschau, Sitemap, Robots, Metadaten | #6 |
| i18n | Englische Fassung, Sprachumschalter, Glossar | #11 |
| Sicherheit | Meldeweg, Kontakt, HTTP-Header-Empfehlung | #7 |
| Qualitätssicherung | Prüfwerkzeuge, Barrierefreiheit, Gegenproben | #8, #12 |

GitHub-Zuweisungen sind in diesem privaten Repository nicht möglich, solange
es keine GitHub-Teams mit Schreibrecht gibt. Die Rolle ist deshalb hier und
in `docs/AGENTEN-BRETT.md` verbindlich dokumentiert. Sobald Teams existieren,
wird die Zuweisung zusätzlich in GitHub gesetzt.

## Reihenfolge und Abhängigkeiten

```
                 #4
                        |
    +-------------------+-------------------+
    |                   |                   |
#5  #6  #7
    |                   |                   |
    +---------+---------+                   |
              |                             |
     #9          #8
              |                             |
              +-------------+---------------+
                            |
                    #10
                            |
                    #11
                            |
                    #12
```

- **Recht, SEO, Sicherheit** sind unabhängig von den Texten und starten sofort.
- **Redaktion** braucht den Textbestand, aber keine Rechtstexte.
- **Design** misst auf dem Endstand der Inhalte und startet daher spät.
- **i18n** setzt den finalen deutschen Text voraus.
- **QA-Barrierefreiheit** prüft alle Endseiten und kommt zuletzt.

Die Reihenfolge ist eine Empfehlung, keine Sperre. Abhängigkeiten, die
tatsächlich blockieren, stehen im jeweiligen Issue unter „Abhängigkeiten".

## Aufgabenliste

<!-- BEGIN:AUFGABENLISTE -->
| Aufgabe | Rolle | Status |
|---|---|---|
| [#4](https://github.com/predatorhwg-commits/superintelnex/issues/4) Projekt-Brief und Dokumentationsbasis | koordination | offen |
| [#5](https://github.com/predatorhwg-commits/superintelnex/issues/5) Rechtstexte: Impressum und Datenschutzerklärung | recht | offen |
| [#6](https://github.com/predatorhwg-commits/superintelnex/issues/6) Social-Vorschau und Suchmaschinen | seo | offen |
| [#7](https://github.com/predatorhwg-commits/superintelnex/issues/7) Sicherheits-Meldeweg | sicherheit | offen |
| [#8](https://github.com/predatorhwg-commits/superintelnex/issues/8) Prüfwerkzeuge erweitern und Gegenproben dokumentieren | qa | offen |
| [#9](https://github.com/predatorhwg-commits/superintelnex/issues/9) Inhaltsqualität und Redaktion | redaktion | offen |
| [#10](https://github.com/predatorhwg-commits/superintelnex/issues/10) Struktur, Lesbarkeit und Responsive-Verhalten | design | offen |
| [#11](https://github.com/predatorhwg-commits/superintelnex/issues/11) Englische Fassung | i18n | offen |
| [#12](https://github.com/predatorhwg-commits/superintelnex/issues/12) Barrierefreiheit vertiefen | qa | offen |
<!-- END:AUFGABENLISTE -->

## Statusübersicht

<!-- BEGIN:STATUSUEBERSICHT -->
| Status | Anzahl |
|---|---|
| offen | 9 |
<!-- END:STATUSUEBERSICHT -->

## Definition of Done für ein Arbeits-Issue

Ein Issue wird erst geschlossen, wenn **alle** Punkte erfüllt sind:

- [ ] Alle Abnahmekriterien des Issues sind einzeln bestätigt.
- [ ] Der vollständige Prüflauf ist grün (`tools/release-check.py`).
- [ ] Keine Secrets, Keys, Logs, `status.json`, Build-Artefakte oder `*.bak_*`
      im Commit.
- [ ] Keine erfundenen Inhalte: keine Preise, keine Teilnehmerzahlen, keine
      Zitate ohne Quelle, keine Partnerlogos, keine „geprüft von"-Angaben.
- [ ] Jede geplante Funktion trägt sichtbar den Status **Geplant**.
- [ ] Der Risikohinweis (`#risiko`) ist auf der Startseite weiterhin sichtbar.
- [ ] `docs/AGENTEN-BRETT.md` ist mit Agent, Aufgabe, Dateien, Status und Commit
      aktualisiert.
- [ ] Der PR verlinkt das Issue und nennt den Prüflauf als Nachweis.

## Offene Produktentscheidungen

Diese Punkte brauchen eine Antwort vom Betreiber. Sie blockieren die
jeweiligen Aufgaben, aber nicht den Rest des Projekts.

| Frage | Blockiert | Stand |
|---|---|---|
| Betreiber, Rechtsform, Sitz, Kontaktadresse | #5 | offen |
| Hosting-Anbieter (für Datenschutzerklärung) | #5 | offen |
| Token-Kürzel, Blockchain, Gesamtmenge, Verteilung, Sperrfristen | #9 (Abschnitt `#offen`) | offen |
| Offizielle Token-Adresse | #9 | offen |
| Bestätigte Social-Media-Konten | #9, #6 | offen |
| Sicherheitskontakt für Meldungen | #7 | offen |
| Anredeform „Sie" oder „du" | #9 | offen |
| Hosting-Ziel für den Livegang | #6 (canonical, Sitemap) | offen |

Die vollständige Liste mit Erläuterungen steht in `docs/project-brief.md`.

## Protokoll

- **Check-in-Format:** `Agent | Aufgabe | Dateien | Status | Commit`
- **Status-Werte:** offen, in Arbeit, blockiert, in Prüfung, erledigt
- **Nachweise:** Prüflauf-Ausgabe, Screenshots der Messwerte, oder ein
  Kommentar im Issue, der das Kriterium einzeln bestätigt.
