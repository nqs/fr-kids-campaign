#!/usr/bin/env python3
"""Sync the repo's Markdown content to a BookStack shelf.

The repo is the single source of truth; this script talks to the BookStack
REST API and makes the "Forgotten Realms Kids Campaign" shelf mirror the
curated content here, mapping the repo tree onto BookStack's
shelf -> book -> chapter -> page hierarchy:

    Shelf: Forgotten Realms Kids Campaign
      Book "Campaign Guide"      <- campaign/*.md
        Chapter "The Party"      <- campaign/party/*.md
        Chapter "NPC Roster"     <- campaign/roster/*.md
      Book "Sessions"
        Chapter per session      <- sessions/session <N>/*.md
      Book "DM Operating Docs"   <- AGENTS.md, dnd-adventure-generator.md

Same content set as scripts/build_wiki.py, minus the GitHub-wiki-only nav
pages (Home.md, _Sidebar.md) — BookStack's shelf/book navigation replaces
them. Raw machine transcripts (*.m4a.md), binaries, and references/ stay in
the main repo and are linked back to GitHub.

Transforms applied while rendering a page:
  * The leading H1 becomes the BookStack page title and is stripped from the
    body (BookStack renders the title itself).
  * Internal links to synced .md files are rewritten to their BookStack page
    URLs; links to binaries/references fall back to absolute GitHub URLs.
  * GitHub alert blockquotes ([!NOTE] etc.) become plain bold labels.
  * Inline images are already absolute URLs and pass through untouched.

The sync is idempotent and stateless: every synced page carries a trailing
`<!-- bookstack-sync: <path> <hash> -->` marker. Pages are matched by that
marker, skipped when the hash is unchanged, updated when it differs, and
deleted (to BookStack's recycle bin) when their source file disappears.
Pages without a marker are never touched, so hand-made pages in the same
books survive. No third-party dependencies (stdlib only), matching the rest
of scripts/.

Usage:
    BOOKSTACK_API_TOKEN=<token_id>:<token_secret> scripts/sync_bookstack.py
    ... --dry-run    # read server state, print planned writes, change nothing

Environment:
    BOOKSTACK_API_TOKEN  required, "<token_id>:<token_secret>" from the
                         BookStack profile page (Edit Profile -> API Tokens)
    BOOKSTACK_URL        default https://wiki.nqs.io
    BOOKSTACK_SHELF      default "Forgotten Realms Kids Campaign"
"""
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from urllib.parse import quote, unquote

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BOOKSTACK_URL = os.environ.get("BOOKSTACK_URL", "https://wiki.nqs.io").rstrip("/")
SHELF_NAME = os.environ.get("BOOKSTACK_SHELF", "Forgotten Realms Kids Campaign")
API_TOKEN = os.environ.get("BOOKSTACK_API_TOKEN", "")

REPO_SLUG = os.environ.get("GITHUB_REPOSITORY", "nqs/fr-kids-campaign")
SOURCE_BRANCH = os.environ.get("WIKI_SOURCE_BRANCH", "main")
BLOB = f"https://github.com/{REPO_SLUG}/blob/{SOURCE_BRANCH}"
RAW = f"https://raw.githubusercontent.com/{REPO_SLUG}/{SOURCE_BRANCH}"

RATE_LIMIT_SLEEP = 0.35  # stay inside BookStack's default 180 req/min
IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".gif")

MD_LINK = re.compile(r"(!?)\[([^\]]*)\]\(\s*<?([^>\s)]+)>?\s*\)")
H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
HEADING_RE = re.compile(r"^#{1,6}\s+(.+?)\s*$", re.MULTILINE)
ALERT_RE = re.compile(r"^(>\s*)\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]\s*$", re.MULTILINE)
# Source paths may contain spaces ("sessions/session 3/session 3 - log.md"),
# so the path is everything up to the final whitespace-delimited hash token.
MARKER_RE = re.compile(r"<!--\s*bookstack-sync:\s*(.+?)\s+([0-9a-f]+|pending)\s*-->")
INLINE_MD_RE = re.compile(r"\*\*([^*]+)\*\*|\*([^*]+)\*|_([^_]+)_|`([^`]+)`")

