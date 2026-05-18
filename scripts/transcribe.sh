#!/usr/bin/env bash
set -euo pipefail

usage() {
    echo "Usage: $0 <input_audio_file> [output_file]" >&2
    exit 1
}

if [ $# -lt 1 ] || [ $# -gt 2 ]; then
    usage
fi

INPUT="$1"
OUTPUT="${2:-${INPUT}.md}"

if [ ! -f "$INPUT" ]; then
    echo "Error: input file '$INPUT' not found." >&2
    exit 1
fi

# Resolve to absolute paths before changing directory.
INPUT="$(cd "$(dirname "$INPUT")" && pwd)/$(basename "$INPUT")"
OUTPUT_DIR="$(cd "$(dirname "$OUTPUT")" && pwd)"
OUTPUT="${OUTPUT_DIR}/$(basename "$OUTPUT")"
SCRIPTS_DIR="$(cd "$(dirname "$0")" && pwd)"

cd "$SCRIPTS_DIR"

if [ "${SKIP_PYENV:-0}" != "1" ]; then
    if ! command -v pyenv >/dev/null 2>&1; then
        echo "Error: pyenv is not installed or not on PATH." >&2
        echo "Install it from https://github.com/pyenv/pyenv#installation" >&2
        exit 1
    fi

    PYENV_VERSIONS="$(pyenv versions --bare)"
    if ! grep -qx "3.11.9" <<<"$PYENV_VERSIONS"; then
        echo "Error: pyenv does not have Python 3.11.9 installed." >&2
        echo "Install it with: pyenv install 3.11.9" >&2
        exit 1
    fi

    pyenv local 3.11.9
fi

if [ ! -d "whisper-env" ] || [ ! -f "whisper-env/bin/activate" ]; then
    echo "whisper-env not found; creating virtual environment..."
    python -m venv whisper-env
fi

# shellcheck disable=SC1091
source whisper-env/bin/activate

if ! command -v whisperx >/dev/null 2>&1; then
    echo "whisperx not found in whisper-env; installing..."
    pip install --upgrade pip
    pip install whisperx anthropic
fi

if [ -n "${HF_TOKEN:-}" ]; then
    HF_TOKEN_VALUE="$HF_TOKEN"
elif [ -f huggingface.token ]; then
    HF_TOKEN_VALUE="$(cat huggingface.token)"
else
    echo "Error: no Hugging Face token found." >&2
    echo "Set the HF_TOKEN environment variable or create a 'huggingface.token' file in $(pwd)." >&2
    exit 1
fi

WHISPERX_TMPDIR="$(mktemp -d)"
trap 'rm -rf "$WHISPERX_TMPDIR"' EXIT

MODEL="${WHISPERX_MODEL:-large-v2}"

whisperx "$INPUT" \
    --model "$MODEL" \
    --diarize \
    --min_speakers 4 \
    --max_speakers 7 \
    --hf_token "$HF_TOKEN_VALUE" \
    --compute_type int8 \
    --output_format json \
    --output_dir "$WHISPERX_TMPDIR"

INPUT_STEM="$(basename "$INPUT")"
INPUT_STEM="${INPUT_STEM%.*}"

# Discover an optional speaker mapping file next to the audio.
AUDIO_DIR="$(dirname "$INPUT")"
if [ -f "${AUDIO_DIR}/speakers.json" ]; then
    SPEAKERS_ARG="--speakers ${AUDIO_DIR}/speakers.json"
elif [ -f "${AUDIO_DIR}/speakers.yaml" ]; then
    SPEAKERS_ARG="--speakers ${AUDIO_DIR}/speakers.yaml"
else
    SPEAKERS_ARG=""
fi

# Auto-detect speaker names from a roll-call intro if no mapping file exists.
if [ -z "$SPEAKERS_ARG" ] && [ -n "${ANTHROPIC_API_KEY:-}" ]; then
    echo "No speakers.json found; attempting auto-detection from intro..."
    REPO_ROOT="$(cd "$SCRIPTS_DIR/.." && pwd)"
    python "$SCRIPTS_DIR/detect_speakers.py" \
        "$WHISPERX_TMPDIR/${INPUT_STEM}.json" \
        "$INPUT" \
        --campaign-dir "$REPO_ROOT/campaign" || true
    if [ -f "${AUDIO_DIR}/speakers.json" ]; then
        SPEAKERS_ARG="--speakers ${AUDIO_DIR}/speakers.json"
        echo "Auto-detected speaker mapping written to ${AUDIO_DIR}/speakers.json"
    fi
fi

# shellcheck disable=SC2086
python "$SCRIPTS_DIR/format_transcript.py" \
    "$WHISPERX_TMPDIR/${INPUT_STEM}.json" \
    "$OUTPUT" \
    --source "$(basename "$INPUT")" \
    --model "$MODEL" \
    $SPEAKERS_ARG

# Generate a session log from the transcript if ANTHROPIC_API_KEY is available.
if [ -n "${ANTHROPIC_API_KEY:-}" ]; then
    REPO_ROOT="$(cd "$SCRIPTS_DIR/.." && pwd)"
    python "$SCRIPTS_DIR/update_session_log.py" \
        "$OUTPUT" \
        "$INPUT" \
        --campaign-dir "$REPO_ROOT/campaign" \
        --sessions-dir "$REPO_ROOT/sessions" || true
fi