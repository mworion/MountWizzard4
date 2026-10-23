# Moving Mount Device Initialization into DeviceRegistry - Architecture Plan

## Problem Analysis

Currently:
```python
# mainApp.py - Two-phase initialization
self.mount = MountDevice(self, verbose=True)  # Phase 1: Direct creation
self.dReg: DeviceRegistry = DeviceRegistry(self)  # Phase 2: Registry creation
```

The circular dependency issue:
```
If we move mount creation into DeviceRegistry.__init__():
  app.dReg["mount"] is being created
    └─ But other devices (Camera, SeeingWeather, etc.) need app.mount during THEIR __init__
       ├─ app.mount doesn't exist yet (it's being created right now)
       └─ CIRCULAR DEPENDENCY ❌

Also, app.dReg isn't even assigned to app yet during DeviceRegistry.__init__()!
```

### Devices That Depend on Mount During Initialization

1. **camera.py** (line ~45): `self.obsSite = app.mount.obsSite` in __init__
2. **hipparcos.py** (line ~60): `self.lat = app.mount.obsSite.location.latitude.degrees` in __init__
3. **seeingWeather.py** (line ~51): `self.location = app.mount.obsSite.location` in __init__
4. **All other devices**: Can safely access mount via registry or deferred init

---

## Solution: Dependency-Aware Sequential Initialization

### Key Insight

The mount device has **no dependencies** on other devices during its creation. Therefore we can:

1. Create mount first
2. Register it with app
3. Create other devices (which can now access app.mount)
4. Store them in registry

**The trick**: Don't try to create mount INSIDE DeviceRegistry.__init__(). Instead, restructure to use a **factory method pattern** with explicit sequencing.

---

## Implementation Strategy

### Option A: Move Mount Creation to App, Control Registry Sequencing (Recommended)

**Pros**:
- Simplest change
- Maintains single responsibility (app handles initialization sequencing)
- Registry focuses on device management
- Backward compatible

**Cons**:
- Mount creation still outside registry (but registry controls other devices)

```python
# mainApp.__init__()
self.mount = MountDevice(self, verbose=True)  # Create mount first
self.dReg: DeviceRegistry = DeviceRegistry(self)  # Registry handles all other devices
```

### Option B: Move Mount Creation Inside Registry with Two-Phase Init (More Ambitious)

**Pros**:
- Single source of truth for device initialization
- Cleaner from a code organization perspective

**Cons**:
- Requires careful refactoring of registry initialization
- Requires devices to accept optional mount dependency parameter

```python
# Registry.__init__()
def __init__(self, app: Any) -> None:
    self.app = app
    
    # Phase 1: Create mount (no dependencies)
    mount_instance = MountDevice(app, verbose=True)
    app.mount = mount_instance
    self.mount_entry = DeviceEntry(...)
    
    # Phase 2: Create dependent devices
    # Now app.mount exists, so dependent devices can access it
    self.drivers = {...}
```

### Option C: Hybrid - Factory with Dependency Injection

**Pros**:
- Maximum flexibility
- Explicit dependency management
- Easy to test

**Cons**:
- More refactoring required
- Requires changing device constructors

```python
# Device constructors accept optional mount parameter
class Camera:
    def __init__(self, app: Any, mount: MountDevice | None = None):
        self.app = app
        self.mount = mount or app.mount  # Use provided or fallback
        self.obsSite = self.mount.obsSite
```

---

## Recommended Solution: Option B (Two-Phase Registry Initialization)

This is the cleanest long-term architecture because:
- **Single source of truth**: All device initialization happens in registry
- **No hidden dependencies**: Device creation order is explicit in registry code
- **Future-proof**: Easy to add new devices and understand initialization order

### Implementation Steps

1. **Extract mount creation logic** from mainApp to a separate method in MountDevice
2. **Refactor DeviceRegistry.__init__()** with explicit two phases:
   - **Phase 1**: Create mount (set app.mount)
   - **Phase 2**: Create other devices
3. **Update mainApp**: Just call DeviceRegistry, which handles everything
4. **Add dependency tracking** (comments/documentation) in registry

---

## Code Changes Required

### File 1: mountcontrol/mount.py
- Add class method `createMountDevice()` if needed (optional, direct instantiation is fine)

### File 2: base/deviceRegistry.py
```python
def __init__(self, app: Any) -> None:
    self.app = app
    
    # Phase 1: Create mount device (no dependencies)
    from mw4.mountcontrol.mount import MountDevice
    mount_instance = MountDevice(app, verbose=True)
    app.mount = mount_instance  # Make available for dependent devices
    
    # Phase 2: Create all other devices
    # Now app.mount exists, so Camera, SeeingWeather, Hipparcos can access it safely
    self.drivers: dict[str, DeviceEntry] = {
        "camera": ...  # Can access app.mount
        "mount": DeviceEntry(name="mount", instance=app.mount, ...)
        ...
    }
```

### File 3: mainApp.py
```python
def __init__(self, ...):
    # ... earlier setup ...
    
    # Single initialization point:
    # DeviceRegistry now handles ALL device setup in correct sequence
    self.dReg: DeviceRegistry = DeviceRegistry(self)
    
    # mount is now available via self.dReg["mount"] or self.mount (already set by registry)
```

---

## Benefits of This Architecture

1. **No Circular Dependencies**: Mount created first, then dependent devices
2. **Single Initialization Point**: All device setup in DeviceRegistry
3. **Explicit Dependencies**: Registry code documents what depends on what
4. **Maintainability**: New devices added to one place with clear sequence
5. **Testability**: Easy to mock registry initialization phases
6. **Loose Coupling**: App doesn't need to know mount creation details

---

## Potential Issues & Mitigations

### Issue 1: Import Cycle
- **Problem**: deviceRegistry.py imports MountDevice, mainApp imports DeviceRegistry
- **Solution**: This is fine! One-way dependency is not circular

### Issue 2: Device Initialization Errors
- **Problem**: If mount creation fails, other devices shouldn't be created
- **Solution**: Wrap in try-except with proper error handling

### Issue 3: Testing with Mock Registry
- **Problem**: Tests might need to mock registry
- **Solution**: Add factory option: `DeviceRegistry(app, create_mount=True)`

### Issue 4: Backward Compatibility
- **Problem**: Code might reference `app.mount` directly
- **Solution**: Registry sets `app.mount`, so it still works

---

## Alternative Consideration: Keep Current Architecture

If keeping current two-statement approach, could improve by:
1. Adding validation that mount is set before registry creation
2. Adding explicit comments about required order
3. But this doesn't solve the fundamental issue of scattered initialization logic

---

## Recommendation

**Implement Option B (Two-Phase Registry Initialization)** because:
1. ✅ Solves circular dependency cleanly
2. ✅ Centralizes device initialization logic
3. ✅ Makes dependency order explicit
4. ✅ Easier to maintain long-term
5. ✅ No need to change device constructors
6. ✅ Backward compatible (app.mount still available)

The key insight is: **Mount has zero dependencies, so create it first and make it available before creating dependent devices**.

---

*Architecture Plan - June 6, 2026*

