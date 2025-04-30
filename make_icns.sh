#!/usr/bin/env bash
set -e

SRC="icon.png"
ICON_NAME="MyIcon"
ICONSET="${ICON_NAME}.iconset"

# 1) Clean out any old iconset / icns
rm -rf "$ICONSET" "${ICON_NAME}.icns"

# 2) Make the iconset folder
mkdir "$ICONSET"

# 3) For each required size, down‐sample your PNG
for SIZE in 16 32 128 256 512; do
  # @1x
  sips -z $SIZE $SIZE "$SRC" --out "$ICONSET/icon_${SIZE}x${SIZE}.png"
  # @2x
  sips -z $((SIZE*2)) $((SIZE*2)) "$SRC" \
       --out "$ICONSET/icon_${SIZE}x${SIZE}@2x.png"
done

# 4) Build the .icns
iconutil -c icns "$ICONSET" --output "${ICON_NAME}.icns"

echo "✅ Generated ${ICON_NAME}.icns"