CAMPAIGN_PAGE_ORDER = ["world.md", "geography.md", "factions.md", "roster.md",
                       "party.md", "session-log.md"]
SESSION_FILE_ORDER = ["-0-overview", "-1-adventure", "-2-combat-tracker",
                      "-3-player-handouts", "-4-dm-quick-ref"]


# --- BookStack API plumbing -------------------------------------------------

class BookStack:
    def __init__(self, base_url, token, dry_run=False):
        self.api = f"{base_url}/api"
        self.token = token
        self.dry_run = dry_run
        self.writes = 0

    def request(self, method, path, body=None, retries=5):
        if self.dry_run and method != "GET":
            self.writes += 1
            print(f"  [dry-run] {method} {path} {json.dumps(body)[:120] if body else ''}")
            # Fabricate just enough of a response for the caller to continue.
            return {"id": -self.writes, "slug": f"dry-run-{self.writes}",
                    "name": (body or {}).get("name", "")}
        url = f"{self.api}{path}"
        data = json.dumps(body).encode("utf-8") if body is not None else None
        last_err = None
        for attempt in range(retries):
            req = urllib.request.Request(url, data=data, method=method)
            req.add_header("Authorization", f"Token {self.token}")
            req.add_header("Content-Type", "application/json")
            req.add_header("Accept", "application/json")
            try:
                with urllib.request.urlopen(req) as resp:
                    time.sleep(RATE_LIMIT_SLEEP)
                    raw = resp.read().decode("utf-8")
                    return json.loads(raw) if raw.strip() else {}
            except urllib.error.HTTPError as e:
                err_body = e.read().decode("utf-8", "replace")
                if e.code == 429 or e.code >= 500:
                    wait = float(e.headers.get("Retry-After") or 2 ** attempt)
                    time.sleep(wait)
                    last_err = RuntimeError(
                        f"BookStack API {method} {path} failed: {e.code} {err_body}")
                    continue
                raise RuntimeError(
                    f"BookStack API {method} {path} failed: {e.code} {err_body}")
        raise last_err

    def paginated(self, path):
        offset = 0
        while True:
            res = self.request("GET", f"{path}?count=100&offset={offset}")
            data = res.get("data", [])
            yield from data
            offset += len(data)
            if offset >= res.get("total", 0) or not data:
                return


# --- Plan: what the shelf should contain ------------------------------------

def strip_inline_md(text):
    return INLINE_MD_RE.sub(lambda m: next(g for g in m.groups() if g is not None), text)


def read_file(repo_rel):
    with open(os.path.join(REPO, repo_rel), encoding="utf-8") as fh:
        return fh.read()


def humanize(filename):
    base = os.path.splitext(os.path.basename(filename))[0]
    return re.sub(r"\s*-\s*", " — ", base.replace("-", " ").strip()).title()


def page_title(repo_rel, text=None):
    """First H1 wins; fall back to any first heading, then the filename."""
    text = read_file(repo_rel) if text is None else text
    m = H1_RE.search(text) or HEADING_RE.search(text)
    if m:
        return strip_inline_md(m.group(1))
    return humanize(repo_rel)


def list_md(dirpath, exclude_transcripts=True):
    absdir = os.path.join(REPO, dirpath)
    if not os.path.isdir(absdir):
        return []
    out = []
    for fn in sorted(os.listdir(absdir)):
        if fn.endswith(".md") and not (exclude_transcripts and fn.endswith(".m4a.md")):
            out.append(f"{dirpath}/{fn}")
    return out


def session_dirs():
    root = os.path.join(REPO, "sessions")
    if not os.path.isdir(root):
        return []
    dirs = []
    for name in os.listdir(root):
        m = re.match(r"session\s+(\d+)$", name)
        if m and os.path.isdir(os.path.join(root, name)):
            dirs.append((int(m.group(1)), f"sessions/{name}"))
    return [d for _, d in sorted(dirs)]


