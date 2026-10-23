# Plan – Review 2026-09-29, Recommendation 9: Type `Signal(object, …)` payloads

Source: `2026-09-29-review.md`, section 3.3. 53 `Signal(object, …)` declarations,
with `MountWizzard4.msg` first.

## 1. How PySide6 treats signal types (checked on PySide6 6.11.2)

| Declared type | Behavior on `emit` |
|---|---|
| `int`, `float`, `str`, `bool` | Converted. A mismatch is **silently coerced**: `None`→`0`/`''`, `Path`→`''`, `3.7`→`3`. Only a line on stderr: `_pythonToCppCopy: Cannot copy-convert` |
| `dict`, `list` | **Copied** to `QVariantMap` / `QVariantList`. The receiver gets a different object (shared mutation is lost), and a dict with non-`str` keys arrives as `{}` |
| Python class (`Path`, `ObsSite`, `Time`, …) | Passed through as `PyObject`, same object, `None` allowed. Serves as documentation, no conversion |
| `object` | Passed through as is |

**Rules:**
1. Use primitives only where **every** emit site is proven to pass exactly that
   type.
2. **Never** use `dict` / `list`. Those payloads stay `object`.
3. Use domain classes where the payload is always one class (documentation, no
   runtime risk).
4. Keep `object` for mixed, `None`-able or generic payloads (worker results,
   plate-solve result dicts).

**Safety net:** coverage is 100 %, so every emit site runs in the tests. After
typing, a serial `-s` run of the full suite is searched for
`Cannot copy-convert`. Every hit is a type mismatch that has to be fixed.

## 2. Target types

| Class / file | Signal | New type | Evidence |
|---|---|---|---|
| `MountWizzard4` (`mainApp.py`) and stub `App` | `msg` | `(int, str, str, str)` | Level literal plus texts. Verified by the runtime check |
| | `operationRunning` | `(int)` | `STATUS_*` constants |
| | `playSound` | `(str)` | Sound names |
| | `remoteCommand` | `(str)` | `read().toStdString()` |
| | `showImage`, `showAnalyse` | `(Path)` | Image / model paths |
| | `updateSatellite` | `(Time, GeographicPosition)` | `ts.now()`, `obsSite.location` |
| | `showSatellite` | `(EarthSatellite, object, object, object, str)` | Orbits / alt / az are arrays or lists |
| | `sendSatelliteData` | stays `(object, object)` | Emitted with `[]`, received as `np.ndarray` |
| | `material` | **removed** | Never emitted or connected |
| `MountSignals` | `pointDone`, `locationDone` | `(ObsSite)` | `mount.obsSite` |
| | `settingDone` | `(Setting)` | |
| | `getModelDone`, `namesDone` | `(Model)` | |
| | `firmwareDone` | `(Firmware)` | |
| | `calcTLEdone`, `statTLEdone`, `getTLEdone` | `(TLEParams)` | |
| | `calcTrajectoryDone` | `(TrajectoryParams)` | |
| | `mountIsUp` | `(bool)` | `True` / `False` literals |
| | `domeDone` | **removed** | Never emitted or connected |
| `ModelData` | `statusRetry` | `(int)` | `self.retries` |
| | `statusExpose`, `statusSlew`, `statusSolve` | stay `object` | list / list / shared dict (rule 2) |
| `HidControllerSignals` | `hidABXY`, `hidPMH`, `hidDirection` | `(int)` | HID report bytes |
| | `hidSL`, `hidSR` | `(int, int)` | |
| `KeypadSignals` | `keyPressed`, `keyUp`, `keyDown` | `(int)` | `keyEvent.key()` / mapped codes |
| | `mousePressed`, `mouseReleased` | `(str)` | `button: str` |
| | `cursorPos` | `(int, int)` | byte arithmetic |
| | `textRow` | `(int, str)` | |
| | `imgChunk` | `(object, int, int)` | ndarray plus offsets |
| `Download` / `UploadPopup` | `signalProgress` | `(int)` | `int(...)`, literal `100` |
| | `signalStatus`, `signalProgressBarColor` | `(str)` | |
| `ImageSignals` | `solveImage` | `(Path)` | |
| `WorkerSignals` (`tpool`) | `error` | `(str)` | `eStr` f-strings |
| | `result` | stays `object` | Generic worker result |
| `clickable()` filter | `clicked` | `(QWidget)` | `widget: QWidget` |
| Stays `object` | `Signals.azimuth` (may be `None`), `Signals.result`, `photometryFinished` (worker result), `pixmapReady` (`QPixmap` or `None`), `setSatListItem` entry | | Rule 4 |

About 45 of the 53 declarations get a real type or are removed. The remaining
`object` declarations are deliberate (rules 2 and 4).

## 3. Steps

1. Change the declarations as in the table. Add the domain imports: mount
   classes in `mountSignals.py`, skyfield classes in `mainApp.py`, and
   `QWidget` in `qtHelpers.py`. Check that there are no import cycles.
2. Remove `material` and `domeDone`. Update `test_mountSignals.py`.
3. Mirror the typed hub signals in the test stub `baseTestApp.App`, so the
   tests go through the same conversion.
4. Serial run `pytest -n 0 -s` → search the output for `Cannot copy-convert`
   and fix every hit (in the source, or in a test that emits wrong types).
5. Add a test: `msg` rejects nothing valid and keeps the types
   (`qtbot.waitSignal`).
6. Ruff, full suite serially and with `-n auto`, coverage 100 %. Update the
   review.

---

## 4. Result – ✅ Done

- All declarations were changed as in the table. `material` (app) and
  `domeDone` (mount) were removed. The stub `App` mirrors the typed hub
  signals. No import cycles.
- 53 → **12** declarations still contain `object`. Each one is deliberate
  (rules 2 and 4): `sendSatelliteData`, three positions in `showSatellite`,
  `statusExpose` / `statusSolve` / `statusSlew`, `photometryFinished`, the
  `setSatListItem` entry, `pixmapReady`, the `imgChunk` array,
  `WorkerSignals.result`, `Signals.azimuth` and `Signals.result`.
- **Conversion check:** the baseline had 0 `Cannot copy-convert` warnings.
  After typing there were 2, and both were **real bugs** that showed garbage in
  the message window:
  - `videoBase.sendImage`: the `cv2.error` object was passed as message
    text. It is now `f"{e}"`.
  - `tabSat_Track.startProg`: `text = "Program", "No track data …"` built a
    **tuple** because of a stray comma. It is now the plain string, with the
    header `"Program error"`.
  After the fixes: 0 warnings.
- Tests: `test_msgSignalIsTyped` and `test_pathSignalPassesThrough` (real
  `MountWizzard4`), regression asserts in `test_sendImage_2` and
  `test_startProg_3`, and `test_mountSignals` (the `domeDone` removal is
  checked, `mountIsUp` is bool, a domain payload is passed by identity).
- **Limit:** the check catches values that **cannot** be converted (`None`,
  `Path`, exceptions, tuples → `int` / `str`). It does not catch
  `float` → `int` truncation. Those `int` signals are backed by the static
  evidence in the table (constants, `int(...)` casts, HID bytes, key codes).
- Verification: Ruff clean. 4583 passed, 38 skipped (serial and `-n auto`).
  Coverage 100 % (18,492 statements). The stress tests still collect.
  `test_loader_main::test_main_1` fails only under `pytest -s` (its
  `LoggerWriter` has no `fileno`). That is not related to this change and it
  passes in normal runs.

