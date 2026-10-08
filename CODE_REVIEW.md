# Code Review Report

**Project:** MountWizzard4  
**Review date:** 2026-10-08  
**Scope:** Current repository codebase; 268 production Python modules and 217
unit-test modules. Generated GUI widgets were excluded.

## Findings

### Medium — Model matching can divide by zero

**Location:** `src/mw4/logic/modelBuild/modelRunSupport.py:120-128`

`findKeysSourceInDest()` divides the HA and DEC differences by the corresponding
reference-model coordinates. A reference point with `ha == 0` or `dec == 0`
therefore raises `ZeroDivisionError` and aborts model matching. Both are valid
astronomical coordinates.

### Low — Plate-solver test fixtures clean a shared temporary directory

**Locations:**

- `tests/unit_tests/logic/plateSolve/test_astap.py:20-26`
- `tests/unit_tests/logic/plateSolve/test_astrometry.py:20-26`
- `tests/unit_tests/logic/plateSolve/test_watney.py:20-26`

Each fixture removes files in the shared `tests/work/temp` directory according
to a filename substring check. This can delete unrelated local files in that
directory when the tests run. Prefer isolated temporary directories or cleanup
limited to files created by each fixture.

## Validation

- `uv run ruff format --check src tests`: passed.
- `uv run ruff check src tests`: passed.
- `uv run pytest tests/unit_tests`: **4,844 passed, 38 skipped**.
- `uv run pyrefly check`: reported **627 errors**. The check is currently
  commented out in the Ubuntu CI workflow.
- A default `uv run pytest` run showed failures in `tests/stress_tests` and was
  stopped before completion; those failures were not diagnosed.

## Worktree note

The plate-solver test fixtures clean and recreate files under
`tests/work/temp`. That directory contained untracked files before the review,
so their contents may have changed during the test run.
