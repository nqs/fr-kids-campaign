#!/usr/bin/env python3
"""Build a session adventure PDF from its three markdown files.

Reusable across all sessions. The session folder must contain:
  <slug>-1-adventure.md
  <slug>-2-combat-tracker.md
  <slug>-3-player-handouts.md
  images.json

Output goes to `<session-folder>/<slug>.pdf`.

Usage:
  python scripts/build_pdf.py                  # latest session folder
  python scripts/build_pdf.py 3                # sessions/session 3
  python scripts/build_pdf.py "sessions/session 3"
  python scripts/build_pdf.py 3 --title "Custom Title"
  python scripts/build_pdf.py 3 --out /tmp/preview.pdf
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Make the scripts/ dir importable so `md_to_pdf` resolves regardless of cwd.
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from md_to_pdf import build_pdf, strip_frontmatter  # noqa: E402

REPO_ROOT = _HERE.parent
SESSIONS_DIR = REPO_ROOT / "sessions"


def _session_number(folder: Path) -> int:
    m = re.search(r"(\d+)", folder.name)
    return int(m.group(1)) if m else -1


def resolve_session_folder(arg: str | None) -> Path:
    """Resolve a CLI arg to a concrete session folder.

    Accepts: a path, a bare session number, or None (latest).
    """
    if arg is None:
        candidates = [p for p in SESSIONS_DIR.glob("session *") if p.is_dir()]
        if not candidates:
            raise SystemExit(f"no session folders under {SESSIONS_DIR}")
        return max(candidates, key=_session_number)
    arg_path = Path(arg)
    if arg_path.is_dir():
        return arg_path.resolve()
    if arg.isdigit():
        candidate = SESSIONS_DIR / f"session {arg}"
        if candidate.is_dir():
            return candidate
    raise SystemExit(f"could not resolve session folder for {arg!r}")


def find_slug(folder: Path) -> str:
    """Infer the adventure slug from `<slug>-1-adventure.md` in the folder."""
    matches = sorted(folder.glob("*-1-adventure.md"))
    if not matches:
        raise SystemExit(f"no <slug>-1-adventure.md in {folder}")
    if len(matches) > 1:
        names = ", ".join(m.name for m in matches)
        raise SystemExit(f"multiple adventure files in {folder}: {names}")
    return matches[0].stem.removesuffix("-1-adventure")


def title_from_md(adventure_md: Path, slug: str) -> str:
    """Pull the PDF title from the adventure file's frontmatter, or titlecase the slug."""
    text = adventure_md.read_text()
    _body, meta = strip_frontmatter(text)
    if meta.get("adventure"):
        return meta["adventure"].strip()
    return " ".join(word.capitalize() for word in slug.split("-"))


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "session", nargs="?",
        help="session folder path, bare session number, or omitted for latest",
    )
    parser.add_argument("--title", help="override PDF title")
    parser.add_argument("--out", help="override output PDF path")
    args = parser.parse_args()

    folder = resolve_session_folder(args.session)
    slug = find_slug(folder)
    md_files = [
        folder / f"{slug}-1-adventure.md",
        folder / f"{slug}-2-combat-tracker.md",
        folder / f"{slug}-3-player-handouts.md",
    ]
    missing = [str(p) for p in md_files if not p.exists()]
    if missing:
        raise SystemExit("missing markdown files: " + ", ".join(missing))
    images_json = folder / "images.json"
    if not images_json.exists():
        raise SystemExit(f"missing {images_json}")

    out_path = Path(args.out) if args.out else folder / f"{slug}.pdf"
    title = args.title or title_from_md(md_files[0], slug)

    print(f"folder: {folder}")
    print(f"slug:   {slug}")
    print(f"title:  {title}")
    print(f"out:    {out_path}")
    build_pdf(md_files, images_json, out_path, title=title)
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
