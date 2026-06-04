#!/usr/bin/env python3
"""Build a GitHub-wiki staging tree from the repo's Markdown content.

The repo is the single source of truth; the GitHub Wiki is generated from it by
`.github/workflows/sync-wiki.yml`, which runs this script and pushes the
resulting ./wiki/ directory into the repo's *.wiki.git. You only ever edit the
main repo.

Transforms applied while staging:
  * Path/file names: spaces -> hyphens (wiki page URLs are hyphenated), so
    `sessions/session 3/session 3 - log.md` -> `sessions/session-3/session-3-log.md`.
  * Internal Markdown links: URL-decoded, space->hyphen normalized, and the
    trailing `.md` stripped (wiki page URLs carry no extension). `#anchors`
    are preserved unchanged.
  * Links into `references/` or to `.pdf` files: rewritten to absolute main-repo
    blob URLs — those assets stay in the main repo, not the wiki.
  * Remote `http(s)`/`mailto:` links and images: left untouched (all inline
    images are already remote URLs).

Only Markdown pages are published; binaries (pdf/m4a/jpg) and the bulky
`references/_raw` trees stay in the main repo.
"""
import os
import re
import shutil
from urllib.parse import quote, unquote

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "wiki")

REPO_SLUG = os.environ.get("GITHUB_REPOSITORY", "nqs/fr-kids-campaign")
SOURCE_BRANCH = os.environ.get("WIKI_SOURCE_BRANCH", "main")
BLOB = f"https://github.com/{REPO_SLUG}/blob/{SOURCE_BRANCH}"

ROOT_FILES = ["Home.md", "_Sidebar.md", "AGENTS.md", "dnd-adventure-generator.md"]
CONTENT_DIRS = ["campaign", "sessions"]

# Repo-relative paths that should resolve to the main repo, not a wiki page.
EXTERNAL_EXTS = (".pdf", ".m4a", ".txt", ".png", ".jpg", ".jpeg")

MD_LINK = re.compile(r"(!?)\[([^\]]*)\]\(\s*<?([^>\s)]+)>?\s*\)")


def norm_path(path):
    """Replace spaces with hyphens in each path segment, collapsing runs."""
    segs = []
    for seg in path.split("/"):
        seg = seg.replace(" ", "-")
        seg = re.sub(r"-{2,}", "-", seg)
        segs.append(seg)
    return "/".join(segs)


def classify(repo_rel):
    """Return 'external' if this repo path is a binary/reference asset."""
    rr = repo_rel.replace("\\", "/")
    if rr.startswith("references/"):
        return "external"
    if os.path.splitext(rr)[1].lower() in EXTERNAL_EXTS:
        return "external"
    return "page"


def rewrite_target(target, src_dir_repo):
    # Leave pure anchors, absolute URLs, and protocol links alone.
    if target.startswith("#") or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", target) or target.startswith("mailto:"):
        return None

    path, _, anchor = target.partition("#")
    anchor = f"#{anchor}" if anchor else ""
    decoded = unquote(path)

    # Resolve to a repo-relative path purely to classify it.
    abs_path = os.path.normpath(os.path.join(REPO, src_dir_repo, decoded))
    repo_rel = os.path.relpath(abs_path, REPO).replace("\\", "/")

    # Anything outside the repo, or not a real path, is left untouched.
    if repo_rel.startswith(".."):
        return None

    if classify(repo_rel) == "external":
        return f"{BLOB}/{quote(repo_rel)}{anchor}"

    # Internal page link: normalize spaces->hyphens, strip trailing .md,
    # preserve the relative form (../, ./) of the original target.
    normalized = norm_path(decoded)
    if normalized.lower().endswith(".md"):
        normalized = normalized[: -len(".md")]
    return f"{normalized}{anchor}"


def transform_links(text, src_repo_rel):
    src_dir_repo = os.path.dirname(src_repo_rel)

    def repl(m):
        bang, label, target = m.group(1), m.group(2), m.group(3)
        new_target = rewrite_target(target, src_dir_repo)
        if new_target is None:
            return m.group(0)
        return f"{bang}[{label}]({new_target})"

    return MD_LINK.sub(repl, text)


def emit(src_repo_rel):
    src_abs = os.path.join(REPO, src_repo_rel)
    with open(src_abs, encoding="utf-8") as fh:
        content = fh.read()
    content = transform_links(content, src_repo_rel)

    dst_rel = norm_path(src_repo_rel)
    dst_abs = os.path.join(OUT, dst_rel)
    os.makedirs(os.path.dirname(dst_abs) or OUT, exist_ok=True)
    with open(dst_abs, "w", encoding="utf-8") as fh:
        fh.write(content)
    return dst_rel


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)

    emitted = []
    for name in ROOT_FILES:
        if os.path.exists(os.path.join(REPO, name)):
            emitted.append(emit(name))

    for d in CONTENT_DIRS:
        for dirpath, _, filenames in os.walk(os.path.join(REPO, d)):
            for fn in filenames:
                # Skip raw machine transcripts (e.g. Session3.m4a.md); they stay
                # in the main repo and don't belong in the curated wiki.
                if fn.endswith(".md") and not fn.endswith(".m4a.md"):
                    rel = os.path.relpath(os.path.join(dirpath, fn), REPO)
                    emitted.append(emit(rel))

    for e in sorted(emitted):
        print("staged:", e)
    print(f"\n{len(emitted)} page(s) staged into {os.path.relpath(OUT, REPO)}/")


if __name__ == "__main__":
    main()
