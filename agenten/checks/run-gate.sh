#!/bin/sh
# ============================================================================
# SuperIntelNex — QA-Release-Gate Runner (run-gate.sh)
# ============================================================================
# Startet einen lokalen http.server (Port 8195, QA-exklusiv), waerft ihn,
# fuehrt agenten/checks/release-gate.py gegen den angegebenen Checkout aus
# und gibt dessen Exit-Code unveraendert weiter (0 = Gate GRUEN, 1 = ROT,
# 2 = Umgebungsfehler).
#
# VERWENDUNG (CEO, auf JEDEM Worktree/Merge lauffaehig):
#
#   agenten/checks/run-gate.sh [REPO_ROOT]
#
#   - Ohne Argument: der eigene Repo-Root wird benutzt (zwei Ebenen ueber
#     diesem Skript, standardmaessig <checkout>/site/).
#   - Mit Argument: der uebergebene Pfad wird als Repo-Root benutzt — so
#     kann das Skript aus deinem Worktree gegen einen ANDEREN Checkout
#     (z. B. den finalen Merge auf main) laufen:
#
#         /path/to/worktree-qa/agenten/checks/run-gate.sh /path/to/main-checkout
#
# Voraussetzungen:
#   - python3 mit playwright (python3 -c "import playwright" muss gehen)
#   - Bundle-Chromium: ~/Library/Caches/ms-playwright/chromium-1223/...
#     (wird vom Skript selbst gefunden)
#   - repo-enthaelt: site/ (3 HTML-Seiten) + .git (fuer Secret-Scan)
#
# Port: QA_GATE_PORT=8195 (ueberschreibbar, Standard 8195). Ist der Port
# bereits belegt, bricht der Runner mit exit 2 ab (kein Hijacking anderer
# Agenten-Server).
# ============================================================================

set -u

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
GATE="$SCRIPT_DIR/release-gate.py"
PORT="${QA_GATE_PORT:-8195}"
LOG="$(mktemp -t sinitgnex-gate-server.XXXXXX 2>/dev/null || echo /tmp/sinitgnex-gate-server.log)"

if [ ! -f "$GATE" ]; then
    echo "FEHLER: release-gate.py nicht gefunden neben run-gate.sh ($SCRIPT_DIR)" >&2
    exit 2
fi

# REPO_ROOT: Argument #1 (falls angegeben und gultig), sonst zwei Ebenen ueber
# dem Skript (Standard-Layout: <checkout>/agenten/checks/run-gate.sh).
REPO_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
if [ $# -ge 1 ] && [ -n "${1:-}" ]; then
    REPO_ROOT="$1"
fi
# absolut + normalisiert
if [ ! -d "$REPO_ROOT" ]; then
    echo "FEHLER: REPO_ROOT-Pfad '$1' existiert nicht" >&2
    exit 2
fi
REPO_ROOT="$(CDPATH= cd -- "$REPO_ROOT" && pwd)"
if [ ! -d "$REPO_ROOT/site" ]; then
    echo "FEHLER: $REPO_ROOT enthaelt kein site/ — kein gultiger SuperIntelNex-Checkout" >&2
    exit 2
fi

echo "== QA-Gate: Repo-Root = $REPO_ROOT (Port $PORT)"

# --- Port-Check: nicht hijacken ------------------------------------------
# Probe mit SO_REUSEADDR: eigene Test-Anfragen hinterlassen kurz TIME-Wait-
# Verbindungen; ohne REUSEADDR wuerde bind() dann falsche "belegt" melden,
# waehrend http.server (allow_reuse_address) trotzdem binden koennte.
port_in_use() {
    python3 - "$PORT" <<'PYEOF'
import socket, sys
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
try:
    s.bind(("127.0.0.1", int(sys.argv[1])))
    s.close()
    sys.exit(1)  # Port frei
except OSError:
    s.close()
    sys.exit(0)  # Port belegt
PYEOF
}
if port_in_use; then
    echo "FEHLER: Port $PORT ist bereits belegt — QA_GATE_PORT setzen oder bestehenden Server beenden." >&2
    exit 2
fi

# --- http.server starten ----------------------------------------------------
cd -- "$REPO_ROOT" || exit 2
python3 -m http.server "$PORT" --bind 127.0.0.1 --directory site >>"$LOG" 2>&1 &
SERVER_PID=$!
trap '
  rc=$?
  kill "$SERVER_PID" 2>/dev/null
  wait "$SERVER_PID" 2>/dev/null
  # Bei Fehler den Server-Log lassen (Diagnose), sonst aufraeumen.
  if [ "$rc" -eq 0 ]; then
      rm -f "$LOG"
  else
      echo "== Server-Log: $LOG"
  fi
' EXIT

# --- auf Port warten (max. 15s) -------------------------------------------
i=0
while [ "$i" -lt 150 ]; do
    if ! kill -0 "$SERVER_PID" 2>/dev/null; then
        echo "FEHLER: http.server ist sofort abgestuerzt:" >&2
        cat "$LOG" >&2
        exit 2
    fi
    if port_in_use; then
        break
    fi
    i=$((i + 1))
    sleep 0.1
done
if ! port_in_use; then
    echo "FEHLER: http.server antwortet nicht auf Port $PORT (Timeout 15s)" >&2
    cat "$LOG" >&2
    exit 2
fi
echo "== http.server laeuft (PID $SERVER_PID) auf http://localhost:$PORT"

# --- Gate laufen lassen ------------------------------------------------------
python3 "$GATE" --repo-root "$REPO_ROOT" --port "$PORT"
GATE_EXIT=$?

# trap raeumt den Server auf
echo "== Server PID $SERVER_PID gestoppt, Gate-Exit-Code: $GATE_EXIT"
exit "$GATE_EXIT"