def session_sort_key(repo_rel):
    base = os.path.basename(repo_rel)
    for i, suffix in enumerate(SESSION_FILE_ORDER):
        if suffix in base:
            return (i, base)
    if base.endswith("log.md"):
        return (len(SESSION_FILE_ORDER), base)
    return (len(SESSION_FILE_ORDER) + 1, base)


def session_chapter_name(dirpath, pages):
    for p in pages:
        if "-0-overview" in os.path.basename(p):
            return page_title(p)
    n = int(re.search(r"(\d+)$", dirpath).group(1))
    return f"Session {n:03d}"


def build_plan():
    """Return the desired shelf contents.

    books: [{name, description, children: [
        {type: 'page', path},
        {type: 'chapter', key, name, description, pages: [path, ...]},
    ]}]
    """
    campaign_children = []
    ordered = [f"campaign/{n}" for n in CAMPAIGN_PAGE_ORDER]
    extras = [p for p in list_md("campaign") if p not in ordered]
    for p in [p for p in ordered if os.path.exists(os.path.join(REPO, p))] + extras:
        campaign_children.append({"type": "page", "path": p})
    for key, name, d in (("campaign/party", "The Party", "campaign/party"),
                         ("campaign/roster", "NPC Roster", "campaign/roster")):
        pages = list_md(d)
        if pages:
            campaign_children.append({"type": "chapter", "key": key, "name": name,
                                      "description": chapter_desc(key), "pages": pages})

    session_children = []
    for d in session_dirs():
        pages = sorted(list_md(d), key=session_sort_key)
        if pages:
            session_children.append({"type": "chapter", "key": d,
                                     "name": session_chapter_name(d, pages),
                                     "description": chapter_desc(d), "pages": pages})

    docs_children = [{"type": "page", "path": p}
                     for p in ("AGENTS.md", "dnd-adventure-generator.md")
                     if os.path.exists(os.path.join(REPO, p))]

    books = [
        {"name": "Campaign Guide", "children": campaign_children,
         "description": "The campaign's canon: world, geography, factions, party, "
                        "NPC roster, and session log. " + SYNC_NOTE},
        {"name": "Sessions", "children": session_children,
         "description": "Per-session deliverables: overview, adventure, combat "
                        "tracker, player handouts, DM quick reference, and log. " + SYNC_NOTE},
        {"name": "DM Operating Docs", "children": docs_children,
         "description": "The agent instructions and adventure-generator workflow "
                        "that drive content generation. " + SYNC_NOTE},
    ]
    return [b for b in books if b["children"]]


SYNC_NOTE = f"Synced automatically from the {REPO_SLUG} repo — edit there, not here."


def chapter_desc(key):
    return f'Synced from "{key}" in the {REPO_SLUG} repo — edit there, not here.'


CHAPTER_KEY_RE = re.compile(r'Synced from "([^"]+)"')


# --- Rendering ---------------------------------------------------------------

def rewrite_target(target, src_dir_repo, url_map):
    if target.startswith("#") or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", target) \
            or target.startswith("mailto:"):
        return None
    path, _, anchor = target.partition("#")
    anchor = f"#{anchor}" if anchor else ""
    abs_path = os.path.normpath(os.path.join(REPO, src_dir_repo, unquote(path)))
    repo_rel = os.path.relpath(abs_path, REPO).replace("\\", "/")
    if repo_rel.startswith(".."):
        return None
    if repo_rel in url_map:
        return f"{url_map[repo_rel]}{anchor}"
    if os.path.splitext(repo_rel)[1].lower() in IMAGE_EXTS:
        return f"{RAW}/{quote(repo_rel)}"
    return f"{BLOB}/{quote(repo_rel)}{anchor}"


