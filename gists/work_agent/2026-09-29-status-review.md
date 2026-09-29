# MountWizzard4 – Consolidated Project Review

**Date:** 2026-09-29
**Baseline:** `8cfc9d644` (`main`, version `4.0.0b34`)
**Scope:** `src/mw4` (excluding generated `gui/widgets`), `tests/unit_tests`,
`pyproject.toml`, `README.rst`
**Input reviews:**
[2026-06-10-review.md](2026-06-10-review.md),
[2026-09-26-review.md](2026-09-26-review.md),
[2026-09-29-review.md](2026-09-29-review.md)

> This report checks every finding from the three earlier reviews against the
> current code and adds new observations. It does **not** change any code. The
> status of each item was checked in the source at the baseline commit.

---

## 1. Executive Summary

The code base is in very good shape. Ruff reports no findings, all 4583 tests
pass in about 10 s with `-n auto`, and coverage is **100 %** (18,492 statements).
The structural items from June and early September are done: the nested event
loop sleep is gone, `app: Any` is gone, the model run is event-driven, and the
signal payloads are typed.

The **2026-09-29 review tracked only its own list**. Most findings from the
**2026-09-26 review** (threading, mount protocol parsing, ALPACA/ASCOM driver
handling, config symmetry, tooling) were never picked up and are **still open**.
They are now the main risk area, because they concern runtime correctness with
real hardware. Tests do not catch them, because the tests mock the hardware.

**Overall maturity rating:** Strong (4 / 5). Structure and test quality are
5 / 5. Robustness against faulty devices and networks is the weak spot.

| Dimension             | Rating | Short note                                                       |
|-----------------------|:------:|------------------------------------------------------------------|
| PySide6 / Qt6         |  5/5   | No nested loops; `processEvents` only in splash and plot base    |
| Pythonic style        |  4/5   | Ruff clean; 29 defs without return annotation; 4 × `except Exception` |
| Architecture          |  4/5   | `AppProtocol` in place; test hooks and framework boilerplate remain |
| Robustness / hardware |  3/5   | Protocol parsing, ALPACA blacklisting, SGPro waits have no guards |
| Performance           |  4/5   | One socket per mount command; otherwise good                    |
| Test health           |  5/5   | 4583 passed, 38 skipped, 100 % coverage, xdist-safe              |
| Tooling / metadata    |  3/5   | Python versions, classifier, and header text are inconsistent   |

---

## 2. Measured State

| Metric                                   | Value                                         |
|------------------------------------------|-----------------------------------------------|
| `ruff check src tests`                   | ✅ All checks passed                          |
| `ruff format --check src tests`          | ✅ 463 files already formatted                |
| `pytest tests/unit_tests -n auto --cov`  | ✅ 4583 passed, 38 skipped, 9.7 s             |
| Coverage (macOS)                         | ✅ 100 % (18,492 statements, 0 missed)        |
| `# pragma: no cover` / `# noqa` / `TODO` | 0 / 0 / 0                                     |
| `Signal(object …)` (excl. widgets)       | 10 (by design, see Sep rec 9)                 |
| `parent: Any`                            | 51                                            |
| `except Exception`                       | 4 (`tpool.py:69`, `alpacaAscomCommon.py:67,86,106`) |
| `except (…, Exception)`                  | 5 in `mountcontrol/connection.py`             |
| `time.sleep` in src                      | 7 (all in worker threads)                     |
| Single-line `def` without `->`           | 29                                            |
| Largest modules                          | `alignstars.py` (840), `obsSite.py` (740), `styleSheets.py` (703), `tabMount_Sett.py` (533) |

---

## 3. Status of Earlier Recommendations

### 3.1 2026-06-10 review

| #  | Topic                                       | Status                                                            |
|----|---------------------------------------------|-------------------------------------------------------------------|
| 1  | `mainThreadSleep` nested loop               | ✅ Done (`threadUtils.py` deleted)                                |
| 2  | `# pragma: no cover`                        | ✅ Done                                                           |
| 3  | Misplaced docstrings in `mainApp.py`        | ✅ Done                                                           |
| 4  | `AppProtocol` instead of `app: Any`         | ✅ Done                                                           |
| 5  | Split the app signal hub into groups        | ⏸ Kept – decision 2026-09-29 (section 8); payloads are typed      |
| 6  | Mount status enum / helpers                 | ✅ Done                                                           |
| 7  | Data-driven `addDevices` / status GUI       | ✅ Done                                                           |
| 8  | Disk / twilight on slower cadence           | ✅ Done                                                           |
| 9  | `TabAddon` base                             | ✅ Done                                                           |
| 10 | `MAX_THREAD_COUNT`                          | ✅ Done                                                           |

