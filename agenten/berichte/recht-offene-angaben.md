# Recht — Offene Angaben für den Betreiber (Lieferliste)

**Agent:** Recht & Compliance · **Stand:** 2026-11-09 · **Status:** offen — die folgenden Angaben fehlen.
Bis dahin sind sie in `site/impressum.html` und `site/datenschutz.html` als sichtbar markierte
`PLATZHALTER — wird ergänzt`-Boxen enthalten. **Keine Muster- oder Beispieldaten verwenden.**

Vorrang-Kriterium: Pflichtangaben (§ 5 DDG / § 18 MStV) vor „schön-oder-besser“-Angaben.
Gesetzeslage (Stand November 2026): § 5 TMG wurde durch § 5 DDG (Digitale-Dienste-Gesetz, in Kraft seit 14.05.2024)
ersetzt; § 18 RStV ist in § 18 MStV (Medienstaatsvertrag, in Kraft seit 01.01.2020) übergegangen.
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
| 8 | **Verantwortlicher für journalistisch-redaktionelle Inhalte i. S. d. § 18 Abs. 2 MStV** (falls redaktionelle Inhalte über den Community-Status hinaus geplant werden) | MStV-Pflichtangabe (Nachfolger des früheren § 55 Abs. 2 RStV), wenn journalistisch-redaktionelle Inhalte vorliegen | Wenn die Website nur Community-Status (keine redaktionellen Inhalte) hat: P2-8 entfällt. Hinweis: Ein Verweis auf „§ 55 Abs. 2 RStV“ ist nicht mehr zulässig (RStV seit 2020 außer Kraft) — Abmahnrisiko. |

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