def render_page(repo_rel, url_map):
    """Return (title, markdown body ready for BookStack, sans marker)."""
    text = read_file(repo_rel)
    title = page_title(repo_rel, text)

    # Drop the leading H1 (it becomes the page title).
    m = H1_RE.search(text)
    if m and text[:m.start()].strip() == "":
        text = text[m.end():].lstrip("\n")

    def repl(link):
        new = rewrite_target(link.group(3), os.path.dirname(repo_rel), url_map)
        if new is None:
            return link.group(0)
        return f"{link.group(1)}[{link.group(2)}]({new})"

    text = MD_LINK.sub(repl, text)
    text = ALERT_RE.sub(lambda m: f"{m.group(1)}**{m.group(2).title()}**", text)
    return title, text.strip() + "\n"


def content_hash(title, container_key, priority, body):
    h = hashlib.sha256(f"{title}\n{container_key}\n{priority}\n{body}".encode("utf-8"))
    return h.hexdigest()[:16]


def with_marker(body, repo_rel, digest):
    return f"{body}\n<!-- bookstack-sync: {repo_rel} {digest} -->\n"


# --- Sync --------------------------------------------------------------------

def ensure_shelf(bs):
    for shelf in bs.paginated("/shelves"):
        if shelf["name"].strip().lower() == SHELF_NAME.lower():
            return bs.request("GET", f"/shelves/{shelf['id']}")
    print(f"creating shelf: {SHELF_NAME}")
    return bs.request("POST", "/shelves", {
        "name": SHELF_NAME,
        "description": f"D&D 5e Forgotten Realms kids campaign. {SYNC_NOTE}"})


def inventory_book(bs, book):
    """Read a managed book's chapters and marker-carrying pages.

    Returns (chapters, pages):
      chapters: key-or-name -> {id, name}
      pages: source path -> {id, name, hash, chapter_id, slug}
    """
    detail = bs.request("GET", f"/books/{book['id']}")
    chapters, pages = {}, {}
    page_stubs = []
    for item in detail.get("contents", []):
        if item["type"] == "chapter":
            cd = bs.request("GET", f"/chapters/{item['id']}")
            key_m = CHAPTER_KEY_RE.search(cd.get("description") or "")
            key = key_m.group(1) if key_m else item["name"]
            chapters[key] = {"id": item["id"], "name": item["name"],
                             "managed": key_m is not None}
            page_stubs.extend((p, item["id"]) for p in item.get("pages", []))
        else:
            page_stubs.append((item, None))
    for stub, chapter_id in page_stubs:
        pd = bs.request("GET", f"/pages/{stub['id']}")
        marker = MARKER_RE.search(pd.get("markdown") or "")
        if not marker:
            print(f"  leaving unmanaged page alone: {pd['name']!r} (id {pd['id']})")
            continue
        pages[marker.group(1)] = {"id": pd["id"], "name": pd["name"],
                                  "hash": marker.group(2), "slug": pd["slug"],
                                  "chapter_id": chapter_id}
    return chapters, pages


