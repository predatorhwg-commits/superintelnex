#!/usr/bin/env python3
"""Prueft interne Links und Anker aller HTML-Seiten.

Aufruf:
    python3 tools/check-links.py [seitenverzeichnis] [basis-url]

Exit 0 = alles in Ordnung, Exit 1 = mindestens ein toter Verweis.
"""
from __future__ import annotations

import os
import sys
import urllib.parse
import urllib.request
from html.parser import HTMLParser

DEFAULT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TIMEOUT = 10


class RefParser(HTMLParser):
    """Sammelt href-/src-Referenzen und alle vergebenen IDs."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.refs: list[str] = []
        self.ids: set[str] = set()
        self.imgs_without_alt = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = dict(attrs)
        for key in ("href", "src"):
            val = a.get(key)
            if val:
                self.refs.append(val)
        if a.get("id"):
            self.ids.add(a["id"])
        if a.get("name"):
            self.ids.add(a["name"])
        if tag == "img" and a.get("alt") is None:
            self.imgs_without_alt += 1

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)


def find_pages(root: str) -> list[str]:
    pages: list[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [
            d
            for d in dirnames
            if d not in {".git", "node_modules", ".well-known", "fonts", "vendor"}
        ]
        for name in filenames:
            if name.endswith(".html"):
                pages.append(os.path.join(dirpath, name))
    return sorted(pages)


def parse(path: str) -> RefParser:
    with open(path, encoding="utf-8") as fh:
        html = fh.read()
    p = RefParser()
    p.feed(html)
    return p


def main() -> int:
    root = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DIR
    base = (sys.argv[2] if len(sys.argv) > 2 else "http://127.0.0.1:8188").rstrip("/")

    pages = find_pages(root)
    if not pages:
        print("FEHLER: keine HTML-Dateien gefunden.")
        return 1

    parsed = {p: parse(p) for p in pages}
    by_rel: dict[str, RefParser] = {}
    for path, p in parsed.items():
        rel = os.path.relpath(path, root)
        by_rel[rel.replace(os.sep, "/")] = p

    problems: list[str] = []
    checked = 0
    external: list[str] = []

    for path, p in parsed.items():
        page_rel = os.path.relpath(path, root).replace(os.sep, "/")
        for ref in p.refs:
            if ref.startswith(("mailto:", "tel:", "data:", "javascript:", "#")):
                if ref.startswith("#") and len(ref) > 1:
                    if ref[1:] not in p.ids:
                        problems.append(f"{page_rel}: Anker {ref} existiert auf der Seite nicht.")
                continue
            if ref.startswith(("http://", "https://", "//")):
                external.append(ref)
                continue
            if ref.startswith("?"):
                continue

            target, _, frag = ref.partition("#")
            target = target.split("?", 1)[0]
            if not target:
                continue

            checked += 1

            # Existiert die Datei lokal?
            local = os.path.normpath(os.path.join(os.path.dirname(path), target))
            if os.path.exists(local):
                if frag:
                    tgt_rel = os.path.relpath(local, root).replace(os.sep, "/")
                    tgt_parser = by_rel.get(tgt_rel)
                    if tgt_parser and frag not in tgt_parser.ids:
                        problems.append(
                            f"{page_rel}: Anker #{frag} fehlt in {tgt_rel}."
                        )
                continue

            # Sonst: HTTP-Status pruefen (z.B. GitHub-Pages-Weiterleitung auf Ordner)
            url = urllib.parse.urljoin(f"{base}/{page_rel}", target)
            code = 0
            try:
                req = urllib.request.Request(url, method="GET")
                with urllib.request.urlopen(req, timeout=TIMEOUT) as res:
                    code = res.status
            except urllib.error.HTTPError as exc:
                code = exc.code
            except Exception as exc:  # Netzwerkfehler: Hinweis, kein harter Fehler
                problems.append(f"{page_rel}: {target} nicht erreichbar ({exc}).")
                continue
            if code not in (200, 301, 302, 308):
                problems.append(f"{page_rel}: {target} liefert HTTP {code}.")

    for path, p in parsed.items():
        page_rel = os.path.relpath(path, root).replace(os.sep, "/")
        if p.imgs_without_alt:
            problems.append(
                f"{page_rel}: {p.imgs_without_alt} Bild(er) ohne alt-Attribut."
            )

    print(f"Geprüfte Seiten: {len(pages)}")
    print(f"Geprüfte interne Verweise: {checked}")
    print(f"Externe Verweise (nicht geprüft): {len(set(external))}")
    for url in sorted(set(external)):
        print(f"  - {url}")

    if problems:
        print(f"\n{len(problems)} Problem(e):")
        for prob in problems:
            print(f"  ! {prob}")
        return 1

    print("\nAlle internen Links, Anker und alt-Attribute in Ordnung.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
