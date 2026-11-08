#!/usr/bin/env python3
"""Prueft die Markup-Struktur aller HTML-Seiten.

Geprueft werden: genau ein h1, lueckenlose Ueberschriftenhierarchie, doppelte
IDs, Pflicht-Landmarks, Sprunglink mit Ziel, lang-Attribut, Bildattribute.

Aufruf:
    python3 tools/verify-markup.py [seitenverzeichnis]

Exit 0 = keine Befunde, Exit 1 = Befunde.
"""
from __future__ import annotations

import os
import sys
from html.parser import HTMLParser

DEFAULT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "param", "source", "track", "wbr"}


class DocParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.headings: list[tuple[int, str]] = []
        self.ids: list[str] = []
        self.lang: str | None = None
        self.landmarks: set[str] = set()
        self.landmark_counts: dict[str, int] = {}
        self.skip_link_targets: list[str] = []
        self.img_no_dims = 0
        self.img_no_alt = 0
        self.inline_handlers: list[str] = []
        self.has_main_id = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = dict(attrs)
        if tag == "html":
            self.lang = a.get("lang")
        if a.get("id"):
            self.ids.append(a["id"])
            if tag == "main" and a["id"] == "main":
                self.has_main_id = True
        if tag in {"header", "nav", "main", "footer", "aside", "form"}:
            self.landmarks.add(tag)
            self.landmark_counts[tag] = self.landmark_counts.get(tag, 0) + 1
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            level = int(tag[1])
            self.headings.append((level, tag))
        if tag == "a" and a.get("class", "") and "skip-link" in a["class"].split():
            href = a.get("href", "")
            if href.startswith("#"):
                self.skip_link_targets.append(href[1:])
        if tag == "img":
            if a.get("alt") is None:
                self.img_no_alt += 1
            if not a.get("width") or not a.get("height"):
                self.img_no_dims += 1
        for key in a:
            if key.startswith("on"):
                self.inline_handlers.append(f"{tag}@{key}")

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)


def find_pages(root: str) -> list[str]:
    out: list[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in {".git", "node_modules"}]
        for name in filenames:
            if name.endswith(".html"):
                out.append(os.path.join(dirpath, name))
    return sorted(out)


def main() -> int:
    root = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DIR
    pages = find_pages(root)
    if not pages:
        print("FEHLER: keine HTML-Dateien gefunden.")
        return 1

    problems: list[str] = []
    for path in pages:
        rel = os.path.relpath(path, root).replace(os.sep, "/")
        with open(path, encoding="utf-8") as fh:
            p = DocParser()
            p.feed(fh.read())

        # doppelte IDs
        seen: set[str] = set()
        dups = sorted({i for i in p.ids if i in seen or seen.add(i)})  # type: ignore[func-returns-value]
        if dups:
            problems.append(f"{rel}: doppelte IDs: {', '.join(dups)}")

        # genau ein h1
        h1 = sum(1 for lvl, _ in p.headings if lvl == 1)
        if h1 != 1:
            problems.append(f"{rel}: {h1} h1-Elemente (erwartet: genau 1).")

        # lueckenlose Hierarchie
        prev = 0
        for lvl, tag in p.headings:
            if prev and lvl > prev + 1:
                problems.append(
                    f"{rel}: Ueberschriftensprung {prev} -> {lvl} ({tag})."
                )
            prev = lvl

        # Landmarks
        if "main" not in p.landmarks:
            problems.append(f"{rel}: kein <main>.")
        if "nav" not in p.landmarks:
            problems.append(f"{rel}: kein <nav>.")
        if "footer" not in p.landmarks:
            problems.append(f"{rel}: kein <footer>.")
        if p.landmark_counts.get("main", 0) != 1:
            problems.append(
                f"{rel}: {p.landmark_counts.get('main', 0)} <main>-Elemente (erwartet: 1)."
            )

        # Sprunglink
        if not p.skip_link_targets:
            problems.append(f"{rel}: kein Sprunglink (.skip-link).")
        elif "main" not in p.skip_link_targets and not p.has_main_id:
            problems.append(f"{rel}: Sprunglink zeigt auf unbekanntes Ziel.")

        # lang
        if not p.lang:
            problems.append(f"{rel}: <html> ohne lang-Attribut.")

        # Bilder
        if p.img_no_alt:
            problems.append(f"{rel}: {p.img_no_alt} Bild(er) ohne alt-Attribut.")
        if p.img_no_dims:
            problems.append(
                f"{rel}: {p.img_no_dims} Bild(er) ohne width/height (Layout-Sprung)."
            )

        # Inline-Handler
        if p.inline_handlers:
            problems.append(
                f"{rel}: Inline-Handler gefunden: {', '.join(sorted(set(p.inline_handlers)))}"
            )

    print(f"Geprüfte Seiten: {len(pages)}")
    if problems:
        print(f"\n{len(problems)} Befund(e):")
        for prob in problems:
            print(f"  ! {prob}")
        return 1
    print("\nMarkup in Ordnung: Überschriften, IDs, Landmarks, Sprunglink, lang, Bilder.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
