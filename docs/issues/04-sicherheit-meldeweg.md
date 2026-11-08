---
id: sicherheit-meldeweg
titel: "Sicherheits-Meldeweg"
status: offen
rolle: sicherheit
labels: bereich:design,rolle:sicherheit,status:offen
dateien: ".well-known/security.txt, SECURITY.md, docs/SICHERHEIT.md, index.html"
---

# Sicherheits-Meldeweg

## Ziel

Für ein Finanzprojekt muss ein Sicherheitskontakt existieren, bevor die
Community den Token diskutiert. Wer den Token bewirbt, muss erreichbar sein,
wenn jemand eine Schwachstelle in der Website oder im geplanten Token findet.

## Konkrete Ergebnisse

- [ ] `.well-known/security.txt` nach RFC 9116.
- [ ] `SECURITY.md` im Wurzelverzeichnis.
- [ ] `docs/SICHERHEIT.md` mit technischen Notizen und Header-Empfehlung.
- [ ] Der Sicherheitsabschnitt ist von der Startseite aus sichtbar verlinkt.

## Abnahmekriterien

- [ ] `.well-known/security.txt` folgt dem Standard (RFC 9116) und enthält
      `Contact:`, `Expires:`, `Preferred-Languages:`, `Canonical:`, `Policy:`.
- [ ] `Expires:` liegt in der Zukunft und wird **nicht** auf ein festes Datum
      zur Erstellungszeit eingetragen. `docs/SICHERHEIT.md` erklärt, wie und
      wann der Wert aktualisiert wird.
- [ ] Die Kontaktadresse ist als Platzhalter **sichtbar markiert** und in
      `docs/SICHERHEIT.md` als offener Punkt geführt.
- [ ] `SECURITY.md` erklärt: wie man meldet, was gemeldet wird, welche Frist
      für eine Antwort gilt, und was **nicht** gemeldet wird
      (Schwachstellen in Drittanbieter-Diensten, Social-Media-Missbrauch).
- [ ] `docs/SICHERHEIT.md` nennt die HTTP-Header, die der Hosting-Anbieter
      setzen soll: `X-Content-Type-Options`, `Referrer-Policy`,
      `X-Frame-Options`, `Permissions-Policy`, `Strict-Transport-Security`.
- [ ] Der Sicherheitsabschnitt ist in `index.html` verlinkt — sichtbar, nicht
      versteckt. Zulässig: ein Eintrag im Footer oder ein Verweis aus
      `#risiko`.
- [ ] `tools/check-links.py` findet den Verweis auf `.well-known/security.txt`
      und meldet ihn nicht als toten Link.
- [ ] `python3 tools/release-check.py http://127.0.0.1:8188` ist grün.

## Abhängigkeiten

- **Keine harte Abhängigkeit.** Startet sofort.
- **Benötigt vom Betreiber:** eine Sicherheitskontaktadresse. Derzeit offen.
  Die Struktur entsteht jetzt, die Adresse folgt.
- **Berührt `index.html`:** Koordination mit #{{design-struktur}} absprechen.

## Zuständige Rolle

Sicherheit. Keine andere Rolle ändert `.well-known/security.txt` oder
`SECURITY.md`.

## Betroffene Dateien und Bereiche

| Datei | Art der Änderung |
|---|---|
| `.well-known/security.txt` | neu |
| `SECURITY.md` | neu |
| `docs/SICHERHEIT.md` | neu |
| `index.html` | Verweis auf den Sicherheitsabschnitt |

## Nicht tun

- Keine Sicherheitslücken „zum Testen" ankündigen.
- Keine Bug-Bounty-Zahl versprechen, die es nicht gibt.
- Keine Kontaktadresse raten oder aus einem Muster übernehmen.
