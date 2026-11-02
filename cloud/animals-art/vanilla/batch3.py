"""Preview table for the Bestiary and Wyrmlore page (build_page.py --table=batch3)."""
import wyrm
from vanilla import BESTIARY


def preview(tex_root):
    return {**BESTIARY, **wyrm.preview(tex_root)}
