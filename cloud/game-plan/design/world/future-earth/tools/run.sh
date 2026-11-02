#!/bin/sh
# Rebuild the future Earth map after editing future_earth.json.
# Needs git, node, python3 with numpy and Pillow, and a Chromium (CHROMIUM_PATH, default /opt/pw-browsers/chromium).
set -e
here=$(cd "$(dirname "$0")" && pwd)
out=$(dirname "$here")
export FMG_DIR=${FMG_DIR:-/tmp/fmg}
FMG_COMMIT=52e2f59a9ccdfdaf5832ff0961d6e8ed59ac27fd # FMG v1.154.1, the version this map was made with

if [ ! -d "$FMG_DIR/.git" ]; then
  git init -q "$FMG_DIR"
  git -C "$FMG_DIR" fetch -q --depth 1 https://github.com/Azgaar/Fantasy-Map-Generator.git "$FMG_COMMIT"
  git -C "$FMG_DIR" checkout -q FETCH_HEAD
fi
[ -d "$FMG_DIR/node_modules" ] || (cd "$FMG_DIR" && npm ci --ignore-scripts)
(cd "$FMG_DIR" && exec node node_modules/vite/bin/vite.js --port 5173 --strictPort >/dev/null 2>&1) &
vite=$!
trap 'kill $vite' EXIT
until curl -s -o /dev/null http://localhost:5173/; do sleep 1; done

python3 "$here/make_heightmap.py" "$here/future_earth.json" "$FMG_DIR/public/heightmaps/world.png" "$out/future-earth-heightmap.png"
node "$here/build_map.mjs" "$here/future_earth.json" "$out/future-earth-heightmap.png" "$out"
node "$here/verify_load.mjs" "$out/future-earth.map"
