# Betreiberdaten-Ablage (P0/P1/P2) — Formular + Ersatz-Map

**Zuständig:** Recht (Ablage) + Betreiber (Ausfüllen) · Stand 09.11.2026
**Quelle der Pflichtfelder:** `agenten/berichte/recht-offene-angaben.md`

## So geht's

1. **Betreiber** füllt die Felder P0-1…P0-5 (+ P1/P2 falls zutreffend) aus — **keine
   Muster- oder Beispieldaten**, nur echte Angaben.
2. **Recht-Agent** ersetzt die Platzhalter-Blöcke in `site/impressum.html` /
   `site/datenschutz.html` mit den fertigen Ziel-Textbausteinen unten (mechanisch,
   keine Neubewertung der Pflichtstruktur nötig).
3. **Gate:** `bash agenten/checks/run-gate.sh .` — QA-Check „Platzhalter sichtbar
   markiert" muss dann für die ergänzten Blöcke angepasst werden (QA-Task: Erwartung
   von 7+2 Platzhalter-Boxen → restliche Anzahl; nur noch unergänztes bleibt Platzhalter).
4. Berichts-Status: `blockiert (Betreiberdaten ausstehend)` → `fertig`.

## ABLAGE (leer ausfüllen)

```
P0-1 Name / Firma des Betreibers (vollständig):
P0-2 Vollständige Postanschrift (Straße, Hausnr, PLZ, Ort):
P0-3 Vertretungsberechtigter (Name):
P0-4 E-Mail-Kontakt:
P0-5 Rechtsform (Einzelunternehmen / e.K. / GbR / UG / GmbH / e.V.):
P1-6 Registergericht + Register-/VR-Nummer (nur bei eintragungspflichtiger Form, sonst „nicht anwendbar"):
P1-7 EU-Hauptniederlassung / Wohnsitz (Länder: DE / AT / CH) → Aufsichtsbehörde:
P2-8 Verantwortlicher i. S. d. § 18 MStV (nur bei journalistisch-redaktionellen Inhalten, sonst entfällt):
```

## Ersatz-Map (Impressum `site/impressum.html`, Zeilen ~77–83)

| Feld (dt) | Ersetzen durch (Vorlage) |
|---|---|
| `Rechtsform`-dd | `<dt>Rechtsform</dt><dd>{P0-5}{falls P1-6: „, eingetragen beim {P1-6}"}{P0-5 == „Einzelunternehmen" → „ (kein Registerhinweis erforderlich)"}</dd>` — `.placeholder`-Klasse + `.tag` entfernen |
| `Betreiber`-dd | `<dd>{P0-1}</dd>` (Klasse/Tag entfernen) |
| `Vertretungsberechtigt`-dd | `<dd>{P0-3}</dd>` |
| `Anschrift`-dd | `<dd>{P0-2}</dd>` |
| `E-Mail-Kontakt`-dd | `<dd>{P0-4}</dd>` (keine Muster-Adresse) |
| `Register`-dd | Falls P1-6 geliefert: `<dd>{P1-6}</dd>`; sonst: `<dd>Kein Registerhinweis erforderlich ({P0-5} nicht eintragungspflichtig).</dd>` |
| `§ 18 MStV`-dd | Falls P2-8: `<dd>{P2-8}</dd>`; sonst: `<dd>Nicht anwendbar — keine journalistisch-redaktionellen Inhalte.</dd>` |

## Ersatz-Map (Datenschutz `site/datenschutz.html`, Zeilen ~77–78)

| Feld | Ersetzen durch |
|---|---|
| `Verantwortlicher`-dd | `<dd>{P0-1}, {P0-2}{falls P1-7: „, Aufsichtsbehörde: {P1-7}"}</dd>` |
| `Kontaktdaten`-dd | `<dd>{P0-4}</dd>` |

## Kontrolle nach der Ergänzung
- [ ] keine `PLATZHALTER — wird ergänzt`-Tags an ersetzten Stellen mehr
- [ ] keine PLZ/Telefon/VR/VR-Nummern-Pattern ohne Betreiberfreigabe (Geheimnis-Scan)
- [ ] `keine Anlageberatung`, `Netlify`, `Devnet`-Disclaimer unverändert
- [ ] Gate exit 0 (mit QA-Check-Update)
