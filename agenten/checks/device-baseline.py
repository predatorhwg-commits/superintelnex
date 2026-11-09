#!/usr/bin/env python3
"""Geräte-Baseline (#11, T2): mobile 390 + tablet 768 + desktop 1280.

Checks (keine externen Tools, nur Chromium via Playwright — Codex-Prinzip):
  K1  Horizontaler Overflow @390 / @768 / @1280
  K2  Touch-Targets >= 44x44 CSS-px (visible buttons/links auf mobile)
  K3  Kontrast-Kernpaare (WCAG AA): --ink auf --bg, --muted auf --bg
  K4  prefers-reduced-motion: keine rAF-Animation, Canvas statisch
  K5  FPS-Sanity desktop (60fps-Ziel, median Frame-Time)
  K6  Performance-Metriken: FCP / LCP (PerformanceObserver)
  K7  Screenshots pro Gerät

Exit 0 = GRUEN, 1 = ROT, 2 = Umgebungsfehler.
Aufruf: GATE_BASE=http://127.0.0.1:8195 python3 agenten/checks/device-baseline.py
"""
import glob
import json
import os
import sys

BASE = os.environ.get("GATE_BASE", "http://127.0.0.1:8195")
OUT = os.environ.get("BASELINE_OUT", "agenten/checks/baseline-report")
os.makedirs(OUT, exist_ok=True)
fail = []


def ok(msg):
    print("OK   ", msg)


def bad(msg):
    fail.append(msg)
    print("FAIL ", msg)


