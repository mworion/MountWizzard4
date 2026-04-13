# Plan: Fix Readability Issues 4.1, 4.2, 4.3, 4.5, 4.7, 4.8

**Date:** 2026-04-13  
**Scope:** Non-breaking renames and annotation additions identified in `code_review_report.md`

---

## Overview

Fix six categories of naming and annotation issues:
- **4.1** — Rename two snake_case Qt signals (`game_sL`/`game_sR`) to camelCase (`gameSL`/`gameSR`)
- **4.2** — Fix `"ImageMange"` dict-key typo → `"ImageManage"`
- **4.3** — Rename three snake_case functions to camelCase
- **4.5** — Extract magic number `30` to named constant `MAX_THREAD_COUNT`
- **4.7** — Add missing `-> bool` return type to `clearAlignAndBackup`
- **4.8** — Annotate all `__init__(self, mainW)` parameters with `MainWindow` type via `TYPE_CHECKING` guard

No runtime behavior changes; only cosmetic and type-system improvements.

---

## Files Changed

### Issue 4.1 — Rename `game_sL` / `game_sR` → `gameSL` / `gameSR`

| File | Change |
|---|---|
| `src/mw4/mainApp.py` lines 94–95 | Rename Signal class attributes |
| `src/mw4/gui/mainWaddon/tabImage_Manage.py` line 58 | `.game_sL.connect(...)` → `.gameSL.connect(...)` |
| `src/mw4/gui/mainWaddon/tabMount_Move.py` line 103 | `.game_sR.connect(...)` → `.gameSR.connect(...)` |
| `src/mw4/gui/mainWaddon/tabSett_Misc.py` lines 159, 161 | `.game_sL.emit(...)` / `.game_sR.emit(...)` → `.gameSL.emit(...)` / `.gameSR.emit(...)` |
| `tests/unit_tests/unitTestAddOns/baseTestApp.py` lines 1160–1161 | Rename signal stubs in App test class |

### Issue 4.2 — Fix `"ImageMange"` typo

| File | Change |
|---|---|
| `src/mw4/gui/mainWindow/mainWindowAddons.py` line 58 | Dict key `"ImageMange"` → `"ImageManage"` |

### Issue 4.3 — Rename snake_case functions to camelCase

| File | Old name | New name |
|---|---|---|
| `src/mw4/logic/environment/sensorWeatherBoltwood.py` | `convert_knots2kmh` | `convertKnots2Kmh` |
| `src/mw4/logic/environment/sensorWeatherBoltwood.py` | `convert_mph2kmh` | `convertMph2Kmh` |
| `src/mw4/logic/satellites/satellite_calculations.py` | `west_of_meridian_at` (inner fn) | `westOfMeridianAt` |
| `src/mw4/cli.py` | `read_options` | `readOptions` |

Test files to update:
- `tests/unit_tests/logic/environment/test_boltwoodWeather.py` — rename 4 test functions, update method call sites
- `tests/unit_tests/mainApp/test_cli.py` — rename 7 test functions, update `cli.read_options()` → `cli.readOptions()` call sites

### Issue 4.5 — Extract magic number

| File | Change |
|---|---|
| `src/mw4/mainApp.py` | Add `MAX_THREAD_COUNT: int = 30` class-level constant; replace `30` in `_initCore` |

### Issue 4.7 — Return type annotation

| File | Change |
|---|---|
| `src/mw4/gui/mainWaddon/tabModel.py` line 177 | `def clearAlignAndBackup(self):` → `def clearAlignAndBackup(self) -> bool:` |

### Issue 4.8 — Annotate `__init__(self, mainW)` across all addon classes

Add `TYPE_CHECKING` guard + `mainW: MainWindow` + `-> None` to all 27 files in `src/mw4/gui/mainWaddon/` and `src/mw4/gui/mainWindow/mainWindowAddons.py`.

Pattern:
```python
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from mw4.gui.mainWindow.mainWindow import MainWindow
...
def __init__(self, mainW: "MainWindow") -> None:
```

---

## Step-by-Step Instructions

**Step 1 — Issue 4.1: Rename gamepad signals**
1. In `mainApp.py` lines 94–95, rename `game_sL` → `gameSL` and `game_sR` → `gameSR`.
2. In `tabImage_Manage.py` line 58: `game_sL` → `gameSL`.
3. In `tabMount_Move.py` line 103: `game_sR` → `gameSR`.
4. In `tabSett_Misc.py` lines 159, 161: update both `.emit()` calls.
5. In `baseTestApp.py` lines 1160–1161: rename the two Signal stub declarations.

**Step 2 — Issue 4.2: Fix typo**
1. In `mainWindowAddons.py` line 58: `"ImageMange"` → `"ImageManage"`.

**Step 3a — Issue 4.3: Boltwood renames in source**
1. `sensorWeatherBoltwood.py` lines 48, 52, 98, 100: rename methods and call sites.

**Step 3b — Issue 4.3: Boltwood test updates**
1. `test_boltwoodWeather.py`: rename 4 test functions; update method call sites.

**Step 3c — Issue 4.3: satellite_calculations rename**
1. `satellite_calculations.py` lines 109, 114, 115: rename inner function and all references.

**Step 3d — Issue 4.3: cli.py rename**
1. `cli.py` lines 22, 53: rename function and call site.

**Step 3e — Issue 4.3: cli test updates**
1. `test_cli.py`: rename 7 test functions; update all `cli.read_options()` → `cli.readOptions()` calls.

**Step 4 — Issue 4.5: Extract magic number**
1. Add `MAX_THREAD_COUNT: int = 30` class-level constant to `MountWizzard4`.
2. Replace literal `30` with `self.MAX_THREAD_COUNT` in `_initCore`.

**Step 5 — Issue 4.7: Return type annotation**
1. `tabModel.py` line 177: add `-> bool`.

**Step 6 — Issue 4.8: Annotate mainW parameter**
1. Add `TYPE_CHECKING` guard + annotate all 28 `__init__` methods.

**Step 7 — Lint and format**
1. `uv run ruff check src/mw4` — fix all violations.
2. `uv run ruff format src/mw4` — normalize formatting.

---

## Testing Strategy

| Changed symbol | Test file(s) to update | Verification |
|---|---|---|
| `gameSL` / `gameSR` signals | `baseTestApp.py` | Signal stubs renamed; all tab tests pass |
| `"ImageManage"` key | none | `test_mainWindowAddons.py` still passes |
| `convertKnots2Kmh` / `convertMph2Kmh` | `test_boltwoodWeather.py` | 4 renamed test functions pass |
| `westOfMeridianAt` (inner fn) | none needed | Inner name not accessed in tests |
| `readOptions` | `test_cli.py` | 7 renamed test functions + updated call sites pass |
| `MAX_THREAD_COUNT` | none | `test_mainApp.py` tests unaffected |
| `clearAlignAndBackup -> bool` | none | Tests use `mock.patch.object`; annotation is non-runtime |
| `mainW: MainWindow` annotations | none | `TYPE_CHECKING` erased at runtime; fixture unaffected |

Full test run after all changes:
```bash
uv run pytest tests/unit_tests/gui/mainWaddon \
              tests/unit_tests/gui/mainWindow \
              tests/unit_tests/logic/environment \
              tests/unit_tests/logic/satellites \
              tests/unit_tests/mainApp
```

