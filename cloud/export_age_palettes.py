"""Writes docs/ui/age_palettes.json: each Age's colours as hex, for every screen that draws its own colours in code
(the Codex's CodexLooks and tools/codex/draw_looks.py take their inks and frames from here, so the Codex matches the shared screens)."""
import json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "art/blender"))
from ui_ages import SKINS  # noqa: E402

h = lambda c: "#%02X%02X%02X" % tuple(int(round(float(v))) for v in c)
out = {age: {"outline": h(s["ramp"][0]), "well": h(s["ramp"][1]), "shadow": h(s["ramp"][2]), "slot": h(s["ramp"][3]),
             "panel": h(s["ramp"][4]), "highlight": h(s["ramp"][5]), "rim": h(s["rim"]), "hot": h(s["hot"]), "metal": h(s["metal"]),
             "grain": s["grain"], "frame": s["frame"], "corner": s["corner"]} for age, s in SKINS.items()}
dst = Path(__file__).resolve().parents[2] / "docs/ui/age_palettes.json"
dst.write_text(json.dumps(out, indent=1) + "\n")
print(dst)
