"""
test_logic.py — Automated verification for csv-cleaner-cli.

Run via:
    pytest test_logic.py -v

All tests operate on /workspace/clean_data.csv produced by the agent's
cleaner.py.  The dirty input is /workspace/dirty_data.csv.

Failure modes deliberately tested (robustness):
  - Output file not created               → FAIL
  - File is identical to input (no-op)    → FAIL
  - Duplicates not removed                → FAIL
  - Empty / whitespace-only rows remain   → FAIL
  - Headers not stripped / lowercased     → FAIL
  - Cell whitespace not stripped          → FAIL
"""

import csv
import subprocess
import sys
from pathlib import Path

import pytest

# ── Paths ─────────────────────────────────────────────────────────────────────
INPUT_PATH  = Path("/workspace/dirty_data.csv")
OUTPUT_PATH = Path("/workspace/clean_data.csv")
SCRIPT_PATH = Path("/workspace/cleaner.py")


# ── Helpers ───────────────────────────────────────────────────────────────────

def _read_csv(path: Path) -> tuple[list[str], list[list[str]]]:
    """Return (headers, rows) from a CSV file."""
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.reader(fh)
        rows = list(reader)
    assert rows, f"CSV file is empty: {path}"
    return rows[0], rows[1:]


def _all_unique(rows: list[list[str]]) -> bool:
    seen: set[tuple] = set()
    for row in rows:
        key = tuple(row)
        if key in seen:
            return False
        seen.add(key)
    return True


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def clean_output():
    """
    Ensures clean_data.csv exists and returns (headers, data_rows).
    If the file is missing the test_output_exists test will catch it; the
    fixture simply skips remaining tests gracefully.
    """
    if not OUTPUT_PATH.exists():
        pytest.skip("clean_data.csv not found — solution may not have run yet.")
    return _read_csv(OUTPUT_PATH)


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestOutputExists:
    def test_output_file_created(self):
        """The output file must exist at the expected path."""
        assert OUTPUT_PATH.exists(), (
            f"Output file not found at {OUTPUT_PATH}. "
            "Did cleaner.py run successfully?"
        )

    def test_output_is_not_copy_of_input(self):
        """Merely copying the input file is not a valid solution."""
        assert OUTPUT_PATH.exists(), "Output file missing."
        input_text  = INPUT_PATH.read_text(encoding="utf-8-sig")
        output_text = OUTPUT_PATH.read_text(encoding="utf-8")
        assert input_text.strip() != output_text.strip(), (
            "Output file is identical to the input file — no cleaning was performed."
        )


class TestHeaderNormalisation:
    def test_headers_are_lowercase(self, clean_output):
        headers, _ = clean_output
        for h in headers:
            assert h == h.lower(), f"Header '{h}' is not lowercase."

    def test_headers_have_no_surrounding_whitespace(self, clean_output):
        headers, _ = clean_output
        for h in headers:
            assert h == h.strip(), f"Header '{h}' has surrounding whitespace."

    def test_expected_header_names(self, clean_output):
        headers, _ = clean_output
        expected = {"name", "age", "email", "city"}
        assert set(headers) == expected, (
            f"Expected headers {expected}, got {set(headers)}."
        )


class TestDataCleaning:
    def test_no_fully_empty_rows(self, clean_output):
        """Every data row must have at least one non-empty cell."""
        _, rows = clean_output
        for i, row in enumerate(rows, start=2):  # start=2: row 1 is the header
            assert any(cell != "" for cell in row), (
                f"Row {i} is fully empty and should have been removed: {row}"
            )

    def test_no_duplicate_rows(self, clean_output):
        """After cleaning, no two data rows should be identical."""
        _, rows = clean_output
        assert _all_unique(rows), "Duplicate rows found in the output."

    def test_cell_values_stripped(self, clean_output):
        """No cell value should have leading or trailing whitespace."""
        _, rows = clean_output
        for i, row in enumerate(rows, start=2):
            for j, cell in enumerate(row):
                assert cell == cell.strip(), (
                    f"Cell [{i},{j}] has unstripped whitespace: {repr(cell)}"
                )

    def test_no_nan_literals(self, clean_output):
        """Cells must not contain the literal strings 'nan', 'None', etc."""
        bad_literals = {"nan", "None", "NaN", "NULL", "null"}
        _, rows = clean_output
        for i, row in enumerate(rows, start=2):
            for j, cell in enumerate(row):
                assert cell not in bad_literals, (
                    f"Cell [{i},{j}] contains a bad missing-value literal: {repr(cell)}"
                )

    def test_no_illegal_characters(self, clean_output):
        """Rule 6: Ensure no zero-width or hidden control characters remain."""
        _, rows = clean_output
        
        bad_chars = ['\u200b', '\x0b', '\x00'] 
        
        for i, row in enumerate(rows, start=2):
            for j, cell in enumerate(row):
                for bad_char in bad_chars:
                    assert bad_char not in cell, (
                        f"Cell [{i},{j}] contains an illegal character. "
                        f"Value representation: {repr(cell)}"
                    )

class TestExpectedCounts:
    """
    Verify the exact expected row count after cleaning dirty_data.csv.

    dirty_data.csv contains:
        - 18 raw data rows (excluding header)
        -  5 fully-empty / whitespace-only rows  → removed
        -  3 duplicate rows (Alice×2, Bob×1, Dave×1, Grace×1) → 4 dupes removed
        Expected unique, non-empty rows = 18 - 5 - 4 = 9
    """

    EXPECTED_DATA_ROWS = 9

    def test_row_count(self, clean_output):
        _, rows = clean_output
        assert len(rows) == self.EXPECTED_DATA_ROWS, (
            f"Expected {self.EXPECTED_DATA_ROWS} data rows, got {len(rows)}. "
            "Check empty-row removal and deduplication."
        )

    def test_column_count(self, clean_output):
        headers, rows = clean_output
        assert len(headers) == 4, f"Expected 4 columns, got {len(headers)}."
        for i, row in enumerate(rows, start=2):
            assert len(row) == 4, (
                f"Row {i} has {len(row)} columns, expected 4: {row}"
            )


class TestRobustness:
    def test_nonexistent_input_exits_nonzero(self):
        """The script must exit with a non-zero code for a missing input file."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH),
             "--input", "/tmp/this_file_does_not_exist_xyz.csv",
             "--output", "/tmp/dummy_out.csv"],
            capture_output=True,
        )
        assert result.returncode != 0, (
            "Script should exit non-zero when the input file does not exist."
        )