### 3.2 2026-09-29 review

| #  | Topic                                               | Status                                                     |
|----|-----------------------------------------------------|------------------------------------------------------------|
| 1–9, 11 | See section 10 of that review                  | ✅ Done, confirmed (Ruff clean, 100 % coverage, xdist green) |
| 10 | Test hooks in `MountWizzard4` / `DeviceRegistry`    | ❌ Open – `mainApp.py:73,110` (`test: int = 0`), `deviceRegistry.py:49` (`hasattr(app, "mount")`, writes back `app.mount`) |
| –  | `moveRaDecHid` → `"STOP"` → `KeyError`              | ✅ Fixed – rec 1 (section 7)                               |
| –  | `closeEvent` does not cancel a running model        | ✅ Fixed – rec 7 (section 7)                               |

### 3.3 2026-09-26 review (not tracked so far)

| #  | Sev | Topic                                                  | Status     | Current evidence |
|----|:---:|--------------------------------------------------------|:----------:|------------------|
| T1 | H   | `QMutex` locked in GUI thread, unlocked in pool thread | ✅ Fixed   | Rec 4: `threading.Lock` busy flag |
| T2 | M   | Reused worker ignores new callbacks                    | ✅ Fixed   | Rec 4: callbacks rebound on reuse |
| T3 | M   | `propertyExceptions` is a `list`                       | ✅ Fixed   | Rec 3: `set[str]` |
| T4 | M   | SGPro busy-wait without deadline                       | ✅ Fixed   | Rec 6: `waitForMessage` with deadlines |
| T5 | M   | Shutdown sequence                                      | ✅ Fixed   | Rec 7: running model cancelled in `closeEvent` |
| T6 | L   | Non-interruptible `time.sleep` in workers              | ✅ Fixed   | Rec 6: `stopEvent.wait` |
| M1 | H   | `parsePointing` field count                            | ✅ Fixed   | Rec 2 (section 7) |
| M2 | H   | `parseSetTargetResponse` indexes before length check   | ✅ Fixed   | Rec 2 (section 7) |
| M3 | M   | Unchecked index access in `firmware.py`                | ✅ Fixed   | Rec 2: `InvalidVersion` handled; `syncPositionToTarget` length check |
| M4 | M   | `except (OSError, Exception)`                          | ✅ Fixed   | Rec 2: `(OSError, RuntimeError)` |
| M5 | M   | `decode("ASCII")` outside `try`                        | ✅ Fixed   | Rec 2: `errors="replace"` |
| M6 | M   | New `QTcpSocket` per command, 10 s connect timeout     | ⏸ Kept     | Decision 2026-09-29 (section 8) |
| M7 | L   | `communicateRaw` returns literal `"Exception"`         | ✅ Fixed   | Rec 2: `"Error: <reason>"` |
| M8 | L   | `mountIsUp` assigned twice                             | ✅ Fixed   | Rec 12 (section 7) |
| D1 | H   | ALPACA/ASCOM blacklists properties on any error        | ✅ Fixed   | Rec 3 (section 7) |
| D2 | H   | `stopCommunication` never disconnects                  | ✅ Fixed   | Rec 3 (section 7) |
| D3 | L   | `ImageArray` no-op branch                              | ✅ Done    | – |
| D4 | M   | `self.process` shared; `stdout.decode()` strict        | ✅ Fixed   | Rec 11 (section 7) |
| D5–D7 | L | Dome `None` contract, typo, iterator sentinel        | ✅ Fixed   | Rec 12 (section 7) |
| C1 | H   | Log level config asymmetric                            | ✅ Fixed   | Rec 5 (section 7) |
| C2 | M   | `config[x] = {}` then refill                           | 🟡 Partial | Rec 5: fixed in `tabSettUpdate.py`; other tabs unchanged |
| C3 | L   | Commented-out `aboutToQuit`                            | ✅ Fixed   | Rec 12 (section 7) |
| C4 | L   | Raw `sys.argv[1]` as message                           | ✅ Fixed   | Rec 12 (section 7) |
| A1 | M   | App as service locator / signal hub                    | ⏸ Kept     | Decision 2026-09-29 (section 8); typed via `AppProtocol` |
| A2 | M   | `DeviceEntry` proxy attributes                         | ⏸ Kept     | Decision 2026-09-29 (section 8) |
| A3 | M   | Test-only branch in `DeviceRegistry`                   | ❌ Open    | Same as Sep rec 10 |
| A4 | M   | `tabMount_Command` uses `Connection` directly          | ⏸ Kept     | Decision 2026-09-29 (section 8) |
| A5 | M   | Model data handling in GUI mixins                      | 🟡 Partial | `ModelData` is event-driven in logic; list handling still in tabs |
| A8 | L   | Framework-dispatch boilerplate                         | ⏸ Kept     | Decision 2026-09-29 (section 8) |
| P1 | M   | Python version mismatch                                | ✅ Fixed   | Rec 9: README / Copilot instructions follow `pyproject.toml` (3.12–3.14) |
| P2 | M   | "Production/Stable" on a beta                          | ⏸ Kept     | Decision 2026-09-29 (section 8) |
| P3 | M   | Runtime dependencies pinned with `==`                  | ✅ Fixed   | Rec 14 (section 7) |
| P4 | M   | Ruff rule set / no type checker                        | ❌ Open    | `ignore = ["N999", "BLE001"]`; no `B`, `BLE`, `ANN`; no mypy/pyright |
| P5 | M   | Missing return annotations                             | ✅ Fixed   | Rec 10 (P5 part): all 29 annotated; `ANN20x` clean |
| P6 | L   | `os.path.basename` in `tpool.py`                       | ✅ Fixed   | Rec 4: `Path(...).name` |
| P7 | L   | "GUI with PyQT5" header                                | ✅ Fixed   | Rec 9: "GUI with PySide" |
| P8 | L   | `ignore::DeprecationWarning`                           | ✅ Fixed   | Rec 14: `error::DeprecationWarning:mw4` |
| R1 | M   | `mainApp` fixture calls missing `shutdown()`           | ✅ Done    | Fixed with Sep rec 4 |
| R2 | M   | Real file I/O in `tests/work`                          | ✅ Done    | Per-worker sandbox in `tests/conftest.py` |
| R3 | L   | Order-dependent module fixtures                        | ✅ Done    | 33 modules fixed |
| R4 | L   | Tracked `.DS_Store`                                    | ✅ Fixed   | Rec 9: 6 files removed from the index; `.gitignore` covers them |
| R5 | L   | Artefacts in working tree                              | ⏸ Kept     | Decision 2026-09-29 (section 8) |

