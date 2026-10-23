# Threading Review – `startWorker` Usage

Scope: all call sites of `startWorker` / the underlying `Worker`, `WorkerSignals`,
`setupWorker` in `../../src/mw4/base/tpool.py`, reviewed for correct threading, mutex /
lock handling, parameter passing, deadlocks and improvement potential.

---

## 1. The mechanism (`../../src/mw4/base/tpool.py`)

```python
def startWorker(
    worker,
    threadPool,
    target,
    *args,
    resultMethod=None,
    finishedMethod=None,
    guard=None,
    **kwargs,
):
    if guard is not None and not guard():
        return None
    if worker is None:
        worker = setupWorker(
            target, *args, resultMethod=resultMethod, finishedMethod=finishedMethod, **kwargs
        )
    else:
        worker.args = args
        worker.kwargs = kwargs
    if not worker.mutex.tryLock():
        return worker
    threadPool.start(worker)
    return worker
```

Design intent (confirmed by tests in `../../tests/unit_tests/base/test_tpool.py`):

- `guard` → skip start entirely, return `None`.
- per‑`Worker` `QMutex` → **"skip if this worker is already running"** (re‑entrancy
  guard). `run()` unlocks the mutex in its `finally` block.
- `worker` may be reused to avoid re‑allocating / re‑connecting signals.

The pool is a single shared `QThreadPool` (`mainApp.py`), `MAX_THREAD_COUNT = 30`.

**Overall the design is sound and there is no classic all‑threads deadlock:** no
worker blocks on the pool waiting for another pooled worker, and the mutex is
per‑worker (never a shared lock two workers contend on), so a cyclic wait cannot
form. The issues below are races, silent no‑ops and starvation/shutdown risks
rather than hard deadlocks.

---

## 2. Findings

| # | Severity | Area | Status | Summary |
|---|----------|------|--------|---------|
| 1 | **High** | tpool | ✅ Fixed | Args/kwargs of a reused worker are overwritten *before* the mutex check → data race with the in‑flight run |
| 2 | **High** | tpool + uploadPopupW | ⚪ Accepted (by design) | Reused worker ignores `resultMethod` / `finishedMethod` — intended and verified; callers create a fresh worker when callbacks change |
| 3 | **Med**  | plateSolve | ✅ Fixed | `workerSolveLoop` started via `threadPool.start()` bypassing `startWorker` → `run()` unlocks a never‑locked `QMutex` (undefined behavior) |
| 4 | **Med**  | many | ⏳ Deferred | `startWorker` returning the same worker on a busy `tryLock` is a silent no‑op; callers cannot tell "started" from "skipped" |
| 5 | **Med**  | shutdown | ✅ Fixed | Long‑running loop workers + `waitForDone(10000)` depend on stop flags being set first; a missed/blocking loop stalls close/profile switch up to 10 s |
| 6 | **Low**  | pool sizing | ⚪ Accepted (by design) | Persistent loop workers permanently occupy pool threads → starvation risk under many devices |
| 7 | **Low**  | tpool | ⚪ Accepted (by design) | `guard` is evaluated in the caller thread and re‑checked nowhere; intended as a start‑time check only — runners handle later state changes |
| 8 | **Low**  | tpool | ✅ Fixed | Broad `except (... Exception ...)` patterns elsewhere aside, `Worker.run` only catches a fixed tuple; other exceptions escape into the Qt thread and skip the `finished`/unlock path |

---

## 3. Details & recommendations

### Finding 1 — Args race on worker reuse (High)

```python
else:
    worker.args = args        # <-- mutates a possibly still-running worker
    worker.kwargs = kwargs
if not worker.mutex.tryLock():
    return worker             # busy: we already corrupted its args
```

If the worker is currently executing, `worker.args`/`worker.kwargs` are overwritten
**before** `tryLock()` detects that it is busy. The running `Worker.run()` reads
`self.fn(*self.args, **self.kwargs)`, so a rapid re‑trigger can change the arguments
of the run already in progress.

Affected call sites are those that pass real arguments and can be re‑triggered
while running:

