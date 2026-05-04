"""Build the Session 002 — The Second Cleft adventure PDF.

Thin entry point. Concatenates the three markdown files in order
(adventure → combat tracker → player handouts) and renders via md_to_pdf.
"""
from pathlib import Path

from md_to_pdf import build_pdf

HERE = Path(__file__).parent
SLUG = "the-second-cleft"
OUT = HERE / f"{SLUG}.pdf"

MD_FILES = [
    HERE / f"{SLUG}-1-adventure.md",
    HERE / f"{SLUG}-2-combat-tracker.md",
    HERE / f"{SLUG}-3-player-handouts.md",
]
IMAGES_JSON = HERE / "images.json"

if __name__ == "__main__":
    out = build_pdf(MD_FILES, IMAGES_JSON, OUT, title="The Second Cleft")
    print(f"Wrote {out}")
