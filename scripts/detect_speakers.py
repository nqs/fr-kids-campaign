#!/usr/bin/env python3
"""Detect speaker-to-character mapping from a WhisperX transcript.

Two-stage approach:
  1. Intro roll call: read the first N seconds and look for each speaker
     saying their character name (e.g. "Kto", "Fiorn"). Fast and cheap.
  2. Full-transcript inference (fallback): if the intro yields fewer than
     2 confident matches, pass the full transcript + party/roster context
     to Claude and infer who is who from class abilities, spells cast, DM
     narration patterns, and names used in dialogue.

Writes speakers.json alongside the audio file on success.

Usage:
  detect_speakers.py <whisperx_json> <audio_path>
      [--intro-seconds 180]
      [--campaign-dir <path>]   # for party.md + roster.md (fallback)

Requires ANTHROPIC_API_KEY. Silent no-op if the key is absent.

Convention: at the start of each session the DM asks "say your character
name for the recording." Each player responds with just their character's
name; the DM says "DM."
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Segment helpers
# ---------------------------------------------------------------------------

def build_segment_text(segments: list[dict]) -> str:
    lines = []
    for seg in segments:
        speaker = seg.get("speaker", "SPEAKER_UNKNOWN")
        text = seg.get("text", "").strip()
        if text:
            lines.append(f"{speaker}: {text}")
    return "\n".join(lines)


def get_client() -> object | None:
    try:
        import anthropic
    except ImportError:
        print("warning: anthropic package not installed; skipping auto-detection", file=sys.stderr)
        return None
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        print("warning: ANTHROPIC_API_KEY not set; skipping auto-detection", file=sys.stderr)
        return None
    import anthropic
    return anthropic.Anthropic(api_key=api_key)


def parse_mapping_response(raw: str) -> dict[str, str] | None:
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    try:
        mapping = json.loads(raw)
    except json.JSONDecodeError:
        return None
    if not isinstance(mapping, dict):
        return None
    return {
        k: v
        for k, v in mapping.items()
        if k.startswith("SPEAKER_") and isinstance(v, str) and v.strip()
    }


# ---------------------------------------------------------------------------
# Stage 1: intro roll call
# ---------------------------------------------------------------------------

def detect_from_intro(segments: list[dict], intro_seconds: float, client: object) -> dict[str, str] | None:
    intro = [s for s in segments if s.get("start", 0) <= intro_seconds]
    if not intro:
        return None

    intro_text = build_segment_text(intro)

    prompt = (
        "This is the opening of a tabletop RPG session recording. "
        "The DM asked each player to say their character's name for the recording "
        "(e.g. 'Kto', 'Fiorn', 'Nalith'). The DM says 'DM'. "
        "Below are the first few minutes of the transcript, with each speaker "
        "identified by a label like SPEAKER_00, SPEAKER_01, etc.\n\n"
        f"{intro_text}\n\n"
        "Based on what each speaker said, produce a JSON object mapping each "
        "SPEAKER_XX label to the character name (or 'DM' for the game master). "
        "Only include speakers you can identify with confidence. "
        "Return only the raw JSON object — no explanation, no markdown fences."
    )

    try:
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=256,
            messages=[{"role": "user", "content": prompt}],
        )
        return parse_mapping_response(message.content[0].text.strip())
    except Exception as exc:
        print(f"warning: intro detection API call failed ({exc})", file=sys.stderr)
        return None


# ---------------------------------------------------------------------------
# Stage 2: full-transcript inference
# ---------------------------------------------------------------------------

def load_campaign_context(campaign_dir: Path) -> str:
    parts = []
    for name in ("party.md", "roster.md"):
        p = campaign_dir / name
        if p.exists():
            parts.append(f"### {name}\n\n{p.read_text(encoding='utf-8')}")
    return "\n\n".join(parts)


def detect_from_full_transcript(
    segments: list[dict],
    campaign_context: str,
    client: object,
) -> dict[str, str] | None:
    full_text = build_segment_text(segments)
    if not full_text:
        return None

    print("Falling back to full-transcript speaker inference...", file=sys.stderr)

    system = (
        "You are analysing a transcript of a D&D 5e tabletop RPG session. "
        "Each participant is labelled SPEAKER_00, SPEAKER_01, etc. "
        "Use the party roster and the full transcript to work out which label "
        "belongs to which character or role.\n\n"
        "Clues to use:\n"
        "- The DM narrates scenes, describes the environment, asks 'what do you do?', "
        "and calls for skill checks by name.\n"
        "- Each class has distinctive abilities: Druid → Wild Shape; "
        "Wizard → named spells (Fireball, Scorching Ray, etc.); "
        "Rogue → Sneak Attack, Cunning Action; "
        "Fighter → Action Surge, Second Wind, Champion crits.\n"
        "- Characters are addressed by name by other speakers.\n"
        "- Players may refer to their own character by name or say 'I cast…', "
        "'I attack…', 'I roll…' with the relevant ability.\n\n"
        "Return a JSON object mapping each SPEAKER_XX to the character name "
        "(or 'DM'). Include only labels you can identify with confidence. "
        "Return only the raw JSON object — no explanation, no markdown fences."
    )

    user = (
        f"Party roster and context:\n\n{campaign_context}\n\n"
        f"Full transcript:\n\n{full_text}"
    )

    try:
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=512,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return parse_mapping_response(message.content[0].text.strip())
    except Exception as exc:
        print(f"warning: full-transcript inference API call failed ({exc})", file=sys.stderr)
        return None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("json_file", help="WhisperX JSON output file")
    parser.add_argument("audio_path", help="Original audio file (speakers.json written alongside it)")
    parser.add_argument("--intro-seconds", type=float, default=180.0,
                        help="Seconds of intro to try first (default: 180)")
    parser.add_argument("--campaign-dir", default="",
                        help="Path to campaign/ dir for party.md + roster.md (used by fallback)")
    args = parser.parse_args(argv)

    client = get_client()
    if client is None:
        return 0

    json_path = Path(args.json_file)
    if not json_path.exists():
        print(f"error: JSON file '{json_path}' not found", file=sys.stderr)
        return 1

    data = json.loads(json_path.read_text(encoding="utf-8"))
    segments: list[dict] = data.get("segments", [])

    # Stage 1: intro roll call.
    print("Attempting speaker detection from intro roll call...", file=sys.stderr)
    mapping = detect_from_intro(segments, args.intro_seconds, client)

    # Stage 2: full-transcript inference if intro didn't find enough speakers.
    if not mapping or len(mapping) < 2:
        print("Intro detection insufficient; trying full-transcript inference...", file=sys.stderr)

        # Resolve campaign dir: explicit arg, or derive from audio path.
        if args.campaign_dir:
            campaign_dir = Path(args.campaign_dir)
        else:
            # audio is at sessions/session N/<file>; repo root is 2 levels up.
            campaign_dir = Path(args.audio_path).resolve().parent.parent.parent / "campaign"

        campaign_context = load_campaign_context(campaign_dir)
        if not campaign_context:
            print("warning: no campaign context found; cannot run full-transcript inference", file=sys.stderr)
            return 0

        mapping = detect_from_full_transcript(segments, campaign_context, client)

    if not mapping or len(mapping) < 2:
        print("Speaker detection could not identify enough speakers; no speakers.json written.", file=sys.stderr)
        return 0

    speakers_path = Path(args.audio_path).parent / "speakers.json"
    speakers_path.write_text(json.dumps(mapping, indent=2) + "\n", encoding="utf-8")
    print(f"Detected {len(mapping)} speaker(s); wrote {speakers_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
