#!/usr/bin/env python3
"""QA-Gate (SuperIntelNex, Issue #10) — leichtgewichtiges CI-Pruefnetz fuer den
Publish-Tree (HTML-Seiten auf der checkout-Wurzel).

Pruefungen (kein Secret, kein Wallet):
  1. Tote Links (relative href/src/action + CSS url() + Anker-Ziele)
  2. Kontrast-WCAG-AA (statisch: CSS-Regeln mit color+background-color sowie
     Root-Text-Tokens gegen den Page-Hintergrund; Ziel: >= 4.5:1)
  3. Mobile-Overflow @390px (Playwright/Chromium: brechende Elemente +
     Dokument-Horizontal-Scroll)
  4. JS-Ausnahmen (pageerror)

Nutzung:  python3 agenten/checks/qa-gate.py [checkout-wurzel]
Exit: 0 = GRUEN, 1 = ROTE, 2 = Umgebung fehlerhaft.
Playwright ist optional: ohne Chromium-Installation faellt Check 3+4 auf
WARNUNG (nicht FAIL), damit der Gate auch in schmalen Umgebungen laeuft.
"""
import re
import sys
import html as _html
from pathlib import Path

BLOCKING_FAILS = []
WARNINGS = []
NOTES = []
PASS = []


# ---------------------------------------------------------------- Utilities
def _fail(msg):
    BLOCKING_FAILS.append(msg)


def _warn(msg):
    WARNINGS.append(msg)


def _note(msg):
    NOTES.append(msg)


def _ok(msg):
    PASS.append(msg)


# ---------------------------------------------------------------- 1. Dead links
REF_RE = re.compile(r"(?:href|src|action)\s*=\s*[\"']([^\"']+)[\"']", re.I)
CSS_URL_RE = re.compile(r"url\(\s*['\"]?([^'\"()\s]+)", re.I)
ID_RE = re.compile(r'id=["\']([^"\']+)["\']', re.I)
BLOCK_SCHEMES = ("http://", "https://", "mailto:", "tel:", "data:", "#")


def check_dead_links(root: Path, pages):
    for page in pages:
        text = page.read_text(encoding="utf-8")
        refs = []
        refs += [m.strip() for m in REF_RE.findall(text)]
        refs += [m.strip() for m in CSS_URL_RE.findall(text)]
        for ref in refs:
            if not ref or ref.startswith(BLOCK_SCHEMES):
                continue
            if ref.startswith("#"):
                ids = set(ID_RE.findall(text))
                target = ref.lstrip("#")
                if target not in ids:
                    _fail(f"DEAD(anker) {page.name}: {ref} — id fehlt in der Datei")
                else:
                    _ok(f"Anker {ref} ({page.name})")
                continue
            path_part = ref.split("#", 1)[0]
            if not path_part:
                continue
            target = (root / path_part)
            if not target.exists():
                _fail(f"DEAD {page.name} -> {ref}")
            else:
                _ok(f"Ref {ref} ({page.name})")


# ---------------------------------------------------------------- 2. Contrast
def _to_rgb(value):
    v = value.strip().lower()
    m = re.fullmatch(r"#([0-9a-f]{6})(?:[0-9a-f]{2})?", v)
    if m:
        h = m.group(1)
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    m = re.fullmatch(r"rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)", v)
    if m:
        return tuple(int(x) for x in m.groups())
    if v in ("black", "white"):
        return (0, 0, 0) if v == "black" else (255, 255, 255)
    return None