- `mount.calcTLE(start)`, `mount.progTrajectory(alt, az, replay=...)`
- `fileHandler.runnerLoadImage(imagePath)`
- `videoBase.runnerVideo(source, frameRate)`
- `cameraSGPro.runnerExpose`

The argument‑less loop workers (INDI/ASCOM/Alpaca/SGPro/HID) are not affected in
practice.

**Recommendation:** acquire the lock first, only then update args:

```python
if worker is None:
    worker = setupWorker(...)
if not worker.mutex.tryLock():
    return worker
worker.args = args
worker.kwargs = kwargs
threadPool.start(worker)
```

### Finding 2 — Reused worker ignores `resultMethod` / `finishedMethod` (Accepted, by design)

`setupWorker` (which does the `.connect()`) runs only on the `worker is None`
branch. On reuse the new `resultMethod` / `finishedMethod` arguments are intentionally
not re‑connected and the worker keeps the connections made on first creation.

This is the intended contract: a reused worker keeps its original callbacks. Call
sites where the callback target changes per call (e.g. `uploadPopupW.py::exec()`,
which binds `finishedMethod=self.loop.quit` to a fresh `QEventLoop`) create a brand
‑new worker (`workerUploadFile is None`) for each run, so the correct loop is always
connected. This behavior has been reviewed and verified.

**Decision:** no change. The "reused workers keep their original callbacks" contract
is intentional; call sites that need per‑call callbacks must start from a fresh
worker (as they already do).

### Finding 3 — `plateSolve` bypasses `startWorker` (Med)

```python
self.workerSolveLoop: Worker = Worker(self.runnerSolveLoop)
...
self.threadPool.start(self.workerSolveLoop)  # no tryLock()
```

`Worker.run()` unconditionally calls `self.mutex.unlock()` in its `finally`. Because
the mutex was never locked here, this unlocks a non‑locked `QMutex` — undefined
behavior in Qt (and inconsistent with every other call site). Double‑start is
prevented only by the `solveLoopRunning` bool, not the mutex.

**Resolution:** routed through `startWorker` (consistent lock handling) **and** added a
`locked` flag so `Worker.run()` only unlocks when it actually acquired the mutex —
a directly started worker can no longer unlock a non‑locked `QMutex`.

### Finding 4 — Silent no‑op on busy worker (Med)

When `tryLock()` fails the function returns the *same* worker object, so the common
pattern `self.workerX = startWorker(self.workerX, ...)` looks identical whether the
work was started or skipped. Callers that need the poll to actually run (e.g. mount
cycle polls) have no signal that a tick was dropped.

**Recommendation (deferred):** this is acceptable as a "coalesce/skip if busy"
policy, but could be made observable — return a status or `None` when skipped, or add
a debug log (`"worker %s busy, skipped"`). At minimum document the three return states
(`None` = guard/skip‑new, `worker` started, `worker` skipped‑busy) which currently
overload the return value ambiguously. **Kept for a later change.**

### Finding 5 — Shutdown / profile‑switch ordering (Med)

`mainWindow.closeEvent` and `switchProfile` do:

```python
self.app.dReg.stopDevices()  # must set every stopEvent / stop flag
...
self.threadPool.waitForDone(10000)
```

Correctness depends on `stopDevices()` setting **all** loop terminators
(`stopEvent.set()`, `commandRunning=False`, `solveLoopRunning=False`, INDI
`txQ.put(None)`, `pollStatusRunState=False`, video/keypad stops) before
`waitForDone`. Any loop that misses its stop signal blocks the full 10 s timeout,
and profile switching then starts new workers on a still‑busy pool.

**Recommendation:** audit `stopDevices()` against the full list of persistent loops
and add a test that asserts `threadPool.activeThreadCount() == 0` shortly after
`stopDevices()`. Consider logging when `waitForDone` actually times out.

### Finding 6 — Persistent loop workers occupy pool threads (Accepted, by design)