**Summary:** of 64 tracked rows, 23 are done, 5 are partial, and 36 are open.
33 of the 36 open rows come from the 2026-09-26 review. A3 and Sep rec 10 are
the same issue, and both are counted.

**Status after recs 1–4 and the decisions of section 8** (recounted, 65 rows;
D5–D7 is one row): 36 done, 2 partial (T5, A5), 6 kept by decision (Jun 5,
M6, A1, A2, A4, A8), 21 open (19 of them from the 2026-09-26 review).

**Status after recs 5, 6, 7, 11, 14** (65 rows): 44 done, 2 partial (A5, C2),
6 kept by decision, 13 open.

**Status after rec 12 (M8, C3, C4) and D5–D7** (65 rows): 48 done, 2 partial
(A5, C2), 6 kept by decision, 9 open.

**Status after rec 9 and P5** (65 rows): 52 done, 2 partial (A5, C2), 8 kept
by decision (+ P2, R5), 3 open (Sep 10, A3, P4).

---

## 4. New Findings

| #  | Sev | Location                                | Finding |
|----|:---:|-----------------------------------------|---------|
| N1 | H   | `gui/mainWaddon/tabMount_Move.py:219-262` | Confirmed bug: `convertDirection` returns `"STOP"` for `[0, 0]`. When the joystick returns to centre, `moveRaDecHid` calls `moveRaDec("STOP")`, which reads `self.setButtons["STOP"]` → `KeyError`. The mount keeps moving because no stop command is sent. The `coord == [0, 0]` branch in `moveRaDec` is unreachable. Also, a missing `return` after `stopMoveAll()` would let the code continue if the branch were reached. |
| N2 | M   | `mountcontrol/connection.py:418`        | Combined with M5: a single non-ASCII byte other than `0xDF` raises in the poll worker, and `tpool` logs it only at `critical`. The polled state stays half-updated. |
| N3 | M   | `base/alpacaAscomCommon.py:61-70`       | The specific `except (AttributeError, OSError, ValueError)` branch logs "not implemented" for `OSError`. A network timeout is reported as a missing feature and blacklisted permanently (D1). |
| N4 | L   | `logic/plateSolve/plateSolve.py:82`     | `stdout.decode()` without `errors="replace"`; ASTAP/Watney on Windows can write code-page output and then raise `UnicodeDecodeError`, which is not in the caught exceptions. |
| N5 | L   | `mainApp.py:73,110`                     | `test: int = 0` connects `update10s` to `mainW.close`. It is part of the public constructor and of the production code path. |
| N6 | L   | Repository                              | `gists/work_agent` has 100+ status/plan markdown files. Most are obsolete. Archive them so the current review and open plans are easy to find. |

