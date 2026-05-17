#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../../.." && pwd)"
OUT_DIR="$ROOT_DIR/Bao_Cao/sample_images/chapter2_bw_preview"
PUPPETEER_CONFIG="$ROOT_DIR/Bao_Cao/diagrams/chapter2/puppeteer-config.json"
CSS_FILE="$SCRIPT_DIR/preview.css"

mkdir -p "$OUT_DIR"

for src in "$SCRIPT_DIR"/hinh_2_*.mmd; do
  name="$(basename "$src" .mmd)"
  mmdc -i "$src" -o "$OUT_DIR/$name.png" -p "$PUPPETEER_CONFIG" -C "$CSS_FILE" -b white -s 3
done

echo "Rendered previews to $OUT_DIR"
