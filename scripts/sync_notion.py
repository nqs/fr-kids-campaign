#!/usr/bin/env python3
"""Push changed repo Markdown files to their live Notion pages.

The repo is the single source of truth; this script is the inverse of
build_wiki.py — instead of staging a wiki tree, it talks to the Notion REST
API directly and replaces a target page's content with a hand-converted
rendering of the source Markdown. Internal links that target another mapped
page become Notion page mentions (matching how the workspace was migrated by
hand); everything else (references/, binaries, unmapped pages) falls back to
an absolute GitHub URL.

Mapping lives in scripts/notion_sync_map.json (repo-relative path -> Notion
page ID). Files not present in the map are skipped with a warning rather than
failing the run — the map only covers the pages confirmed during the initial
migration; extend it as more pages are added.

This is a small, line-based converter for this repo's actual Markdown subset
(ATX headings, fenced code, GFM pipe tables, GitHub-alert blockquotes, flat
bullet/numbered lists, standalone images, basic inline emphasis/links). It is
not a general CommonMark implementation. No third-party dependencies, to
match the rest of scripts/ (stdlib only).

Usage:
    NOTION_TOKEN=secret_xxx scripts/sync_notion.py <file> [<file> ...]
    NOTION_TOKEN=secret_xxx scripts/sync_notion.py --all
"""
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from urllib.parse import quote, unquote

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAP_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "notion_sync_map.json")

REPO_SLUG = os.environ.get("GITHUB_REPOSITORY", "nqs/fr-kids-campaign")
SOURCE_BRANCH = os.environ.get("WIKI_SOURCE_BRANCH", "main")
BLOB = f"https://github.com/{REPO_SLUG}/blob/{SOURCE_BRANCH}"
RAW = f"https://raw.githubusercontent.com/{REPO_SLUG}/{SOURCE_BRANCH}"

NOTION_API = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"
NOTION_TOKEN = os.environ.get("NOTION_TOKEN")

IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".gif")

CODE_LANGS = {
    "python": "python", "py": "python", "json": "json", "bash": "bash",
    "sh": "shell", "shell": "shell", "yaml": "yaml", "yml": "yaml",
    "markdown": "markdown", "md": "markdown", "javascript": "javascript",
    "js": "javascript", "html": "html", "css": "css", "": "plain text",
}

MAX_RICH_TEXT = 2000
MAX_CHILDREN_PER_CALL = 100
RATE_LIMIT_SLEEP = 0.34  # Notion's documented ~3 req/s budget

ATX_RE = re.compile(r"^(#{1,6})\s+(.*)$")
IMG_LINE_RE = re.compile(r"^!\[([^\]]*)\]\(\s*<?([^>\s)]+)>?\s*\)\s*$")
BULLET_RE = re.compile(r"^[ \t]*[-*+]\s+(.*)$")
NUM_RE = re.compile(r"^[ \t]*\d+\.\s+(.*)$")
QUOTE_RE = re.compile(r"^>\s?(.*)$")
HR_RE = re.compile(r"^(-{3,}|\*{3,}|_{3,})$")
TABLE_SEP_RE = re.compile(r"^\s*\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)*\|?\s*$")
FENCE_RE = re.compile(r"^```(\w*)\s*$")
LINK_RE = re.compile(r"(!?)\[([^\]]*)\]\(\s*<?([^>\s)]+)>?\s*\)")
INLINE_RE = re.compile(
    r"(?P<code>`[^`]+`)"
    r"|(?P<bold>\*\*[^*]+\*\*|__[^_]+__)"
    r"|(?P<strike>~~[^~]+~~)"
    r"|(?P<italic>\*[^*]+\*|_[^_]+_)"
    r"|(?P<link>!?\[[^\]]*\]\([^)]+\))"
)


# --- Notion API plumbing -----------------------------------------------

def notion_request(method, path, body=None, retries=5):
    url = f"{NOTION_API}{path}"
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {NOTION_TOKEN}")
    req.add_header("Notion-Version", NOTION_VERSION)
    req.add_header("Content-Type", "application/json")
    last_err = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", "replace")
            if e.code == 429 or e.code >= 500:
                wait = float(e.headers.get("Retry-After", 1)) if e.code == 429 else 2 ** attempt
                time.sleep(wait)
                last_err = RuntimeError(f"Notion API {method} {path} failed: {e.code} {err_body}")
                continue
            raise RuntimeError(f"Notion API {method} {path} failed: {e.code} {err_body}")
    raise last_err


def clear_page(page_id):
    cursor = None
    ids = []
    while True:
        qs = f"?start_cursor={cursor}" if cursor else ""
        res = notion_request("GET", f"/blocks/{page_id}/children{qs}")
        ids.extend(b["id"] for b in res["results"])
        if not res.get("has_more"):
            break
        cursor = res["next_cursor"]
    for bid in ids:
        notion_request("PATCH", f"/blocks/{bid}", {"archived": True})
        time.sleep(RATE_LIMIT_SLEEP)


