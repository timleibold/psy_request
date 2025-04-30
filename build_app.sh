#!/usr/bin/env bash

set -e

# 0) Install Python dependencies
pip install -r requirements.txt

# 1) Clean old artifacts
rm -rf build dist PsychotherapieAntrag.spec

# 2) Bundle into one GUI‐mode binary
pyinstaller \
  --name PsychotherapieAntrag \
  --onefile \
  --windowed \
  --icon=MyIcon.icns \
  --add-data "functions:functions" \
  --collect-all streamlit \
  "app.py"

# to run this type in Terminal: chmod +x build_app.sh
# then: ./build_app.sh