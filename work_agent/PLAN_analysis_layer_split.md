# Analysis GUI/controller/model layer split

## Ownership

Correction: follow the existing `logic/controllers/imageWindow` architecture.
All analysis logic and the QObject worker adapter belong under
`logic/controllers/analyse`. The adapter accepts a thread pool and optional
QObject parent, not an AnalyseWindow; it must not import or retain GUI objects
for business operations. Only the worker adapter may import QtCore.

- `logic/controllers/analyse/analyseModel.py`: pure numerical fitting, alignment
  transforms, comparisons and diagnostics; no Qt or GUI imports.
- `logic/controllers/analyse/analyseTypes.py`: immutable numerical results and state.
- `logic/controllers/analyse/analyseData.py`: file loading, numerical dataset
  preparation, aligned error sorting and pier-side coordinate conversion.
- `logic/controllers/analyse/analyseController.py`: QObject worker orchestration,
  input snapshots, revisions, result publication and lifecycle handling.
- `analyseW.py` and `*Plots.py`: window controls, labels, colors, tooltips,
  view linking and rendering only.

## Implementation

1. Extract the existing calculations/types/data into the logic package without
   changing numerical formulas, tolerances or recorded-setup selection.
2. Wire the window to the logic data and logic controller directly, with no
   GUI compatibility re-exports or GUI imports in the controller.
3. Move sorting and declination sign conversion out of plot renderers into
   logic dataset methods. Preserve strict length checks and point alignment.
4. Move numerical/data/type tests to the mirrored logic test package. Retain
   worker/window/plot tests under GUI, including overlapping-load safeguards.
5. Add controller-area independence and Qt-free numerical module contracts, with
   a QtCore worker exception for the controller. Update directly
   related architecture specifications and plans; keep user docs nontechnical.

## Validation

Run combined logic/GUI analysis tests with 100% branch coverage, Ruff formatting
and lint, type checks and import contracts. Run the overall package suite with
100% coverage as the final validation. Preserve unrelated worktree changes.

## Implementation status

The numerical/type/data extraction and `AnalyseController` worker adapter now
live together under `logic/controllers/analyse`. The window supplies its thread
pool and optional QObject parenting; the controller no longer imports the
window type or retains its app. Plot-data preparation, mirrored test split,
controller independence and Qt-free numerical contracts are implemented.
No numerical formulas, comparison tolerances or worker lifecycle policy changed.
User-facing documentation remains focused on controls and workflow.
