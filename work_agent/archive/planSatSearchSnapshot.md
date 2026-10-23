# Plan – Fix Race Condition in `tabSat_Search.py` (Option A: Snapshot)

## Goal
Eliminate the race condition between `fillSatListName()` (main thread) and
`runnerCalcSatList()` (worker thread) by making the worker operate on an
**immutable snapshot** of the data instead of reading the live `QTableWidget`.
Additionally guard all cross-thread slots with a **generation token** so stale
queued signals from an outdated run are discarded.

## Affected File
- `../../src/mw4/gui/mainWaddon/tabSat_Search.py`
- Mirror test: `../../tests/unit_tests/gui/mainWaddon/test_tabSat_Search.py`

Scope is a single class (`SatSearch`), but touches several methods, so this
plan is recorded first per project convention.

---

## Root Cause (recap)
1. `runnerCalcSatList()` reads the live widget (`satTab.rowCount()`,
   `satTab.model().index(...)`, `satTab.isRowHidden(...)`) while
   `fillSatListName()` may clear and rebuild it concurrently.
2. `self.dataValid` has a check-then-use gap and does not guard queued signals.
3. Queued signals (`setSatListItem`, `setSatListRowHidden`, `setSatGroupTitle`)
   from an old run can land on the freshly rebuilt table.

---

## Design – Option A

### 1. Introduce a generation token
- Add `self.calcGeneration: int = 0` in `__init__`.
- Increment it at the very start of `fillSatListName()` to invalidate any
  running / pending worker and its queued signals.

### 2. Build the snapshot on the main thread
- At the end of `fillSatListName()` (after the table is fully populated),
  build an immutable snapshot list:
  `snapshot = [(row, name, sat, hidden), ...]`
  where `sat` is taken from `self.satellites.objects[name]` and `hidden`
  reflects the current row visibility.
- Pass this snapshot plus the current generation into `calcSatList()` and on
  into `runnerCalcSatList()`.

### 3. Rewrite `runnerCalcSatList(snapshot, generation)`
- Iterate only over `snapshot` – **no live widget reads** for row count,
  names, or hidden state.
- Read the filter parameters (`checkIsSunlit`, `selectTwilight`, `altMin`,
  `loc`, `eph`, `ts`) once at the start (these are cheap main-thread values;
  acceptable to read once at worker start).
- Replace the `if not self.dataValid` loop guard with
  `if generation != self.calcGeneration: break`.
- Emit results with the generation attached (see slot guarding).

### 4. Guard the cross-thread slots with the generation
- Extend the signals to carry the generation:
  - `setSatListItem = Signal(int, int, object, int)`
  - `setSatListRowHidden = Signal(int, bool, int)`
  - `setSatGroupTitle = Signal(str, bool, int)`
- In the receiving slots (`setListSatsEntry`, `updateVisibilityRow`,
  `updateTitleRunning`) return early when the received generation differs
  from `self.calcGeneration`.
- Thread the generation through `updateListSats()` and `calcSat()` so emitted
  items carry the correct token.

### 5. Keep `mutexCalc`
- Retain `mutexCalc` in `calcSatList()` to prevent two workers running at once.
- The generation token handles correctness; the mutex handles concurrency of
  worker start/finish. `runnerCalcSatList` still unlocks in a `finally` block
  to avoid dead-locking if an exception occurs.

### 6. `calcSatListDynamic()` alignment
`calcSatListDynamic()` is triggered by the `update3s` timer. It shares
`updateListSats()` with the filter worker, so it must be adapted to the
generation model. **Note:** Section 9 additionally moves its heavy math into a
worker; the points below define the shared, thread-independent requirements:

- **Pass the current generation**: emit via `updateListSats(..., generation=
  self.calcGeneration)` (the live value, since it always reflects the current
  table state) so the guarded slots accept the items.
- **Keep the `not self.dataValid` early-return** — blocks running against a
  half-rebuilt table.
- **Robustness on lookup**: guard with `sat = self.satellites.objects.get(name)`
  and skip when `sat is None` (name may be stale during teardown).
- **Interleave note**: both the dynamic path and the filter worker write
  columns 3–8 through the same generation-guarded main-thread slots, so writes
  serialize safely; a brief overwrite with the same current generation is
  acceptable and reconciled on the next tick.

### 7. Worker argument passing (confirmed)
`base/tpool.py::Worker(fn, *args, **kwargs)` forwards args to `fn`, so
`Worker(self.runnerCalcSatList, snapshot, generation)` works without changes to
the Worker class.

### 8. Additional improvements identified
- **Snapshot ownership of filter inputs**: capture `checkIsSunlit`,
  `selectTwilight`, and `altMin` on the **main thread** inside
  `fillSatListName()` (or `calcSatList()`), not inside the worker. Reading
  `self.ui.*` widget values from the worker thread is technically another
  cross-thread read; passing them as plain values into the runner removes it.
