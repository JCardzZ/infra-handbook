#!/usr/bin/env bash
# Render every diagrams/*.py file to SVG in docs/assets/diagrams/.
# Requires Graphviz (brew install graphviz) and the Python deps in requirements.txt.
# Run from anywhere: the script switches to the repo root.
set -euo pipefail

cd "$(dirname "$0")/.."

if ! command -v dot >/dev/null 2>&1; then
  echo "Graphviz 'dot' not found. Install it with: brew install graphviz" >&2
  exit 1
fi

export DIAGRAMS_OUT="docs/assets/diagrams"
mkdir -p "$DIAGRAMS_OUT"

shopt -s nullglob
sources=(diagrams/[!_]*.py)  # files starting with _ are shared modules
if [ ${#sources[@]} -eq 0 ]; then
  echo "No diagram sources in diagrams/." >&2
  exit 1
fi

for src in "${sources[@]}"; do
  echo "Rendering $src"
  python3 "$src"
done

# Inline the icons and size the SVGs in px (see scripts/postprocess_svg.py).
python3 scripts/postprocess_svg.py "$DIAGRAMS_OUT"/*.svg
