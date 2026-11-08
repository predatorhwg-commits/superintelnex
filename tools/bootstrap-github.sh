#!/usr/bin/env bash
# Legt die Dokumentationsbasis auf GitHub an: Branch, Commit, Push, PR, Issues.
#
# Voraussetzung: ein GitHub-Token in der Umgebung oder im macOS-Schluesselbund.
#
#   security add-generic-password -s github.com -a predatorhwg-commits -w <token>
#   export GITHUB_TOKEN=<token>
#
# Aufruf:
#   bash tools/bootstrap-github.sh
#
# Der Befehl ist idempotent: existiert der Branch oder das Issue schon,
# wird es uebersprungen und nicht dupliziert.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

BRANCH="docs/project-brief"
BASE="main"
REPO="predatorhwg-commits/superintelnex"
PY="python3"

say() { printf '\n\033[1m==> %s\033[0m\n' "$1"; }

say "1/7 Voraussetzungen pruefen"
command -v git >/dev/null || { echo "FEHLER: git fehlt."; exit 1; }
"$PY" -c "import sys; assert sys.version_info >= (3, 9)" || {
  echo "FEHLER: Python 3.9+ noetig."; exit 1; }
"$PY" -m py_compile tools/gh-api.py
echo "git und Python ok."

say "2/7 Token pruefen"
"$PY" tools/gh-api.py --repo "$REPO" check

say "3/7 Aenderungen pruefen"
if git diff --quiet && git diff --cached --quiet && [ -z "$(git status --porcelain)" ]; then
  echo "Keine Aenderungen im Arbeitsverzeichnis."
else
  git status --short
  echo
  echo "Bitte zuerst selbst committen (das Skript committet nicht fuer dich):"
  echo "  git checkout -b $BRANCH"
  echo "  git add -A && git commit -m 'Dokumentationsbasis: Projekt-Brief und Issues'"
  echo "  bash tools/bootstrap-github.sh"
  exit 0
fi

say "4/7 Branch pruefen und pushen"
if git rev-parse --verify "$BRANCH" >/dev/null 2>&1; then
  echo "Branch $BRANCH existiert bereits — kein neuer Push."
else
  git checkout -b "$BRANCH"
  git push -u origin "$BRANCH"
fi

say "5/7 Pull Request erstellen"
PR_TITLE="Projekt-Brief und Dokumentationsbasis"
if "$PY" tools/gh-api.py --repo "$REPO" pr list --state open | grep -q "$PR_TITLE"; then
  echo "Offener PR mit diesem Titel existiert bereits."
else
  "$PY" tools/gh-api.py --repo "$REPO" pr create \
    --title "$PR_TITLE" \
    --body-file docs/pr/project-brief.md \
    --base "$BASE" --head "$BRANCH"
fi

say "6/7 Issues anlegen"
"$PY" tools/gh-api.py --repo "$REPO" issue create-batch --dir docs/issues

say "7/7 Tracking-Issue fuellen"
TRACKING="$("$PY" tools/gh-api.py --repo "$REPO" issue list --state open \
  | grep 'SuperIntelNex Website' | head -1 | awk '{print $1}' | tr -d '#')"
if [ -z "$TRACKING" ]; then
  echo "FEHLER: Tracking-Issue nicht gefunden. Bitte Nummer manuell eintragen."
  exit 1
fi
echo "Tracking-Issue: #$TRACKING"
"$PY" tools/gh-api.py --repo "$REPO" issue update-tracking "$TRACKING" --dir docs/issues

say "Fertig"
echo "Erste Schritte:"
echo "  1. PR pruefen und mergen."
echo "  2. Rollen den Issues zuweisen und mit der Arbeit beginnen."
echo "  3. Nach jedem Abschluss: Issue-Status setzen und Brett aktualisieren."