- **Progress denominator**: replace `numSats = satTab.rowCount()` with
  `len(snapshot)`; guard the `finished = (row + 1) / numSats * 100` division
  against an empty snapshot (skip the loop / emit 100 % directly when empty).
- **`satOkSGP4` logging from worker**: it calls `self.mainW.log.warning(...)`,
  which is thread-safe (logging), so it can stay; no change needed, just
  documented.
- **`mutexCalc` unlock safety**: wrap the worker body in `try/finally` so an
  exception (e.g. `KeyError`) cannot leave the mutex locked and permanently
  block future filter runs.
- **Skip empty run**: if `snapshot` is empty, emit the final title and return
  early without starting a worker to avoid an unnecessary thread hop.

### 9. Offload `calcSatListDynamic()` to a worker (recommended)
**Rationale**: although `calcSatListDynamic()` only processes the rows visible
in the viewport, each row triggers SGP4 propagation (`findRangeRate`),
`findSunlit`, and `calcAppMag`. Running these on the main thread every 3 s can
noticeably block the GUI when many rows are visible or the ephemeris lookups
are slow. Moving the heavy math to a worker keeps the UI responsive and aligns
with the project rule that longer-running calculations run in `threadPool`
workers.

**Split main-thread vs worker responsibilities** (Qt widgets/geometry must stay
on the main thread):
- **Main thread (`calcSatListDynamic`)** – keep the guards
  (`satTabWidget.currentIndex()`, `isVisible()`, `dataValid`) and build a
  snapshot of the visible rows only: read `viewport().size()`, `visualRect()`,
  `isRowHidden()`, and the row name on the main thread, producing
  `dynSnapshot = [(row, name, sat), ...]`. Read `loc`, `eph`, `ts`, `timeNow`
  here too. Then start the worker.
- **Worker (`runnerCalcSatListDynamic`)** – iterate `dynSnapshot`, do the
  propagation / sunlit / appMag math, and emit results through the same
  generation-guarded `updateListSats(..., generation=...)` path. No widget
  reads inside the worker.

**Concurrency / correctness**:
- Add a dedicated non-blocking mutex `mutexCalcDynamic` (use `tryLock()` with no
  timeout); if a previous dynamic run is still in flight when the next 3 s tick
  arrives, skip that tick instead of queueing — prevents pile-up when a run
  takes longer than the interval.
- Capture the current `self.calcGeneration` on the main thread and pass it in,
  so a refill (`fillSatListName`) invalidates stale dynamic emits exactly like
  the filter worker.
- Unlock `mutexCalcDynamic` in a `try/finally` inside the runner.
- Naming per convention: worker handle `workerCalcSatListDynamic`, runner
  method `runnerCalcSatListDynamic`.

**Trade-offs / decision**:
- Pro: keeps the GUI thread free of astronomical math; consistent worker
  pattern; safe under refills via the generation token.
- Con: adds a second worker path + mutex and slightly more complexity; the
  work per tick is usually small (visible rows only).
- **Decision**: implement it. The per-tick cost is unbounded (depends on how
  many rows the user scrolls into view and ephemeris speed), and the 3 s cadence
  means any main-thread stall is user-visible. The added complexity is modest
  and mirrors the existing filter-worker structure.

### 10. Sequencing: dynamic runs only after a completed filter
The dynamic worker must be strictly ordered **after** the filter worker:

**Enabling conditions for `calcSatListDynamic` (ALL must hold):**
1. **Tab visible / correct tab** — keep the existing test
   (`satTabWidget.currentIndex() == 0` and `satTabWidget.isVisible()`).
2. **A source is selected** — keep this as an additional enabling test (the
   list only makes sense once a satellite source is chosen).
3. `self.dataValid` is `True` (list has been generated).
4. **The filter worker has fully finished** for the *current* generation
   (tracked by a new `self.filterReady: bool`).
5. No dynamic run is already in flight (`mutexCalcDynamic.tryLock()`).

Conditions 1 and 2 remain as the "additional" gate the user requested; they are
necessary but not sufficient — the filter-completion gate (4) is added on top.

**Readiness flag lifecycle (`self.filterReady`):**
- Set `self.filterReady = False` at the very start of `fillSatListName()`
  (together with `dataValid = False` and the generation bump). This immediately
  disables any new dynamic start.
- Set `self.filterReady = True` **only** when `runnerCalcSatList` completes its
  full pass for the generation it was started with, i.e. it was *not* broken
  early by a generation change. Signal completion to the main thread via a new
  `filterDone = Signal(int)` carrying the generation; the slot `onFilterDone`
  sets `self.filterReady = True` only if `gen == self.calcGeneration`, then
  kicks an immediate `calcSatListDynamic()` so the first dynamic pass runs right
  after the filter finishes (instead of waiting up to 3 s).

