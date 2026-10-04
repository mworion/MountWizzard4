# Plan – Status Review 2026-09-29, Rec 12 (rest) and D5–D7

Scope: M8, C3, C4, D5, D6, D7 of
[2026-09-26-review.md](2026-09-26-review.md), tracked in
[2026-09-29-status-review.md](2026-09-29-status-review.md).

| #  | File(s)                                   | Change |
|----|-------------------------------------------|--------|
| M8 | `mountcontrol/mount.py`                   | Remove the second `self.mountIsUp: bool = False` in `__init__`. |
| C3 | `mainApp.py`                              | Commented-out `aboutToQuit` line (and its stale comment) removed. |
| C4 | `cli.py`, `loader.py`, `mainApp.py`       | `cli.formatOptions()` turns the parsed `argparse` options into text; `cli.run` passes it to `loader.main(test, arguments)`, which hands it to `MountWizzard4(..., arguments)`. `MountWizzard4` no longer reads `sys.argv` and emits the text as `Arguments` message only when it is not empty. |
| D5 | `logic/dome/dome.py`                      | `calcSlewTarget` is typed `tuple[float, float, float \| None, float \| None]` and returns `None` for x/y explicitly without geometry **and** on a geometry error (before, a geometry error indexed `intersect = None` → `TypeError`). |
| D6 | `logic/dome/dome.py`                      | `targetInDomeShutter` uses `M - B` in the BC check (as in the referenced formula), typed with `np.ndarray`; typo "mez" → "met". |
| D7 | `logic/modelBuild/modelRun.py`            | `startNewSlew` uses `next(iterator, None)`; `modelRunKey` stays a `str` (`""` when exhausted). |

Tests (mirrored in `tests/unit_tests`): `test_mainApp.py` (arguments message
with/without text), `test_cli.py` (`formatOptions`, `main` call args),
`test_loader_main.py` (arguments passed through), `test_dome.py` (geometry
error without intersect, BC check with `M - B`), `test_modelRun.py`
(`modelRunKey == ""` after the iterator is exhausted).

Finish: Ruff format/check, full unit test run with 100 % coverage, update of
the status review.

## Status (2026-09-29)

| #  | Status |
|----|--------|
| M8 | ✅ Done |
| C3 | ✅ Done |
| C4 | ✅ Done – `cli.formatOptions()` → `loader.main` → `MountWizzard4(..., arguments)` |
| D5 | ✅ Done – also fixes the `TypeError` on a real geometry error |
| D6 | ✅ Done |
| D7 | ✅ Done |

Verification: Ruff format/check clean, 4652 passed, 38 skipped (`-n auto`),
coverage 100 %. Status review updated (sections 3.3, 5, 7).

