#!/usr/bin/env python3
"""Detect speaker-to-name mapping from a roll-call intro in a WhisperX transcript.

Reads the first N seconds of a WhisperX JSON file, sends those segments to
the Claude API, and writes a speakers.json file alongside the audio so that
format_transcript.py can replace SPEAKER_XX labels with real names.

Usage:
  detect_speakers.py <whisperx_json> <audio_path> [--intro-seconds 180]

Requires ANTHROPIC_API_KEY to be set in the environment. Exits silently
(no speakers.json written) if detection fails or the key is absent.

Convention: at the start of each session, the DM asks everyone to say their
name once. This gives each SPEAKER_XX at least one clear self-identification
utterance that the LLM can use to build the mapping.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


def extract_intro_segments(segments: list[dict], intro_seconds: float) -> list[dict]:
    return [s for s in segments if s.get("start", 0) <= intro_seconds]


def build_intro_text(segments: list[dict]) -> str:
    lines = []
    for seg in segments:
        speaker = seg.get("speaker", "SPEAKER_UNKNOWN")
        text = seg.get("text", "").strip()
        if text:
            lines.append(f"{speaker}: {text}")
    return "\n".join(lines)


def call_claude(intro_text: str) -> dict[str, str] | None:
    try:
        import anthropic
    except ImportError:
        print("warning: anthropic package not installed; skipping auto-detection", file=sys.stderr)
        return None

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        print("warning: ANTHROPIC_API_KEY not set; skipping auto-detection", file=sys.stderr)
        return None

    client = anthropic.Anthropic(api_key=api_key)

    prompt = (
        "This is the opening of a tabletop RPG session recording. "
        "The host asked each participant to say their name for the recording. "
        "Below are the first few minutes of the transcript, with each speaker "
        "identified by a label like SPEAKER_00, SPEAKER_01, etc.\n\n"
        f"{intro_text}\n\n"
        "Based on what each speaker said, produce a JSON object mapping each "
        "SPEAKER_XX label to the person's first name (or 'DM' for the game master). "
        "Only include speakers you can confidently identify. "
        "Return only the raw JSON object — no explanation, no markdown fences."
    )

    try:
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=256,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = message.content[0].text.strip()
        # Strip markdown code fences if the model adds them.
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        mapping = json.loads(raw)
        if not isinstance(mapping, dict):
            return None
        # Keep only entries with SPEAKER_XX keys and non-empty string values.
        return {k: v for k, v in mapping.items() if k.startswith("SPEAKER_") and isinstance(v, str) and v}
    except Exception as exc:
        print(f"warning: Claude API call failed ({exc}); skipping auto-detection", file=sys.stderr)
        return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("json_file", help="WhisperX JSON output file")
    parser.add_argument("audio_path", help="Original audio file path (speakers.json written alongside it)")
    parser.add_argument("--intro-seconds", type=float, default=180.0,
                        help="How many seconds of intro to analyze (default: 180)")
    args = parser.parse_args(argv)

    json_path = Path(args.json_file)
    if not json_path.exists():
        print(f"error: JSON file '{json_path}' not found", file=sys.stderr)
        return 1

    data = json.loads(json_path.read_text(encoding="utf-8"))
    segments = data.get("segments", [])

    intro_segments = extract_intro_segments(segments, args.intro_seconds)
    if not intro_segments:
        print("warning: no segments found in intro window; skipping auto-detection", file=sys.stderr)
        return 0

    intro_text = build_intro_text(intro_segments)
    mapping = call_claude(intro_text)

    if not mapping or len(mapping) < 2:
        print("Auto-detection did not find enough speakers; falling back to manual mapping.",
              file=sys.stderr)
        return 0

    speakers_path = Path(args.audio_path).parent / "speakers.json"
    speakers_path.write_text(json.dumps(mapping, indent=2) + "\n", encoding="utf-8")
    print(f"Auto-detected {len(mapping)} speaker(s); wrote {speakers_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
