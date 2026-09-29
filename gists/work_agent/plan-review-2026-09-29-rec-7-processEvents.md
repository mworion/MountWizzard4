# Plan – Review 2026-09-29, Point 3.2 / Recommendation 7

**Status:** implemented

Remove `QApplication.processEvents()` from row/file loops.

Source: `2026-09-29-review.md`, section 3.2

---

## 1. Current State

| File                            | Method                 | Loop over                         | Why `processEvents()` is there     |
|---------------------------------|------------------------|-----------------------------------|------------------------------------|
| `gui/mainWaddon/tabAsteroid.py` | `fillAsteroidListName` | `asteroids.objects` (up to ~40 k) | Keep the GUI responsive while filling |
| `gui/mainWaddon/tabComet.py`    | `fillCometListName`    | `comets.objects` (~1 k)           | Same                               |
| `gui/mainWaddon/tabTools_Rename.py` | `renameRunGUI`     | FITS files in `renameDir`         | Repaint `renameProgress`           |

Findings:

- **Asteroid/Comet:** Each row calls `insertRow` (a model reset per row),
  creates up to 6 `QTableWidgetItem`s, and runs a full event pass. The event
  pass is the main cost, and the table repaints after every row. The loop
  already runs in the GUI thread, because `dataLoaded` is emitted from a worker
  and delivered through a queued connection. While the loop runs, the user can
  trigger a second `dataLoaded` (source change) or a `prog*` upload on a
  half-filled table. That is the re-entrancy risk.
- The two fill methods are ~95 % identical. Only the source keys and the
  column 3 content differ (perihelion date for comets, perihelion distance
  for asteroids).
- **Rename:** This is not a table fill. It is blocking file I/O (FITS open +
  rename) in the GUI thread, and `processEvents()` exists only to show the
  progress. The loop also iterates `renameDir.glob(...)` while it renames files
  in that same directory, so renamed files can be seen twice.

---

## 2. Target Design

### 2.1 Asteroid / Comet – batch fill without event passes (Recommended, S)

For both `fillAsteroidListName` and `fillCometListName`:

```python
def fillAsteroidListName(self) -> None:
    table = self.ui.listAsteroids
    table.setUpdatesEnabled(False)
    table.setSortingEnabled(False)
    table.setRowCount(0)
    table.setRowCount(len(self.asteroids.objects))
    for row, name in enumerate(self.asteroids.objects):
        ...  # setItem(row, col, entry) as today, without insertRow
    table.setUpdatesEnabled(True)
    self.asteroids.dataValid = True
    self.filterListAsteroids()
```

- One `setRowCount(n)` instead of `n × insertRow`.
- `setUpdatesEnabled(False/True)` removes the per-row repaints.
- `processEvents()` and the `QApplication` import are removed.
- `filterListAsteroids` / `filterListComets` get the same
  `setUpdatesEnabled` wrapping, because `setRowHidden` per row has the same
  repaint cost.
- Use `try/finally` so updates are always turned back on.

Expected effect: ~40 k rows go from seconds (with a visible fill) to well below
one second, and nothing re-enters during the fill.

### 2.2 Rename – move file work into a worker (S/M)

Following the project worker rules:

- `renameRunGUI` validates the input and **snapshots** everything the worker
  needs on the GUI thread: the list of files (`list(renameDir.glob(search))`,
  which also fixes the rename-while-globbing issue), `newObjectName`, and the
  current selector texts.
- New `runnerRenameFiles(files, newObjectName, selections)` runs in
  `self.app.threadPool` via
  `self.workerRenameFiles = startWorker(self.workerRenameFiles, ...)`.
- `renameFile(fileName, newObjectName, selections)` no longer reads `self.ui`,
  so it is thread-safe.
- Progress goes back through a new `RenameSignals(QObject)` with
  `progress = Signal(int)`, connected in `__init__` to
  `renameProgress.setValue`.
- The worker `result` (the number of files) goes to `renameFinished` for the
  final message. The worker `finished` signal goes to `renameEnableGUI`, so
  the button is also enabled again after an error.
- `renameStart` is disabled while the worker runs, so a second run cannot
  start.

### 2.3 Optional follow-up – model/view for catalogs (M, not in scope)

A shared `AstroObjectTableModel(QAbstractTableModel)` with a `QTableView`
removes the per-item cost completely. It is not planned now, because it changes
the `.ui` widget type (`QTableWidget` → `QTableView`, a Designer change),
`AstroObjects.progSelected` (`selectedItems()`), and `progFiltered`. With 2.1
the remaining cost is small, so this only makes sense if the catalog sizes grow
(for example, full MPCORB).

---

## 3. Steps

1. `tabAsteroid.py`: rewrite `fillAsteroidListName` and wrap
   `filterListAsteroids` (2.1). Remove the `QApplication` import.
2. `tabComet.py`: same for `fillCometListName` / `filterListComets`.
3. `tabTools_Rename.py`: add `RenameSignals`, `workerRenameFiles`,
   `runnerRenameFiles`, a snapshot in `renameRunGUI`, and a
   parameterized `renameFile` (2.2). Remove the `QApplication` import.
4. Tests (`../../tests/unit_tests/gui/mainWaddon`):
   - `test_tabAsteroid.py`, `test_tabComet.py`: check row count and cell content
     after the fill, and check that updates are enabled again afterwards
     (including the exception path in `finally`). Also cover the filter
     wrapping.
   - `test_tabTools_Rename.py`: `renameRunGUI` starts the worker with a correct
     snapshot; `runnerRenameFiles` emits `progress` / `finished`; `renameFile`
     works with explicit parameters; the button is disabled and enabled again;
     the existing error paths (invalid dir, no files) still work.
5. Update the review: mark 3.2 / recommendation 7 as done in section 10, and
   remove the `processEvents` count from the table in section 1.
6. Ruff format/check, full `pytest tests/unit_tests --cov` → 100 %.

---

## 4. Risks

| Risk                                                    | Mitigation                                                    |
|---------------------------------------------------------|---------------------------------------------------------------|
| GUI stays frozen if an exception happens while updates are off | `try/finally` around the fill                                 |
| Short freeze remains for very large catalogs            | Acceptable at current sizes; 2.3 is the next step if needed   |
| Worker reads Qt widgets                                 | The worker only gets snapshotted plain values                 |
| Rename run started twice                                | Button disabled until `finished`                              |