---

## 5. Prioritized Recommendations

Effort: S (small), M (medium), L (large). Impact: ★ low → ★★★ high.

Status: ✅ done, 🟡 partial, ❌ open, ⏸ kept by decision (section 8).
Status as of 2026-09-29, after recs 1–7, 9, 11, 14, 12 (except C2) and 10 (P5).

| #  | Recommendation                                                                  | Refs          | Impact | Effort | Status |
|----|---------------------------------------------------------------------------------|---------------|:------:|:------:|--------|
| 1  | Fix the HID centre-stick `"STOP"` path (map to `stopMoveAll`, add a test)       | N1            |  ★★★   |   S    | ✅ Done (section 7) |
| 2  | Harden mount response parsing (length checks before indexing, `errors="replace"`, concrete exceptions) | M1, M2, M3, M4, M5, M7, N2 | ★★★ | M | ✅ Done (section 7) |
| 3  | ALPACA/ASCOM: blacklist only real "not implemented", never `Connected`; process the disconnect before the loop exits; use a `set` | D1, D2, T3, N3 | ★★★ | M | ✅ Done (section 7) |
| 4  | Replace the cross-thread `QMutex` unlock in `tpool` with a thread-agnostic busy flag (`threading.Lock` or `QSemaphore(1)`); decide on callback reuse | T1, T2 | ★★★ | S | ✅ Done (section 7) |
| 5  | Fix log level config symmetry (read and write the same key)                    | C1            |  ★★    |   S    | ✅ Done (section 7) |
| 6  | Add deadlines to the SGPro wait loops; use `Event.wait` for interruptible sleeps | T4, T6      |  ★★    |   S    | ✅ Done (section 7) |
| 7  | Cancel a running model in `closeEvent` before `waitForDone`                     | T5            |  ★★    |   S    | ✅ Done (section 7) |
| 8  | Remove test hooks (`test` arg, `hasattr(app, "mount")`) via injection          | Sep 10, A3, N5 |  ★★   |   S    | ❌ Open |
| 9  | Align metadata: Python version (pyproject/README/instructions), classifier `4 - Beta`, header text, `.DS_Store` untracking | P1, P2, P7, R4 | ★★ | S | ✅ Done (section 7); P2 kept (section 8) |
| 10 | Extend Ruff (`B`, `BLE`, `ANN`) and add a type checker in CI; close the 29 missing return types | P4, P5 | ★★ | M | 🟡 Partial – P5 done (section 7); P4 open |
| 11 | Plate solver: local `Popen` context manager, tolerant decode                   | D4, N4        |   ★    |   S    | ✅ Done (section 7) |
| 12 | Small cleanups: `mountIsUp` duplicate, `os.path`, commented code, `argv` handling, config build-then-assign | M8, P6, C2, C3, C4 | ★ | S | 🟡 Partial – P6 with rec 4; C2 for `tabSettUpdate` with rec 5; M8, C3, C4 (and D5–D7) done (section 7); only C2 (other tabs) open |
| 13 | Architecture (longer term): `FrameworkDevice` base, `tabMount_Command` via `MountDevice`, split the signal hub, `parent: Any` typing | A1, A2, A4, A8, Jun 5 | ★★ | L | ⏸ Kept |
| 14 | Relax `==` pins in `[project]` and rely on `uv.lock`; scope `DeprecationWarning` to `mw4` | P3, P8 | ★ | S | ✅ Done (section 7) |
| 15 | Persistent or pooled mount connection instead of one socket per command         | M6            |   ★★   |   L    | ⏸ Kept |

