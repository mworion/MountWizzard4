# Refactoring Plan: Generic `runWorker` worker+mutex abstraction

## 1. Goal

Remove the duplicated "worker + mutex" boilerplate by turning
`MountDevice.runWorker` into a single, reusable abstraction shared by
`MountDevice` (`mount.py`) and `MountTime` (`mountTime.py`) — without
changing the public behaviour of any existing `MountDevice` caller.

## 2. Current Duplication

The same pattern (tryLock → build `Worker` → connect signal → `setattr`
→ `threadPool.start`) exists in three places:

- `src/mw4/mountcontrol/mount.py` → `MountDevice.runWorker` (the generic
  version, using `requireMountUp` + `self.mountIsUp`).
- `src/mw4/mountcontrol/mountTime.py` → `MountTime.checkMountUp`
  (hand-rolled mutex + worker).
- `src/mw4/mountcontrol/mountTime.py` → `MountTime.pollSyncClock`
  (hand-rolled mutex + worker, recently added).

## 3. Coupling Obstacle

`runWorker` currently hard-codes the precondition as
`if requireMountUp and not self.mountIsUp: return`.

- In `MountDevice`, the flag is `self.mountIsUp`.
- In `MountTime`, it is `self.parent.mountIsUp` (no `self.mountIsUp`).

A mixin reading `self.mountIsUp` therefore cannot be reused by
`MountTime` as-is.

## 4. Design

Generalise the precondition from a hard-coded bool into an optional
**`guard` callable**, and extract the body into a shared helper.

### 4.1 Shared helper (`src/mw4/base/tpool.py`)

Add a standalone function:

```python
def runWorker(
    owner: object,
    threadPool: QThreadPool,
    target: Callable[..., Any],
    clearMethod: Callable[..., Any] | None,
    workerAttr: str | None,
    *args: Any,
    mutex: QMutex | None = None,
    useResult: bool = False,
    guard: Callable[[], bool] | None = None,
    **kwargs: Any,
) -> Worker | None:
    if guard is not None and not guard():
        return None
    if mutex is not None and not mutex.tryLock():
        return None
    worker = Worker(target, *args, **kwargs)
    sig = worker.signals.result if useResult else worker.signals.finished
    if clearMethod is not None:
        sig.connect(clearMethod)
    if workerAttr is not None:
        setattr(owner, workerAttr, worker)
    threadPool.start(worker)
    return worker
```

### 4.2 `MountDevice.runWorker` (`mount.py`) — backward-compatible wrapper

Keep the **exact current signature** (`requireMountUp=True`) so no
caller or existing test changes; delegate to the helper:

```python
def runWorker(self, target, clearMethod, workerAttr, *args,
              mutex=None, useResult=False, requireMountUp=True, **kwargs):
    guard = (lambda: self.mountIsUp) if requireMountUp else None
    runWorker(self, self.threadPool, target, clearMethod, workerAttr,
              *args, mutex=mutex, useResult=useResult, guard=guard,
              **kwargs)
```

### 4.3 `MountTime` (`mountTime.py`) — use the helper

- `checkMountUp` →
  `runWorker(self, self.threadPool, self.runnerMountUp,
  self.clearMountUp, "workerCycleMountUp",
  mutex=self.mutexCycleMountUp)` (no guard; unchanged semantics).
- `pollSyncClock` →
  `runWorker(self, self.threadPool, self.runnerPollSyncClock,
  self.clearPollSyncClock, "workerPollSyncClock",
  mutex=self.mutexPollSyncClock,
  guard=lambda: self.parent.mountIsUp)`.

`runnerMountUp`, `runnerPollSyncClock`, `clearMountUp`,
`clearPollSyncClock` are unchanged.

## 5. Scope / Files Touched

- `src/mw4/base/tpool.py` (add helper + imports `QMutex`, `QThreadPool`,
  `Callable`).
- `src/mw4/mountcontrol/mount.py` (`runWorker` delegates).
- `src/mw4/mountcontrol/mountTime.py` (`checkMountUp`, `pollSyncClock`).
- Tests:
  - `tests/unit_tests/base/test_tpool.py` — new tests for the helper
    (guard blocks, mutex blocks, mutex acquired, clearMethod/workerAttr
    optional, useResult wiring).
  - `tests/unit_tests/mountcontrol/test_mount.py` — `runWorker` behaviour
    stays green (delegation), add coverage for `requireMountUp=False`
    path if not already covered.
  - `tests/unit_tests/mountcontrol/test_mountTime.py` — rewire
    `checkMountUp` / `pollSyncClock` dispatcher tests to the helper
    (patch `mw4.mountcontrol.mountTime.runWorker` or keep `Worker`
    patch, whichever keeps 100 %).

## 6. Verification

1. `pytest tests/unit_tests/base/test_tpool.py`
2. `pytest tests/unit_tests/mountcontrol/`
3. `ruff check` + `ruff format` on all touched files.
4. 100 % coverage on `tpool.py`, `mount.py`, `mountTime.py`.
5. Full suite: `pytest tests/unit_tests/`.

## 7. Risks / Notes

- Backward compatibility for `MountDevice.runWorker` is preserved by
  keeping its signature and delegating; its numerous callers are
  untouched.
- The `guard` callable is a strict generalisation of `requireMountUp`;
  `requireMountUp=True` → `guard=lambda: self.mountIsUp`,
  `requireMountUp=False` → `guard=None` (always run).
- Helper takes `owner` + `threadPool` explicitly instead of relying on
  `self`, so it works for any object regardless of where `mountIsUp`
  lives — this is what unblocks `MountTime`.
- No change to mutex objects, cycle timings, or signal semantics.

