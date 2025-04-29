#!/usr/bin/env bash
set -e

# 1) Clean old artifacts
rm -rf build dist PsychotherapieAntrag.spec

# 2) Build with PyInstaller
pyinstaller \
  --name PsychotherapieAntrag \
  --onefile \
  --windowed \
  --add-data "functions:functions" \
  --exclude-module modulegraph \
  --exclude-module PyInstaller \
  app.py