def sync(bs):
    plan = build_plan()
    shelf = ensure_shelf(bs)
    shelf_book_ids = [b["id"] for b in shelf.get("books", [])]
    books_by_name = {b["name"]: b for b in shelf.get("books", [])}

    # Pass 1 — ensure books/chapters exist and every page has a shell with a
    # stable slug, so pass 2 can resolve internal links to real URLs.
    url_map = {}      # repo path -> BookStack page URL
    desired = {}      # repo path -> {page info for pass 2}
    inv_pages_all = {}
    managed_chapters = []  # (book, chapters dict, live keys) for pruning

    for book_plan in plan:
        book = books_by_name.get(book_plan["name"])
        if book is None:
            print(f"creating book: {book_plan['name']}")
            book = bs.request("POST", "/books", {
                "name": book_plan["name"], "description": book_plan["description"]})
            shelf_book_ids.append(book["id"])
            chapters, inv_pages = {}, {}
        else:
            chapters, inv_pages = inventory_book(bs, book)
        inv_pages_all.update(inv_pages)
        live_chapter_keys = set()

        for priority, child in enumerate(book_plan["children"], start=1):
            if child["type"] == "page":
                queue = [(child["path"], {"book_id": book["id"]}, "book:" + book_plan["name"], priority)]
            else:
                live_chapter_keys.add(child["key"])
                chapter = chapters.get(child["key"])
                if chapter is None:
                    print(f"creating chapter: {child['name']} ({child['key']})")
                    chapter = bs.request("POST", "/chapters", {
                        "book_id": book["id"], "name": child["name"],
                        "description": child["description"], "priority": priority})
                    chapters[child["key"]] = {"id": chapter["id"],
                                              "name": child["name"], "managed": True}
                    chapter = chapters[child["key"]]
                elif chapter["name"] != child["name"]:
                    bs.request("PUT", f"/chapters/{chapter['id']}", {
                        "name": child["name"], "description": child["description"],
                        "priority": priority})
                    chapter["name"] = child["name"]
                queue = [(p, {"chapter_id": chapter["id"]}, "chapter:" + child["key"], i)
                         for i, p in enumerate(child["pages"], start=1)]

            for path, container, container_key, prio in queue:
                title = page_title(path)
                existing = inv_pages.get(path)
                if existing is None:
                    created = bs.request("POST", "/pages", dict(
                        container, name=title, priority=prio,
                        markdown=with_marker("*Syncing…*", path, "pending")))
                    existing = {"id": created["id"], "name": title,
                                "hash": "pending", "slug": created["slug"]}
                    inv_pages_all[path] = existing
                elif existing["name"] != title:
                    # Rename before building the URL map so links elsewhere
                    # pick up the post-rename slug in this same run.
                    renamed = bs.request("PUT", f"/pages/{existing['id']}",
                                         {"name": title})
                    existing["name"] = title
                    existing["slug"] = renamed.get("slug", existing["slug"])
                    existing["hash"] = "renamed"
                url_map[path] = f"{BOOKSTACK_URL}/books/{book['slug']}/page/{existing['slug']}"
                desired[path] = {"container": container, "container_key": container_key,
                                 "priority": prio, "existing": existing}

        managed_chapters.append((book, chapters, live_chapter_keys))

    # Pass 2 — render with resolved links; write only what changed.
    skipped = updated = 0
    for path, d in desired.items():
        title, body = render_page(path, url_map)
        digest = content_hash(title, d["container_key"], d["priority"], body)
        if d["existing"]["hash"] == digest and d["existing"]["name"] == title:
            skipped += 1
            continue
        print(f"updating page: {path} -> {title!r}")
        bs.request("PUT", f"/pages/{d['existing']['id']}", dict(
            d["container"], name=title, priority=d["priority"],
            markdown=with_marker(body, path, digest)))
        updated += 1

    # Prune synced pages whose source file is gone, then orphaned chapters.
    for path, info in inv_pages_all.items():
        if path not in desired:
            print(f"deleting stale page: {path} (id {info['id']})")
            bs.request("DELETE", f"/pages/{info['id']}")
    for book, chapters, live_keys in managed_chapters:
        for key, chapter in chapters.items():
            if key not in live_keys and chapter.get("managed"):
                detail = bs.request("GET", f"/chapters/{chapter['id']}")
                if not detail.get("pages"):
                    print(f"deleting empty stale chapter: {chapter['name']} (id {chapter['id']})")
                    bs.request("DELETE", f"/chapters/{chapter['id']}")

    # Make sure the shelf lists every managed book (preserving existing order).
    if shelf_book_ids != [b["id"] for b in shelf.get("books", [])]:
        bs.request("PUT", f"/shelves/{shelf['id']}", {"books": shelf_book_ids})

    print(f"\ndone: {updated} page(s) updated, {skipped} unchanged, "
          f"{len(desired)} total on shelf {SHELF_NAME!r}")


def main():
    dry_run = "--dry-run" in sys.argv[1:]
    if not API_TOKEN or ":" not in API_TOKEN:
        sys.exit("BOOKSTACK_API_TOKEN must be set to '<token_id>:<token_secret>'")
    bs = BookStack(BOOKSTACK_URL, API_TOKEN, dry_run=dry_run)
    sync(bs)
    if dry_run:
        print(f"[dry-run] {bs.writes} write call(s) suppressed")


if __name__ == "__main__":
    main()
