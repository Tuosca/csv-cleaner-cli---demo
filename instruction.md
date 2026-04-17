# Task: CSV Cleaner CLI

## Background

Real-world CSV exports are often messy: duplicate rows, stray whitespace,
empty lines, inconsistent column names, and missing values all make downstream
analysis error-prone. Your job is to write a command-line tool that
**reliably cleans** a dirty CSV file and writes a tidy version to disk.

---

## Task Description

Write a Python CLI script called **`cleaner.py`** that reads a dirty CSV file,
applies a series of cleaning rules, and writes the cleaned result to an output
file.

### Invocation

```bash
python cleaner.py --input <input_path> --output <output_path>
```

Both `--input` and `--output` are **required** arguments.  
The script must exit with code `0` on success and a non-zero code on failure
(e.g., file not found, unreadable CSV).

---

## Cleaning Rules (must all be implemented)

| # | Rule | Details |
|---|------|---------|
| 1 | **Strip whitespace from headers** | Column names must have leading/trailing spaces removed, then be lowercased. |
| 2 | **Strip whitespace from values** | Every cell value must have leading/trailing whitespace removed. |
| 3 | **Remove fully-empty rows** | Any row where **all** cells are empty (or whitespace-only) must be dropped. |
| 4 | **Remove duplicate rows** | Keep only the **first** occurrence of each unique row (after cleaning). |
| 5 | **Normalise missing values** | Cells that are empty after stripping must be written as an empty string `""` (not the literal string `"nan"` or `"None"`). |
| 6 | **Remove illegal characters** |

---

## Input / Output Contract

* Input file: a UTF-8 encoded CSV file (may contain a BOM).
* Output file: a UTF-8 encoded CSV file **without** BOM.
* The output must retain the **original column order** (after header normalisation).
* The output must include the header row as the first line.

---

## Files Provided

| File | Location | Purpose |
|------|----------|---------|
| `dirty_data.csv` | `/workspace/dirty_data.csv` | The dirty input file your script must clean. |

Your script should write the cleaned output to `/workspace/clean_data.csv`
when called as:

```bash
python cleaner.py --input /workspace/dirty_data.csv --output /workspace/clean_data.csv
```

---

## Constraints

* Python standard library only — **no third-party packages** (no pandas, no numpy).
* The script must run correctly under **Python 3.11**.
* Total runtime must be under **30 seconds** for inputs up to 100 000 rows.

---

## Evaluation

Your solution is evaluated by an automated test suite (`tests/test.sh`).
The suite checks:

1. The output file is created at the specified path.
2. All five cleaning rules are correctly applied.
3. Row and column counts match the expected clean dataset.
4. The script rejects a non-existent input file with a non-zero exit code.

A solution that merely copies the input file to the output path will **fail**
the test suite.
