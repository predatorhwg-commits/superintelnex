# Recht — Offene Angaben für den Betreiber (Lieferliste)

**Agent:** Recht & Compliance · **Datum:** 2026-11-09 · **Status:** offen — die folgenden Angaben fehlen.
Bis dahin sind sie in `site/impressum.html` und `site/datenschutz.html` als sichtbar markierte
`PLATZHALTER — wird ergänzt`-Boxen enthalten. **Keine Muster- oder Beispieldaten verwenden.**

Vorrang-Kriterium: Pflichtangaben (§ 5 TMG / § 18 RStV) vor „schön-oder-besser“-Angaben.
Innerhalb einer Stufe: P0 erst, dann P1, dann P2.

## P0 — Pflichtangaben (Impressum lückenhaft ohne diese)

| # | Angabe | Für welche Pflichtangabe fehlt? | Begründung / was mitgebracht werden muss |
|---|--------|---------------------------------|------------------------------------------|
| 1 | **Name / Firma des Betreibers** (vollständig) | Pflicht „Name der verantwortlichen Person / des Unternehmens“ | Ohne Namen des Verantwortlichen ist das Impressum unvollständig — gravierendster Mangel. |
| 2 | **Vollständige Postanschrift** (Straße mit Hausnummer, PLZ, Ort) | Pflicht „vollständige Postanschrift“ | Nur als konkrete Anschrift; keine Postfach-Floskeln. |
| 3 | **Vertretungsberechtigter** (wer tritt den Betreiberschaft für diese Seite — Name) | Pflicht „Vertretungsberechtigte(r) Person“ | Bei Einzelunternehmer: der Inhaber selbst; bei Personengesellschaft: die vertretungsbefugten Gesellschafter. |
| 4 | **Kontakt: E-Mail** (ggf. zusätzlich Telefon) | Pflicht „elektronisch erreichbare Anschrift“ (E-Mail ist Pflicht; Telefon nur, wenn vorhanden) | E-Mail genügt; die Telefonnummer darf nicht erfunden werden — nur mitliefern, wenn es eine gibt. |
| 5 | **Rechtsform** | Pflicht „Rechtsform“ (falls nicht Einzelunternehmen) | z. B. e. K., GbR, UG, GmbH — entscheidet auch, ob Registerangabe nötig (P1-5). |

## P1 — Register & Aufsichtsbehörde (hängt von P0 ab)

| # | Angabe | Für welche Pflichtangabe fehlt? | Begründung |
|---|--------|---------------------------------|------------|
| 6 | **Registergericht + Register-/VR-Nummer** — nur wenn Rechtsform registrierungspflichtig (GmbH, UG, GbR im VR, e. V.) | Pflicht „Registerangaben, falls zutreffend“ | Wenn die Rechtsform keine Eintragungspflicht hat: „nicht anwendbar“ — dann keine Angabe nötig. |
| 7 | **Staat der EU-Hauptniederlassung / der Wohnsitz des Verantwortlichen** | Aufsichtsbehörde (Datenschutz) | Erst mit Sitz ist die zuständige Landes-Aufsichtsbehörde benennbar. Bis dahin ist der Datenschutz-Platzhalter „wird ergänzt“. |

## P2 — optional, aber sinnvoll (Finanzprojekt)

| # | Angabe | Für welche Pflichtangabe fehlt? | Begründung |
|---|--------|---------------------------------|------------|
| 8 | **Verantwortlicher für den Inhalt im Sinne des § 18 RStV** (falls redaktionelle Inhalte über den Community-Status hinaus geplant werden) | RStV-Pflichtangabe, falls Telemedien mit redaktionellen Inhalten vorliegen | Wenn die Website nur Community-Status (kein Rundfunk/keine redaktionellen Inhalte) hat: P2-8 entfällt. |

## Offene Rechtsfragen (nicht betreibergespeist, aber relevant)

- **Rechtsform-Entscheidung:** Ist der Betreiber Einzelunternehmer, Personengesellschaft, UG/GmbH?
  → entscheidet, ob Registerangabe (P1-6) nötig ist und wie die Vertretung (P0-3) aussieht.
- **EU-Sitz:** Hat der Betreiber einen Wohnsitz bzw. eine Niederlassung in der EU (Länder: DE / AT / CH)?
  → entscheidet, welche Aufsichtsbehörde im Datenschutz benannt werden kann (P1-7).
- **Hauptgeschäftsort vs. Domain:** Die Ziel-Domain ist `superintelnex.com`, Live-Link läuft über Netlify-Subdomain.
  → keine rechtliche Pflicht, aber für die Impressum-Angabe „Projekt / Website“ konsistent halten.

## Nächster Schritt

**Betreiber:** Die P0-Posten 1–5 mit den echten Daten liefern.
**CEO/Recht:** Die Platzhalter im Impressum/Datenschutz dann konkret ersetzen und den Berichts-Status von
`blockiert (Betreiberdaten ausstehend)` auf `fertig` setzen.
