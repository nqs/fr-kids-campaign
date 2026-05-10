#!/usr/bin/env bash
set -euo pipefail

SCRIPT="$(cd "$(dirname "$0")/.." && pwd)/scripts/transcribe.sh"
PASS=0
FAIL=0

pass() { echo "PASS: $1"; PASS=$((PASS + 1)); }
fail() { echo "FAIL: $1"; FAIL=$((FAIL + 1)); }

assert_exits_nonzero() {
    local desc="$1"; shift
    if SKIP_PYENV=1 bash "$SCRIPT" "$@" 2>/dev/null; then
        fail "$desc (expected non-zero exit)"
    else
        pass "$desc"
    fi
}

# No arguments
assert_exits_nonzero "exits with error when given no arguments"

# Too many arguments
assert_exits_nonzero "exits with error when given too many arguments" a b c

# Non-existent input file
assert_exits_nonzero "exits with error when input file does not exist" /nonexistent/file.m4a

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
