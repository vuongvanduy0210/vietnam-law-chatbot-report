#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPORT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
OUT_DIR="$REPORT_DIR/sample_images"
PUPPETEER_CONFIG="$SCRIPT_DIR/puppeteer-config.json"
CSS_FILE="$SCRIPT_DIR/../chapter2_mermaid_bold/mermaid_bold.css"

if ! command -v mmdc >/dev/null 2>&1; then
  echo "mmdc was not found."
  echo "Install Mermaid CLI first, then rerun this script:"
  echo "  npm install -g @mermaid-js/mermaid-cli"
  exit 1
fi

mkdir -p "$OUT_DIR"

for src in "$SCRIPT_DIR"/hinh_2_*.mmd; do
  name="$(basename "$src" .mmd)"
  echo "Rendering $name.png"
  mmdc \
    -i "$src" \
    -o "$OUT_DIR/$name.png" \
    -p "$PUPPETEER_CONFIG" \
    -C "$CSS_FILE" \
    -b white \
    -s 3
done

echo "Done. PNG files written to: $OUT_DIR"
