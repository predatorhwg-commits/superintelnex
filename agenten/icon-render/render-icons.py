#!/usr/bin/env python3
"""Apple-Touch-/Manifest-Icons rendern (Chromium-Screenshot), deterministisch,
keine externen Tools. Ausgang: superintelnex-sn-anthrazit.svg auf #000-Bg."""
import glob, os, sys
from playwright.sync_api import sync_playwright
import io
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC = os.path.join(ROOT, "agenten", "icon-render", "render.html")
OUT = os.path.join(ROOT)

def find_chromium():
    pat = os.path.expanduser("~/Library/Caches/ms-playwright/chromium-*/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing")
    found = sorted(glob.glob(pat))
    return found[0] if found else None

with sync_playwright() as p:
    kw = dict(headless=True, args=["--force-color-profile=srgb"])
    ep = find_chromium()
    if ep:
        kw["executable_path"] = ep
    b = p.chromium.launch(**kw)
    pg = b.new_page(viewport={"width": 512, "height": 512})
    pg.goto(f"file://{SRC}", wait_until="load")
    pg.wait_for_timeout(300)
    base = io.BytesIO(pg.locator(".stage").screenshot())
    Image.open(base).save(os.path.join(OUT, "icon-512.png"), format="PNG")
    for size, name in ((192, "icon-192.png"), (180, "apple-touch-icon.png")):
        Image.open(base).resize((size, size), Image.LANCZOS).save(os.path.join(OUT, name), format="PNG")
    b.close()
for name in ("apple-touch-icon.png", "icon-192.png", "icon-512.png"):
    path = os.path.join(OUT, name)
    import struct
    h = open(path, "rb").read(24)
    w, hh = struct.unpack(">II", h[16:24])
    print(name, f"{w}x{hh}", os.path.getsize(path), "B")