**Immediate stop + restart on a new iteration:**
- When `fillSatListName()` starts a new iteration it bumps `calcGeneration` and
  clears `filterReady`. The **running dynamic worker checks the generation each
  row and breaks immediately** (already part of the generation model), so the
  dynamic pass stops as soon as possible.
- Any queued dynamic emits from the old generation are dropped by the
  generation-guarded slots.
- Dynamic will only restart once the *new* filter run finishes and
  `onFilterDone` re-sets `filterReady = True` (or a later 3 s tick finds all
  conditions satisfied).

**Result:** the ordering is `fillSatListName → filter worker (full pass) →
filterReady=True → dynamic worker`, and any new `fillSatListName` tears down the
dynamic worker at once and re-gates it behind the next completed filter.

---

## Method-Level Change List

| Method | Change |
| ------ | ------ |
| `__init__` | add `self.calcGeneration = 0`, `self.filterReady = False`; add `self.mutexCalcDynamic` and `self.workerCalcSatListDynamic` |
| `SatSearchSignals` | add `int` generation arg to the three signals; add `filterDone = Signal(int)` |
| `fillSatListName` | bump generation; set `filterReady=False`; capture filter inputs; build snapshot; pass to `calcSatList` |
| `calcSatList` | accept `snapshot`, `generation`, filter inputs; skip empty; pass to worker via `Worker` args |
| `runnerCalcSatList` | accept `snapshot`, `generation`, filter inputs; iterate snapshot; guard by generation; on full (non-broken) pass emit `filterDone(generation)`; `try/finally` unlock; progress uses `len(snapshot)` |
| `onFilterDone` | new slot: set `filterReady=True` when `gen==calcGeneration`; trigger immediate `calcSatListDynamic()` |
| `calcSat` | accept and forward `generation` |
| `updateListSats` | accept and forward `generation` in emits |
| `calcSatListDynamic` | gate on tab-visible + source-selected + `dataValid` + `filterReady`; build visible-row `dynSnapshot` + read `loc`/`eph`/`ts` on main thread; `tryLock` `mutexCalcDynamic`; start `workerCalcSatListDynamic` |
| `runnerCalcSatListDynamic` | new: iterate `dynSnapshot`; math only; guard by generation; emit via `updateListSats(generation=...)`; `try/finally` unlock `mutexCalcDynamic` |
| `setListSatsEntry` | accept `generation`; drop if stale |
| `updateVisibilityRow` | accept `generation`; drop if stale |
| `updateTitleRunning` | accept `generation`; drop if stale |

---

## Testing (target: 100 % coverage)
Add / update `../../tests/unit_tests/gui/mainWaddon/test_tabSat_Search.py`:
- `fillSatListName` increments `calcGeneration` and builds a snapshot.
- `runnerCalcSatList` processes a snapshot without touching live widget.
- Stale generation: `runnerCalcSatList` breaks early when generation changed.
- Slot guards: `setListSatsEntry`, `updateVisibilityRow`, `updateTitleRunning`
  drop calls with an outdated generation and apply with a matching one.
- `try/finally` unlock path (including exception in loop).
- Empty snapshot: `calcSatList` returns early without starting a worker.
- Sequencing gate: `calcSatListDynamic` does **not** start a dynamic worker
  while `filterReady` is `False` (filter not finished), even when tab-visible
  and a source is selected; and it does start once all conditions hold.
- `filterReady` lifecycle: `fillSatListName` clears it; `runnerCalcSatList`
  emits `filterDone(gen)` only on a full (non-broken) pass; `onFilterDone` sets
  `filterReady=True` only for the matching generation and triggers an immediate
  dynamic pass. A stale `filterDone` (old generation) is ignored.
- Immediate stop: bumping the generation in `fillSatListName` makes a running
  `runnerCalcSatListDynamic` break on its next row and drop queued emits.
- `calcSatListDynamic`: builds the visible-row `dynSnapshot`, `tryLock`s
  `mutexCalcDynamic`, and starts `runnerCalcSatListDynamic`; skips the tick when
  the mutex is already held.
- `runnerCalcSatListDynamic`: processes `dynSnapshot`, guards by generation,
  emits with the captured generation, skips rows where the sat lookup is
  `None`, and unlocks in `finally` (including on exception).
- Existing behavior (sunlit filter, twilight filter, SGP4 skip) preserved.

Mock the worker/threadPool so the runner is invoked synchronously.

---

## Finalization Steps
1. Implement edits in `tabSat_Search.py`.
2. Run the module tests to 100 % coverage.
3. Run Ruff (format + lint); resolve all findings.
4. Run the overall package test suite as the last step.

---

## Non-Goals
- No change to the astronomical calculation logic itself (`findRangeRate`,
  `findSunlit`, `calcAppMag`, `checkTwilight`); only where it runs (worker) and
  the generation guarding change.
- No new features; behavior stays identical aside from the race-condition fix
  and moving dynamic updates off the GUI thread.













