#!/usr/bin/env python3
"""Extract a PDF to Markdown using pymupdf4llm.

Writes:
  <out_dir>/full.md            — single concatenated markdown
  <out_dir>/pages/page-NNNN.md — one file per page (for chapter splitting later)
  <out_dir>/images/            — extracted figures/maps

Usage:
  python scripts/extract_pdf.py <pdf_path> <out_dir>
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import pymupdf4llm


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 2

    pdf_path = Path(sys.argv[1]).resolve()
    out_dir = Path(sys.argv[2]).resolve()
    if not pdf_path.exists():
        print(f"error: {pdf_path} does not exist", file=sys.stderr)
        return 1

    pages_dir = out_dir / "pages"
    images_dir = out_dir / "images"
    pages_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)

    print(f"extracting {pdf_path.name} -> {out_dir}")
    t0 = time.time()

    # page_chunks=True returns a list of dicts, one per page, with 'text' and metadata.
    # write_images=True extracts figures into image_path.
    chunks = pymupdf4llm.to_markdown(
        str(pdf_path),
        page_chunks=True,
        write_images=True,
        image_path=str(images_dir),
        image_format="png",
        dpi=150,
        show_progress=True,
    )

    full_md_parts: list[str] = []
    for i, chunk in enumerate(chunks, start=1):
        text = chunk.get("text", "") if isinstance(chunk, dict) else str(chunk)
        page_file = pages_dir / f"page-{i:04d}.md"
        page_file.write_text(text, encoding="utf-8")
        full_md_parts.append(f"<!-- page {i} -->\n\n{text}\n")

    full_md = "\n".join(full_md_parts)
    (out_dir / "full.md").write_text(full_md, encoding="utf-8")

    elapsed = time.time() - t0
    print(
        f"done in {elapsed:.1f}s · {len(chunks)} pages · "
        f"{len(full_md):,} chars · "
        f"{sum(1 for _ in images_dir.iterdir())} images"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
