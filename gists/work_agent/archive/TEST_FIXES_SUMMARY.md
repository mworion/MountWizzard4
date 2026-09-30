# Test Fixes Summary - Host/MAC Property Migration

## Overview
Fixed unit tests that were broken by the refactoring of the Mount device configuration, where the `host` property was split into `hostAddress` and `port`, and the `MAC` property was moved to the config dataclass.

## Changes Made

### 1. Source Code Fix
**File**: `src/mw4/mountcontrol/mount.py`

Fixed the `bootMount()` method which was trying to access `self.MAC` (non-existent attribute) instead of the correct `self.config.MAC`:

- **Line 374**: Changed `if self.MAC is None:` to `if self.config.MAC is None:`
- **Line 382**: Changed `wakeonlan.send_magic_packet(self.MAC, **kwargs)` to `wakeonlan.send_magic_packet(self.config.MAC, **kwargs)`

### 2. Test Fixtures Fixed

#### test_mount.py
- **Fixture** (lines 27-35): Updated `MountDevice` constructor call to remove deprecated `host=None` and `MAC="..."` parameters. Set MAC via `config` instead.
- **test_properties_MAC** (line 41-43): Changed to use `function.config.MAC` instead of `function.MAC`
- **test_cycleCheckMountIsUp_1-3** (lines 166-184): Replaced `function.host` with proper `function.config.hostAddress` and `function.config.port` assignments
- **test_bootMount_1-5** (lines 398-430): 
  - Replaced `function._MAC` with `function.config.MAC`
  - Removed deprecated `bAddress` and `bPort` parameters
  - Set config values directly: `function.config.wolAddress`, `function.config.wolPort`
- **test_bootMount_with_bAddress_only** (lines 627-631): Updated to set config properties instead of method parameters

#### test_geometry.py
- **Fixture** (lines 22-33): Updated `MountDevice` constructor to remove deprecated `host=None` and `MAC=None` parameters

#### test_obsSite.py
- **Parent class** (lines 27-34): Added `config` attribute with `hostAddress` and `port` properties to support Connection class initialization

## Test Results

### Before Fixes
- test_mount.py: 6 failures (cycleCheckMountIsUp and bootMount tests)
- test_geometry.py: 18 errors (fixture initialization)
- test_obsSite.py: 6 failures (Connection initialization)
- Overall mountcontrol: 6 failed, 699 passed, 18 errors

### After Fixes
- test_mount.py: **99 passed** ✓
- test_geometry.py: **18 passed** ✓
- test_obsSite.py: **133 passed** ✓
- Overall mountcontrol: **723 passed** ✓
- Overall base tests: **375 passed** ✓

## Files Modified
1. `src/mw4/mountcontrol/mount.py` - Fixed source code bug
2. `tests/unit_tests/mountcontrol/test_mount.py` - Fixed 7 tests
3. `tests/unit_tests/mountcontrol/test_geometry.py` - Fixed fixture
4. `tests/unit_tests/mountcontrol/test_obsSite.py` - Fixed Parent class

## Linting & Formatting
All modified files pass:
- ✓ Ruff linting
- ✓ Ruff formatting

## Migration Pattern
The refactoring follows the pattern:
```python
# Old
function.host = ("localhost", 3492)
self.MAC = "00:00:00:00:00:00"

# New
function.config.hostAddress = "localhost"
function.config.port = 3492
function.config.MAC = "00:00:00:00:00:00"
```

## Notes
- The `host` parameter in MountDevice constructor has been completely removed
- Configuration is now centralized in the `DeviceConfigMount` dataclass
- The Connection class properly accesses `parent.config.hostAddress` and `parent.config.port`
- All test Parent classes now properly define config attributes when needed

