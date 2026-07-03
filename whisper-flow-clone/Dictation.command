#!/usr/bin/env bash
# Double-clickable launcher. Opens in Terminal, which already has the
# microphone/accessibility permissions, and starts dictation.
# To start it at login: System Settings > General > Login Items >
# "Open at Login" > + > pick this file.
cd "$(dirname "$0")"
exec ./run.sh
