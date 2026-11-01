# AnalyseWindow Improvement Plan

## Scope

Improve `src/mw4/gui/extWindows/analyseW.py` for correctness, robustness,
readability, and testability without changing the existing UI or model-file
format. Keep the work limited to `AnalyseWindow` and its unit tests.

## Plan

1. **Correct error sorting alignment** — completed
   - In `drawErrorAscending`, sort each point's error, star index, and pier side
     together so the plotted coordinates and colors remain associated.
   - Add a unit test with deliberately unsorted errors and distinct indices and
     pier sides; assert the plotted data remains aligned after sorting.

2. **Make signal setup idempotent** — completed
   - Move persistent signal/slot connections out of `showWindow` into one-time
     initialization, while preserving the window's current show behavior.
   - Add a test that calls `showWindow` more than once and verifies each user
     action invokes its slot only once.

3. **Validate loaded model data** — completed
   - Define the minimum structure required by `writeGui` and `generateDataSets`
     (non-empty list of records and the keys those methods consume).
   - Reject malformed or incomplete model content through the existing
     application logging/error-reporting convention; do not silently substitute
     a success-shaped empty model.
   - Add tests for empty input, missing required keys, and valid model data.

4. **Reduce duplicated plot setup** — completed
   - Extract a small private-to-the-module helper or class method for shared
     Alt/Az chart labels, ticks, ranges, and ISO-contour settings.
   - Keep chart-specific widgets and error arrays explicit at call sites.
   - Add focused tests for the shared setup and retain the existing per-chart
     behavior tests.

5. **Validate** — focused tests (`45 passed`) and Ruff checks pass. The full
   package suite finished with 5319 passed, 37 skipped, 7 failures, and 2 teardown
   errors. Failures are in stress tests outside the focused AnalyseWindow suite;
   full-suite validation is therefore not clean.

## Out of Scope

- Changing the `.ui` file or the on-disk model format.
- Moving plotting or Qt responsibilities out of the GUI layer.
- Broad refactoring of unrelated windows or application-wide signal patterns.
