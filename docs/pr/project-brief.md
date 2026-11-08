# Projekt-Brief und Dokumentationsbasis

## Was dieses PR tut

Er stellt die Dokumentationsbasis für die gesamte Website-Arbeit her:

- `docs/project-brief.md` — bestätigte Fakten, offene Entscheidungen, Umfang
  der ersten Version.
- `docs/issues/` — der Issuesatz, aus dem das Tracking-Issue und die
  Arbeits-Issues entstehen.
- `docs/AGENTEN-BRETT.md` — Verweis auf den Brief als verbindliche Grundlage.
- `tools/gh-api.py` — GitHub-API-Helfer, der `gh` ersetzt. `AGENTS.md` verweist
  bereits auf diese Datei, sie fehlte aber.

## Warum

`AGENTS.md` verlangt Koordination über ein GitHub-Issue und über das
Agenten-Brett. Das Brett existierte, das Issue und der Brief nicht. Ohne
Brief arbeiten die Rollen ohne gemeinsame Grundlage: keine Einigkeit darüber,
was bestätigt ist, was offen ist und was die erste Version umfasst.

## Aufbau von `docs/issues/`

Jede Datei ist ein Issue mit maschinenlesbarem Frontmatter:

```
---
id: rechtstexte
titel: "Rechtstexte: Impressum und Datenschutzerklärung"
status: offen
rolle: recht
labels: bereich:inhalte,rolle:recht,status:offen
dateien: "impressum.html, datenschutz.html, docs/RECHT.md, index.html"
---
```

`id` dient als Schlüssel für Verweise zwischen den Issues. `{{rechtstexte}}`
wird beim Anlegen durch die tatsächliche Issue-Nummer ersetzt, `{{#rechtstexte}}`
durch einen Link auf das Issue.

Die Rollen sind: Koordination, Redaktion, Design, Recht, SEO, i18n,
Sicherheit, Qualitätssicherung. Jeder Arbeitsbereich gehört genau einer Rolle.

## Erzeugen der Issues

```bash
# 1. Token bereitstellen (einmalig)
security add-generic-password -s github.com -a predatorhwg-commits -w <token>
# oder: export GITHUB_TOKEN=...

# 2. Zugriff prüfen
python3 tools/gh-api.py check

# 3. Alle Issues anlegen (Legenden, Issues, Verweise auflösen)
python3 tools/gh-api.py issue create-batch --dir docs/issues

# 4. Tracking-Issue mit Aufgabenliste und Statusübersicht füllen
python3 tools/gh-api.py issue update-tracking <NUMMER> --dir docs/issues
```

`create-batch` legt die Issues in der Reihenfolge der Dateinamen an,
erzeugt die Labels und ersetzt anschließend alle `{{id}}`-Verweise mit den
tatsächlichen Nummern. `update-tracking` schreibt die verlinkte Aufgabenliste
und die Statusübersicht in die markierten Abschnitte des Tracking-Issues.

## Nächste Schritte

Nach dem Merge dieses PRs:

1. `python3 tools/gh-api.py issue create-batch --dir docs/issues` ausführen.
2. Das Tracking-Issue als Referenz im Agenten-Brett vermerken.
3. Die Rollen den Issues zuweisen und mit der Arbeit beginnen.

## Prüfung

Die Änderung betrifft keine Webseite. Der Prüflauf muss unverändert grün sein:

```bash
python3 -m http.server 8188
python3 tools/release-check.py http://127.0.0.1:8188
```

Keine Secrets in diesem PR: Das Token wird zur Laufzeit aus der Umgebung oder
dem Schlüsselbund gelesen und steht in keiner Datei.

## Nicht tun

- Keine Angaben ergänzen, die der Betreiber nicht geliefert hat.
- Keine Preise, Teilnehmerzahlen oder Termine.
- Keine internen Zugangsdaten in Dateien.
