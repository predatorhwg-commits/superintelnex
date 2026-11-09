#!/usr/bin/env python3
"""Lokales QA-Gate (#4/#9): 0 pageerror, 0 tote interne Links,
kein horizontaler Overflow @390x844/1280x800, #9-Dateien 200, #dust vorhanden.
Exit 0=GRUEN, 1=ROT, 2=Umgebungsfehler. Aufruf: GATE_BASE=http://127.0.0.1:8195"""
import os, sys, urllib.request, glob

BASE = os.environ.get("GATE_BASE", "http://127.0.0.1:8195")
fail = []

# C1: #9-Dateien erreichbar
for f in ("robots.txt", "sitemap.xml", "manifest.webmanifest",
         "apple-touch-icon.png", "icon-192.png", "icon-512.png",
         "og-image.png", "superintelnex-sn-anthrazit.svg"):
    try:
        r = urllib.request.urlopen(BASE + "/" + f, timeout=5)
        ok = r.status == 200
        print(("OK   " if ok else "FAIL "), f, r.status)
        if not ok:
            fail.append(f + " -> " + str(r.status))
    except Exception as e:
        fail.append(f + " -> " + str(e))
        print("FAIL ", f, e)

chromium = None
for p in sorted(glob.glob(os.path.expanduser(
        "~/Library/Caches/ms-playwright/chromium-*/chrome-mac-arm64/"
        "Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"))):
    chromium = p
    break

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Umgebungsfehler: playwright fehlt"); sys.exit(2)

pages = ["index.html", "impressum.html", "datenschutz.html", "404.html"]
with sync_playwright() as pw:
    kw = dict(headless=True, args=["--force-color-profile=srgb", "--disable-gpu"])
    if chromium:
        kw["executable_path"] = chromium
    try:
        b = pw.chromium.launch(**kw)
    except Exception as e:
        print("Umgebungsfehler: Chromium-Start:", e); sys.exit(2)

    for pagef in pages:
        page = b.new_page(viewport={"width": 1280, "height": 800})
        errs = []
        page.on("pageerror", lambda e: errs.append(str(e)))
        page.on("console", lambda m: m.type == "error" and errs.append(m.text))
        try:
            page.goto(BASE + "/" + pagef, wait_until="load", timeout=15000)
            page.wait_for_timeout(600)
        except Exception as e:
            fail.append(pagef + " Laden: " + str(e)); print("FAIL", pagef, e)
            page.close(); continue
        if errs:
            fail.append(pagef + " pageerror: " + "; ".join(errs))
            print("FAIL ", pagef, errs)
        else:
            print("OK   ", pagef, "0 pageerror")
        dead = []
        for a in page.locator("a[href]").all():
            h = a.get_attribute("href")
            if h and not h.startswith("http") and not h.startswith("#") and not h.startswith("mailto:"):
                u = BASE + "/" + h.lstrip("/")
                try:
                    st = urllib.request.urlopen(u, timeout=5).status
                except Exception as e:
                    st = getattr(e, "code", 0)
                if st in (0, 404):
                    dead.append(h + " -> " + str(st))
        if dead:
            fail.append(pagef + " tote Links: " + ", ".join(dead))
            print("FAIL ", pagef, dead)
        else:
            print("OK   ", pagef, "0 tote interne Links")
        for w, hh in ((390, 844), (1280, 800)):
            page.set_viewport_size({"width": w, "height": hh})
            page.wait_for_timeout(300)
            d = page.evaluate(
                "document.documentElement.scrollWidth - document.documentElement.clientWidth")
            if d != 0:
                fail.append(pagef + " Overflow @%dpx: %s" % (w, d))
                print("FAIL ", pagef, "@%dpx d=%s" % (w, d))
            else:
                print("OK   ", pagef, "@%dpx kein Overflow" % w)
        if pagef == "index.html":
            has = page.evaluate("!!document.querySelector('#dust')")
            if not has:
                fail.append("index: #dust fehlt")
                print("FAIL index #dust fehlt")
            else:
                print("OK   index #dust vorhanden")
        page.close()
    b.close()

print("=" * 40)
if fail:
    print("GATE ROT:")
    for f in fail:
        print(" -", f)
    sys.exit(1)
print("GATE GRUEN (lokal)")
