#!/usr/bin/env bash
# solve.sh — Run the golden solution inside the Docker container.
#
# Assumptions (met by the Dockerfile + test harness):
#   /workspace/dirty_data.csv   → input data (copied in by Dockerfile)
#   /workspace/cleaner.py       → solution script (copied in by test.sh)
#
# Output:
#   /workspace/clean_data.csv   → cleaned result

set -euo pipefail

INPUT="/workspace/dirty_data.csv"
OUTPUT="/workspace/clean_data.csv"
SCRIPT="/workspace/cleaner.py"

echo "[solve.sh] Running cleaner.py ..."
python3 "$SCRIPT" --input "$INPUT" --output "$OUTPUT"

echo "[solve.sh] Output written to $OUTPUT"
