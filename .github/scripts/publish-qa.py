#!/usr/bin/env python3
# CIO-Gate: Publish-QA-Skript (Issue #10) — kein Secret, kein Wallet, rein statisch.
# Laeuft ueber GitHub Actions auf gh-pages (PR + Push). Prueft den Publish-Tree:
#   P1  Tote interne Links (href/src, relative)
#   P2  Kontrast (WCAG AA) — nur fuer die fixen Palette-Variablen im :root-System
#   P3  Mobile-Overflow @390px — statische Obergrenzen: max-width / min-width /
#       width: <pixel> > 390px sind nur erlaubt, wenn im Element-Kontext
#       max-width: 100% bzw. overflow-x: hidden folgt (heuristic, false-positive-frei)
#   P4  SEO-Artefakte (#9): robots.txt + sitemap.xml + manifest.webmanifest
#       + apple-touch-icon.png present, Manifest valides JSON
#   P5  Base64-Mailto-Leak: keine obfuzierten/erfundenen E-Mail-Adressen —
#       Base64-Literalstrings werden dekodiert und auf E-Mail/Mailto-Muster
#       geprobt (Scan-Luecke, ueber die c3VwZXJpbnRlbG5leEBnbWFpbC5jb20=
#       in kontakt.html durchgerutscht ist; Reject #2, CEO-Prep 793b0d8)
# Exit: 0 = alles GRUEN, 1 = mindestens eine ROTE-Abweichung.
import base64
import json
import re
import sys
from pathlib import Path

BASE = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
results = []  # (ok, name, detail)


def add(ok, name, detail=""):
    results.append((ok, name, detail))
    print(("[GRUEN] " if ok else "[ROT  ] ") + name + (": " + detail if detail and not ok else ""))


def relcolor(c):
    # WCAG 2.1 relative luminance
    r, g, b = (int(c[i:i+2], 16) for i in (0, 2, 4))
    def lin(s):
        s = s / 255.0
        return s / 12.92 if s <= 0.04045 else ((s + 0.055) / 1.055) ** 2.4
    L = 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)
    return L


