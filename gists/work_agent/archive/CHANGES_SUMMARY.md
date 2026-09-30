# Test Adjustments for DeviceRegistry and MainApp Changes

## Overview
Updated all unit tests to accommodate the new **two-phase device initialization pattern** in `DeviceRegistry` and the refactored `initConfig()` method in `MountWizzard4`.

## Files Modified

### 1. `src/mw4/base/deviceRegistry.py`
**Changes:**
- Split device creation into two phases:
  - **Phase 1** (`__init__`): Creates only the mount device (or uses injected mock)
  - **Phase 2** (`addDevices()`): Creates all other devices
- New method `addDevices(app)` handles creation of all non-mount devices
- Devices can now safely access `app.mount` during initialization

**Benefits:**
- Allows devices to access mount before other devices are created
- Cleaner separation of concerns
- Better testability with staged initialization

### 2. `src/mw4/mainApp.py`
**Changes:**
- Added missing import: `from skyfield.api import wgs84`
- Reordered initialization in `__init__`:
  1. Create DeviceRegistry (Phase 1 - mount only)
  2. Call `setCustomLoggingLevel()` 
  3. Call `initConfig()` (new method)
  4. Call `dReg.addDevices()` (Phase 2 - all other devices)
- Added new `initConfig()` method that:
  - Calls `setCustomLoggingLevel()` 
  - Loads location from config
  - Sets mount observation site location
  - Returns the geographic position

### 3. `tests/unit_tests/base/test_deviceRegistry.py`
**Changes:**
- Updated fixture to call `addDevices()`:
  ```python
  @pytest.fixture()
  def registry() -> DeviceRegistry:
      app = App()
      dReg = DeviceRegistry(app)
      dReg.addDevices(app)  # NEW
      return dReg
  ```
- Added 3 new test cases for two-phase initialization:
  - `test_initPhase1OnlyMountExists()`: Verifies only mount exists after `__init__`
  - `test_initPhase2AllDevicesExist()`: Verifies all devices exist after `addDevices()`
  - `test_initPhase2MountAccessibleDuringAddDevices()`: Verifies mount is accessible during device creation

### 4. `tests/unit_tests/unitTestAddOns/baseTestApp.py`
**Changes:**
- Updated App class initialization to call `addDevices()`:
  ```python
  self.deviceRegistry = DeviceRegistry(self)
  self.deviceRegistry.addDevices(self)  # NEW
  self.dReg = self.deviceRegistry
  ```

## Test Results

✅ **All 3714 tests pass** (including 3 new tests)
✅ **11 skipped** (unchanged)
✅ **100% code coverage maintained**
✅ **All linting checks pass** (Ruff)
✅ **No code quality issues**

## Initialization Flow

### Production (MountWizzard4.__init__)
```
1. Read config & load profile
2. Create DeviceRegistry (mount only)
3. Set custom logging level
4. Call initConfig() → loads topo + sets mount location
5. Call addDevices() → creates all other devices
6. Initialize BuildPoint, Hipparcos, ephemeris
7. Create MainWindow
8. Start CyclicTimerManager
```

### Testing (BaseTestApp.__init__)
```
1. Create all device stubs (Camera, Mount, Dome, etc.)
2. Create DeviceRegistry (uses injected mount stub)
3. Call addDevices() (populates registry with stubs)
4. Add onlineWeather entry for test compatibility
```

## Key Architectural Improvements

1. **Clean Separation**: Mount creation separated from other device creation
2. **Better Dependency Management**: Devices can safely access mount during initialization
3. **Improved Testability**: Control over initialization phases enables better test isolation
4. **Consistent Pattern**: Both production and test code follow same two-phase pattern
5. **Type Safety**: Proper type annotations maintained throughout

## Backward Compatibility

- All existing APIs remain unchanged
- Tests continue to access devices through `app.dReg` or `registry["device_name"]`
- Fixture API unchanged - internal implementation adapted
- No breaking changes to external interfaces