**Progress:** 10 done, 2 partial (10, 12), 1 open (8), 2 kept. All ★★★
recommendations and all correctness and hardware robustness items are done.

### Suggested sequencing (remaining)

1. **Hygiene (S):** 8, 12 (C2 in the remaining tabs).
2. **Tooling (M):** 10 (P4: Ruff rules, type checker).
3. **Architecture (L):** 13, 15 – not scheduled; the current architecture is
   kept (decision 2026-09-29, section 8).

---

## 6. Closing Note

The refactoring cycle from June to September delivered what it aimed for: a
clean, typed, event-driven Qt application with a complete and parallel-safe
test suite. The remaining risk is no longer in the structure. It is at the
**edges**, where the application talks to real devices: the mount protocol
parser, the ALPACA/ASCOM property handling, SGPro polling, and the worker mutex.
These issues were found on 2026-09-26 but never scheduled. The next cycle should
start with them, together with the confirmed HID `"STOP"` bug (N1), which is the
only finding here with a direct safety impact on mount motion.

---

## 7. Implementation Update (2026-09-29)

| #  | Change                                                                                     | Status  |
|----|--------------------------------------------------------------------------------------------|---------|
| 1  | N1: `moveRaDecHid` calls `stopMoveAll()` when the stick returns to centre (`"STOP"`) and `moveRaDec(direction)` otherwise; `oldDirection` is updated in both cases. The unreachable `coord == [0, 0]` branch was removed from `moveRaDec`. Tests: the fake `"STOP"` button test was replaced; new `test_moveRaDecHid_centreStops` and `test_moveRaDecHid_centreRealStop` (real path down to `obsSite.stopMoveAll`); direction assertions added to the existing HID tests. Ruff clean, 4585 passed, 38 skipped, coverage 100 %. | ✅ Done |
| 2  | Plan: `plan-review-2026-09-29-status-rec-2-mountParsing.md`. `Connection`: all `except (…, Exception)` narrowed to `(OSError, RuntimeError)` (`buildClient` also `TypeError`, `ValueError` from the port conversion) (M4). `receiveData` / `communicateRaw` decode with `errors="replace"` (M5, N2). `communicateRaw` returns `"Error: <reason>"` instead of the literal `"Exception"` (M7). `ObsSite.parsePointing` checks ≥ 8 fields in `:Ginfo` and ≥ 5 in `:GaE` before it assigns anything (M1). `parseSetTargetResponse` checks the length (4 chunks, first chunk ≥ 3 chars) before indexing (M2). `syncPositionToTarget` checks for ≥ 2 chunks (M3). `Firmware.parse` catches `InvalidVersion` and leaves the fields unchanged (M3). Tests: generic `Exception` side effects replaced by `OSError` / `RuntimeError`; new tests for non-ASCII bytes, an unexpected exception that now propagates, short pointing/target/sync responses, and an invalid firmware version. Ruff clean, 4595 passed, 38 skipped (serial and `-n auto`), coverage 100 %. Follow-up (out of scope): the `timeJD` setter still raises `TypeError` for a non-numeric value. | ✅ Done |
| 3  | `AlpacaAscomCommon` only (the subclasses are unchanged). `propertyExceptions` is a `set` (T3). The three `except` pairs in `getDeviceProp` / `setDeviceProp` / `callDeviceMethod` go through one `handleDeviceError`. A property or method is blocked only if `isNotImplemented` is true: `AttributeError`, `NotImplementedError`, alpyca `NotImplementedException` / `ActionNotImplementedException`, or a COM error whose `excepinfo` scode is `0x80040400` (ASCOM `PropertyNotImplemented` / `MethodNotImplemented`, checked by duck typing so it is testable on every OS). `Connected` is never blocked (`NEVER_BLOCKED`). Timeouts (`OSError` / `requests` errors), `InvalidValue`, `InvalidOperation`, `NotConnected` and driver errors are logged with their type and retried (D1, N3). This also fixes a single out-of-range `set` blocking the setter for the whole session. Disconnect (D2): `stopCommunication` queues `Connected = False` **before** it sets `stopEvent`, and `runnerCommunicationLoop` calls `processCommandQueue()` after the loop, so the disconnect is actually sent. The loop starts with `clearCommandQueue()`, so a disconnect queued while no loop was running is not replayed after the next connect. Tests: 25 new (not-implemented classification incl. COM scode, no blocking for timeouts/invalid values/operations/`Connected`, stale queue dropped, disconnect sent on stop, queue-before-stop order); list → set updates in the `alpacaClass` / `ascomClass` tests. Ruff clean, 4620 passed, 38 skipped (serial and `-n auto`), coverage 100 %. | ✅ Done |
| 4  | `tpool.py` only. T1: the `QMutex` is replaced by `Worker.busyLock` (`threading.Lock`, which may be released by any thread) behind a small API: `tryAcquire()` (sets `locked`) and `release()` (no-op when not acquired). `startWorker` acquires in the calling thread, `Worker.run` releases in `finally` in the pool thread. T2 (decision: callbacks follow the call): `Worker` stores `resultMethod` / `finishedMethod`; `setCallbacks` disconnects the old and connects the new slot only if it changed. `startWorker` rebinds on reuse only after `tryAcquire` succeeded, so a running call keeps its callbacks and a busy skip changes nothing. P6: `Path(...).name` instead of `os.path.basename`. Tests: `test_tpool.py` rewritten for the new API (32 tests, incl. release from a `threading.Thread` and from a real `QThreadPool`, callback rebind/keep/remove); 22 test modules moved from `worker.mutex.lock/unlock` and manual `locked` resets to `tryAcquire()` / `release()`. The teardown message `QMutex: destroying locked mutex` (3.4 of the Sep review) no longer appears. Ruff clean, 4621 passed, 38 skipped (serial and `-n auto`), coverage 100 %. `test_loader_main::test_main_1` still fails only in a full `pytest -s` run, as it does on the baseline. | ✅ Done |
| 5, 6, 7, 11, 14 | Plan: `plan-review-2026-09-29-status-rec-5-6-7-11-14.md`. **Rec 5 (C1):** `mainApp.initConfig` derives the log level from `SettingUpdate.loglevelInfo/Trace` (default `DEBUG`); `storeConfig` no longer writes a top-level `loglevel` and removes an old key. `SettUpdate.storeConfig` updates its section with `setdefault` instead of replacing it (C2 for this file). **Rec 6 (T4, T6):** `CameraSGPro.waitForMessage` polls with `stopEvent.wait(0.1)` and has deadlines (start 30 s, exposure time + 60 s, download 120 s, save 60 s); a timeout logs a warning, shows a message and ends the run; `exposeFinished()` is always called. `SGProClass.connectDevice` and `KMRelay.runnerPulse` use `stopEvent.wait` (the relay "off" command is always sent). **Rec 7 (T5):** new `TabAddon.shutdown()` hook, dispatched by `MainWindowAddons.shutdown()`, called first in `closeEvent`; `Model.shutdown()` cancels a running model batch. **Rec 11 (D4, N4):** `runSolverBin` uses `with subprocess.Popen(...)`, reads the return code from the local process, resets `self.process` in `finally`, decodes with `errors="replace"`; `abort()` works on a local copy. **Rec 14 (P3, P8):** runtime dependencies use `>=X,<next major` (`0.x`: next minor; `pyside6 <6.12`; `pywin32 >=312`); `uv lock` changed only the specifiers, no resolved version. `filterwarnings` adds `error::DeprecationWarning:mw4`, which found `QMouseEvent.pos()` in `qtHelpers.clickable` → replaced by `position().toPoint()`. Ruff clean, 4647 passed, 38 skipped (serial and `-n auto`), coverage 100 %. | ✅ Done |
| 12 (M8, C3, C4), D5–D7 | Plan: `plan-review-2026-09-29-status-rec-12-cleanups.md`. **M8:** duplicate `self.mountIsUp` in `Mount.__init__` removed. **C3:** commented-out `aboutToQuit` line and its stale comment removed from `mainApp.py`. **C4:** `MountWizzard4` no longer reads `sys.argv`; new `cli.formatOptions()` turns the parsed `argparse` options into text (`dpi=…, scale=…, test=…`), `cli.run` passes it via `loader.main(test, arguments)` to `MountWizzard4(..., arguments)`, which emits it as `Arguments` message only if it is not empty. **D5:** `Dome.calcSlewTarget` is typed `tuple[float, float, float \| None, float \| None]` and returns `None` for x/y explicitly without geometry and on a geometry error – before, a real geometry error (`intersect is None`) raised `TypeError`. **D6:** `targetInDomeShutter` uses `M - B` in the BC check (as in the referenced formula), typed with `np.ndarray`; typo "mez" → "met". **D7:** `ModelRun.startNewSlew` uses `next(iterator, None)`; `modelRunKey` stays a `str` (`""` when exhausted). Tests: `test_cli` (`formatOptions`, `main` call args), `test_loader_main` (arguments passed through), `test_mainApp` (message with/without arguments, raw `sys.argv` ignored), `test_dome` (geometry error without intersect, `slewDome` slews without `checkSlewNeeded`), `test_modelRun` (`modelRunKey == ""`). Ruff clean, 4652 passed, 38 skipped (`-n auto`), coverage 100 %. | ✅ Done |
| 9, 10 (P5) | Plan: `plan-review-2026-09-29-status-rec-9-metadata-P5.md`. **P1:** `pyproject.toml` (`>=3.12,<3.15`) is the reference; `README.rst` says 3.12-3.14, `.github/copilot-instructions.md` says 3.12–3.14 and 3.12 language features. **P7:** `pyproject.toml` header "GUI with PySide". **R4:** 6 tracked `.DS_Store` files (`.github/`, `doc/`, `doc/config/`, `doc/workflows/`, `src/mw4/assets/`, `tests/`) removed from the index with `git rm --cached`; `.gitignore` already lists `.DS_Store`. **P2, R5:** kept (section 8). **P5:** all 29 functions without return annotation annotated (26 × `None`, `Telescope.create -> bool`, `dataPlots -> dict[str, dict]`, `Styles.generateCMaps -> list[pg.ColorMap]`); `ruff check --select ANN201,ANN202,ANN204,ANN205,ANN206` (excl. `gui/widgets`) is clean. No behaviour change. Ruff clean, 4652 passed, 38 skipped (`-n auto`), coverage 100 %. | ✅ Done |

---

## 8. Decisions

| Date       | Rec | Decision | Affected findings |
|------------|-----|----------|-------------------|
| 2026-09-29 | 13  | **Keep the current architecture.** No `FrameworkDevice` base class, no split of the app signal hub, `tabMount_Command` keeps its direct `Connection`, `DeviceEntry` keeps its proxy attributes, `parent: Any` stays. The per-framework `self.run = {…}` dispatch is accepted as explicit, readable code. | A1, A2, A4, A8, Jun rec 5 (⏸ Kept) |
| 2026-09-29 | 15  | **Keep one socket per mount command.** The 10micron command protocol stays stateless per call, so no connection pool is added. The robustness work of rec 2 (concrete exceptions, tolerant decoding, length checks) covers the error handling. | M6 (⏸ Kept) |
| 2026-09-29 | 9   | **Keep the classifier `Development Status :: 5 - Production/Stable`** although the version is a beta. | P2 (⏸ Kept) |
| 2026-09-29 | –   | **Artefacts in the working tree are accepted** (untracked test assets, `data/`). | R5 (⏸ Kept) |

These items are closed as "kept" and are no longer counted as open. They
should only be reopened if a measured problem appears (e.g. latency or socket
exhaustion on the mount for rec 15).
