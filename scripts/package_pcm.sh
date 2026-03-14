#!/usr/bin/env bash
set -e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PLUGIN_DIR="$ROOT/plugin"

OUT="$ROOT/coilforge_kicad.zip"

cd "$PLUGIN_DIR"

rm -f "$OUT"

zip -r "$OUT" metadata.json plugins resources \
    -x "*.DS_Store" \
    -x "__MACOSX/*"

echo "PCM package created:"
echo "$OUT"