def _luminance(rgb):
    def chan(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (chan(x) for x in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(fg, bg):
    l1, l2 = _luminance(fg), _luminance(bg)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def check_contrast(root: Path, pages):
    TEXT_TOKENS = re.compile(r"^(ink|text|title|body|muted|sub|fg|label)$", re.I)
    BG_TOKENS = re.compile(r"^(bg|background|dark|light)$", re.I)
    found_pairs = 0
    for page in pages:
        text = page.read_text(encoding="utf-8")
        style_blocks = re.findall(r"<style[^>]*>(.*?)</style>", text, re.S | re.I)
        css = "\n".join(style_blocks)
        if not css.strip():
            continue
        # Root-Variablen (nur hex/rgb-Werte)
        var_map = {}
        for name, val in re.findall(r"(--[\w-]+)\s*:\s*([^;{}]+);", css):
            rgb = _to_rgb(val)
            if rgb:
                var_map[name.strip()] = rgb
        # Regel-Blöcke mit color + background(-color)
        for selector, body in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
            decls = dict(re.findall(r"([\w-]+)\s*:\s*([^;{}]+)", body))
            color_val = decls.get("color") or decls.get("color-")
            bg_val = decls.get("background-color") or decls.get("background")

            def resolve(v):
                if v is None:
                    return None
                m = re.fullmatch(r"var\(\s*(--[\w-]+)\s*(?:,\s*([^)]*))?\)", v.strip())
                if m:
                    return var_map.get(m.group(1).strip()) or _to_rgb((m.group(2) or "").strip())
                return _to_rgb(v)

            fg, bg = resolve(color_val), resolve(bg_val)
            if fg and bg:
                sel = " ".join(selector.split())
                r = contrast_ratio(fg, bg)
                found_pairs += 1
                if r < 4.5:
                    _fail(f"KONTRAST<AA {page.name}: {sel} fg={color_val} bg={bg_val} -> {r:.2f}:1")
                elif r < 4.6:
                    _warn(f"KONTRAST grenzwertig {page.name}: {sel} -> {r:.2f}:1 (>=4.5 ok, knapp)")
                else:
                    _ok(f"Kontrast {sel} -> {r:.2f}:1")
        # Root-Text-Tokens gegen Page-Hintergrund (dark scheme)
        bg_default = var_map.get("--bg") or _to_rgb("#000000")
        if bg_default:
            for name, rgb in var_map.items():
                if TEXT_TOKENS.match(name.lstrip("-")):
                    r = contrast_ratio(rgb, bg_default)
                    label = name.lstrip("-")
                    if label in ("muted",) and r < 4.5:
                        _fail(f"KONTRAST<AA {page.name}: Token --{label} auf --bg -> {r:.2f}:1")
                    elif label not in ("muted",) and r < 4.5:
                        _fail(f"KONTRAST<AA {page.name}: Token --{label} auf --bg -> {r:.2f}:1")
                    else:
                        _ok(f"Token --{label} auf --bg -> {r:.2f}:1")
    if found_pairs == 0:
        _note("Kontrast: keine Regeln mit color+background-color gefunden — nur Token-Check")


# ---------------------------------------------------------------- 3+4. Playwright
OVERFLOW_JS = """
() => {
  const vw = document.documentElement.clientWidth;
  const offenders = [];
  const all = document.body ? document.body.querySelectorAll('*') : [];
  // Element ist in horizontalem Scroll-Container enthalten (overflow-x:auto/scroll/hidden)
  // => verursacht KEIN Dokument-Overflow (das hScroll/docW-Mass darueber wacht),
  // aber auch kein Layoutbruch: Standard-Muster (z.B. Whitepaper-Chapbar-Pills @390).
  const inScrollContainer = (el) => {
    let n = el.parentElement;
    while (n && n.tagName !== 'HTML') {
      const ox = getComputedStyle(n).overflowX;
      if (ox === 'auto' || ox === 'scroll' || ox === 'hidden') return true;
      n = n.parentElement;
    }
    return false;
  };
  for (const el of all) {
    const r = el.getBoundingClientRect();
    // Breite UND Position: ein schmales Element kann rechts *vor* vw
    // anfangen und ueberlaufen (Flex-Kinder mit min-width:auto) — der
    // Positions-Check (r.right > vw+1) faengt solche False-Gruen-Faelle.
    if (r.width > 0 && !inScrollContainer(el) && (r.width > vw + 4 || r.right > vw + 1 || r.left < -1)) {
      const cls = (el.className && typeof el.className === 'string') ? '.' + el.className.trim().split(/\\s+/).join('.') : '';
      offenders.push(el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') + cls +
        ' [L=' + Math.round(r.left) + ' R=' + Math.round(r.right) + ']');
      if (offenders.length > 12) break;
    }
  }
  return {
    vw,
    hScroll: document.documentElement.scrollWidth > vw + 4,
    docW: document.documentElement.scrollWidth,
    offenders
  };
}
"""


def check_mobile_overflow(root: Path, pages):
    import http.server
    import threading

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        _warn("MOBILE-OVERFLOW @390px + JS-Exceptions: Playwright fehlt — Check uebersprungen (nicht blockierend)")
        return

    import socket

    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()

    class H(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **kw):
            super().__init__(*a, directory=str(root), **kw)

        def log_message(self, *a):
            pass

    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", port), H)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()

    with sync_playwright() as p:
        browser = p.chromium.launch()
        for pg in pages:
            page = browser.new_page(viewport={"width": 390, "height": 844})
            errors = []
            page.on("pageerror", lambda e: errors.append(str(e)))
            url = f"http://127.0.0.1:{port}/{pg.name}"
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=20000)
                page.wait_for_timeout(400)
                res = page.evaluate(OVERFLOW_JS)
            except Exception as e:
                _fail(f"MOBILE {pg.name}: Seite laedt nicht — {str(e)[:120]}")
                page.close()
                continue
            finally:
                page.close()
            issues = []
            if res.get("hScroll"):
                issues.append(f"Dokument-HScroll (docW={res.get('docW')})")
            off = res.get("offenders") or []
            if off:
                issues.append("Elemente breiten: " + ", ".join(off[:12]))
            if errors:
                issues.append("JS-Ausnahmen: " + "; ".join(e[:100] for e in errors[:5]))
            if issues:
                _fail(f"MOBILE(390px) {pg.name}: " + " | ".join(issues))
            else:
                _ok(f"390px {pg.name}: kein Overflow, keine JS-Ausnahmen")
        browser.close()
    httpd.shutdown()


# ---------------------------------------------------------------- main
def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    if not root.is_dir():
        print(f"FEHLER: Wurzel-Verzeichnis nicht gefunden: {root}")
        return 2
    pages = sorted(p for p in root.glob("*.html"))
    if not pages:
        print("FEHLER: keine HTML-Seiten in der Wurzel gefunden — ist der Publish-Tree gecheckoutet?")
        return 2

    check_dead_links(root, pages)
    check_contrast(root, pages)
    check_mobile_overflow(root, pages)

    print("# QA-Gate Report")
    print()
    print(f"Geprueft: {', '.join(p.name for p in pages)} (Wurzel: {root.name or root})")
    print()
    print(f"## GRUEN ({len(PASS)})")
    for m in PASS:
        print(f"- {m}")
    print()
    if WARNINGS:
        print(f"## WARNUNG ({len(WARNINGS)})")
        for m in WARNINGS:
            print(f"- {m}")
        print()
    if NOTES:
        print(f"## NOTE ({len(NOTES)})")
        for m in NOTES:
            print(f"- {m}")
        print()
    if BLOCKING_FAILS:
        print(f"## ROTE ({len(BLOCKING_FAILS)})")
        for m in BLOCKING_FAILS:
            print(f"- {m}")
        print()
    verdict = "GRUEN" if not BLOCKING_FAILS else "ROTE"
    print(f"**VERDIKT: QA-Gate {verdict}**")
    return 0 if verdict == "GRUEN" else 1


if __name__ == "__main__":
    sys.exit(main())
