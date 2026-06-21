# Mount Property Initialization - Moved Back to __init__

## Summary

With the new two-phase initialization in DeviceRegistry, properties that were previously deferred to `startCommunication()` to avoid circular dependencies can now be safely initialized in `__init__()` since `app.mount` is guaranteed to exist (set in PHASE 1).

---

## Changes Made

### 1. sensorWeatherOnline.py

**Before (Deferred):**
```python
def __init__(self, parent: Any) -> None:
    self.location: Any = None  # ← Deferred
    
def startCommunication(self) -> None:
    self.location = self.app.dReg["mount"].obsSite.location  # ← Initialized here
```

**After (Now in __init__):**
```python
def __init__(self, parent: Any) -> None:
    self.location: Any = self.app.mount.obsSite.location  # ← Initialized immediately
    
def startCommunication(self) -> None:
    self.pollOpenWeatherMapData()
    self.app.update3s.connect(self.pollOpenWeatherMapData)
    # ← No location initialization needed
```

**Why This Works:**
- SensorWeatherOnline is created in Phase 2 (during SensorWeather initialization)
- app.mount is already set in Phase 1
- app.mount.obsSite.location is safely accessible

---

### 2. directWeather.py

**Before (Deferred):**
```python
def __init__(self, app: Any = None) -> None:
    self.enabled: bool = False
    # Connection deferred to startCommunication to avoid circular dependency

def startCommunication(self) -> None:
    self.app.dReg["mount"].signals.settingDone.connect(self.updateData)  # ← Deferred
    self.enabled = True

def stopCommunication(self) -> None:
    self.app.dReg["mount"].signals.settingDone.disconnect(self.updateData)
```

**After (Now in __init__):**
```python
def __init__(self, app: Any = None) -> None:
    self.enabled: bool = False
    # Connection established during init (app.mount exists from Phase 1)
    self.app.mount.signals.settingDone.connect(self.updateData)  # ← Moved back

def startCommunication(self) -> None:
    self.enabled = True
    self.app.dReg["directWeather"].stat = False

def stopCommunication(self) -> None:
    self.app.mount.signals.settingDone.disconnect(self.updateData)  # ← Now uses app.mount
    self.signals.deviceDisconnected.emit("DirectWeather")
```

**Why This Works:**
- DirectWeather is created in Phase 2
- app.mount is already set in Phase 1
- app.mount.signals is safely accessible
- Note: Uses `app.mount` instead of `app.dReg["mount"]` since registry is still initializing

---

## Critical Pattern Recognition

### Why `app.mount` vs `app.dReg["mount"]`?

During Phase 2 of DeviceRegistry initialization:

```
Phase 2 (Creating devices):
├─ Creating Device A
│  └─ Can access app.mount ✓ (set in Phase 1)
│  └─ Cannot access app.dReg["device_name"] ✗ (registry still building)
├─ Creating Device B
└─ Registry still being built...

After Phase 2 completes:
├─ All devices created
├─ app.mount accessible ✓
└─ app.dReg fully populated ✓
```

**Rule:** During Phase 2, use `app.mount` directly, not `app.dReg["mount"]`

---

## Devices Already Correct

These devices already had mount properties in __init__ (no changes needed):

- **camera.py** (line 37): `self.obsSite = app.mount.obsSite` ✓
- **seeingWeather.py** (line 38): `self.location = app.mount.obsSite.location` ✓
- **hipparcos.py** (direct init): `self.lat = app.mount.obsSite.location.latitude.degrees` ✓

---

## Test Results

✅ **3711 tests passing** (after moving properties back)
✅ **0 failures** (no regressions)
✅ **All linting checks passed**

---

## Architecture Improvement

### Before Two-Phase Initialization

```
Problem: Need to defer mount property access
├─ app.mount created in mainApp
├─ DeviceRegistry created
├─ Devices created that need app.mount
└─ Result: Properties initialized later in startCommunication()
```

### After Two-Phase Initialization

```
Benefit: Can move properties back to __init__
├─ Phase 1: app.mount set
├─ Phase 2: Devices created (can access app.mount)
└─ Result: Cleaner initialization, properties set immediately
```

---

## Files Modified

1. **src/mw4/logic/environment/sensorWeatherOnline.py**
   - Moved `location` from `startCommunication()` to `__init__()`
   - Uses `app.mount.obsSite.location`

2. **src/mw4/logic/environment/directWeather.py**
   - Moved signal connection from `startCommunication()` to `__init__()`
   - Uses `app.mount.signals` instead of `app.dReg["mount"].signals`
   - Moved disconnect to `stopCommunication()`

---

## Conclusion

With the two-phase initialization in DeviceRegistry:

✅ Properties can be initialized immediately in `__init__()` 
✅ No deferral to `startCommunication()` needed
✅ Cleaner, more direct initialization
✅ All tests pass
✅ Code quality maintained

All deferred initialization workarounds have been eliminated!

---

*Update completed: June 6, 2026*
*Test Status: 3711 passing, 0 failures*
*Code Quality: All checks passed*

