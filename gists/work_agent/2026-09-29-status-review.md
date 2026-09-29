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
| 5  | Split the app signal hub into groups        | 🟡 Partial – payloads typed, hub still on `MountWizzard4`         |
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
| –  | `moveRaDecHid` → `"STOP"` → `KeyError`              | ❌ Open – see N1                                           |
| –  | `closeEvent` does not cancel a running model        | ❌ Open – `mainWindow.py:166` has no `modelData.cancelRun()` |

### 3.3 2026-09-26 review (not tracked so far)

| #  | Sev | Topic                                                  | Status     | Current evidence |
|----|:---:|--------------------------------------------------------|:----------:|------------------|
| T1 | H   | `QMutex` locked in GUI thread, unlocked in pool thread | ❌ Open    | `tpool.py:120` `tryLock()` in the caller, `tpool.py:82` `unlock()` in `Worker.run`. A `locked` flag was added, but the cross-thread unlock is unchanged |
| T2 | M   | Reused worker ignores new callbacks                    | ❌ Open    | `tpool.py:124-126` updates only `args`/`kwargs` |
| T3 | M   | `propertyExceptions` is a `list`                       | ❌ Open    | `alpacaAscomCommon.py:43` |
| T4 | M   | SGPro busy-wait without deadline                       | ❌ Open    | `cameraSGPro.py:68-91`, four `while … time.sleep(0.1)` loops |
| T5 | M   | Shutdown sequence                                      | 🟡 Partial | `closeEvent` now stops `timeMgr` and devices before `waitForDone(10000)`; a running model is not cancelled |
| T6 | L   | Non-interruptible `time.sleep` in workers              | ❌ Open    | `kmRelay.py`, `sgproClass.py`, `cameraSGPro.py:108` |
| M1 | H   | `parsePointing` field count                            | ✅ Fixed   | Rec 2 (section 7) |
| M2 | H   | `parseSetTargetResponse` indexes before length check   | ✅ Fixed   | Rec 2 (section 7) |
| M3 | M   | Unchecked index access in `firmware.py`                | ✅ Fixed   | Rec 2: `InvalidVersion` handled; `syncPositionToTarget` length check |
| M4 | M   | `except (OSError, Exception)`                          | ✅ Fixed   | Rec 2: `(OSError, RuntimeError)` |
| M5 | M   | `decode("ASCII")` outside `try`                        | ✅ Fixed   | Rec 2: `errors="replace"` |
| M6 | M   | New `QTcpSocket` per command, 10 s connect timeout     | ❌ Open    | `connection.py:350-354` |
| M7 | L   | `communicateRaw` returns literal `"Exception"`         | ✅ Fixed   | Rec 2: `"Error: <reason>"` |
| M8 | L   | `mountIsUp` assigned twice                             | ❌ Open    | `mount.py:75,95` |
| D1 | H   | ALPACA/ASCOM blacklists properties on any error        | ❌ Open    | `alpacaAscomCommon.py:62-68`; `OSError` (timeout) also blacklists, including `Connected` |
| D2 | H   | `stopCommunication` never disconnects                  | ❌ Open    | `alpacaAscomCommon.py:181-185`: `stopEvent` set first, queued `Connected=False` is never processed |
| D3 | L   | `ImageArray` no-op branch                              | ✅ Done    | – |
| D4 | M   | `self.process` shared; `stdout.decode()` strict        | ❌ Open    | `plateSolve.py:64,82` |
| D5–D7 | L | Dome `None` contract, typo, iterator sentinel        | ❌ Open    | Not addressed |
| C1 | H   | Log level config asymmetric                            | ❌ Open    | `mainApp.py:119` reads `SettingUpdate.loglevel`, `:130` writes top-level `loglevel`; value never read back |
| C2 | M   | `config[x] = {}` then refill                           | ❌ Open    | `tabSettUpdate.py:54` |
| C3 | L   | Commented-out `aboutToQuit`                            | ❌ Open    | `mainApp.py:107` |
| C4 | L   | Raw `sys.argv[1]` as message                           | ❌ Open    | `mainApp.py:112-113` |
| A1 | M   | App as service locator / signal hub                    | 🟡 Partial | Typed via `AppProtocol`; still one hub |
| A2 | M   | `DeviceEntry` proxy attributes                         | ❌ Open    | – |
| A3 | M   | Test-only branch in `DeviceRegistry`                   | ❌ Open    | Same as Sep rec 10 |
| A4 | M   | `tabMount_Command` uses `Connection` directly          | ❌ Open    | – |
| A5 | M   | Model data handling in GUI mixins                      | 🟡 Partial | `ModelData` is event-driven in logic; list handling still in tabs |
| A8 | L   | Framework-dispatch boilerplate                         | ❌ Open    | 16 logic modules define `self.run = {…}` |
| P1 | M   | Python version mismatch                                | ❌ Open    | `pyproject.toml` `>=3.12,<3.15`, README "3.11-3.13", Copilot instructions "3.11" |
| P2 | M   | "Production/Stable" on a beta                          | ❌ Open    | `pyproject.toml:36` |
| P3 | M   | Runtime dependencies pinned with `==`                  | ❌ Open    | 42 `==` pins; `uv.lock` already pins |
| P4 | M   | Ruff rule set / no type checker                        | ❌ Open    | `ignore = ["N999", "BLE001"]`; no `B`, `BLE`, `ANN`; no mypy/pyright |
| P5 | M   | Missing return annotations                             | ❌ Open    | 29 single-line `def`s without `->` |
| P6 | L   | `os.path.basename` in `tpool.py`                       | ❌ Open    | `tpool.py:45` |
| P7 | L   | "GUI with PyQT5" header                                | ❌ Open    | `pyproject.toml:9` |
| P8 | L   | `ignore::DeprecationWarning`                           | ❌ Open    | `pyproject.toml:127` |
| R1 | M   | `mainApp` fixture calls missing `shutdown()`           | ✅ Done    | Fixed with Sep rec 4 |
| R2 | M   | Real file I/O in `tests/work`                          | ✅ Done    | Per-worker sandbox in `tests/conftest.py` |
| R3 | L   | Order-dependent module fixtures                        | ✅ Done    | 33 modules fixed |
| R4 | L   | Tracked `.DS_Store`                                    | ❌ Open    | `git status` still shows modified `doc/`, `tests/`, `src/mw4/assets/.DS_Store` |
| R5 | L   | Artefacts in working tree                              | ❌ Open    | Untracked `tests/work/assets/*`, `tests/work/config/new.yaml`, `data/` |