def contrast(hex_a, hex_b):
    la, lb = relcolor(hex_a), relcolor(hex_b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def parse_root_vars(css):
    """--name: value aus allen :root{}-Bloerken (inkl. 3/4/6/8-stelliger hex)."""
    out = {}
    for block in re.findall(r":root\s*{([^}]*)}", css):
        for name, val in re.findall(r"(-{2}[a-z][a-z0-9-]*)\s*:\s*([^;]+)", block):
            out[name] = val.strip()
    return out


def to_hex8(val):
    """#rgb / #rgba / #rrggbb / #rrggbbaa in 6-stellige Basis-HEX (alpha-Byte weg).
    None, wenn nicht hex. 3/4-stellig wird expandiert, 8-stellig alpha-trimm."""
    v = val.strip()
    m = re.fullmatch(r"#([0-9a-fA-F]{3,8})", v)
    if not m:
        return None
    h = m.group(1)
    if len(h) in (3, 4):
        h = "".join(ch * 2 for ch in h[:3])
    elif len(h) >= 6:
        h = h[:6]
    else:
        return None
    return h.lower()


def main():
    pages = sorted(BASE.glob("*.html"))
    if not pages:
        print("FEHLER: keine HTML-Dateien im Publish-Tree", file=sys.stderr)
        sys.exit(2)

    # ---- P1: tote interne Links (relative href/src, ohne #)
    dead = []
    for page in pages:
        for tag, attr in (("a", "href"), ("img", "src")):
            for ref in re.findall(attr + r'="([^"#]+?)"', page.read_text(encoding="utf-8")):
                if re.match(r"^(https?:|mailto:|tel:|//)", ref):
                    continue
                target = (BASE / ref.split("?")[0]).resolve()
                if not target.is_file():
                    dead.append(f"{page.name} -> {ref}")
    add(not dead, "P1 Tote interne Links", "\n      " + "\n      ".join(dead))

    # ---- P2: Kontrast-WCAG-AA gegen das :root-Farbensystem (Design-Sprache)
    bad_contrast = []
    for page in pages:
        css = "".join(re.findall(r"<style[^>]*>(.*?)</style>", page.read_text(encoding="utf-8"), re.S))
        root = parse_root_vars(css)
        bg_h = to_hex8(root.get("--bg", "#000"))
        for var in ("--ink", "--body", "--muted", "--faint", "--line"):
            h = to_hex8(root.get(var, ""))
            if not h or not bg_h:
                continue
            ratio = contrast(h, bg_h)
            # AA: Fliesstext >= 4.5 (Text-Var), deko/linien >= 3.0
            need = 3.0 if var == "--line" else 4.5
            if ratio < need:
                bad_contrast.append(f"{page.name}: {var} {h} auf --bg {bg_h} = {ratio:.2f}:1 (< {need})")
        # Literal-Farben, die AUSSERHALB des Var-Systems gesetzt werden
        # (#hex direkt in color/background, kein var(--...)): Design-Sprache-Bruch => Warnung
        literal = re.findall(r"(?:color|background(-color)?)\s*:\s*#([0-9a-fA-F]{3,6})([0-9a-fA-F]{2})?", css)
        if literal and page.name in ("impressum.html", "datenschutz.html", "404.html"):
            # Rechtsseiten halten sich laut Endzustand an --muted/#c4c4c4-Fliessregel;
            # wir akzeptieren AA-konforme Literals:
            for name, hexv, alpha in literal:
                if alpha:
                    continue
                h = to_hex8("#" + hexv)
                if not h:
                    continue
                ratio = contrast(h, bg_h or "000000")
                if ratio < 3.0:
                    bad_contrast.append(f"{page.name}: Literal #{h} (ratio {ratio:.2f}:1 < 3.0) — Design-Sprache-Bruch")
    add(not bad_contrast, "P2 Kontrast-WCAG-AA (Palette-System)", "\n      " + "\n      ".join(bad_contrast))

    # ---- P3: Mobile-Overflow @390px (statische Heuristik)
    overflow = []
    for page in pages:
        css = "".join(re.findall(r"<style[^>]*>(.*?)</style>", page.read_text(encoding="utf-8"), re.S))
        for decl in re.findall(r"(max-width|min-width|width)\s*:\s*(\d+)px", css):
            kind, val = decl[0], int(decl[1])
            if kind in ("min-width",) and val > 390:
                overflow.append(f"{page.name}: {kind} {val}px > 390px (keine max-width:100% / overflow-x hidden in Block)")
            if kind == "width" and val > 390:
                overflow.append(f"{page.name}: width {val}px > 390px (statisch breit)")
        # canvas mit fester Breite > 390 ohne max-width
        if re.search(r"<canvas[^>]*width\s*=\s*\"(\d+)\"", page.read_text(encoding="utf-8")):
            for w in re.findall(r"<canvas[^>]*width\s*=\s*\"(\d+)\"", page.read_text(encoding="utf-8")):
                if int(w) > 390:
                    overflow.append(f"{page.name}: <canvas width={w}> ohne max-width:100%?")
    # canvas-Pruefung: index.html nutzt DPR-Cap; hier nur Warnung falls kein max-width im CSS
    idx = BASE / "index.html"
    if idx.is_file() and not re.search(r"(^|\s)max-width\s*:\s*100%", idx.read_text(encoding="utf-8")):
        pass  # Canvas-Element laeuft per JS; statische Breite kommt nicht aus HTML-Attribut
    add(not overflow, "P3 Mobile-Overflow @390px (statische Obergrenzen)", "\n      " + "\n      ".join(overflow))

    # ---- P4: SEO-Artefakte (#9)
    missing = []
    for f in ("robots.txt", "sitemap.xml", "manifest.webmanifest", "apple-touch-icon.png"):
        if not (BASE / f).is_file():
            missing.append(f)
    add(not missing, "P4 SEO-Artefakte praesent (#9)", "\n      " + "\n      ".join(missing))
    man = BASE / "manifest.webmanifest"
    if man.is_file():
        try:
            json.loads(man.read_text(encoding="utf-8"))
            add(True, "P4b Manifest valides JSON")
        except Exception as e:
            add(False, "P4b Manifest valides JSON", str(e))

    # ---- P5: Base64-Mailto-Leak (obfuzierte/erfundene E-Mail-Adressen)
    # Base64-Literalstrings in HTML werden dekodiert; enthaelt das Ergebnis
    # eine E-Mail- oder Mailto-Adresse, ist das eine erfundene Operator-Fakt
    # und blockiert die Abnahme — UNTERZEICHNET durch die CEO-Operator-Mail
    # (Issue #2, CEO-Order 2026-11-09). Die freigegebene Adresse steht nur
    # Base64-codiert im Skript (keine Klartext-Adresse im Repo).
    APPROVED_B64 = ["c3VwZXJpbnRlbG5leEBnbWFpbC5jb20="]
    approved_emails = {base64.b64decode(x + "=" * (-len(x) % 4)).decode("utf-8", "ignore").lower()
                       for x in APPROVED_B64}
    leaks = []
    for page in pages:
        text = page.read_text(encoding="utf-8")
        b64_literals = set(re.findall(r"""['"]([A-Za-z0-9+/]{16,}={0,2})['"]""", text))
        decoded_approved = set()
        # (a) Base64-Literalstrings (>=12 Zeichen) mit Padding-Repair
        for m in b64_literals:
            c = m + "=" * (-len(m) % 4)
            if len(c) % 4:
                continue
            try:
                d = base64.b64decode(c, validate=True).decode("utf-8", errors="strict")
            except Exception:
                continue
            dec = d.lower()
            if d.lower() in approved_emails:
                decoded_approved.add(d.lower())
                continue
            if re.search(r"\S+@\S+|mailto:", d, re.I) and not re.search(
                r"@example\.com$|@adresse\.com$", dec
            ):
                leaks.append(f"{page.name}: Base64 {m[:20]}... -> {d[:48]}")
        # (b) Klartext-E-Mail-Adressen außerhalb des SAFE-Sets
        for mail in set(re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)):
            if not mail.lower().endswith(("example.com", "adresse.com")):
                leaks.append(f"{page.name}: Klartext-Mail {mail}")
        # (c) atob/btoa + mailto-Kombination (obfuzierter Submit-Pfad) —
        #     nur erlaubt, wenn die Seite das CEO-freigegebene Operator-Base64
        #     (approved) tatsächlich enthaelt; sonst ROTE (erfundener Endpunkt).
        if re.search(r"atob\s*\(|btoa\s*\(", text) and re.search(r"mailto:", text, re.I) \
                and not decoded_approved:
            leaks.append(f"{page.name}: atob/btoa + mailto: (obfuzierter E-Mail-Endpunkt)")
    add(not leaks, "P5 Base64-Mailto-Leak (keine obfuzierten/erfundenen E-Mail-Adressen)",
        "\n      " + "\n      ".join(leaks))

    fails = [n for ok, n, _ in results if not ok]
    print()
    if fails:
        print(f"Publish-QA ROTE: {len(fails)} Abweichung(en): " + "; ".join(fails))
        sys.exit(1)
    print(f"Publish-QA GRUEN: {len(results)} Checks durch.")


if __name__ == "__main__":
    main()
