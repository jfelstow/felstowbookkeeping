#!/usr/bin/env bash
# Fully-background start-at-login via a macOS LaunchAgent (no Terminal
# window). Requires granting permissions to the Python interpreter itself —
# the script prints the exact path to add.
#
#   ./autostart.sh install     start at login (and start now)
#   ./autostart.sh uninstall   stop and remove
#   ./autostart.sh status      is it running? show recent log lines
set -euo pipefail
cd "$(dirname "$0")"

LABEL="com.felstow.dictation"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
LOG="$HOME/Library/Logs/dictation.log"

if [ "$(uname)" != "Darwin" ]; then
    echo "This installer is macOS-only. On Linux, use a systemd user service."
    exit 1
fi

case "${1:-}" in
install)
    if [ ! -d .venv ]; then
        echo "Run ./run.sh once first so the environment exists."
        exit 1
    fi
    REAL_PY="$(./.venv/bin/python -c 'import os,sys;print(os.path.realpath(sys.executable))')"
    mkdir -p "$HOME/Library/LaunchAgents" "$HOME/Library/Logs"
    cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key><string>$LABEL</string>
    <key>ProgramArguments</key>
    <array>
        <string>$PWD/.venv/bin/python</string>
        <string>$PWD/dictate.py</string>
    </array>
    <key>RunAtLoad</key><true/>
    <key>KeepAlive</key><dict><key>SuccessfulExit</key><false/></dict>
    <key>StandardOutPath</key><string>$LOG</string>
    <key>StandardErrorPath</key><string>$LOG</string>
</dict>
</plist>
EOF
    launchctl bootout "gui/$(id -u)" "$PLIST" 2>/dev/null || true
    launchctl bootstrap "gui/$(id -u)" "$PLIST"
    cat <<EOF

Installed. Dictation now starts at login and runs in the background.

IMPORTANT - one-time permission setup, because it no longer runs inside
Terminal, macOS needs you to trust the Python interpreter itself:

  System Settings > Privacy & Security >
    - Accessibility      -> '+' -> Cmd+Shift+G -> paste the path below
    - Input Monitoring   -> same
    - Microphone         -> approve the popup the first time you dictate

  Path to add:  $REAL_PY

Log file: $LOG   (check it if dictation seems dead)
To stop: ./autostart.sh uninstall
EOF
    ;;
uninstall)
    launchctl bootout "gui/$(id -u)" "$PLIST" 2>/dev/null || true
    rm -f "$PLIST"
    echo "Removed. Dictation no longer starts at login."
    ;;
status)
    if launchctl print "gui/$(id -u)/$LABEL" >/dev/null 2>&1; then
        echo "Running (LaunchAgent loaded)."
    else
        echo "Not running."
    fi
    [ -f "$LOG" ] && { echo "--- last log lines ---"; tail -n 10 "$LOG"; }
    ;;
*)
    echo "Usage: ./autostart.sh install | uninstall | status"
    exit 1
    ;;
esac