**Summary:** of 64 tracked rows, 23 are done, 5 are partial, and 36 are open.
33 of the 36 open rows come from the 2026-09-26 review. A3 and Sep rec 10 are
the same issue, and both are counted.

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

| #  | Recommendation                                                                  | Refs          | Impact | Effort |
|----|---------------------------------------------------------------------------------|---------------|:------:|:------:|
| 1  | Fix the HID centre-stick `"STOP"` path (map to `stopMoveAll`, add a test)       | N1            |  ★★★   |   S    |
| 2  | ✅ Harden mount response parsing (length checks before indexing, `errors="replace"`, concrete exceptions) | M1, M2, M3, M4, M5, M7, N2 | ★★★ | M |
| 3  | ALPACA/ASCOM: blacklist only real "not implemented", never `Connected`; process the disconnect before the loop exits; use a `set` | D1, D2, T3, N3 | ★★★ | M |
| 4  | Replace the cross-thread `QMutex` unlock in `tpool` with a thread-agnostic busy flag (`threading.Lock` or `QSemaphore(1)`); decide on callback reuse | T1, T2 | ★★★ | S |
| 5  | Fix log level config symmetry (read and write the same key)                    | C1            |  ★★    |   S    |
| 6  | Add deadlines to the SGPro wait loops; use `Event.wait` for interruptible sleeps | T4, T6      |  ★★    |   S    |
| 7  | Cancel a running model in `closeEvent` before `waitForDone`                     | T5            |  ★★    |   S    |
| 8  | Remove test hooks (`test` arg, `hasattr(app, "mount")`) via injection          | Sep 10, A3, N5 |  ★★   |   S    |
| 9  | Align metadata: Python version (pyproject/README/instructions), classifier `4 - Beta`, header text, `.DS_Store` untracking | P1, P2, P7, R4 | ★★ | S |
| 10 | Extend Ruff (`B`, `BLE`, `ANN`) and add a type checker in CI; close the 29 missing return types | P4, P5 | ★★ | M |
| 11 | Plate solver: local `Popen` context manager, tolerant decode                   | D4, N4        |   ★    |   S    |
| 12 | Small cleanups: `mountIsUp` duplicate, `os.path`, commented code, `argv` handling, config build-then-assign | M8, P6, C2, C3, C4 | ★ | S |
| 13 | Architecture (longer term): `FrameworkDevice` base, `tabMount_Command` via `MountDevice`, split the signal hub, `parent: Any` typing | A2, A4, A8, Jun 5 | ★★ | L |
| 14 | Relax `==` pins in `[project]` and rely on `uv.lock`; scope `DeprecationWarning` to `mw4` | P3, P8 | ★ | S |
| 15 | Persistent or pooled mount connection instead of one socket per command         | M6            |   ★★   |   L    |

### Suggested sequencing

1. **Correctness quick wins (S):** 1, 4, 5, 7. These are user-visible bugs or
   undefined behaviour and each needs only a small change plus tests.
2. **Hardware robustness (M):** 2, 3, 6, 11. Add a plan first (more than one
   class). Build the tests from recorded or garbled mount and ALPACA responses.
3. **Hygiene (S):** 8, 9, 12, 14.
4. **Tooling (M):** 10. After 2 and 3, so that the new rules do not hit
   code that is about to change.
5. **Architecture (L):** 13, 15.

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


