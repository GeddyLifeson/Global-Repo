"""One GUI skin per Age (docs/ui/UI_SCHEMA.md). A screen is drawn in the skin of the Age its block or mod is unlocked in
(content/tech_ages.json); shared and vanilla screens use the earliest, Age I. Panels stay light because the game draws
dark labels on them. Codex looks (Codex README 4a) set the materials: bark scroll, leather case, vellum, printed
volume, brass page drum, green reader, phone glass, Rodos tablet."""
import json, os
from pathlib import Path

import numpy as np

AGE_FILE = Path(__file__).resolve().parents[3] / "content" / "tech_ages.json"
ORDER = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "RODOS"]


def rgb(*cols):
    return np.array(cols, np.float32)


# ramp rows: outline, slot shadow, panel shadow, slot floor, panel face, highlight (matches gui_lane.UI_L)
SKINS = {
    "I": dict(ramp=rgb((34, 24, 16), (52, 38, 26), (110, 84, 56), (74, 56, 38), (178, 148, 106), (216, 190, 144)),
              rim=(196, 150, 60), hot=(222, 170, 70), metal=(150, 130, 96), grain="bark", frame="stitch", corner="peg"),
    "II": dict(ramp=rgb((28, 18, 14), (46, 30, 22), (96, 62, 40), (66, 44, 30), (170, 120, 78), (208, 158, 106)),
               rim=(196, 108, 64), hot=(236, 146, 84), metal=(190, 106, 60), grain="leather", frame="copper", corner="cap"),
    "III": dict(ramp=rgb((40, 30, 22), (58, 44, 34), (150, 134, 104), (96, 78, 58), (228, 214, 178), (248, 240, 214)),
                rim=(170, 124, 62), hot=(176, 48, 40), metal=(170, 124, 62), grain="vellum", frame="rubric", corner="rubric"),
    "IV": dict(ramp=rgb((30, 22, 16), (46, 34, 24), (120, 96, 66), (80, 62, 44), (208, 186, 142), (236, 218, 174)),
               rim=(206, 164, 62), hot=(236, 196, 80), metal=(206, 164, 62), grain="paper", frame="tooled", corner="clasp"),
    "V": dict(ramp=rgb((24, 26, 18), (38, 42, 28), (96, 100, 64), (60, 66, 42), (166, 168, 114), (208, 208, 152)),
              rim=(200, 164, 62), hot=(238, 150, 48), metal=(196, 160, 60), grain="turned", frame="brass", corner="rivet"),
    "VI": dict(ramp=rgb((10, 28, 16), (14, 38, 22), (84, 120, 84), (28, 60, 36), (150, 184, 138), (192, 222, 172)),
               rim=(92, 220, 110), hot=(150, 255, 150), metal=(60, 130, 74), grain="scan", frame="casing", corner="led"),
    "VII": dict(ramp=rgb((30, 42, 58), (44, 58, 78), (150, 166, 186), (72, 90, 114), (216, 228, 240), (248, 251, 255)),
                rim=(80, 170, 230), hot=(96, 190, 245), metal=(120, 150, 184), grain="glass", frame="hair", corner="none"),
    "VIII": dict(ramp=rgb((28, 22, 52), (40, 32, 72), (150, 138, 190), (66, 54, 104), (226, 220, 242), (250, 247, 255)),
                 rim=(70, 230, 205), hot=(140, 255, 225), metal=(150, 134, 200), grain="hex", frame="lightline", corner="node"),
    "RODOS": dict(ramp=rgb((36, 40, 52), (52, 58, 76), (170, 176, 190), (84, 92, 116), (243, 245, 247), (255, 255, 255)),
                  rim=(60, 100, 220), hot=(70, 112, 236), metal=(110, 130, 190), grain="none", frame="hair", corner="none"),
}
for s in SKINS.values():
    for k in ("rim", "hot", "metal"):
        s[k] = np.array(s[k], np.float32)


def load_ages():
    d = json.loads(AGE_FILE.read_text(encoding="utf-8"))
    return {ns: ("I" if a == "TELLING" else a) for ns, a in d["namespaces"].items()}


NS_AGE = load_ages()


def age_of(ns):
    """Mods outside tech_ages.json (vanilla, quality of life, libraries) share the earliest look."""
    return NS_AGE.get(ns, "I")


def skin_of(ns):
    """The namespace's own Age, or DIAITHIR_FORCE_AGE when the shared-screen packs are built (one run per Age)."""
    return SKINS[os.environ.get("DIAITHIR_FORCE_AGE") or age_of(ns)]