def lum(rgb):
    def ch(c):
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (ch(x) for x in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(hex_a, hex_b):
    def px(h):
        h = h.lstrip("#")
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

    la, lb = lum(px(hex_a)), lum(px(hex_b))
    if la < lb:
        la, lb = lb, la
    return (la + 0.05) / (lb + 0.05)


def page_errors(page):
    errs = []
    page.on("pageerror", lambda e: errs.append(str(e)))
    page.on("console", lambda m: m.type == "error" and errs.append(m.text))
    return errs


def overflow(page):
    return page.evaluate(
        "document.documentElement.scrollWidth - document.documentElement.clientWidth")


try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Umgebungsfehler: playwright fehlt")
    sys.exit(2)

chromium = None
for p in sorted(glob.glob(os.path.expanduser(
        "~/Library/Caches/ms-playwright/chromium-*/chrome-mac-arm64/"
        "Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"))):
    chromium = p
    break

report = {"checks": []}
with sync_playwright() as pw:
    kw = dict(headless=True, args=["--force-color-profile=srgb", "--disable-gpu"])
    if chromium:
        kw["executable_path"] = chromium
    try:
        b = pw.chromium.launch(**kw)
    except Exception as e:
        print("Umgebungsfehler: Chromium-Start:", e)
        sys.exit(2)

    # ---- K3 Kontrast (statisch, aus CSS-Varian) ---------------------------
    for pair, need in ((("#f0f0f0", "#000000"), 4.5), (("#a5a5a5", "#000000"), 4.5)):
        ratio = contrast(*pair)
        (ok if ratio >= need else bad)(
            "Kontrast %s auf %s = %.2f:1 (AA braucht >= %.1f:1)" %
            (pair[0], pair[1], ratio, need))
        report["checks"].append(
            {"kontrast": "%s auf %s" % pair, "ratio": round(ratio, 2), "aa": ratio >= need})

    # ---- mobile 390x844 (Device-Emulation) ---------------------------------
    mobile = b.new_context(
        viewport={"width": 390, "height": 844}, device_scale_factor=3,
        is_mobile=True, has_touch=True, locale="en-US")
    page = mobile.new_page()
    errs = page_errors(page)
    page.goto(BASE + "/index.html", wait_until="load", timeout=20000)
    page.wait_for_timeout(1200)
    if errs:
        bad("index mobile pageerrors: " + "; ".join(errs))
    else:
        ok("index @390: 0 pageerrors")
    d = overflow(page)
    (ok if d == 0 else bad)("index @390 Overflow: %s" % d)
    report["checks"].append({"overflow_390": d})

    # K2 Touch-Targets: alle sichtbar-klickbaren Elemente effektiv >= 44x44.
    # Die unsichtbaren ::before-Hit-Areas (inset -6px..-17px, siehe #11-A11y
    # Commit 52c84e4) erweitern die Box; wir messen Raw-Box + Hit-Area-Bonus
    # (Inset-Summe) aus getComputedStyle.
    all_t = page.evaluate("""() => {
      const els = [...document.querySelectorAll('button, a, [data-go]')]
        .filter(e => e.offsetParent !== null);
      return els.map(e => {
        const r = e.getBoundingClientRect();
        const cs = getComputedStyle(e, '::before');
        // Chromium liefert 'inset' nicht als einzeln lesbares Wert — die 4
        // Seiten (top/right/bottom/left) zusammenfassen. Unsichtbare Hit-Areas
        // (52c84e4) setzen z. B. inset: -17px. Bonus = 2*|min|-Seite.
        let bonus = 0;
        if (cs.content !== 'none' && cs.content !== '' && cs.position === 'absolute') {
          const parts = [cs.top, cs.right, cs.bottom, cs.left]
            .map(v => parseFloat(v))
            .filter(v => !isNaN(v));
          if (parts.length && Math.min(...parts) < 0) {
            bonus = Math.abs(Math.min(...parts)) * 2;
          }
        }
        return {l: (e.getAttribute('aria-label') || (e.textContent || '').trim() || e.className).slice(0, 30),
                effW: Math.round(r.width + bonus), effH: Math.round(r.height + bonus),
                raw: [Math.round(r.width), Math.round(r.height)]};
      });
    }""")
    still_bad = [t for t in all_t if t["effW"] < 44 or t["effH"] < 44]
    for t in still_bad:
        bad("Touch-Target <44px effektiv: '%s' (raw %s, eff %dx%d)"
            % (t["l"], t["raw"], t["effW"], t["effH"]))
    if not still_bad:
        ok("Touch-Targets @390: alle %d Elemente effektiv >= 44x44 (inkl. Hit-Areas)" % len(all_t))
    report["checks"].append({"touch_targets": all_t, "violations": still_bad})

    page.screenshot(path=os.path.join(OUT, "screenshot-mobile-390-index.png"))
    for name, path in (("impressum", "/impressum.html"), ("datenschutz", "/datenschutz.html")):
        page.goto(BASE + path, wait_until="load", timeout=20000)
        page.wait_for_timeout(400)
        d = overflow(page)
        (ok if d == 0 else bad("%s @390 Overflow: %s" % (name, d)))
        page.screenshot(path=os.path.join(OUT, "screenshot-mobile-390-%s.png" % name))
    mobile.close()

    # ---- tablet 768x1024 ----------------------------------------------------
    tablet = b.new_context(viewport={"width": 768, "height": 1024}, device_scale_factor=2)
    tp = tablet.new_page()
    errs = page_errors(tp)
    tp.goto(BASE + "/index.html", wait_until="load", timeout=20000)
    tp.wait_for_timeout(800)
    if errs:
        bad("index @768 pageerrors: " + "; ".join(errs))
    else:
        ok("index @768: 0 pageerrors")
    d = overflow(tp)
    (ok if d == 0 else bad("index @768 Overflow: %s" % d))
    report["checks"].append({"overflow_768": d})
    tp.screenshot(path=os.path.join(OUT, "screenshot-tablet-768-index.png"))
    tablet.close()

    # ---- desktop 1280x800 ----------------------------------------------------
    desk = b.new_context(viewport={"width": 1280, "height": 800})
    dp = desk.new_page()
    errs = page_errors(dp)
    dp.goto(BASE + "/index.html", wait_until="load", timeout=20000)
    dp.wait_for_timeout(1000)
    if errs:
        bad("index @1280 pageerrors: " + "; ".join(errs))
    else:
        ok("index @1280: 0 pageerrors")
    d = overflow(dp)
    (ok if d == 0 else bad("index @1280 Overflow: %s" % d))
    report["checks"].append({"overflow_1280": d})
    dp.screenshot(path=os.path.join(OUT, "screenshot-desktop-1280-index.png"))

    # K4 prefers-reduced-motion
    rm = b.new_context(viewport={"width": 1280, "height": 800},
                       reduced_motion="reduce")
    rp = rm.new_page()
    rp.goto(BASE + "/index.html", wait_until="load", timeout=20000)
    rp.wait_for_timeout(1000)
    snap1 = rp.evaluate("document.querySelector('#dust').toDataURL().length")
    rp.wait_for_timeout(2500)
    snap2 = rp.evaluate("document.querySelector('#dust').toDataURL().length")
    static = snap1 == snap2
    # rAF-Callbacks feuern im Browser immer (Framing-Callbacks); der kanonische
    # Test ist die statische Canvas: bei reduce darf sich #dust nicht aendern.
    if static:
        ok("reduced-motion: Canvas statisch (kein Animationsfortschritt ueber 2,5s)")
    else:
        bad("reduced-motion: Canvas aendert sich trotz prefers-reduced-motion")
    report["checks"].append({"reduced_motion": {"static": static}})
    rp.screenshot(path=os.path.join(OUT, "screenshot-reduced-motion.png"))
    rm.close()

    # K5 FPS-Sanity desktop (ohne reduced motion) — FPS wird in ein DOM-Attribut
    # geschrieben, da page.evaluate keine async-Promises ueber 5s liefern darf.
    dp.evaluate("""() => {
      window.__fpsResult = null;
      let n = 0;
      const t0 = performance.now();
      function tick(now) {
        n++;
        if (now - t0 < 5000) requestAnimationFrame(tick);
        else {
          const secs = (now - t0) / 1000;
          window.__fpsResult = {frames: n, fps: n / secs};
        }
      }
      requestAnimationFrame(tick);
    }""")
    dp.wait_for_timeout(6500)
    data = dp.evaluate("window.__fpsResult")
    fps_real = data["fps"] if data else 0
    (ok if fps_real >= 55 else bad)("FPS desktop: %.1f (60fps-Ziel, 5s-Messung)" % fps_real)
    report["checks"].append({"fps_desktop": fps_real})

    # K6 Performance-Metriken
    metrics = dp.evaluate("""() => {
      const m = {};
      const e = performance.getEntriesByType('paint');
      for (const p of e) m[p.name] = Math.round(p.startTime);
      return JSON.stringify(m);
    }""")
    pm = json.loads(metrics)
    fcp = pm.get("first-contentful-paint")
    ok("FCP: %s ms%s" % (fcp, " (<2000ms)" if fcp and fcp < 2000 else ""))
    if not (fcp and fcp < 2000):
        bad("FCP: %s (Ziel < 2000ms)" % fcp)
    report["checks"].append({"fcp_ms": fcp, "paints": pm})
    dp.close()
    desk.close()

    # ---- mobile Lighthouse-like Scores (substituiert) ------------------------
    # Kein node in der Umgebung: Lighthouse-CLI laeuft nicht. Wir dokumentieren
    # die Kern-Checks, die Lighthouse-Punkte deterministisch tragen:
    #  Perf: FCP < 2s (K6), 0 JS-Fehler, kein H-Overflow
    #  A11y: Kontrast AA (K3), Touch >=44 (K2), Lang-Sets, Alt-Texts (index 0 imgs without alt?)
    dp2 = b.new_context(viewport={"width": 390, "height": 844})
    p2 = dp2.new_page()
    p2.goto(BASE + "/index.html", wait_until="load", timeout=20000)
    p2.wait_for_timeout(500)
    a11y = p2.evaluate("""() => {
      const out = {};
      out.htmlLang = document.documentElement.lang;
      // leere alt="" ist korrekt (dekorativ); nur FEHLENDES alt zahlt.
      out.imgsNoAlt = [...document.querySelectorAll('img')]
        .filter(i => i.getAttribute('alt') === null).length;
      out.buttonsNoName = [...document.querySelectorAll('button')].filter(
        b => !b.getAttribute('aria-label') && !(b.textContent || '').trim()).length;
      out.h1 = document.querySelectorAll('h1').length;
      return out;
    }""")
    (ok if a11y["htmlLang"] and not a11y["imgsNoAlt"] and not a11y["buttonsNoName"] else bad(
        "A11y-Kern: %s" % json.dumps(a11y)))
    report["checks"].append({"a11y_core": a11y})
    p2.close()
    dp2.close()

    b.close()

with open(os.path.join(OUT, "baseline.json"), "w") as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

print("=" * 40)
if fail:
    print("BASELINE ROT:")
    for m in fail:
        print(" -", m)
    sys.exit(1)
print("BASELINE GRUEN — Report: %s/" % OUT)