def append_blocks(page_id, blocks):
    for i in range(0, len(blocks), MAX_CHILDREN_PER_CALL):
        chunk = blocks[i:i + MAX_CHILDREN_PER_CALL]
        notion_request("POST", f"/blocks/{page_id}/children", {"children": chunk})
        time.sleep(RATE_LIMIT_SLEEP)


# --- Link / image resolution -------------------------------------------

def split_target(target):
    path, _, anchor = target.partition("#")
    return path, (f"#{anchor}" if anchor else "")


def resolve_internal(path_part, anchor, src_dir_repo, sync_map):
    """Resolve a relative repo-internal link.

    Returns ('mention', page_id) if the target is a mapped Notion page,
    ('url', href) for a GitHub fallback, or None if the link should be left
    untouched (outside the repo).
    """
    decoded = unquote(path_part)
    abs_path = os.path.normpath(os.path.join(REPO, src_dir_repo, decoded))
    repo_rel = os.path.relpath(abs_path, REPO).replace("\\", "/")
    if repo_rel.startswith(".."):
        return None
    if repo_rel in sync_map:
        return "mention", sync_map[repo_rel]
    ext = os.path.splitext(repo_rel)[1].lower()
    if ext in IMAGE_EXTS:
        return "url", f"{RAW}/{quote(repo_rel)}{anchor}"
    return "url", f"{BLOB}/{quote(repo_rel)}{anchor}"


def resolve_image_url(url, src_dir_repo):
    if not url or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", url):
        return url
    decoded = unquote(url)
    abs_path = os.path.normpath(os.path.join(REPO, src_dir_repo, decoded))
    repo_rel = os.path.relpath(abs_path, REPO).replace("\\", "/")
    return f"{RAW}/{quote(repo_rel)}"


# --- Rich text -----------------------------------------------------------

def chunk_text(s):
    return [s[i:i + MAX_RICH_TEXT] for i in range(0, len(s), MAX_RICH_TEXT)] or [""]


def text_rt(s, annotations=None, link=None):
    out = []
    for piece in chunk_text(s):
        rt = {"type": "text", "text": {"content": piece}}
        if link:
            rt["text"]["link"] = {"url": link}
        if annotations:
            rt["annotations"] = annotations
        out.append(rt)
    return out


def mention_rt(page_id):
    return [{"type": "mention", "mention": {"type": "page", "page": {"id": page_id}}}]


def inline_to_rich_text(text, src_repo_rel, sync_map):
    src_dir = os.path.dirname(src_repo_rel)
    rich = []
    pos = 0
    for m in INLINE_RE.finditer(text):
        if m.start() > pos:
            rich.extend(text_rt(text[pos:m.start()]))
        if m.group("code"):
            rich.extend(text_rt(m.group("code")[1:-1], {"code": True}))
        elif m.group("bold"):
            rich.extend(text_rt(m.group("bold")[2:-2], {"bold": True}))
        elif m.group("strike"):
            rich.extend(text_rt(m.group("strike")[2:-2], {"strikethrough": True}))
        elif m.group("italic"):
            rich.extend(text_rt(m.group("italic")[1:-1], {"italic": True}))
        elif m.group("link"):
            link_m = LINK_RE.match(m.group("link"))
            _bang, label, target = link_m.groups()
            path_part, anchor = split_target(target)
            if not path_part or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", path_part) or path_part.startswith("mailto:"):
                rich.extend(text_rt(label or target, link=target))
            else:
                resolved = resolve_internal(path_part, anchor, src_dir, sync_map)
                if resolved is None:
                    rich.extend(text_rt(label or target, link=target))
                elif resolved[0] == "mention":
                    rich.extend(mention_rt(resolved[1]))
                else:
                    rich.extend(text_rt(label or target, link=resolved[1]))
        pos = m.end()
    if pos < len(text):
        rich.extend(text_rt(text[pos:]))
    return rich or text_rt("")


# --- Block builders --------------------------------------------------------

def paragraph_block(text, src_repo_rel, sync_map):
    return {"object": "block", "type": "paragraph",
            "paragraph": {"rich_text": inline_to_rich_text(text, src_repo_rel, sync_map)}}


def heading_block(level, text, src_repo_rel, sync_map):
    key = f"heading_{min(level, 3)}"
    return {"object": "block", "type": key,
            key: {"rich_text": inline_to_rich_text(text, src_repo_rel, sync_map)}}


def list_block(kind, text, src_repo_rel, sync_map):
    return {"object": "block", "type": kind,
            kind: {"rich_text": inline_to_rich_text(text, src_repo_rel, sync_map)}}


def quote_block(text, src_repo_rel, sync_map):
    return {"object": "block", "type": "quote",
            "quote": {"rich_text": inline_to_rich_text(text, src_repo_rel, sync_map)}}


def code_block(code, lang):
    lang = CODE_LANGS.get(lang.lower(), "plain text")
    return {"object": "block", "type": "code",
            "code": {"rich_text": text_rt(code), "language": lang}}


def divider_block():
    return {"object": "block", "type": "divider", "divider": {}}


def image_block(url):
    return {"object": "block", "type": "image",
            "image": {"type": "external", "external": {"url": url}}}


