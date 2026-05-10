# Plan: `ascomClass.py` — Single-Loop Architecture (in-place edit)

Replace the timer-driven multi-worker design of `AscomClass` with a
single `threading.Event`-controlled loop worker that unifies connection
management, polling, and `queue.Queue`-based command dispatch — without
any `QTimer` instances and without multiple worker objects.

> **Scope**: The existing file `src/mw4/base/ascomClass.py` is edited
> in-place. The class name remains `AscomClass`. No new file is created.
> All subclasses already import from `ascomClass` — their imports
> require no change.

**Change history**
| Date | Change |
|------|--------|
| 2026-05-10 | Initial plan |
| 2026-05-10 | `self.propertyExceptions` removed entirely |
| 2026-05-10 | `callerInitUnInit` and `callMethodThreaded` removed; `CoInitialize`/`CoUninitialize` bracket the entire loop; `Dispatch` moved inside loop |
| 2026-05-10 | Naming convention: no-suffix = native (loop thread), `Queued`-suffix = enqueued (GUI thread); camera exposure becomes loop-internal `pollData` state machine |

---

## Naming convention

| Method | Thread | Purpose |
|--------|--------|---------|
| `getAscomProperty(prop)` | loop | direct COM read |
| `setAscomProperty(prop, value)` | loop | direct COM write |
| `callAscomMethod(name, param)` | loop | direct COM method call, returns value |
| `getAndStoreAscomProperty(prop, elem)` | loop | read + store in `self.data` |
| `setAscomPropertyQueued(prop, value)` | GUI | enqueue a write command |
| `callAscomMethodQueued(name, param)` | GUI | enqueue a method-call command |

`processCommandQueue` (loop thread) drains the queue and calls
`setAscomProperty` / `callAscomMethod` natively.

---

## Part 1 – `ascomClass.py`

### Step 1 – Imports
Remove: `Callable`, `QMutex`, `QTimer`. Add: `queue`, `threading`,
`dataclass`, `field`.

### Step 2 – `CommandItem` dataclass (module level)
`cmdType: str`, `name: str`, `args: tuple`, `value: Any`

### Step 3 – `__init__` changes
Remove: `tM`, all per-task workers, `propertyExceptions`, both QTimers.
Add: `commandQueue`, `stopEvent`, `workerCommunicationLoop`.

### Step 4 – Remove obsolete methods
`startAscomTimer`, `stopAscomTimer`, `callerInitUnInit`,
`callMethodThreaded`, `processPolledData`, `workerPollData`,
`workerGetInitialConfig`, `workerPollStatus`, `workerConnectDevice`,
old `pollStatus`, old `getInitialConfig` dispatcher, old `pollData`
dispatcher.

### Step 5–10 – New/updated methods
`getAscomProperty`, `setAscomProperty`, `callAscomMethod` (direct),
`getAndStoreAscomProperty` (unchanged), `setAscomPropertyQueued`,
`callAscomMethodQueued`, `processCommandQueue`, `connectDevice`,
`getInitialConfig`, `pollData` (base = pass), `handleDeviceConnect`,
`handleDeviceDisconnect`, `runnerCommunicationLoop` (CoInitialize at
start, Dispatch inside, CoUninitialize in finally),
`startCommunication` (just validates name and starts worker),
`stopCommunication` (sets stopEvent, emits signals; loop finally
handles COM teardown), `selectAscomDriver` (unchanged).

---

## Part 2 – Device subclass migrations

All subclasses: rename `workerPollData`→`pollData`,
`workerGetInitialConfig`→`getInitialConfig`, remove
`processPolledData`, replace `callMethodThreaded`→`callAscomMethodQueued`,
`setAscomProperty` in GUI methods→`setAscomPropertyQueued`, remove
`deviceConnected` guards, remove `propertyExceptions` references.

Camera specific: remove `workerExpose`/`expose`/`waitFunc`, add
`exposurePending`/`exposing` flags, implement exposure state machine
inside `pollData`.

---

## Part 3 – Tests
Update all affected test files (remove QTimer mocks, rename tests,
assert queue contents for command methods).

## Part 4 – Final validation
100% coverage + Ruff on all changed files.