Each connected device with a loop runner holds a pool thread for its entire
lifetime: INDI uses **two** (`runnerQueueClient` + `runnerProcessRxQueue`), plus
ASCOM/Alpaca/SGPro/HID (1 each), `plateSolve` solve loop, video, keypad,
upload poll‑status. With `MAX_THREAD_COUNT = 30` and many simultaneous devices the
transient workers (model polling, TLE, photometry, file load) compete for the
remainder. Not a deadlock, but latency/starvation risk.

**Decision:** keep a single shared `QThreadPool`. `MAX_THREAD_COUNT = 30` provides
ample headroom for the realistic number of concurrent loop devices plus transient
workers, and one common pool keeps lifecycle/shutdown handling simple. No change.

### Finding 7 — Guard evaluated once in caller thread (Accepted, by design)

`guard=lambda: self.mountIsUp` is checked synchronously in the calling thread. It
only prevents *starting*; nothing re‑checks after the worker is queued.

**Decision:** intended behavior — the guard is a start‑time check only. Runners
already handle a state change (e.g. mount going down) during execution, so no
re‑check after queueing is needed. No change.

### Finding 8 — Narrow exception capture in `Worker.run` (Low)

`run()` catches a fixed tuple `(OSError, ValueError, RuntimeError, TypeError,
AttributeError, KeyError)`. Any other exception propagates out of `run()` on the pool
thread, skipping `signals.finished.emit()` **and** `self.mutex.unlock()` — leaving
the worker's mutex permanently locked, so that worker can never be restarted (a
localized, per‑worker "stuck" state). Given no `# pragma: no cover` policy and 100 %
coverage goal, the untested escape path is also a coverage gap.

**Recommendation:** put `self.mutex.unlock()` + `finished.emit()` in `finally` (already
the case) but broaden the `except` to `except Exception` for the log/emit path so the
worker always releases its mutex, or add a bare `finally` that guarantees unlock even
on unexpected exception types (it already runs, but the exception then re‑raises on
the pool thread — wrap to swallow after logging).

---

## 4. Summary

- **No hard deadlock** exists in the current design (per‑worker mutex, no nested
  pool waits).
- **Fixed:** #1 (args race on reuse), #3 (plateSolve mutex asymmetry), #5 (shutdown
  drain logging) and #8 (unlock guarantee on unexpected exceptions).
- **Accepted as designed:** #2 (reused workers keep original callbacks — verified),
  #6 (single shared thread pool with `MAX_THREAD_COUNT = 30`), #7 (guard is a
  start‑time check only).
- **Deferred:** #4 (make the "skipped because busy" return value observable) — kept
  for a later change.

---

## 5. Resolution status

Implemented (findings 1, 3, 5, 8):

- **#1** — `startWorker` now acquires `worker.mutex.tryLock()` **before** assigning
  `worker.args`/`worker.kwargs`; a busy (already running) worker is no longer mutated.
- **#3** — `Worker` gained a `locked` flag set by `startWorker` on a successful lock;
  `run()` only unlocks when `locked` is set, so a directly started worker can never
  unlock a non‑locked mutex. `plateSolve.startSolveLoop` now routes through
  `startWorker` for consistency.
- **#5** — `mainWindow.closeEvent` and `switchProfile` now check the return of
  `threadPool.waitForDone(10000)` and log a warning with the active thread count when
  the pool fails to drain in time.
- **#8** — `Worker.run` catches unexpected exceptions in an additional
  `except Exception` branch (logs + emits `error`); the `finally` block always releases
  the mutex (when held) and emits `finished`, so an unexpected exception can no longer
  leave a worker permanently locked or escape into the pool thread.

Accepted as designed (no change):

- **#2** — reused workers intentionally keep their original callbacks; call sites with
  per‑call callbacks start from a fresh worker. Reviewed and verified.
- **#6** — a single shared `QThreadPool` is kept by decision; `MAX_THREAD_COUNT = 30`
  gives sufficient headroom for concurrent loop devices plus transient workers.
- **#7** — `guard` is intended as a start‑time check only; runners handle later state
  changes during execution.

Deferred:

- **#4** — making the busy/skipped return value observable is kept for a later change.
