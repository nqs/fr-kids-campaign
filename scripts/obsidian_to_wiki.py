#!/usr/bin/env python3
"""One-shot converter: Obsidian-flavoured markdown -> GitHub-flavoured markdown.

Transforms applied to campaign/ and sessions/ content files:
  * Obsidian wikilinks  [[target]] / [[target|alias]]  ->  relative [alias](path)
  * Obsidian/Admonition callouts  > [!type] Title  ->  GitHub alerts + bold label

References under references/_raw are intentionally left untouched (auto-extracted
sourcebook text, no hand-authored Obsidian syntax). Index/tooling files
(home.md, AGENTS.md, dnd-adventure-generator.md) are converted by hand.
"""
import os
import re
import sys
from urllib.parse import quote

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Bare wikilink target -> repo-relative path.
NAME_MAP = {
    "world": "campaign/world.md",
    "geography": "campaign/geography.md",
    "factions": "campaign/factions.md",
    "party": "campaign/party.md",
    "roster": "campaign/roster.md",
    "session-log": "campaign/session-log.md",
    "agents": "AGENTS.md",
    "dnd-adventure-generator": "dnd-adventure-generator.md",
    "home": "Home.md",
}

# Obsidian callout type -> (GitHub alert, friendly label)
CALLOUT_MAP = {
    "note": ("NOTE", "Note"),
    "cite": ("NOTE", "Source"),
    "lore": ("NOTE", "Lore"),
    "quote": ("NOTE", "Read-aloud"),
    "read-aloud": ("NOTE", "Read-aloud"),
    "dm": ("IMPORTANT", "DM"),
    "hook": ("TIP", "Hook"),
    "flag": ("WARNING", "Flag"),
}

WIKILINK = re.compile(r"\[\[([^\]|]+?)(?:\\?\|([^\]]+))?\]\]")
CALLOUT = re.compile(r"^(\s*>+\s*)\[!([a-zA-Z-]+)\]\s*(.*?)\s*$")


def resolve_target(raw_target):
    """Return a repo-relative path (with extension) for a wikilink target."""
    target = raw_target.strip()
    if target in NAME_MAP:
        return NAME_MAP[target]
    # path-style target (e.g. "sessions/session 3/the-foo")
    candidate_md = target + ".md"
    candidate_pdf = target + ".pdf"
    if os.path.exists(os.path.join(REPO, candidate_md)):
        return candidate_md
    if os.path.exists(os.path.join(REPO, candidate_pdf)):
        return candidate_pdf
    # default to .md if no extension already present
    return target if os.path.splitext(target)[1] else candidate_md


def convert_wikilinks(text, file_dir):
    def repl(m):
        target, alias = m.group(1), m.group(2)
        repo_path = resolve_target(target)
        rel = os.path.relpath(os.path.join(REPO, repo_path), file_dir)
        # URL-encode only path separators safely: keep '/', encode spaces etc.
        href = quote(rel, safe="/#")
        label = alias.strip() if alias else os.path.basename(target).strip()
        return f"[{label}]({href})"

    return WIKILINK.sub(repl, text)


def convert_callouts(lines):
    out = []
    for line in lines:
        m = CALLOUT.match(line)
        if not m:
            out.append(line)
            continue
        prefix, ctype, title = m.group(1), m.group(2).lower(), m.group(3).strip()
        alert, label = CALLOUT_MAP.get(ctype, ("NOTE", ctype.upper()))
        out.append(f"{prefix.rstrip()} [!{alert}]")
        if title:
            if label.lower() in title.lower():
                out.append(f"{prefix.rstrip()} **{title}**")
            else:
                out.append(f"{prefix.rstrip()} **{label}:** {title}")
        else:
            out.append(f"{prefix.rstrip()} **{label}**")
    return out


def convert_file(path):
    with open(path, encoding="utf-8") as fh:
        original = fh.read()

    file_dir = os.path.dirname(os.path.abspath(path))
    lines = original.split("\n")

    # Track fenced code blocks; skip wikilink/callout transforms inside them.
    fence = None
    new_lines = []
    for line in lines:
        stripped = line.lstrip()
        if fence is None and (stripped.startswith("```") or stripped.startswith("~~~")):
            fence = stripped[:3]
            new_lines.append(line)
            continue
        if fence is not None:
            new_lines.append(line)
            if stripped.startswith(fence):
                fence = None
            continue
        new_lines.append(line)

    # Apply callout transform first (line-structured), skipping code fences.
    code_flags = []
    fence = None
    for line in new_lines:
        stripped = line.lstrip()
        opening = fence is None and (stripped.startswith("```") or stripped.startswith("~~~"))
        in_code = fence is not None or opening
        code_flags.append(in_code)
        if opening:
            fence = stripped[:3]
        elif fence is not None and stripped.startswith(fence):
            fence = None

    # callouts
    processed = []
    for line, in_code in zip(new_lines, code_flags):
        if in_code:
            processed.append(line)
        else:
            processed.extend(convert_callouts([line]))

    # wikilinks: rebuild code_flags for the (possibly longer) processed list by
    # re-tracking fences, then convert only non-code lines.
    final = []
    fence = None
    for line in processed:
        stripped = line.lstrip()
        opening = fence is None and (stripped.startswith("```") or stripped.startswith("~~~"))
        in_code = fence is not None or opening
        if opening:
            fence = stripped[:3]
        elif fence is not None and stripped.startswith(fence):
            fence = None
        final.append(line if in_code else convert_wikilinks(line, file_dir))

    result = "\n".join(final)
    if result != original:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(result)
        return True
    return False


def main():
    roots = ["campaign", "sessions"]
    changed = []
    for root in roots:
        for dirpath, _, filenames in os.walk(os.path.join(REPO, root)):
            for name in filenames:
                if name.endswith(".md"):
                    p = os.path.join(dirpath, name)
                    if convert_file(p):
                        changed.append(os.path.relpath(p, REPO))
    for c in sorted(changed):
        print("converted:", c)
    print(f"\n{len(changed)} file(s) changed")


if __name__ == "__main__":
    main()
