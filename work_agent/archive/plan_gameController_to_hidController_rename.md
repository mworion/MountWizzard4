# Plan: Rename gameController to hidController

## Overview
Rename the `gameController` module and all related classes, methods, signals, and references to `hidController` to better reflect its purpose as a HID (Human Interface Device) controller.

## Scope of Changes

### 1. Directory Structure
- Rename directory: `src/mw4/logic/gameController/` → `src/mw4/logic/hidController/`
- Rename directory: `tests/unit_tests/logic/gameController/` → `tests/unit_tests/logic/hidController/`

### 2. Files to Rename
| Old Path | New Path |
|----------|----------|
| `src/mw4/logic/gameController/gameController.py` | `src/mw4/logic/hidController/hidController.py` |
| `src/mw4/logic/gameController/__init__.py` | `src/mw4/logic/hidController/__init__.py` |
| `tests/unit_tests/logic/gameController/test_gameController.py` | `tests/unit_tests/logic/hidController/test_hidController.py` |
| `tests/unit_tests/logic/gameController/__init__.py` | `tests/unit_tests/logic/hidController/__init__.py` |

### 3. Class Names to Rename
| Old Name | New Name |
|----------|----------|
| `GameController` | `HidController` |
| `GameControllerSignals` | `HidControllerSignals` |
| `DeviceConfigGameController` | `DeviceConfigHidController` |

### 4. Variable and Method Names

#### In HidController class:
- `workerGameController` → `workerHidController`
- `runnerGameController()` → `runnerHidController()`
- `readGameController()` → `readHidController()`
- `sendGameControllerSignals()` → `sendHidControllerSignals()`
- `isValidGameControllers()` → `isValidHidControllers()`

#### Local variables in methods:
- `gameControllerDevice` → `hidControllerDevice`
- `reportOld` → `reportOld` (keep as is)

### 5. Signal Names in mainApp.py
| Old Signal Name | New Signal Name |
|-----------------|-----------------|
| `gameControllerIsRunning` | `hidControllerIsRunning` |
| `gameABXY` | `hidABXY` |
| `gamePMH` | `hidPMH` |
| `gameDirection` | `hidDirection` |
| `gameSL` | `hidSL` |
| `gameSR` | `hidSR` |

### 6. Files Requiring Import/Reference Updates
| File Path | Changes |
|-----------|---------|
| `src/mw4/base/deviceRegistry.py` | Update import: `from mw4.logic.gameController.gameController` → `from mw4.logic.hidController.hidController` |
| `src/mw4/gui/extWindows/devicePopupW.py` | Update import: `from mw4.logic.gameController.gameController` → `from mw4.logic.hidController.hidController` |
| `tests/unit_tests/gui/extWindows/test_devicePopupW.py` | Update imports and references (2 occurrences) |

### 7. Device Registry Entry
In `src/mw4/base/deviceRegistry.py`:
- Change entry name: `"gameController"` → `"hidController"`
- Update reference in `deviceSpec`

### 8. UI Files and Config
- `src_add/widgets/setting.ui`: Widget names reference `hidDevice`, `hidSetup`, `hidGroup`, `hidList` (already updated or will be handled separately)
- No changes needed for UI file as it references the generic "hid" framework

### 9. Log Messages
Update log messages and comments that reference "GameController" → "HidController"

## Implementation Steps

1. **Create new directories**
   - Create `src/mw4/logic/hidController/`
   - Create `tests/unit_tests/logic/hidController/`

2. **Rename/Move files**
   - Move and rename `gameController.py` → `hidController.py`
   - Move and rename test files
   - Move `__init__.py` files

3. **Update source code in hidController.py**
   - Rename all class names
   - Rename all method names
   - Rename all variable names

4. **Update test files**
   - Update imports and class names
   - Rename test functions and classes
   - Update all references

5. **Update import statements**
   - `deviceRegistry.py`
   - `devicePopupW.py`
   - `test_devicePopupW.py`

6. **Update signal names in mainApp.py**
   - Rename all gamepad-related signals

7. **Update device registry entry**
   - Change device name in `deviceSpec`

8. **Delete old directories**
   - Remove `src/mw4/logic/gameController/`
   - Remove `tests/unit_tests/logic/gameController/`

9. **Run tests**
   - Verify all tests pass
   - Verify 100% coverage
   - Run Ruff linter

## Files Modified Summary
- **Source files**: 1 (hidController.py)
- **Test files**: 1 (test_hidController.py)
- **Registry/config files**: 2 (deviceRegistry.py, devicePopupW.py)
- **Main app**: 1 (mainApp.py)
- **Test utilities**: 1 (test_devicePopupW.py)
- **Total files**: 6 files to modify + 2 test files + 4 files to rename/move

## Testing Strategy
- All existing tests will be updated to use new class/method names
- Coverage must remain at 100%
- Ruff linting must pass
- No functional changes, only renaming