def table_row_block(cells, src_repo_rel, sync_map):
    return {"object": "block", "type": "table_row",
            "table_row": {"cells": [inline_to_rich_text(c.strip(), src_repo_rel, sync_map) for c in cells]}}


# --- Markdown -> blocks ------------------------------------------------

def markdown_to_blocks(text, src_repo_rel, sync_map):
    src_dir = os.path.dirname(src_repo_rel)
    lines = text.split("\n")
    blocks = []
    n = len(lines)
    i = 0
    quote_buf = []

    def flush_quote():
        if quote_buf:
            blocks.append(quote_block("\n".join(quote_buf), src_repo_rel, sync_map))
            quote_buf.clear()

    while i < n:
        line = lines[i]

        if line.strip() == "":
            flush_quote()
            i += 1
            continue

        fence_m = FENCE_RE.match(line.strip())
        if fence_m:
            flush_quote()
            lang = fence_m.group(1)
            code_lines = []
            i += 1
            while i < n and lines[i].strip() != "```":
                code_lines.append(lines[i])
                i += 1
            i += 1  # closing fence
            blocks.append(code_block("\n".join(code_lines), lang))
            continue

        qm = QUOTE_RE.match(line)
        if qm:
            quote_buf.append(qm.group(1))
            i += 1
            continue
        flush_quote()

        img_m = IMG_LINE_RE.match(line.strip())
        if img_m:
            blocks.append(image_block(resolve_image_url(img_m.group(2), src_dir)))
            i += 1
            continue

        h_m = ATX_RE.match(line)
        if h_m:
            blocks.append(heading_block(len(h_m.group(1)), h_m.group(2), src_repo_rel, sync_map))
            i += 1
            continue

        if HR_RE.match(line.strip()):
            blocks.append(divider_block())
            i += 1
            continue

        if "|" in line and i + 1 < n and TABLE_SEP_RE.match(lines[i + 1]):
            rows = [line.strip().strip("|").split("|")]
            i += 2
            while i < n and "|" in lines[i] and lines[i].strip():
                rows.append(lines[i].strip().strip("|").split("|"))
                i += 1
            width = max(len(r) for r in rows)
            rows = [r + [""] * (width - len(r)) for r in rows]
            blocks.append({
                "object": "block", "type": "table",
                "table": {
                    "table_width": width,
                    "has_column_header": True,
                    "has_row_header": False,
                    "children": [table_row_block(r, src_repo_rel, sync_map) for r in rows],
                },
            })
            continue

        b_m = BULLET_RE.match(line)
        if b_m:
            blocks.append(list_block("bulleted_list_item", b_m.group(1), src_repo_rel, sync_map))
            i += 1
            continue

        num_m = NUM_RE.match(line)
        if num_m:
            blocks.append(list_block("numbered_list_item", num_m.group(1), src_repo_rel, sync_map))
            i += 1
            continue

        para_lines = [line]
        i += 1
        while i < n and lines[i].strip() != "" and not (
            ATX_RE.match(lines[i]) or BULLET_RE.match(lines[i]) or NUM_RE.match(lines[i])
            or QUOTE_RE.match(lines[i]) or IMG_LINE_RE.match(lines[i].strip())
            or FENCE_RE.match(lines[i].strip()) or HR_RE.match(lines[i].strip())
        ):
            para_lines.append(lines[i])
            i += 1
        blocks.append(paragraph_block(" ".join(l.strip() for l in para_lines), src_repo_rel, sync_map))

    flush_quote()
    return blocks


# --- CLI -----------------------------------------------------------------

def load_map():
    with open(MAP_PATH, encoding="utf-8") as fh:
        raw = json.load(fh)
    return {k: v for k, v in raw.items() if not k.startswith("_")}


def sync_file(repo_rel, sync_map):
    page_id = sync_map.get(repo_rel)
    if not page_id:
        print(f"skip (not in notion_sync_map.json): {repo_rel}")
        return
    abs_path = os.path.join(REPO, repo_rel)
    if not os.path.exists(abs_path):
        print(f"skip (deleted on disk; Notion page left as-is): {repo_rel}")
        return
    with open(abs_path, encoding="utf-8") as fh:
        text = fh.read()
    blocks = markdown_to_blocks(text, repo_rel, sync_map)
    print(f"syncing {repo_rel} -> {page_id} ({len(blocks)} blocks)")
    clear_page(page_id)
    if blocks:
        append_blocks(page_id, blocks)


def main():
    if not NOTION_TOKEN:
        sys.exit("NOTION_TOKEN environment variable is required")
    sync_map = load_map()
    args = sys.argv[1:]
    if args and args[0] == "--all":
        paths = list(sync_map.keys())
    else:
        paths = [os.path.relpath(os.path.abspath(p), REPO).replace("\\", "/") for p in args]
    if not paths:
        sys.exit("usage: sync_notion.py <file> [<file> ...] | --all")

    failures = []
    for p in paths:
        try:
            sync_file(p, sync_map)
        except Exception as exc:
            print(f"ERROR syncing {p}: {exc}", file=sys.stderr)
            failures.append(p)
    if failures:
        sys.exit(f"failed to sync {len(failures)} file(s): {', '.join(failures)}")


if __name__ == "__main__":
    main()
