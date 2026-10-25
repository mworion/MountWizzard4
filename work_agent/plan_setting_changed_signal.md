# Plan: detect changed mount settings and emit a signal

## Goal
After `Setting.parseSetting` succeeds, know whether any setting value changed
and notify listeners via a new signal. Existing `settingDone` stays untouched.

## Design
`Setting` is a plain class (no Qt, layer `mountcontrol`), and polling runs in a
worker thread. So `Setting` only *detects* and *returns* the change; the
`MountDevice` (QObject) *emits* the signal in the result method (main thread).

### 1. `setting.py`
- Add `self.changed: set[str] = set()` in `__init__` (names of changed fields).
- Add `WATCHED_FIELDS: ClassVar[tuple[str, ...]]` (decided with user):
  - mount limits: `meridianLimitTrack`, `meridianLimitSlew`,
    `horizonLimitHigh`, `horizonLimitLow`
  - flip tolerance: `timeToFlip` (value of `:Gmte#`; assumed to be the
    flip tolerance - confirm)
  - all other fields are not watched.
- Add `snapshot(self) -> dict[str, Any]`: `{n: getattr(self, n) for n in SETTING_FIELDS}`.
- Change `parseSetting`:
  1. `before = self.snapshot()` after validation passed (not on failed parse,
     so a malformed response never reports changes).
  2. parse as today (the early `return True` for old firmware stays).
  3. Split the parsing into `parseSetting` (wrapper) + `parseValues`
     (existing assignments), so both firmware return paths end in one place:
     `self.changed = {n for n, v in self.snapshot().items() if before[n] != v}`.
- Add `hasChanged(self) -> bool: return bool(self.changed)`.
- First parse after start: all values differ from defaults -> reports changed.
  That is acceptable (initial load); optionally skip when a
  `self.initialized` flag is False.

### 2. `mountSignals.py`
- Add `settingChanged = Signal(Setting)` (optionally `Signal(set)` with names;
  prefer passing `Setting`, listeners read `setting.changed`).

### 3. `mount.py`
- `resultCycleSetting`:
  ```python
  if result:
      self.signals.settingDone.emit(self.setting)
      if self.setting.hasChanged():
          self.signals.settingChanged.emit(self.setting)
  ```
- Thread note: `changed` is written in the worker and read in the result
  method after the worker finished, so no lock is needed.

### 4. GUI (only if requested)
- No consumer is added now (stay within task). Listeners connect with
  `self.app.dReg.mount.signals.settingChanged.connect(...)`.

### 5. Tests (module scope, 100 % coverage)
- `../tests/unit_tests/mountcontrol/test_setting.py`
  - first parse -> `changed` non-empty (or empty when `initialized` logic used)
  - second parse with identical response -> `changed == set()`
  - parse with one chunk modified -> `changed == {"expectedField"}`
  - ignored volatile fields do not appear
  - failed parse (wrong chunks / malformed) -> `changed` untouched
  - both firmware paths (< and >= 3.2.5)
  - `hasChanged` true/false
- `../tests/unit_tests/mountcontrol/test_mount.py`
  - `resultCycleSetting(True)` with changes -> both signals emitted
  - without changes -> only `settingDone`
  - `result=False` -> no signal

### 6. Finish
- `uv run ruff format` / `ruff check`, `uv run lint-imports`
- Full test run with coverage, must stay at 100 %.

## Open questions
1. ~~Which fields~~ answered: mount limits and flip tolerance (see above).
2. Should the first parse after startup emit `settingChanged`?
3. Signal payload: `Setting` (listener reads `changed`) or the set of names?



