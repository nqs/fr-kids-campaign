#!/usr/bin/env python3
"""Generate a session log from a diarized transcript using Claude.

Usage:
  update_session_log.py <transcript_md> <audio_path>
      [--campaign-dir <path>]   # defaults to <repo_root>/campaign
      [--sessions-dir <path>]   # defaults to <repo_root>/sessions
      [--force]                 # overwrite an existing log

Creates sessions/session N/session N - log.md from the transcript.
Skips if the log already exists unless --force is passed.
Also appends the new session to campaign/session-log.md.

Requires ANTHROPIC_API_KEY.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def find_session_number(session_dir: Path) -> int | None:
    """Extract the session number from a directory named 'session N'."""
    m = re.search(r"session\s+(\d+)", session_dir.name, re.IGNORECASE)
    return int(m.group(1)) if m else None


def find_existing_log(session_dir: Path) -> Path | None:
    """Return the first *log*.md file in the session directory, if any."""
    for p in sorted(session_dir.glob("*log*.md")):
        return p
    return None


def find_example_log(sessions_dir: Path, current_session: int) -> str:
    """Return the content of the most recent prior session log, for format reference."""
    best: Path | None = None
    best_num = -1
    for d in sessions_dir.iterdir():
        if not d.is_dir():
            continue
        n = find_session_number(d)
        if n is None or n >= current_session:
            continue
        log = find_example_log_in_dir(d)
        if log and n > best_num:
            best, best_num = log, n
    if best:
        return best.read_text(encoding="utf-8")
    return ""


def find_example_log_in_dir(session_dir: Path) -> Path | None:
    for p in sorted(session_dir.glob("*log*.md")):
        return p
    return None


def read_campaign_file(campaign_dir: Path, name: str) -> str:
    p = campaign_dir / name
    return p.read_text(encoding="utf-8") if p.exists() else ""


# ---------------------------------------------------------------------------
# Claude calls
# ---------------------------------------------------------------------------

def call_claude_session_log(
    *,
    transcript: str,
    session_num: int,
    campaign_context: str,
    example_log: str,
    api_key: str,
) -> str:
    import anthropic

    client = anthropic.Anthropic(api_key=api_key)

    session_label = f"{session_num:03d}"
    system_content = (
        f"You are a campaign keeper for a D&D 5e campaign set in the Forgotten Realms "
        f"(Shadowdale). Your task is to write a detailed, accurate session log for "
        f"Session {session_label} based on the transcript provided by the user.\n\n"
        f"## Required output format\n\n"
        f"Produce a single Markdown document with this exact structure:\n\n"
        f"```\n"
        f"---\n"
        f"title: Session {session_label} — <invented title based on main events>\n"
        f"type: log\n"
        f"tags:\n"
        f"  - sessions\n"
        f"  - log\n"
        f"  - session-{session_label}\n"
        f"---\n\n"
        f"## Session {session_label} — <same title>\n"
        f"**Date played:**\n"
        f"**Location in-world:** <locations visited this session>\n"
        f"**Players present:** <Player (Character)>, ...\n"
        f"**Absent:** <Player (Character)> (omit this line if no one was absent)\n"
        f"**Session ended at:** <where/when the session stopped>\n\n"
        f"### What Happened\n"
        f"[Scene-by-scene bullet points. Be specific: name the DC, roll result, outcome.]\n\n"
        f"### Key Decisions & Consequences\n"
        f"[Bullet points on choices made and their implications.]\n\n"
        f"### NPC Interactions\n"
        f"[One entry per NPC, in bold. What happened, what was established.]\n\n"
        f"### Combat & Encounters\n"
        f"[One entry per encounter with XP/CR and notable moments.]\n\n"
        f"### Loot & Rewards\n"
        f"**Confirmed looted:**\n"
        f"[List items]\n\n"
        f"**Deferred:**\n"
        f"[List pending rewards]\n\n"
        f"> [!hook] Loose Ends & Hooks\n"
        f"> - [one bullet per open thread]\n\n"
        f"> [!dm] DM Notes\n"
        f"> - [observations, pacing notes, table management notes]\n"
        f"```\n\n"
        f"Important rules:\n"
        f"- Leave **Date played:** blank (the DM fills it in).\n"
        f"- Use exact names from the campaign context (characters, NPCs, places).\n"
        f"- Where the transcript is garbled or ambiguous, note uncertainty in brackets "
        f"e.g. [unclear — possibly X].\n"
        f"- Do not add narrative flourish; write in the same terse, factual DM-notes style "
        f"as the example.\n"
        f"- Output only the Markdown document — no preamble, no explanation.\n\n"
    )

    if example_log:
        system_content += f"## Example log (for format reference only — not this session)\n\n{example_log}\n\n"

    system_content += f"## Campaign context\n\n{campaign_context}"

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=[
            {
                "type": "text",
                "text": system_content,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[
            {
                "role": "user",
                "content": (
                    f"Here is the full transcript for Session {session_label}. "
                    f"Write the complete session log.\n\n"
                    f"<transcript>\n{transcript}\n</transcript>"
                ),
            }
        ],
    )
    return message.content[0].text.strip()


def call_claude_campaign_log_update(
    *,
    session_log_content: str,
    current_campaign_log: str,
    session_num: int,
    session_dir_name: str,
    api_key: str,
) -> str:
    """Generate the updated campaign/session-log.md content."""
    import anthropic

    client = anthropic.Anthropic(api_key=api_key)

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=[
            {
                "type": "text",
                "text": (
                    "You are a campaign keeper. Update campaign/session-log.md to "
                    "reflect the newly completed session. Preserve the exact Markdown "
                    "format and all existing content — only add or update the following:\n"
                    "1. Add a row to the Session Index table for the new session.\n"
                    "2. Replace the 'Campaign Arc So Far' paragraph with a version that "
                    "includes this session's key events in 2–4 sentences.\n"
                    "3. Replace the 'Recent Session' section with a quick-reference block "
                    "for the new session (5–8 bullets, same style as existing).\n"
                    "4. In the Master Loose Ends Tracker, strike through resolved hooks "
                    "and add new hooks from this session.\n"
                    "Output only the complete updated campaign/session-log.md content — "
                    "no preamble, no explanation."
                ),
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[
            {
                "role": "user",
                "content": (
                    f"Current campaign/session-log.md:\n\n"
                    f"<campaign_log>\n{current_campaign_log}\n</campaign_log>\n\n"
                    f"New session log for Session {session_num:03d} "
                    f"(link target: {session_dir_name}/session {session_num} - log):\n\n"
                    f"<session_log>\n{session_log_content}\n</session_log>"
                ),
            }
        ],
    )
    return message.content[0].text.strip()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("transcript_md", help="Path to the generated transcript .md file")
    parser.add_argument("audio_path", help="Original audio file (used to locate session dir)")
    parser.add_argument("--campaign-dir", default="", help="Path to campaign/ directory")
    parser.add_argument("--sessions-dir", default="", help="Path to sessions/ directory")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing log")
    args = parser.parse_args(argv)

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        print("warning: ANTHROPIC_API_KEY not set; skipping session log generation", file=sys.stderr)
        return 0

    try:
        import anthropic  # noqa: F401
    except ImportError:
        print("warning: anthropic package not installed; skipping session log generation", file=sys.stderr)
        return 0

    session_dir = Path(args.audio_path).parent.resolve()
    session_num = find_session_number(session_dir)
    if session_num is None:
        print(f"warning: could not determine session number from '{session_dir.name}'; skipping", file=sys.stderr)
        return 0

    # Locate campaign and sessions directories.
    repo_root = session_dir.parent.parent  # sessions/session N/ → repo root
    campaign_dir = Path(args.campaign_dir) if args.campaign_dir else repo_root / "campaign"
    sessions_dir = Path(args.sessions_dir) if args.sessions_dir else repo_root / "sessions"

    log_path = session_dir / f"session {session_num} - log.md"
    if log_path.exists() and not args.force:
        print(f"Session log already exists at {log_path}; skipping (use --force to overwrite).")
        return 0

    transcript = Path(args.transcript_md).read_text(encoding="utf-8")

    # Build campaign context block.
    party = read_campaign_file(campaign_dir, "party.md")
    roster = read_campaign_file(campaign_dir, "roster.md")
    session_log_md = read_campaign_file(campaign_dir, "session-log.md")
    campaign_context = f"### party.md\n\n{party}\n\n### roster.md\n\n{roster}\n\n### session-log.md\n\n{session_log_md}"

    example_log = find_example_log(sessions_dir, session_num)

    print(f"Generating session log for Session {session_num:03d}...")
    try:
        log_content = call_claude_session_log(
            transcript=transcript,
            session_num=session_num,
            campaign_context=campaign_context,
            example_log=example_log,
            api_key=api_key,
        )
    except Exception as exc:
        print(f"error: Claude API call failed: {exc}", file=sys.stderr)
        return 1

    log_path.write_text(log_content + "\n", encoding="utf-8")
    print(f"Wrote session log: {log_path}")

    # Update campaign/session-log.md.
    campaign_log_path = campaign_dir / "session-log.md"
    if campaign_log_path.exists() and session_log_md:
        print("Updating campaign/session-log.md...")
        try:
            updated_campaign_log = call_claude_campaign_log_update(
                session_log_content=log_content,
                current_campaign_log=session_log_md,
                session_num=session_num,
                session_dir_name=session_dir.name,
                api_key=api_key,
            )
            campaign_log_path.write_text(updated_campaign_log + "\n", encoding="utf-8")
            print(f"Updated {campaign_log_path}")
        except Exception as exc:
            print(f"warning: failed to update campaign/session-log.md: {exc}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
