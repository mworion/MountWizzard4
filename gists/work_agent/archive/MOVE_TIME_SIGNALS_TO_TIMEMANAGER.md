# Move Time Signals to TimeManager Class

## Overview
Move cyclic time signals from `MountWizzard4` class to `TimeManager` class, making TimeManager the single source of truth for these signals.

## Signals to Move
- Cyclic signals: `update0_1s`, `update1s`, `update3s`, `update10s`, `update30s`, `update3m`, `update30m`
- Start signals: `start3s`

## Changes Required

### 1. TimeManager Class (timeManager.py)
- Add signal definitions as class attributes
- Update `emitCyclic()` to emit from `self` instead of `self.app`
- Update `emitStart()` to emit from `self` instead of `self.app`

### 2. MountWizzard4 Class (mainApp.py)
- Remove signal definitions (lines 73-81)
- No functional changes needed; connections still work via `app.timeMgr.<signal>`

### 3. BaseTestApp Class (baseTestApp.py)
- Option 1: Remove duplicate signal definitions and access via `self.timeMgr`
- Option 2: Create convenience properties that reference `timeMgr` signals

### 4. Code Using These Signals (40+ files)
- Update all `.connect()` calls from `app.<signal>` to `app.timeMgr.<signal>`
- Update all `.disconnect()` calls similarly

### 5. Test Files
- Update test mock connections to reference `timeMgr` signals
- Ensure test coverage remains at 100%

## Files to Update

### Core Files
- `src/mw4/base/timeManager.py` - Add signals, update emission logic
- `src/mw4/mainApp.py` - Remove signal definitions
- `tests/unit_tests/unitTestAddOns/baseTestApp.py` - Update signal access
- `tests/unit_tests/base/test_timeManager.py` - Update tests

### GUI Files (40+ files)
- `src/mw4/gui/mainWindow/mainWindow.py`
- `src/mw4/gui/extWindows/video/videoBase.py`
- `src/mw4/gui/extWindows/hemisphere/hemisphereDraw.py`
- `src/mw4/gui/extWindows/measure/measureW.py`
- `src/mw4/gui/extWindows/messageW.py`
- `src/mw4/gui/extWindows/simulator/dome.py`
- `src/mw4/gui/extWindows/image/imageW.py`
- `src/mw4/gui/extWindows/keypadW.py`
- `src/mw4/gui/mainWaddon/tabEnviron_Weather.py`
- `src/mw4/gui/mainWaddon/tabMount_Sett.py`
- `src/mw4/gui/mainWaddon/tabSat_Search.py`

### Logic Files (5+ files)
- `src/mw4/mountcontrol/mount.py`
- `src/mw4/logic/dome/dome.py`
- `src/mw4/logic/environment/seeingWeather.py`
- `src/mw4/logic/environment/sensorWeatherBoltwood.py`
- `src/mw4/logic/environment/sensorWeatherOnline.py`

## Benefits
- Cleaner architecture: TimeManager owns the signals it emits
- Single source of truth for cyclic signals
- Easier to understand signal flow
- Better encapsulation

