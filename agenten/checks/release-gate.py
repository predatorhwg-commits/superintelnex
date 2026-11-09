#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SuperIntelNex Release-Gate (Playwright, synchron)
==================================================

QA-Gate vor jedem Push: alle Checks grün → exit 0, sonst → exit 1.

Aufruf (normalerweise über agenten/checks/run-gate.sh):
    python3 agenten/checks/release-gate.py
    # oder explizit:
    python3 agenten/checks/release-gate.py --repo-root <pfad> --port 8195

Repo-Auflösung: Das Skript liegt in <REPO_ROOT>/agenten/checks/ → REPO_ROOT
wird zwei Ebenen nach oben relativ zu __file__ aufgelöst (generisch).

Exit-Codes:
    0 = GATE GRÜN
    1 = GATE ROT (Fehlerliste auf stdout)
    2 = Umgebungsfehler (Port belegt/unerreichbar, site/ fehlt, kein HTML)

Checks:
    C1  Alle site/*.html: 0 pageerror, 0 Konsolenfehler, 0 tote interne
        Links (relatives .html-Ziel → HTTP 200 am lokalen Server); externe
        Links nur auf korrekte URL-Syntax.
    C2  Kein horizontaler Overflow (scrollWidth - clientWidth === 0) bei
        390×844 UND 1280×800, auf jeder Seite.
    C3  index.html: Canvas #dust rendert (~800ms nach Load, getImageData →
        >0 nicht-schwarze Pixel).
    C4  index.html: 3 ODER 4 Szenen (.scene) — alle per data-go-Button und
        Pfeiltasten erreichbar, document.title wechselt pro Szene
        (enthält "Start"/"Vision"/"Projektstatus"/["Fragen"]).
    C5  index.html: Motion-Toggle #motion → aria-pressed wechselt
        true → false, 0 Fehler.
    C6  Rechtstext-Scan (impressum + datenschutz): "Platzhalter" (visible
        Marks), "keine Anlageberatung", datenschutz: "Netlify" +
        Devnet-Disclaimer (Testnetz / kein echtes Geld / keinen realen
        Wert / kein realer Wert).
    C7  Secret-Scan (git ls-files / git grep):
          (a) Base58-Key-ähnliche 64–88-Char-Strings in token/docs,
              site/, agenten/ (bekannte public Devnet-Adressen allowlisted)
           (b) "BEGIN [A-Z0-9 ]*PRIVATE KEY" in getrackten Dateien (agenten/ ausgenommen, dort steht die Scan-Spec im Text selbst)
           (c) "secretKey" außerhalb token/scripts/ (agenten/ ebenfalls ausgenommen)
          (d) token/wallets/ und token/result/ sind NICHT getrackt
    C8  OG-Image (nur wenn site/og-image.png existiert): >10KB,
        PNG-Signatur, 1200×630 (struct auf IHDR-Bytes 16..23).
    P   Performance-Snapshot (informationell, NIE blockierend): Load-Zeit
        und rAF-Framerate (~5s) bei 1280px.
"""

import argparse
import json
import os
import re
import socket
import struct
import subprocess
import sys
import urllib.request
from urllib.parse import urlparse, urljoin

from playwright.sync_api import sync_playwright

PORT_DEFAULT = 8195
VIEWPORTS = ((390, 844), (1280, 800))
REPO_ROOT_DEFAULT = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
)

# Bekannte, öffentlich dokumentierte Solana-Adressen (Devnet-Mint, Mint-Tx,
# Transfer-Txs), die in token/docs und site/ vorkommen. Öffentlich und
# KEINE Keys → erlaubt. Bei neuen Adressen hier ergänzen (CEO-Sicht!).
B58_ALLOWLIST = {
    "CyEcfZw2FogCrehQqkWxksKtsndNwrtKHQqDfPdHCLLf",  # Devnet-Mint (public, 44-Char-Adresse)
    "2XqsCnzDeDrE4cpMDcxqLANsuDsWBvhYxgbQ4tYBEcrsbXadB3mVZGMKxdSiDzJY3QM1nTJjXLB8wrWNnD1eoAyQ",  # ATA-Recipient (public)
    "3aNM3HavfKXGdBfVBvF2YAzfo35JRUQatE59c2S6MTrCUPkoCk9Lt7iVnicDeE9Yn6RVYYZjv1yeV2UkkwjeXrbh",  # Checked-Transfer-Test (public)
    "3xTz68ijmkYEB9iZo3AdG8kDRX2xqfftubaHAPNN6jTEXPmzDmTTHYehrw5YznymVueCTKf1SLfLfpg67vmsRExX",  # create-mint (public)
    "4bemaL978Uupk6PJ4wv3Q7VjzUgtNj7xYVy8NmrW8uuouSM7x2bJwAMAEoz7r4sAoofAbDuUQ4KmcnzdgnLW7mLp",  # mint-initial 100B SIN (public)
    "4kGskHXLRV48b5AGfFJL4bZzV5JUzvGLUpfK96CyYE3N2n2sCMVFdJJB9myNCMstEquPbDnn31sPPCBqT53xjzpb",  # Mint-Vollmacht entzogen (public)
    "4rUFwheZM9g8xgyCBqwP2SYWdE1B361fkCPqydTrGECPpkSU7qse2baFtVGc5d9MEnrHs2N1wXxPHXUozz1ik2XQ",  # Freeze-Vollmacht entzogen (public)
    "4rnmBpepdUCdmU4D5XyS794DbQms7xB13Rv24mJ8wAxT4Wghqr88khzzRnacPi94Yn46gUeJt3oUVm9k9Bqa4ntY",  # Faucet-Airdrop 0,5 Test-SOL (public)
    "5ssTrnJQNRM8ivmxyfansm68se8q28UEUFPvLWY19KB4JNj5atrFSN2us9JR2mzTmKaZJmYaMhACZNQCsfyauQKC",  # Transfer 1.000.000 SIN (public)
}

# Base58-ähnliche Runs von 64–88 Zeichen, nur durch Nicht-Base58-Zeichen
# begrenzt. (Schließt Base64-/Hex-Hashe in lock-Dateien aus, da 0/I/O/l
# oder 64+ Zeichen außerhalb des Alphabets die Runs aufbrechen.)
B58_RE = re.compile(
    r"(?<![0-9A-Za-z_])"
    r"([1-9A-HJ-NP-Za-km-z]{64,88})"
    r"(?![0-9A-Za-z_])"
)
# Scan-Bereiche für (a): nur getrackte Dateien unter diesen Prefixen.
B58_SCAN_PREFIXES = ("token/docs/", "site/", "agenten/")

DEVNET_DISCLAIMER_RE = re.compile(
    r"Testnetz|kein echtes Geld|keinen realen Wert|kein realer Wert", re.I
)


class Report:
    def __init__(self):
        self.results = []  # (ok, name, detail_lines)

    def add(self, ok, name, details=None):
        self.results.append((ok, name, details or []))

    def add_info(self, name, details=None):
        # Nicht blockierend (z. B. Performance-Snapshot).
        self.results.append((True, name, details or []))

    def summary(self):
        lines = []
        for ok, name, details in self.results:
            mark = "GRÜN" if ok else "ROT "
            lines.append(f"[{mark}] {name}")
            for d in details:
                lines.append(f"        - {d}")
        return "\n".join(lines)

    def all_ok(self):
        return all(ok for ok, _, _ in self.results)

    def failed(self):
        return [name for ok, name, _ in self.results if not ok]


# ---------------------------------------------------------------- Seitenchecks

def list_site_htmls(base_url, repo_root):
    site_dir = os.path.join(repo_root, "site")
    if not os.path.isdir(site_dir):
        print(f"FEHLER: {site_dir} existiert nicht (REPO_ROOT korrekt?)")
        sys.exit(2)
    htmls = sorted(f for f in os.listdir(site_dir) if f.endswith(".html"))
    if not htmls:
        print("FEHLER: keine site/*.html gefunden")
        sys.exit(2)
    return [f"{base_url}/{f}" for f in htmls], htmls


def attach_error_collectors(page):
    page_errors, console_errors = [], []

    def on_page_error(e):
        page_errors.append(e.message)

    def on_console(m):
        if m.type == "error":
            console_errors.append(m.text)

    page.on("pageerror", on_page_error)
    page.on("console", on_console)
    return page_errors, console_errors


def check_page_errors_and_links(context, urls, report):
    """C1: 0 pageerror, 0 Konsolenfehler, 0 tote interne Links."""
    for url in urls:
        page = context.new_page()
        page_errors, console_errors = attach_error_collectors(page)
        resp = page.goto(url, wait_until="load", timeout=20000)
        details = []
        name = os.path.basename(url)
        if resp is None or resp.status != 200:
            status = resp.status if resp else "kein Response"
            details.append(f"Fehler in {name}: HTTP-Status {status}")
        for e in page_errors[:10]:
            details.append(f"Fehler in {name}: pageerror: {e}")
        for e in console_errors[:10]:
            details.append(f"Fehler in {name}: Konsolenfehler: {e}")
        # Links: interne → HTTP 200 am lokalen Server, externe → Syntax nur
        hrefs = page.eval_on_selector_all(
            "a[href]", "els => els.map(e => e.getAttribute('href'))"
        )
        seen, link_issues = set(), []
        for href in hrefs:
            if not href or href in seen:
                continue
            seen.add(href)
            if href.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
                continue
            if href.startswith("//"):
                parsed = urlparse("https:" + href)
                if parsed.netloc:
                    continue  # extern, syntaktisch ok
                link_issues.append(f"Fehler in {name}: kaputter externer Link: {href}")
                continue
            if re.match(r"^[a-z][a-z0-9+.\-]*:", href, re.I):
                # Extern (http/https/…): nur URL-Syntax prüfen
                parsed = urlparse(href)
                if parsed.scheme in ("http", "https") and not parsed.netloc:
                    link_issues.append(f"Fehler in {name}: kaputter externer Link: {href}")
                continue
            # Interner relativer Link → 200 am lokalen Server
            target = urljoin(url, href)
            try:
                r = urllib.request.urlopen(target, timeout=15)
                code = r.getcode()
                r.close()
                if code != 200:
                    link_issues.append(
                        f"Fehler in {name}: toter interner Link <a href='{href}'> → HTTP {code}"
                    )
            except Exception as exc:
                code = getattr(exc, "code", None)
                link_issues.append(
                    f"Fehler in {name}: toter interner Link <a href='{href}'> → {code or exc}"
                )
        page.close()
        report.add(not details and not link_issues, f"{name}: 0 pageerror / 0 Konsolenfehler / 0 tote Links", details + link_issues)


def check_overflow(context, urls, report):
    """C2: scrollWidth - clientWidth === 0 bei 390×844 und 1280×800."""
    for url in urls:
        page = context.new_page()
        issues = []
        for w, h in VIEWPORTS:
            page.set_viewport_size({"width": w, "height": h})
            page.goto(url, wait_until="load")
            overflow = page.evaluate(
                "document.documentElement.scrollWidth - document.documentElement.clientWidth"
            )
            if overflow != 0:
                issues.append(
                    f"Fehler in {os.path.basename(url)}: horizontaler Overflow @ {w}px: scrollWidth-clientWidth = {overflow}"
                )
        page.close()
        report.add(not issues, f"{os.path.basename(url)}: kein Overflow (390×844 + 1280×800)", issues)


def check_canvas(context, index_url, report):
    """C3: Canvas #dust rendert (nach ~800ms >0 nicht-schwarze Pixel)."""
    page = context.new_page()
    page.set_viewport_size({"width": 1280, "height": 800})
    page.goto(index_url, wait_until="load")
    issues = []
    try:
        page.wait_for_function(
            """() => {
                  const c = document.getElementById('dust');
                  return c && c.width > 0 && c.height > 0;
                }""",
            timeout=10000,
        )
        page.wait_for_timeout(800)
        result = page.evaluate(
            """() => {
                  const c = document.getElementById('dust');
                  if (!c) return {error: 'Canvas #dust fehlt'};
                  const ctx = c.getContext('2d');
                  if (!ctx) return {error: '2D-Context nicht erreichbar'};
                  const w = c.width, h = c.height;
                  // Mitte (30%) des Canvases abfragen — Ränder sind meist leer.
                  const sw = Math.max(1, Math.floor(w * 0.3)), sh = Math.max(1, Math.floor(h * 0.3));
                  const sx = Math.floor((w - sw) / 2), sy = Math.floor((h - sh) / 2);
                  const d = ctx.getImageData(sx, sy, sw, sh).data;
                  let lit = 0;
                  for (let i = 0; i < d.length; i += 4) {
                      if (d[i] > 8 || d[i + 1] > 8 || d[i + 2] > 8) lit++;
                  }
                  return {width: w, height: h, litPixels: lit};
                }"""
        )
        if "error" in result:
            issues.append(f"Fehler in index.html: {result['error']}")
        elif result["litPixels"] <= 0:
            issues.append(
                f"Fehler in index.html: Canvas rendert nur Schwarz (litPixels=0, {result['width']}x{result['height']})"
            )
        report.add(not issues, "index.html: Canvas #dust rendert (>0 nicht-schwarze Pixel)",
                   issues + ([f"litPixels={result.get('litPixels')}, {result.get('width')}x{result.get('height')}"] if not issues else []))
    except Exception as exc:
        issues.append(f"Fehler in index.html: Canvas-Check fehlgeschlagen: {exc}")
        report.add(False, "index.html: Canvas #dust rendert (>0 nicht-schwarze Pixel)", issues)
    finally:
        page.close()


def check_scenes(context, index_url, report):
    """C4: 3 oder 4 Szenen — alle per data-go + Pfeiltasten erreichbar."""
    issues = []
    n = 0
    page = context.new_page()
    errors, _ = attach_error_collectors(page)
    page.set_viewport_size({"width": 1280, "height": 800})
    page.goto(index_url, wait_until="load")
    try:
        n = page.evaluate("() => document.querySelectorAll('.scene').length")
        if n not in (3, 4):
            issues.append(f"Fehler in index.html: erwartet 3 oder 4 .scene-Elemente, gefunden: {n}")
        else:
            # Tab-Titel pro Szene: enthält Start / Vision / Projektstatus / [Fragen]
            expected = {0: "Start", 1: "Vision", 2: "Projektstatus", 3: "Fragen"}

            def expect_title(i, via):
                # Version-agnostisch: Argument direkt in die Expression baked —
                # funktioniert mit alter (positional "arg") und neuer
                # (keyword "expected") Playwright-Signatur.
                kw = json.dumps(expected[i])
                page.wait_for_function(
                    f"() => document.title.includes({kw})", timeout=8000
                )

            # --- data-go-Buttons (Klick-Navigation) ---
            for i in range(n):
                try:
                    page.click(f"nav button[data-go='{i}']")
                    expect_title(i, f"Klick data-go={i}")
                except Exception:
                    issues.append(
                        f"Fehler in index.html: Szene {i} ('{expected[i]}') per Klick (data-go={i}) nicht erreicht"
                    )
            # --- Pfeiltasten ---
            try:
                page.click("nav button[data-go='0']")
                expect_title(0, "Reset")
                for i in range(1, n):
                    page.keyboard.press("ArrowRight")
                    expect_title(i, "ArrowRight")
                for i in range(n - 1, 0, -1):
                    page.keyboard.press("ArrowLeft")
                    expect_title(i - 1, "ArrowLeft")
            except Exception:
                issues.append("Fehler in index.html: Pfeiltasten-Navigation (→/←) nicht vollständig durchlaufen")
            # --- prev/next-Pfeile (Footer) ---
            try:
                page.click("nav button[data-go='0']")
                expect_title(0, "Reset")
                for i in range(1, n):
                    page.click("#next")
                    expect_title(i, "#next")
                for i in range(n - 1, 0, -1):
                    page.click("#prev")
                    expect_title(i - 1, "#prev")
            except Exception:
                issues.append("Fehler in index.html: prev/next-Pfeile führen nicht durch alle Szenen")
    except Exception as exc:
        issues.append(f"Fehler in index.html: Szenen-Check abgebrochen: {exc}")
    finally:
        if errors:
            issues.append(f"Fehler in index.html: {len(errors)} Konsolen-/Page-Fehler während Szenen-Test: {errors[:3]}")
        page.close()
    report.add(
        not issues,
        f"index.html: {n}-Szenen-Check: alle .scene-Szenen (3 oder 4) via data-go + Pfeiltasten erreichbar, Titel wechselt",
        issues,
    )


def check_motion_toggle(context, index_url, report):
    """C5: #motion → aria-pressed wechselt von true nach false, 0 Fehler."""
    issues = []
    page = context.new_page()
    page_errors, console_errors = attach_error_collectors(page)
    page.set_viewport_size({"width": 1280, "height": 800})
    page.goto(index_url, wait_until="load")
    try:
        before = page.get_attribute("#motion", "aria-pressed")
        if before != "true":
            issues.append(f"Fehler in index.html: #motion hat aria-pressed='{before}' statt 'true' im Ausgangszustand")
        page.click("#motion")
        after = page.get_attribute("#motion", "aria-pressed")
        if after != "false":
            issues.append(f"Fehler in index.html: #motion aria-pressed nach Klick '{after}', erwartet 'false'")
        if page_errors or console_errors:
            issues.append(f"Fehler in index.html: Motion-Toggle verursachte Fehler: {page_errors + console_errors}")
    except Exception as exc:
        issues.append(f"Fehler in index.html: Motion-Toggle-Check fehlgeschlagen: {exc}")
    finally:
        page.close()
    report.add(not issues, "index.html: Motion-Toggle #motion (aria-pressed true→false, 0 Fehler)", issues)


# ------------------------------------------------------------ Rechtstext-Scan

def fetch_text(base_url, page_name):
    req = urllib.request.urlopen(f"{base_url.rstrip('/')}/{page_name}", timeout=15)
    html = req.read().decode("utf-8", errors="replace")
    req.close()
    # innerText-Proxy: Text-Knoten rohen HTML (ohne style/script) extrahieren
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    return text


def check_legal(base_url, report):
    """C6: Platzhalter + keine Anlageberatung + Netlify + Devnet-Disclaimer."""
    impressum = fetch_text(base_url, "impressum.html")
    datenschutz = fetch_text(base_url, "datenschutz.html")
    index_text = fetch_text(base_url, "index.html")
    checks = [
        ("index.html: 'keine Anlageberatung' im Footer/Risikohinweis",
         re.search(r"keine Anlageberatung", index_text, re.I) is not None,
         "Fehler in index.html: 'keine Anlageberatung' fehlt (Footer/Risikohinweis)"),
        ("impressum.html: 'Platzhalter' sichtbar markiert",
         "Platzhalter" in impressum,
         "Fehler in impressum.html: Hinweis 'Platzhalter' fehlt (visible Marks)"),
        ("datenschutz.html: 'Platzhalter' sichtbar markiert",
         "Platzhalter" in datenschutz,
         "Fehler in datenschutz.html: Hinweis 'Platzhalter' fehlt (visible Marks)"),
        ("impressum.html: 'keine Anlageberatung'",
         re.search(r"keine Anlageberatung", impressum, re.I) is not None,
         "Fehler in impressum.html: 'keine Anlageberatung' fehlt"),
        ("datenschutz.html: 'keine Anlageberatung'",
         re.search(r"keine Anlageberatung", datenschutz, re.I) is not None,
         "Fehler in datenschutz.html: 'keine Anlageberatung' fehlt"),
        ("datenschutz.html: 'Netlify' genannt",
         "Netlify" in datenschutz,
         "Fehler in datenschutz.html: 'Netlify' fehlt"),
        ("datenschutz.html: Devnet-Disclaimer (Testnetz / kein echtes Geld / keinen realen Wert / kein realer Wert)",
         DEVNET_DISCLAIMER_RE.search(datenschutz) is not None,
         "Fehler in datenschutz.html: Devnet-Disclaimer fehlt (keine von: Testnetz, kein echtes Geld, keinen realen Wert, kein realer Wert)"),
    ]
    for name, ok, fail_msg in checks:
        report.add(ok, name, [] if ok else [fail_msg])


# ---------------------------------------------------------------- Secret-Scan

def check_secrets(report, repo_root):
    """C7: Secret-Scan über git ls-files / git grep."""

    def run(*cmd):
        return subprocess.run(list(cmd), capture_output=True, text=True)

    # (d) token/wallets/ und token/result/ dürfen NICHT getrackt sein
    ls = run("git", "-C", repo_root, "ls-files")
    if ls.returncode != 0:
        report.add(False, "Secret-Scan: git ls-files nicht verfügbar", [ls.stderr.strip()])
        return
    tracked = [l for l in ls.stdout.splitlines() if l.strip()]
    forbidden = [f for f in tracked if f.startswith(("token/wallets/", "token/result/"))]
    report.add(
        not forbidden,
        "Secret-Scan: token/wallets/ und token/result/ sind NICHT getrackt",
        [f"verletzt — getrackt: {f}" for f in forbidden],
    )

    # (b) "BEGIN PRIVATE KEY" in beliebiger getrackter Datei (git grep = nur getrackt)
    out = run(
        "git", "-C", repo_root, "grep", "-n", "-E",
        r"BEGIN [A-Z0-9 ]*PRIVATE KEY", "--", ":(exclude)agenten",
    )
    hits = [l for l in out.stdout.splitlines() if l.strip()] if out.returncode == 0 else []
    report.add(
        not hits,
        "Secret-Scan: kein 'BEGIN ... PRIVATE KEY' in getrackten Dateien (außer agenten/)",
        [f"gefunden: {h}" for h in hits[:20]],
    )

    # (c) "secretKey" nur in token/scripts — Treffer außerhalb = rot
    out = run(
        "git", "-C", repo_root, "grep", "-n", "-F", "secretKey",
        "--", ":(exclude)token/scripts", ":(exclude)agenten",
    )
    hits = [l for l in out.stdout.splitlines() if l.strip()] if out.returncode == 0 else []
    report.add(
        not hits,
        "Secret-Scan: 'secretKey' kommt nur in token/scripts vor",
        [f"Fehler in {h.split(':', 1)[0]}: 'secretKey' außerhalb token/scripts: {h}" for h in hits[:20]],
    )

    # (a) Base58-Key-ähnliche Strings (64–88) in token/docs, site/, agenten/
    issues = []
    scanned = 0
    for rel in tracked:
        if not rel.startswith(B58_SCAN_PREFIXES):
            continue
        if rel.endswith((".png", ".jpg", ".jpeg", ".gif", ".webp", ".lock")):
            continue
        scanned += 1
        path = os.path.join(repo_root, rel)
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                content = fh.read()
        except OSError:
            continue
        for m in B58_RE.finditer(content):
            token = m.group(1)
            if token in B58_ALLOWLIST:
                continue
            line_no = content.count("\n", 0, m.start()) + 1
            issues.append(
                f"Fehler in {rel}:{line_no}: Base58-ähnlicher {len(token)}-Char-String "
                f"(möglicher Key): {token[:24]}…"
            )
    report.add(
        not issues,
        f"Secret-Scan: keine Key-ähnlichen Base58-Strings (64–88) in token/docs, site/, agenten/ ({scanned} Dateien, {len(B58_ALLOWLIST)} allowlisted)",
        issues[:50],
    )


# ---------------------------------------------------------------- OG-Image

def check_og_image(report, repo_root):
    """C8: Nur wenn site/og-image.png existiert (analog: alle .png in site/)."""
    og_files = sorted(
        f for f in (os.listdir(os.path.join(repo_root, "site"))
                    if os.path.isdir(os.path.join(repo_root, "site")) else [])
        if f == "og-image.png" or f.startswith("og-")
    )
    if not og_files:
        report.add_info(
            "OG-Image: site/og-image.png existiert nicht → Check übersprungen (Design-Branch liefert)",
            ["- Datei fehlt, kein Fehler im aktuellen Stand"],
        )
        return
    for fname in og_files:
        path = os.path.join(repo_root, "site", fname)
        issues = []
        size = os.path.getsize(path)
        if size <= 10 * 1024:
            issues.append(f"Fehler in site/{fname}: nur {size} Bytes (erwartet >10KB)")
        with open(path, "rb") as fh:
            head = fh.read(24)
        png_sig = b"\x89PNG\r\n\x1a\n"
        if len(head) < 24 or not head.startswith(png_sig):
            issues.append(f"Fehler in site/{fname}: keine gültige PNG-Signatur")
        else:
            w, h = struct.unpack(">II", head[16:24])
            if (w, h) != (1200, 630):
                issues.append(f"Fehler in site/{fname}: Abmessungen {w}×{h}, erwartet 1200×630")
        ok = not issues
        report.add(
            ok,
            f"site/{fname}: OG-Image (>10KB, PNG, 1200×630)" + ("" if ok else ""),
            issues,
        )


# --------------------------------------------------------- Performance-Snapshot

def check_perf(context, index_url, report):
    """P: Informationell — Load-Zeit + rAF-Framerate (~5s). NIE blockierend."""
    page = context.new_page()
    page.set_viewport_size({"width": 1280, "height": 800})
    page.goto(index_url, wait_until="load")
    notes = []
    try:
        perf = page.evaluate(
            """() => {
                  const nav = performance.getEntriesByType('navigation')[0];
                  return nav ? {
                      loadMs: Math.round(nav.loadEventEnd),
                      domMs: Math.round(nav.domComplete ? domMsSafe() : 0),
                  } : {};
                  function domMsSafe() { return performance.getEntriesByType('navigation')[0].domComplete; }
            }"""
        )
        # LCP-Approximation (buffered) — falls verfügbar
        try:
            lcp = page.evaluate(
                """() => {
                      return new Promise((resolve) => {
                          let v = null;
                          try {
                              const obs = new PerformanceObserver((list) => {
                                  for (const e of list.getEntries()) v = e.startTime;
                              });
                              obs.observe({type: 'largest-contentful-paint', buffered: true});
                          } catch (e) {}
                          setTimeout(() => resolve(v === null ? null : Math.round(v)), 2000);
                      });
            }"""
            )
            if lcp is not None:
                notes.append(f"LCP-Approximation: {lcp}ms")
        except Exception:
            pass
        load_ms = perf.get("loadMs")
        if load_ms:
            notes.append(f"Time-to-Load (NavigationStart→Load): {load_ms}ms")
            if load_ms > 5000:
                notes.append(f"WARNUNG (nicht blockierend): Load {load_ms}ms über Ziel <5000ms")
        fps = page.evaluate(
            """() => {
                  return new Promise((resolve) => {
                      let frames = 0;
                      const t0 = performance.now();
                      const tick = () => {
                          const elapsed = performance.now() - t0;
                          if (elapsed < 5000) {
                              frames++;
                              requestAnimationFrame(tick);
                          } else {
                              const secs = elapsed / 1000;
                              resolve({
                                  frames,
                                  seconds: Math.round(secs * 100) / 100,
                                  fps: Math.round((frames / secs) * 10) / 10,
                              });
                          }
                      };
                      requestAnimationFrame(tick);
                  });
            }"""
        )
        if fps:
            notes.append(f"Framerate: {fps['fps']}fps ({fps['frames']} Frames in {fps['seconds']}s)")
            if fps["fps"] < 50:
                notes.append("bekannt, nicht blockierend: SwiftShader (CPU-GL) unter 50fps — GPU-Build messen")
    except Exception as exc:
        notes.append(f"Performance-Snapshot unvollständig: {exc}")
    page.close()
    report.add_info("Performance-Snapshot (informationell, nicht blockierend): index.html @1280px", notes)


# ------------------------------------------------------------------- main

def server_reachable(base_url, port):
    try:
        s = socket.create_connection(("127.0.0.1", port), timeout=3)
        s.close()
        return True
    except OSError:
        return False


def main():
    ap = argparse.ArgumentParser(description="SuperIntelNex Release-Gate (QA)")
    ap.add_argument("--repo-root", default=REPO_ROOT_DEFAULT,
                    help="Repo-Root mit site/ und .git (Default: zwei Ebenen über dem Skript)")
    ap.add_argument("--port", type=int, default=PORT_DEFAULT,
                    help="Port des lokalen http.server (Default 8195, QA-exklusiv)")
    args = ap.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    base_url = f"http://localhost:{args.port}"

    if not os.path.isdir(os.path.join(repo_root, "site")):
        print(f"FEHLER: {repo_root} enthält kein site/ — REPO_ROOT-Fehler (exit 2)")
        sys.exit(2)
    if not server_reachable(base_url, args.port):
        print(
            f"FEHLER: Port {args.port} nicht erreichbar (port belegt / Server läuft nicht) — "
            f"starte `python3 -m http.server {args.port} --directory site` oder nutze run-gate.sh (exit 2)"
        )
        sys.exit(2)

    report = Report()
    urls, _ = list_site_htmls(base_url, repo_root)
    index_url = f"{base_url}/index.html"

    def find_chromium():
        import glob as _glob
        pat = os.path.expanduser(
            "~/Library/Caches/ms-playwright/chromium-*/chrome-mac-arm64/"
            "Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"
        )
        found = sorted(_glob.glob(pat))
        return found[0] if found else None

    with sync_playwright() as p:
        launch_kwargs = dict(
            headless=True,
            args=[
                "--use-gl=angle",
                "--use-angle=swiftshader",
                "--enable-unsafe-swiftshader",
            ],
        )
        exec_path = find_chromium()
        if exec_path:
            launch_kwargs["executable_path"] = exec_path
        browser = p.chromium.launch(**launch_kwargs)
        context = browser.new_context(viewport={"width": 1280, "height": 800})

        check_page_errors_and_links(context, urls, report)
        check_overflow(context, urls, report)
        check_canvas(context, index_url, report)
        check_scenes(context, index_url, report)
        check_motion_toggle(context, index_url, report)
        check_perf(context, index_url, report)
        browser.close()

    check_legal(base_url, report)
    check_secrets(report, repo_root)
    check_og_image(report, repo_root)

    print(report.summary())
    failed = report.failed()
    if failed:
        print(f"\nGATE ROT — {len(failed)} Check(s) fehlgeschlagen:")
        for name, _, details in report.results:
            if name in failed:
                print(f"  ✗ {name}")
                for d in details:
                    print(f"      {d}")
        sys.exit(1)
    print("\nGATE GRÜN — alle Checks bestanden.")
    sys.exit(0)


if __name__ == "__main__":
    main()
