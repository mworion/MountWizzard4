# Plan – Status Review 2026-09-29, Recommendations 5, 6, 7, 11, 14

**Date:** 2026-09-29
**Source:** `gists/work_agent/2026-09-29-status-review.md`, section 5

## Rec 5 – Log level config symmetry (C1)

Today `MountWizzard4.initConfig` reads `SettingUpdate.loglevel` (never
written) and `storeConfig` writes a top-level `loglevel` (never read). The
level the user chooses is stored by the settings tab as
`SettingUpdate.loglevelInfo/Debug/Trace`.

- `mainApp.initConfig`: derive the level from the settings tab keys, which are
  the single source of truth (`INFO` / `TRACE` / default `DEBUG`).
- `mainApp.storeConfig`: stop writing the top-level `loglevel`; drop an old
  top-level key from existing profiles (`pop`).
- `SettUpdate.storeConfig`: update the existing `SettingUpdate` section
  (`setdefault`) instead of replacing it with `{}`, so keys owned by others
  (e.g. `isOnline` read by `mainApp`) are never lost (part of C2 for this file).

## Rec 6 – SGPro deadlines, interruptible sleeps (T4, T6)

- `CameraSGPro`: one helper `waitForMessage(text, present, timeout, tick)`.
  It polls `Device.Message` every 0.1 s with `stopEvent.wait`, stops when
  `exposing` is cleared (abort, unchanged behaviour), returns `False` on
  deadline or when communication is stopped. Deadlines are class constants:
  start 30 s, exposure = exposure time + 60 s, download 120 s, save 60 s.
  `runnerExpose` only continues to the next step when the previous one did not
  time out; a timeout logs a warning and shows a message, and
  `exposeFinished()` is always called. The 1 s pause after saving uses
  `stopEvent.wait`.
- `SGProClass.connectDevice`: retry pause with `stopEvent.wait(0.2)`; stops
  retrying when communication is stopped.
- `KMRelay`: `stopEvent` (`threading.Event`), cleared in `startCommunication`,
  set in `stopCommunication`. `runnerPulse` waits with
  `stopEvent.wait(PULSEWIDTH)`; the "off" command is always sent.

## Rec 7 – Cancel a running model on close (T5)

- `TabAddon`: new no-op lifecycle hook `shutdown()`.
- `MainWindowAddons.shutdown()`: dispatches to all addons.
- `Model.shutdown()`: calls `modelData.cancelRun()` if a model batch is
  running (`app.statusOperationRunning == STATUS_MODEL_BATCH`).
- `MainWindow.closeEvent`: calls `mainWindowAddons.shutdown()` first, before
  timers and devices are stopped and before `waitForDone`.

## Rec 11 – Plate solver process (D4, N4)

- `runSolverBin`: `with subprocess.Popen(...) as process:` so pipes are
  always closed and the process is reaped. `self.process` is only a reference
  for `abort()` and is reset to `None` in `finally`. The return code is read
  from the local process. Output is decoded with `errors="replace"`.
- `abort()`: kills via a local copy of `self.process` (no race with the reset).

## Rec 14 – Dependency ranges, deprecation warnings (P3, P8)

- `[project] dependencies`: `==X.Y.Z` → `>=X.Y.Z,<next>`, where `next` is the
  next major (for `0.x` packages the next minor). Exception: `pyside6` is
  limited to `<6.12`, because Qt minor releases change behaviour. `pywin32`
  gets `>=312`. `uv.lock` keeps the exact versions; `uv lock` must not change
  any resolved version.
- `[tool.pytest.ini_options] filterwarnings`: third-party deprecations stay
  ignored, deprecations raised from `mw4` code become errors
  (`error::DeprecationWarning:mw4`).

## Tests

Mirrored under `tests/unit_tests/`: `mainApp`, `setting/tabSettUpdate`,
`camera/cameraSGPro`, `base/sgproClass`, `powerswitch/kmRelay`,
`mainWaddon/tabAddon`, `mainWindow/mainWindowAddons`, `mainWaddon/tabModel`,
`mainWindow/mainWindow`, `plateSolve/plateSolve`.

## Done Criteria

Ruff clean, full suite green serially and with `-n auto`, coverage 100 %,
review report updated.

