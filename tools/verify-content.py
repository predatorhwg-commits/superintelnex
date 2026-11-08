#!/usr/bin/env python3
"""Prueft die inhaltlichen Regeln der Seite.

Der Kern dieser Pruefung: die Seite darf nichts behaupten, was es nicht gibt.
Geprueft werden:

  1. Keine Preisangaben ($, EUR, BTC-Amount) im sichtbaren Text
  2. Keine Prozentangaben ohne Kontext
  3. Keine Marketing-Superlative ohne Beleg
  4. Jede geplante Funktion traegt den Status "Geplant"
  5. Keine Kauf-Buttons
  6. Keine erfundenen Kennzahlen ("X Teilnehmer", "Y Nutzer")
  7. Keine Audit-/Zertifizierungsbehauptung ohne Namen
  8. Der Risikohinweis ist vorhanden

Aufruf:
    python3 tools/verify-content.py [seitenverzeichnis]

Exit 0 = keine Befunde, Exit 1 = Befunde.
"""
from __future__ import annotations

import os
import re
import sys
from html.parser import HTMLParser

DEFAULT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Verbotene Muster. Bewusst als Regex, damit Varianten auffallen.
FORBIDDEN = [
    (r"\$", "Preisangabe in Dollar"),
    (r"\b\d[\d.,]*\s*(?:€|EUR|USD|GBP|CHF)\b", "Preisangabe"),
    (r"\b\d[\d.,]*\s*(?:BTC|ETH|SOL|USDT|USDC)\b", "Token-Menge im sichtbaren Text"),
    (r"\b\d+\s*%\s*(?:Rendite|Gewinn|Profit|Return)", "Renditeversprechen"),
    (r"(?:Rendite|Gewinn|Profit)\s*(?:von|bis zu)\s*\d", "Renditeversprechen"),
    (r"\b(?:revolutionär|bahnbrechend|weltweit\s+führend|marktführend|"
     r"der\s+beste|das\s+beste|unsinnig\s+gut)\b", "Superlativ ohne Beleg"),
    (r"\b(?:sicher|garantiert|riskofrei|verlustfrei)\b", "Sicherheitsversprechen"),
    (r"\b(?:Jetzt\s+kaufen|Jetzt\s+beitreiten|Zum\s+Kauf|BUY\s+NOW)\b",
     "Kauf-Aufruf"),    (r"\b(?:Limitierte\s+Plätze|Nur\s+heute|Countdown|Aktion\s+endet)\b",
     "Künstlicher Dringlichkeitsdruck"),
    (r"\b(?:geprüft\s+von|auditiert\s+von|zertifiziert\s+von)\b",
     "Audit- oder Zertifizierungsbehauptung ohne genannten Prüfer"),
    (r"\b(?:Analystenempfehlung|Kursziel|Preisziel)\b", "Kursprognose"),
    (r"\b(?:Krypto[- ]?Börse|Börse\s+unterstützt|Liquidität\s+garantiert)\b",
     "Behauptung über Börsen-/Liquiditätslage"),
]

# Kontext-Ausnahmen: Steht das verbotene Wort in einer erklaerenden oder
# verneinenden Umgebung ("Keine ... 'Jetzt kaufen'-Schaltflaechen"), ist es kein
# Befund. Sonst waere jede Selbstauskunft auf der Seite ein Treffer.
NEGATION_CONTEXT = re.compile(
    r"(?:kein[eo]?|keine[nr]?|ohne|nicht|nichts|nie|niemals|verboten|"
    r"unzulaessig|bewusst\s+kein|wird\s+nicht|keine\s+erfunden\w*)\s"
    r"[^.!?]{0,90}$",
    re.IGNORECASE,
)

# Erlaubte Ausnahmen: Platzhalter in Anfuehrungszeichen, die auf die Variable
# hinweisen, plus Zahlen, die keine Kennzahl sind.
ALLOWED_PATTERNS = [
    r"superintelnex\.com",
    r"\b\d{4}\b",  # Jahreszahlen
]

NUMBER_CLAIM = re.compile(
    r"\b(\d[\d.,]*)\s*(?:Nutzer|Teilnehmer|Mitglieder|Halter|Investoren|Anleger|"
    r"Käufer|Follower|Downloads|Transaktionen|Wallets?|Mitglieder)\b",
    re.IGNORECASE,
)

