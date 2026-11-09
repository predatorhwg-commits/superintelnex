#!/usr/bin/env python3
"""GitHub-API-Helfer fuer SuperIntelNex (ersetzt `gh` auf dieser Maschine).

Spraecht die GitHub-REST-API direkt an. Standard-Repository:
predatorhwg-commits/superintelnex. Aufrufbeispiele:

    python3 tools/gh-api.py check
    python3 tools/gh-api.py issue list --state open
    python3 tools/gh-api.py issue create-batch --dir docs/issues
    python3 tools/gh-api.py issue update-tracking 21 --dir docs/issues
    python3 tools/gh-api.py issue set-status 5 in-arbeit
    python3 tools/gh-api.py pr create --title "..." --body-file docs/pr/project-brief.md \
        --base main --head docs/project-brief

Token-Quellen (in dieser Reihenfolge):
    1. --token-Parameter
    2. GITHUB_TOKEN oder GH_TOKEN in der Umgebung
    3. `security find-generic-password -s github.com -a <owner> -w`
    4. `security find-internet-password -s github.com -w`

In dieser Datei und im Repository stehen keine Zugangsdaten.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

STANDARD_REPO = "predatorhwg-commits/superintelnex"
API = "https://api.github.com"
WEB = "https://github.com"

# Farben fuer neu angelegte Labels. Bestehende Labels werden so uebernommen,
# wie sie schon im Repository existieren (Beleg: label-sichern ist
# idempotent). Bestehende Farben der Vorlage:
#   rolle:* -> ededed,  dokumentation -> c2e0c6
LABEL_COLORS = {
    "rolle:koordination": "ededed",
    "rolle:recht": "ededed",
    "rolle:redaktion": "ededed",
    "rolle:design": "ededed",
    "rolle:seo": "ededed",
    "rolle:sicherheit": "ededed",
    "rolle:qa": "ededed",
    "rolle:i18n": "ededed",
    "dokumentation": "c2e0c6",
    "bereich:inhalte": "5319e7",
    "bereich:design": "bf59f0",
    "bereich:qualitaet": "ebc04f",
    "bereich:implementierung": "1d76db",
    "status:offen": "fbca04",
    "status:in-arbeit": "1d76db",
    "status:blockiert": "d73a49",
    "status:in-pruefung": "008677",
    "status:erledigt": "2da44e",
}
DEFAULT_LABEL_COLOR = "888888"

STATUS_WERTE = ("offen", "in-arbeit", "blockiert", "in-pruefung", "erledigt")


def fehlermeldung(text: str) -> None:
    print(f"FEHLER: {text}", file=sys.stderr)
    sys.exit(1)


def token_finden(owner: str) -> str:
    """Liest das Token aus der Umgebung oder aus dem macOS-Schluesselbund."""
    for var in ("GITHUB_TOKEN", "GH_TOKEN"):
        wert = os.environ.get(var, "").strip()
        if wert:
            return wert
    for kommando in (
        ["security", "find-generic-password", "-s", "github.com", "-a", owner, "-w"],
        ["security", "find-internet-password", "-s", "github.com", "-w"],
    ):
        try:
            ausgabe = subprocess.run(
                kommando, capture_output=True, text=True, timeout=15
            )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
        if ausgabe.returncode == 0 and ausgabe.stdout.strip():
            return ausgabe.stdout.strip()
    fehlermeldung(
        "Kein GitHub-Token gefunden.\n"
        "  export GITHUB_TOKEN=<token>\n"
        f"oder: security add-generic-password -s github.com -a {owner} -w <token>"
    )
    return ""


def api(rueck: str, methode: str, pfad: str, token: str,
        daten: dict | None = None) -> dict:
    """Spraecht die GitHub-REST-API an und liefert das JSON-Ergebnis."""
    kopf = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "User-Agent": "superintelnex-gh-api",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    rochuss = None
    if daten is not None:
        rochuss = json.dumps(daten).encode("utf-8")
        kopf["Content-Type"] = "application/json"
    anfrage = urllib.request.Request(
        f"{API}/{pfad}", data=rochuss, headers=kopf, method=methode
    )
    try:
        with urllib.request.urlopen(anfrage, timeout=60) as antwort:
            roh = antwort.read().decode("utf-8")
    except urllib.error.HTTPError as fehler:
        detail = fehler.read().decode("utf-8", "replace")
        try:
            detail = json.loads(detail).get("message", detail)
        except (json.JSONDecodeError, TypeError):
            pass
        fehlermeldung(f"GitHub meldete {fehler.code}: {detail} (bei {pfad})")
    except urllib.error.URLError as fehler:
        fehlermeldung(f"Kein Zugriff auf die GitHub-API ({fehler.reason}, {pfad})")
    return json.loads(roh or "{}")


# ---------------------------------------------------------------------
# Frontmatter und Platzhalter
# ---------------------------------------------------------------------


def frontmatter_lesen(pfad: str) -> dict:
    """Liest `schluessel: wert`-Zeilen zwischen den `---`-Markierungen.

    Fortsatzzeilen (einrueckend) werden zum aktuellen Schluessel
    angehaengt, weil `dateien` in den Issue-Dateien umgebrochen ist.
    """
    meta: dict[str, str] = {}
    with open(pfad, encoding="utf-8") as inhalt:
        zeilen = inhalt.readlines()
    if not zeilen or zeilen[0].strip() != "---":
        fehlermeldung(f"{pfad}: kein Frontmatter (erwartet `---` als erste Zeile)")
    aktuel: str | None = None
    for zeile in zeilen[1:]:
        if zeile.strip() == "---":
            break
        treffer = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", zeile)
        if treffer:
            aktuel = treffer.group(1)
            meta[aktuel] = treffer.group(2).strip()
        elif aktuel is not None:
            meta[aktuel] = meta[aktuel] + " " + zeile.strip()
    for benoetigt in ("id", "titel"):
        if benoetigt not in meta:
            fehlermeldung(f"{pfad}: Frontmatter fehlt die Zeile `{benoetigt}`")
    return meta


def koerper_lesen(pfad: str) -> str:
    """Liefert den Dateiinhalt ab der ersten Zeile nach dem Frontmatter."""
    with open(pfad, encoding="utf-8") as inhalt:
        zeilen = inhalt.readlines()
    if not zeilen or zeilen[0].strip() != "---":
        return "".join(zeilen)
    for index in range(1, len(zeilen)):
        if zeilen[index].strip() == "---":
            return "".join(zeilen[index + 1:])
    return "".join(zeilen)


def frontmatter_bewahren(pfad: str, koerper: str) -> None:
    """Schreibt die Datei neu: altes Frontmatter + neuer Koerper."""
    with open(pfad, encoding="utf-8") as inhalt:
        zeilen = inhalt.readlines()
    kopf: list[str] = []
    for index, zeile in enumerate(zeilen):
        kopf.append(zeile)
        if index > 0 and zeile.strip() == "---":
            break
    with open(pfad, "w", encoding="utf-8") as ausgabe:
        ausgabe.write("".join(kopf) + koerper)


def platzaehler_aufloesen(koerper: str, nummern: dict[str, int],
                          repo: str) -> str:
    """Ersetzt Referenzplatzhalter mit Nummern und Links.

    - `{{#id}}`  wird zum GitHub-Link
    - `#{{id}}`  wird zu `#N`
    - `{{id}}`   wird zu `#N`
    Unbekannte Kennungen bleiben unangetastet, damit fuehlt sie beim
    Pruefen sichtbar bleiben.
    """
    owner, name = repo.split("/")
    basis = f"{WEB}/{owner}/{name}/issues"

    def link_sub(match: re.Match) -> str:
        if match.group(1) in nummern:
            n = nummern[match.group(1)]
            return f"[#{n}]({basis}/{n})"
        return match.group(0)

    def nummer_sub(match: re.Match) -> str:
        if match.group(1) in nummern:
            return f"#{nummern[match.group(1)]}"
        return match.group(0)

    koerper = re.sub(r"\{\{#([\w-]+)\}\}", link_sub, koerper)
    koerper = re.sub(r"#\{\{([\w-]+)\}\}", nummer_sub, koerper)
    koerper = re.sub(r"\{\{([\w-]+)\}\}", nummer_sub, koerper)
    return koerper


# ---------------------------------------------------------------------
# Grundbefehle
# ---------------------------------------------------------------------


def info_zeigen(repo: str, token: str) -> dict:
    return api(repo, "GET", f"repos/{repo}", token)


def cmd_check(repo: str, token: str) -> int:
    info = info_zeigen(repo, token)
    print(f"Repository: {info['full_name']} (privat: {info['private']})")
    print(f"Standardbranch: {info['default_branch']}")
    print(f"URL: {info['html_url']}")
    return 0


def cmd_repo(repo: str, token: str) -> int:
    info = info_zeigen(repo, token)
    for beschriftung, wert in (
        ("Name", info["name"]),
        ("Owner", info["owner"]["login"]),
        ("Privat", str(info["private"])),
        ("Standardbranch", info["default_branch"]),
        ("Offene Issues/PRs", str(info.get("open_issues_count", "?"))),
        ("URL", info["html_url"]),
    ):
        print(f"{beschriftung:16} {wert}")
    return 0


def cmd_labels(repo: str, token: str) -> int:
    alle: list[dict] = []
    seite = 1
    while True:
        daten = api(repo, "GET", f"repos/{repo}/labels?per_page=100&page={seite}",
                    token)
        if not daten:
            break
        alle.extend(daten)
        if len(daten) < 100:
            break
        seite += 1
    for label in alle:
        zeile = f"  {label['name']:26} #{label.get('color', '?')}"
        beschreibung = (label.get("description") or "").strip()
        if beschreibung:
            zeile += f"   {beschreibung}"
        print(zeile)
    print(f"{len(alle)} Labels gesamt." if alle else "(noch keine Labels)")
    return 0


def labels_sichern(repo: str, token: str, namen: list[str]) -> None:
    """Stellt sicher, dass alle benoetigten Labels existieren."""
    vorhanden = {
        label["name"]
        for label in api(repo, "GET", "repos/{}/labels?per_page=100".format(repo),
                        token)
    }
    for name in sorted(namen):
        if name in vorhanden:
            continue
        farbe = LABEL_COLORS.get(name, DEFAULT_LABEL_COLOR)
        api(repo, "POST", f"repos/{repo}/labels", token,
            {"name": name, "color": farbe})
        print(f"  Label angelegt: {name}")
    if not (set(namen) - vorhanden):
        print("  Alle Labels vorhanden.")


def issues_listen(repo: str, token: str, state: str) -> list[dict]:
    daten = api(
        repo, "GET",
        f"repos/{repo}/issues?state={state}&per_page=100&sort=created&direction=asc",
        token,
    )
    return [i for i in daten if "pull_request" not in i]


def cmd_issue_list(repo: str, token: str, state: str) -> int:
    issues = issues_listen(repo, token, state)
    for issue in issues:
        marke = "offen" if issue["state"] == "open" else "geschlossen"
        print(f"#{issue['number']} [{marke}] {issue['title']}")
    if not issues:
        print(f"(keine Issues im Zustand `{state}`)")
    return 0


def cmd_issue_create(repo: str, token: str, titel: str, textdatei: str,
                    labels: str) -> int:
    """Legt ein einzelnes Issue an (ergaenzt create-batch fuer Nachruester)."""
    with open(textdatei, encoding="utf-8") as inhalt:
        koerper = inhalt.read()
    label_list = [x.strip() for x in labels.split(",") if x.strip()]
    if label_list:
        labels_sichern(repo, token, label_list)
    neu = api(repo, "POST", f"repos/{repo}/issues", token,
              {"title": titel, "body": koerper, "labels": label_list})
    print(f"#{neu['number']} erstellt: {neu['html_url']}")
    return 0


def issue_finden(repo: str, token: str, nummer: int) -> dict:
    return api(repo, "GET", f"repos/{repo}/issues/{nummer}", token)


def issue_koerper_setzen(repo: str, token: str, nummer: int, koerper: str) -> None:
    api(repo, "PATCH", f"repos/{repo}/issues/{nummer}", token, {"body": koerper})


# ---------------------------------------------------------------------
# create-batch und update-tracking
# ---------------------------------------------------------------------


def create_batch(repo: str, token: str, ablage: str) -> int:
    """Legt alle Issues aus `*.md`-Dateien an und loest Verweise auf.

    Reihenfolge: Dateinamen (das Tracking-File kommt damit zuerst).
    Nach dem Anlegen werden in allen Koerpersen (auf GitHub und lokal)
    die Platzhalter mit den tatsaechlichen Nummern ersetzt.
    """
    dateien = sorted(
        os.path.join(ablage, f) for f in os.listdir(ablage) if f.endswith(".md")
    )
    if not dateien:
        fehlermeldung(f"Keine .md-Dateien in {ablage}")
    metae = [(pfad, frontmatter_lesen(pfad)) for pfad in dateien]
    kennungen = [m["id"] for _, m in metae]
    if len(kennungen) != len(set(kennungen)):
        fehlermeldung("Doppelte `id`-Werte im Frontmatter; jede id nur einmal.")

    benoetigt: set[str] = set()
    for _, m in metae:
        benoetigt.update(
            x.strip() for x in m.get("labels", "").split(",") if x.strip()
        )
        benoetigt.add(f"status:{m.get('status', 'offen').strip()}")
    print("Labels sicherstellen:")
    labels_sichern(repo, token, sorted(benoetigt))

    nummern: dict[str, int] = {}
    entwoerfe: list[tuple[str, int, dict, str]] = []
    print("Issues anlegen:")
    for pfad, m in metae:
        labels = [x.strip() for x in m.get("labels", "").split(",") if x.strip()]
        titel = m["titel"].strip().strip('"').strip("'")
        koerper = koerper_lesen(pfad)
        neu = api(repo, "POST", f"repos/{repo}/issues", token,
                  {"title": titel, "body": koerper, "labels": labels})
        nummern[m["id"]] = neu["number"]
        print(f"  #{neu['number']}  {m['id']:<20} {titel}")
        entwoerfe.append((pfad, neu["number"], m, koerper))

    print("Referenzen auflösen:")
    gezaehlt = 0
    for pfad, nummer, _, koerper in entwoerfe:
        alt = koerper
        neu = platzaehler_aufloesen(koerper, nummern, repo)
        if neu == alt:
            continue
        gezaehlt += 1
        issue_koerper_setzen(repo, token, nummer, neu)
        frontmatter_bewahren(pfad, neu)
        print(f"  #{nummer} aktualisiert (#{gezaehlt})")
    print(f"Fertig: {gezaehlt} von {len(entwoerfe)} Issues mit Referenzen "
          f"(lokal und auf GitHub).")
    if "tracking" in nummern:
        print(f"Tracking-Issue: #{nummern['tracking']}")
    return 0


def aufgabenliste_bauen(
    metae: list[dict], nummern: dict[str, int], repo: str
) -> tuple[str, dict[str, list[str]]]:
    zeilen = ["| Aufgabe | Rolle | Status |", "|---|---|---|"]
    status_gruppe: dict[str, list[str]] = {}
    for m in metae:
        titel = m["titel"].strip().strip('"').strip("'")
        status = m.get("status", "offen").strip()
        if m["id"] in nummern:
            n = nummern[m["id"]]
            aufgabe = f"[#{n}]({WEB}/{repo}/issues/{n}) {titel}"
        else:
            aufgabe = f"`{{{{{m['id']}}}}}` (noch nicht angelegt) {titel}"
        zeilen.append(f"| {aufgabe} | {m.get('rolle', '?')} | {status} |")
        status_gruppe.setdefault(status, []).append(aufgabe)
    return "\n".join(zeilen), status_gruppe


def statusuebersicht_bauen(status_gruppe: dict[str, list[str]]) -> str:
    zeilen = ["| Status | Anzahl |", "|---|---|"]
    for status in STATUS_WERTE:
        if status in status_gruppe:
            zeilen.append(f"| {status} | {len(status_gruppe[status])} |")
    return "\n".join(zeilen)


def abschnitt_fuellen(koerper: str, marke: str, inhalt: str) -> str:
    """Ersetzt den Text zwischen den BEGIN/END-Markierungen."""
    muster = (r"(?ms)^<!-- BEGIN:%s -->.*?^<!-- END:%s -->$"
              % (re.escape(marke), re.escape(marke)))
    ersetzt = (f"<!-- BEGIN:{marke} -->\n{inhalt}\n<!-- END:{marke} -->")
    neu, anzahl = re.subn(muster, ersetzt, koerper)
    if anzahl != 1:
        fehlermeldung(
            f"Markierung `{marke}` fehlt oder kommt mehr als einmal vor; "
            f"{anzahl} Treffer"
        )
    return neu


def update_tracking(repo: str, token: str, nummer_arg: str, ablage: str) -> int:
    """Füllt die markierten Abschnitte des Tracking-Issues.

    `AUFGABENLISTE` und `STATUSUEBERSICHT` entstehen aus den lokalen
    Issue-Dateien; die Nummern kommen aus den offenen Issues. Das
    Tracking-Issue auf GitHub und die lokale `00-tracking.md` werden
    gleich gefuellt.
    """
    try:
        nummer = int(nummer_arg)
    except ValueError:
        fehlermeldung("Tracking-Issue-Nummer muss eine Zahl sein.")
    tracking = issue_finden(repo, token, nummer)
    koerper = tracking.get("body") or ""
    for marke in ("AUFGABENLISTE", "STATUSUEBERSICHT"):
        if f"<!-- BEGIN:{marke} -->" not in koerper:
            fehlermeldung(
                f"Tracking-Issue #{nummer} fehlt die Markierung "
                f"`BEGIN:{marke}`"
            )

    dateien = sorted(
        os.path.join(ablage, f) for f in os.listdir(ablage) if f.endswith(".md")
    )
    metae = []
    for pfad in dateien:
        m = frontmatter_lesen(pfad)
        if m["id"] != "tracking":
            metae.append(m)

    # Nummern nach id ermitteln (offene und geschlossene Issues)
    nummern: dict[str, int] = {}
    titel_zu_id = {
        m["titel"].strip().strip('"').strip("'"): m["id"] for m in metae
    }
    for issue in issues_listen(repo, token, "all"):
        tid = titel_zu_id.get(issue["title"])
        if tid:
            nummern[tid] = issue["number"]

    liste, gruppen = aufgabenliste_bauen(metae, nummern, repo)
    tabelle = statusuebersicht_bauen(gruppen)
    koerper = abschnitt_fuellen(koerper, "AUFGABENLISTE", liste)
    koerper = abschnitt_fuellen(koerper, "STATUSUEBERSICHT", tabelle)
    issue_koerper_setzen(repo, token, nummer, koerper)
    print(f"Tracking-Issue #{nummer} gefuellt "
          f"({len(metae)} Aufgaben, {len(gruppen)} Statusgruppen).")

    spiegel = os.path.join(ablage, "00-tracking.md")
    if os.path.exists(spiegel):
        lokal = koerper_lesen(spiegel)
        lokal = platzaehler_aufloesen(lokal, nummern, repo)
        lokal = abschnitt_fuellen(lokal, "AUFGABENLISTE", liste)
        lokal = abschnitt_fuellen(lokal, "STATUSUEBERSICHT", tabelle)
        frontmatter_bewahren(spiegel, lokal)
        print(f"  Lokale Spiegelung geschrieben: {spiegel}")
    return 0


# ---------------------------------------------------------------------
# Uebrliche Issue-Befehle
# ---------------------------------------------------------------------


def cmd_issue_status(repo: str, token: str, nummer_arg: str, status: str) -> int:
    nummer = int(nummer_arg)
    issue = issue_finden(repo, token, nummer)
    labels = [l["name"] for l in issue.get("labels", [])]
    labels = [x for x in labels if not x.startswith("status:")]
    labels.append(f"status:{status}")
    api(repo, "PATCH", f"repos/{repo}/issues/{nummer}", token, {"labels": labels})
    print(f"#{nummer} → status:{status}")
    return 0


def cmd_issue_close(repo: str, token: str, nummer_arg: str) -> int:
    nummer = int(nummer_arg)
    api(repo, "POST", f"repos/{repo}/issues/{nummer}/close", token, {})
    print(f"#{nummer} geschlossen.")
    return 0


def cmd_issue_comment(repo: str, token: str, nummer_arg: str, text: str) -> int:
    nummer = int(nummer_arg)
    api(repo, "POST", f"repos/{repo}/issues/{nummer}/comments", token,
        {"body": text})
    print(f"Kommentar auf #{nummer} geschrieben.")
    return 0


def cmd_issue_view(repo: str, token: str, nummer_arg: str) -> int:
    nummer = int(nummer_arg)
    issue = issue_finden(repo, token, nummer)
    marke = "offen" if issue["state"] == "open" else "geschlossen"
    print(f"#{issue['number']} [{marke}] {issue['title']}")
    labels = [l["name"] for l in issue.get("labels", [])]
    if labels:
        print(f"Labels: {', '.join(labels)}")
    print()
    print(issue.get("body") or "(kein Text)")
    return 0


# ---------------------------------------------------------------------
# Pull Requests
# ---------------------------------------------------------------------


def pr_list(repo: str, token: str, state: str) -> list[dict]:
    if state == "all":
        return (api(repo, "GET", "repos/{}/pulls?state=open&per_page=100".format(repo),
                    token)
                + api(repo, "GET",
                      "repos/{}/pulls?state=closed&per_page=100".format(repo),
                      token))
    return api(repo, "GET",
               f"repos/{repo}/pulls?state={state}&per_page=100", token)


def cmd_pr_list(repo: str, token: str, state: str) -> int:
    prs = pr_list(repo, token, state)
    for pr in prs:
        marke = pr["state"]
        print(f"#{pr['number']} [{marke}] {pr['title']} "
              f"({pr['head']['label']} → {pr['base']['label']})")
    if not prs:
        print(f"(keine PRs im Zustand `{state}`)")
    return 0


def cmd_pr_create(repo: str, token: str, titel: str, textdatei: str,
                  basis: str, kopf: str) -> int:
    with open(textdatei, encoding="utf-8") as inhalt:
        koerper = inhalt.read()
    pr = api(repo, "POST", f"repos/{repo}/pulls", token,
             {"title": titel, "body": koerper, "base": basis, "head": kopf})
    print(f"PR #{pr['number']} erstellt: {pr['html_url']}")
    return 0


# ---------------------------------------------------------------------
# Datei-Inhalt aus dem Repository
# ---------------------------------------------------------------------


def cmd_raw(repo: str, token: str, pfad: str) -> int:
    daten = api(repo, "GET",
                f"repos/{repo}/contents/{urllib.parse.quote(pfad)}", token)
    if "content" not in daten:
        fehlermeldung(f"{pfad}: API lieferte keinen Inline-Inhalt")
    print(base64.b64decode(daten["content"]).decode("utf-8"), end="")
    return 0


# ---------------------------------------------------------------------
# Argumente
# ---------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="gh-api.py",
        description="GitHub-API-Helfer fuer SuperIntelNex (ersetzt `gh`).",
    )
    parser.add_argument("--repo", default=STANDARD_REPO,
                        help="Repository als owner/name "
                             f"(Standard: {STANDARD_REPO})")
    parser.add_argument("--token", default=None,
                        help="GitHub-Token (ueberschreibt Umgebung/Schluesselbund)")
    sub = parser.add_subparsers(dest="befehl", required=True)

    sub.add_parser("check", help="Zugriff und Repository-Info pruefen")
    sub.add_parser("repo", help="Repository-Details anzeigen")
    sub.add_parser("labels", help="Alle Labels auflisten")

    issue_p = sub.add_parser("issue", help="Issue-Befehle")
    issue_sub = issue_p.add_subparsers(dest="issue_befehl", required=True)
    i_list = issue_sub.add_parser("list", help="Issues auflisten")
    i_list.add_argument("--state", default="open",
                        choices=["open", "closed", "all"])
    i_batch = issue_sub.add_parser("create-batch",
                                   help="Alle Issues aus .md-Dateien anlegen")
    i_batch.add_argument("--dir", default="docs/issues")
    i_create = issue_sub.add_parser("create",
                                    help="Ein einzelnes Issue anlegen")
    i_create.add_argument("titel")
    i_create.add_argument("--body-file", required=True)
    i_create.add_argument("--labels", default="",
                          help="kommagetrennte Labels, werden bei Bedarf angelegt")
    i_track = issue_sub.add_parser("update-tracking",
                                   help="Tracking-Issue mit Aufgabenliste und "
                                       "Statusuebersicht fuellen")
    i_track.add_argument("nummer")
    i_track.add_argument("--dir", default="docs/issues")
    i_status = issue_sub.add_parser("set-status",
                                    help="Status-Label eines Issues setzen")
    i_status.add_argument("nummer")
    i_status.add_argument("status", choices=list(STATUS_WERTE))
    i_close = issue_sub.add_parser("close", help="Issue schliessen")
    i_close.add_argument("nummer")
    i_comment = issue_sub.add_parser("comment", help="Kommentar schreiben")
    i_comment.add_argument("nummer")
    i_comment.add_argument("text")
    i_view = issue_sub.add_parser("view", help="Issue-Text anzeigen")
    i_view.add_argument("nummer")

    pr_p = sub.add_parser("pr", help="Pull-Request-Befehle")
    pr_sub = pr_p.add_subparsers(dest="pr_befehl", required=True)
    p_list = pr_sub.add_parser("list", help="PRs auflisten")
    p_list.add_argument("--state", default="open",
                        choices=["open", "closed", "all", "merged"])
    p_create = pr_sub.add_parser("create", help="PR aus Branch erstellen")
    p_create.add_argument("--title", required=True)
    p_create.add_argument("--body-file", required=True)
    p_create.add_argument("--base", required=True)
    p_create.add_argument("--head", required=True)

    raw_p = sub.add_parser("raw",
                          help="Inhalt einer Datei aus dem Repository ausgeben")
    raw_p.add_argument("pfad")

    args = parser.parse_args()
    repo = args.repo
    token = args.token or token_finden(repo.split("/")[0])

    if args.befehl == "check":
        return cmd_check(repo, token)
    if args.befehl == "repo":
        return cmd_repo(repo, token)
    if args.befehl == "labels":
        return cmd_labels(repo, token)
    if args.befehl == "issue":
        unterbefehl = args.issue_befehl
        if unterbefehl == "list":
            return cmd_issue_list(repo, token, args.state)
        if unterbefehl == "create-batch":
            return create_batch(repo, token, args.dir)
        if unterbefehl == "create":
            return cmd_issue_create(repo, token, args.titel, args.body_file,
                                    args.labels)
        if unterbefehl == "update-tracking":
            return update_tracking(repo, token, args.nummer, args.dir)
        if unterbefehl == "set-status":
            return cmd_issue_status(repo, token, args.nummer, args.status)
        if unterbefehl == "close":
            return cmd_issue_close(repo, token, args.nummer)
        if unterbefehl == "comment":
            return cmd_issue_comment(repo, token, args.nummer, args.text)
        if unterbefehl == "view":
            return cmd_issue_view(repo, token, args.nummer)
    if args.befehl == "pr":
        if args.pr_befehl == "list":
            return cmd_pr_list(repo, token, args.state)
        if args.pr_befehl == "create":
            return cmd_pr_create(repo, token, args.title, args.body_file,
                                 args.base, args.head)
    if args.befehl == "raw":
        return cmd_raw(repo, token, args.pfad)

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
