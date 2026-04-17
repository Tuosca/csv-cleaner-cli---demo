#!/usr/bin/env bash
# test.sh — Entry point for the automated test harness.
#
# This script:
#   1. Copies the agent's solution into /workspace/
#   2. Runs the solution to produce clean_data.csv
#   3. Runs pytest to verify the output
#
# Exit codes:
#   0 → all tests passed  (CORRECT solution)
#   1 → any test failed   (INCORRECT / incomplete solution)
#
# Usage (inside the Docker container):
#   bash tests/test.sh <path_to_agent_solution_dir>
#
# If no argument is given, the golden solution is used (for self-verification).

set -uo pipefail

# ── Config ────────────────────────────────────────────────────────────────────
WORKSPACE="/workspace"
INPUT_CSV="$WORKSPACE/dirty_data.csv"
OUTPUT_CSV="$WORKSPACE/clean_data.csv"

# ── Determine solution source ─────────────────────────────────────────────────
SOLUTION_DIR="${1:-/solution}"    # default: golden solution dir mounted at /solution

AGENT_SCRIPT="$SOLUTION_DIR/cleaner.py"

if [[ ! -f "$AGENT_SCRIPT" ]]; then
    echo "[test.sh] ERROR: cleaner.py not found at $AGENT_SCRIPT" >&2
    exit 1
fi

# ── Step 1: Copy solution into workspace ──────────────────────────────────────
echo "[test.sh] Copying solution to $WORKSPACE ..."
cp "$AGENT_SCRIPT" "$WORKSPACE/cleaner.py"

# ── Step 2: Run the solution ──────────────────────────────────────────────────
echo "[test.sh] Running cleaner.py ..."
python3 "$WORKSPACE/cleaner.py" --input "$INPUT_CSV" --output "$OUTPUT_CSV"
RUN_EXIT=$?

if [[ $RUN_EXIT -ne 0 ]]; then
    echo "[test.sh] FAIL: cleaner.py exited with code $RUN_EXIT" >&2
    exit 1
fi

# ── Step 3: Run pytest ────────────────────────────────────────────────────────
echo "[test.sh] Running test suite ..."

# Install pytest if not present (slim image may not have it)
if ! python3 -m pytest --version > /dev/null 2>&1; then
    pip install --quiet pytest
fi

python3 -m pytest /tests/test_logic.py -v --tb=short
TEST_EXIT=$?

# ── Summary ───────────────────────────────────────────────────────────────────
if [[ $TEST_EXIT -eq 0 ]]; then
    echo ""
    echo "✅  All tests PASSED — solution is correct."
else
    echo ""
    echo "❌  One or more tests FAILED — solution is incorrect."
fi

exit $TEST_EXIT
