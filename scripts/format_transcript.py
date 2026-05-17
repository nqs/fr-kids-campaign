#!/usr/bin/env python3
"""Convert a WhisperX JSON transcript to an Obsidian-compatible Markdown note.

Usage:
  format_transcript.py <whisperx_json> <output_md>
      [--source <audio_basename>]
      [--model <model_name>]
      [--speakers <speakers_file>]   # JSON or YAML, maps SPEAKER_XX -> name

Produces a Markdown file with YAML frontmatter and one diarized line per
sentence, formatted as:

    [DisplayName]: text of utterance

If no --speakers file is given, raw SPEAKER_XX labels are preserved so the
DM can identify them, then re-run with a speakers file.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def load_speaker_map(path_str: str | None) -> dict[str, str]:
    if not path_str:
        return {}
    path = Path(path_str)
    if not path.exists():
        print(f"warning: speakers file '{path}' not found; using raw labels", file=sys.stderr)
        return {}
    text = path.read_text(encoding="utf-8")
    if path.suffix in (".yaml", ".yml"):
        # Avoid requiring PyYAML — the format is simple "SPEAKER_XX: Name" lines.
        mapping: dict[str, str] = {}
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" in line:
                key, _, val = line.partition(":")
                mapping[key.strip()] = val.strip()
        return mapping
    return json.loads(text)


def _ends_sentence(text: str) -> bool:
    stripped = text.rstrip()
    return stripped.endswith((".", "!", "?", "..."))


def build_lines(segments: list[dict], speaker_map: dict[str, str]) -> list[str]:
    """Collapse consecutive same-speaker segments into one line per sentence."""
    lines: list[str] = []
    if not segments:
        return lines

    current_speaker = ""
    current_text = ""

    for seg in segments:
        raw_speaker = seg.get("speaker", "SPEAKER_UNKNOWN")
        display = speaker_map.get(raw_speaker, raw_speaker)
        text = seg.get("text", "").strip()
        if not text:
            continue

        if not current_speaker:
            current_speaker = display
            current_text = text
        elif display == current_speaker and not _ends_sentence(current_text):
            current_text = current_text + " " + text
        else:
            lines.append(f"[{current_speaker}]: {current_text}")
            current_speaker = display
            current_text = text

    if current_text:
        lines.append(f"[{current_speaker}]: {current_text}")

    return lines


def build_speakers_block(speaker_map: dict[str, str]) -> str:
    if not speaker_map:
        return ""
    lines = ["speakers:"]
    for k, v in sorted(speaker_map.items()):
        lines.append(f"  {k}: {v}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("json_file", help="WhisperX JSON output file")
    parser.add_argument("output_md", help="Destination .md file")
    parser.add_argument("--source", default="", help="Audio file basename for frontmatter")
    parser.add_argument("--model", default="large-v2", help="Model name for frontmatter")
    parser.add_argument("--speakers", default="", help="Path to speakers JSON or YAML file")
    args = parser.parse_args(argv)

    json_path = Path(args.json_file)
    if not json_path.exists():
        print(f"error: JSON file '{json_path}' not found", file=sys.stderr)
        return 1

    data = json.loads(json_path.read_text(encoding="utf-8"))
    segments: list[dict] = data.get("segments", [])

    speaker_map = load_speaker_map(args.speakers or None)
    transcript_lines = build_lines(segments, speaker_map)
    transcript_body = "\n".join(transcript_lines)

    transcribed_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    speakers_block = build_speakers_block(speaker_map)

    frontmatter_parts = [
        "---",
        f"source: {args.source}",
        f"transcribed: {transcribed_at}",
        f"model: {args.model}",
    ]
    if speakers_block:
        frontmatter_parts.append(speakers_block)
    frontmatter_parts.append("---")
    frontmatter = "\n".join(frontmatter_parts)

    output_path = Path(args.output_md)
    output_path.write_text(f"{frontmatter}\n\n{transcript_body}\n", encoding="utf-8")
    print(f"wrote {output_path} ({len(transcript_lines)} lines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
