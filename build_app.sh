#!/usr/bin/env bash
set -e

# 1) Clean old artifacts
rm -rf build dist PsychotherapieAntrag.spec

# 2) Bundle into one GUI‐mode binary
pyinstaller \
  --name PsychotherapieAntrag \
  --onefile \
  --windowed \                    # on Windows use --noconsole if you don’t want a cmd window
  --icon=MyIcon.icns \            # your .icns (mac) or .ico (win)
  --add-data "functions:functions" \
  app.py