PLANNED_FUNCTIONS = ["Übertragen", "Handeln", "Bezahlen", "KI-Anwendungen"]


class TextCollector(HTMLParser):
    """Sammelt sichtbaren Text (ohne script/style)."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.skip_depth = 0
        self.parts: list[str] = []
        self.headings: list[tuple[int, str]] = []
        self.current_heading: int | None = None
        self.heading_text: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "template"):
            self.skip_depth += 1
        if tag in ("h1", "h2", "h3", "h4"):
            self.current_heading = int(tag[1])
            self.heading_text = []

    def handle_endtag(self, tag):
        if tag in ("script", "style", "template") and self.skip_depth:
            self.skip_depth -= 1
        if tag in ("h1", "h2", "h3", "h4") and self.current_heading is not None:
            self.headings.append((self.current_heading, " ".join(self.heading_text).strip()))
            self.current_heading = None

    def handle_data(self, data):
        if self.skip_depth:
            return
        text = data.strip()
        if not text:
            return
        self.parts.append(text)
        if self.current_heading is not None:
            self.heading_text.append(text)


def visible_text(html: str) -> str:
    p = TextCollector()
    p.feed(html)
    return " ".join(p.parts)


def main() -> int:
    root = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DIR
    pages: list[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in {".git", "node_modules"}]
        for name in filenames:
            if name.endswith(".html"):
                pages.append(os.path.join(dirpath, name))
    pages.sort()

    if not pages:
        print("FEHLER: keine HTML-Dateien gefunden.")
        return 1

    problems: list[str] = []
    index_path = os.path.join(root, "index.html")

    for path in pages:
        rel = os.path.relpath(path, root).replace(os.sep, "/")
        with open(path, encoding="utf-8") as fh:
            html = fh.read()
        text = visible_text(html)

        for pattern, label in FORBIDDEN:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                before = text[max(0, match.start() - 120): match.start()]
                if NEGATION_CONTEXT.search(before):
                    continue  # erklaerende oder verneinende Umgebung
                snippet = text[max(0, match.start() - 40): match.end() + 40]
                problems.append(f"{rel}: {label} — …{snippet.strip()}…")

        for match in NUMBER_CLAIM.finditer(text):
            problems.append(
                f"{rel}: erfundene Kennzahl „{match.group(0).strip()}' "
                f"— keine Quelle in docs/QUELLEN.md"
            )

    # Spezifische Regeln fuer die Startseite
    if os.path.exists(index_path):
        with open(index_path, encoding="utf-8") as fh:
            html = fh.read()
        parser = TextCollector()
        parser.feed(html)
        text = " ".join(parser.parts)

        # Risikohinweis
        if "Verlust" not in text or "Risiko" not in text:
            problems.append("index.html: Risikohinweis unvollstaendig.")

        # "Geplant"-Status
        geplant_count = len(re.findall(r"\bGeplant\b", html))
        if geplant_count < len(PLANNED_FUNCTIONS):
            problems.append(
                f"index.html: nur {geplant_count}× 'Geplant' — "
                f"erwartet mindestens {len(PLANNED_FUNCTIONS)} (eine je Funktion)."
            )

        # jede geplante Funktion traegt den Status
        for fn in PLANNED_FUNCTIONS:
            if fn not in html:
                problems.append(f"index.html: Funktion '{fn}' fehlt.")

        # keine Buttons, die zum Kauf verleiten
        for m in re.finditer(r"<button[^>]*>(.*?)</button>", html, re.DOTALL | re.IGNORECASE):
            label = visible_text(m.group(1)).strip().lower()
            if any(w in label for w in ("kauf", "kaufen", "buy", "jetzt")):
                problems.append(f"index.html: kaufverleitender Button: '{label}'")

    print(f"Geprüfte Seiten: {len(pages)}")
    print(f"Geprüfte Verbotsmuster: {len(FORBIDDEN)} + Kennzahlen + Geplant-Status")
    if problems:
        print(f"\n{len(problems)} Befund(e):")
        for prob in problems:
            print(f"  ! {prob}")
        return 1
    print("\nInhalt in Ordnung: keine erfundenen Angaben, keine Kauf-Buttons, Risikohinweis vorhanden.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
