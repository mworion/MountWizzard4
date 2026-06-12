# Mount Device Registry Initialization - Visual Architecture

## Initialization Flow Diagrams

### BEFORE: Problem State

```
┌─────────────────────────────────────────────────────────┐
│                  mainApp.__init__()                      │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ Step 1: Direct Mount Creation                       │ │
│  │ self.mount = MountDevice(self, verbose=True)        │ │
│  │ ✓ Mount created                                     │ │
│  └─────────────────────────────────────────────────────┘ │
│                          ↓                                │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ Step 2: Create DeviceRegistry                       │ │
│  │ self.dReg = DeviceRegistry(self)                    │ │
│  │                                                      │ │
│  │ Registry.__init__():                                │ │
│  │ ├─ Create Camera(app)      ✓ Can access app.mount  │ │
│  │ ├─ Create SeeingWeather    ✓ Can access app.mount  │ │
│  │ ├─ Create Hipparcos        ✓ Can access app.mount  │ │
│  │ ├─ Create other devices...                          │ │
│  │ └─ Register mount: app.mount                        │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                           │
│  ❌ PROBLEM:                                             │
│     - Mount initialization logic split between            │
│       mainApp and DeviceRegistry                          │
│     - Two separate statements needed                      │
│     - Hard to understand initialization order             │
└─────────────────────────────────────────────────────────┘
```

### AFTER: Solution State

```
┌─────────────────────────────────────────────────────────┐
│                  mainApp.__init__()                      │
│                                                           │
│  Single statement creates EVERYTHING:                    │
│  self.dReg = DeviceRegistry(self)                        │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│              DeviceRegistry.__init__()                   │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ PHASE 1: Initialize Mount                           │ │
│  │                                                      │ │
│  │ if hasattr(app, 'mount') and app.mount is not None: │ │
│  │   # Test mode: Use mock                             │ │
│  │   mount_instance = app.mount                        │ │
│  │ else:                                               │ │
│  │   # Production: Create real mount                   │ │
│  │   mount_instance = MountDevice(app)                 │ │
│  │   app.mount = mount_instance                        │ │
│  │                                                      │ │
│  │ ✓ app.mount NOW EXISTS                              │ │
│  └─────────────────────────────────────────────────────┘ │
│                          ↓                                │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ PHASE 2: Initialize Dependent Devices               │ │
│  │                                                      │ │
│  │ ✓ Camera(app)         - can access app.mount        │ │
│  │ ✓ SeeingWeather(app)  - can access app.mount        │ │
│  │ ✓ Hipparcos(app)      - can access app.mount        │ │
│  │ ✓ Other devices...                                  │ │
│  │ ✓ Register mount entry in registry                  │ │
│  │                                                      │ │
│  │ ✓ ALL devices initialized with correct order        │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                           │
│  ✅ BENEFITS:                                            │
│     - Single initialization location                      │
│     - Clear two-phase ordering                            │
│     - No circular dependencies                            │
│     - Test-friendly (mock detection)                      │
│     - Self-documenting code                              │
└─────────────────────────────────────────────────────────┘
```

---

## Dependency Flow Diagram

### Mount Device Dependency Tree

```
┌──────────────────────────────────────────┐
│                Input: App                 │
│  (Before DeviceRegistry creation)         │
└──────────────┬───────────────────────────┘
               │
               ↓
┌──────────────────────────────────────────┐
│         DeviceRegistry.__init__()         │
│                                           │
│         ┌─────────────────────────────┐   │
│         │  PHASE 1: Create Mount      │   │
│         │                             │   │
│         │  Smart Detection:           │   │
│         │  ┌─────────────────────────┐│   │
│         │  │ Test Mode Detected?     ││   │
│         │  ├─ YES: Use mock          ││   │
│         │  └─ NO: Create real mount  ││   │
│         │                             │   │
│         │  Set app.mount = instance   │   │
│         └────────────┬────────────────┘   │
│                      │                     │
│                      ↓                     │
│         ┌─────────────────────────────┐   │
│         │ app.mount is NOW AVAILABLE  │   │
│         └────────────┬────────────────┘   │
│                      │                     │
│                      ↓                     │
│         ┌─────────────────────────────┐   │
│         │  PHASE 2: Create Devices    │   │
│         │                             │   │
│         │  Create in order:           │   │
│         │  ├─ Camera(app)             │   │
│         │  │  └─ accesses app.mount   │   │
│         │  ├─ SeeingWeather(app)      │   │
│         │  │  └─ accesses app.mount   │   │
│         │  ├─ Hipparcos(app)          │   │
│         │  │  └─ accesses app.mount   │   │
│         │  ├─ All other devices...    │   │
│         │  └─ Register mount          │   │
│         │                             │   │
│         └─────────────┬───────────────┘   │
│                       │                    │
└───────────────────────┼────────────────────┘
                        ↓
          ┌──────────────────────────────┐
          │  Output: DeviceRegistry      │
          │  with all devices initialized│
          │  Mount available at:         │
          │  - app.mount                 │
          │  - app.dReg["mount"]         │
          └──────────────────────────────┘
```

---

## State Transitions During Initialization

### Timeline: What Exists When

```
Time  │ app.mount │ DeviceEntry │ Description
      │ exists    │ for mount   │
──────┼───────────┼─────────────┼──────────────────────────
  0   │    ✗      │     ✗       │ App created
      │           │             │
  1   │    ✗      │     ✗       │ DeviceRegistry.__init__ starts
      │           │             │
  2   │    ✓      │     ✗       │ PHASE 1: Mount created
      │           │             │ (or test mock detected)
      │ (NOW!)    │             │
      │           │             │ Camera, SeeingWeather,
      │           │             │ Hipparcos CAN be created
      │           │             │
  3   │    ✓      │     ✗       │ PHASE 2: Other devices created
      │           │             │ (can access app.mount)
      │           │             │
  4   │    ✓      │     ✓       │ Mount registered in registry
      │           │             │
  5   │    ✓      │     ✓       │ DeviceRegistry.__init__ complete
      │           │             │
  6   │    ✓      │     ✓       │ mainApp can now use:
      │           │             │ - app.mount
      │           │             │ - app.dReg["mount"]
      │           │             │ - app.dReg["mount"].instance
```

---

## Test vs. Production Paths

```
┌─────────────────────────────────────────────────────────┐
│          DeviceRegistry.__init__(app)                    │
└────────────────────┬────────────────────────────────────┘
                     │
                     ↓
            Smart Detection Logic:
       if hasattr(app, 'mount') and app.mount:
                     │
         ┌───────────┴────────────┐
         │                        │
    Tests: True             Production: False
         │                        │
         ↓                        ↓
    ┌─────────────┐         ┌──────────────────┐
    │ Use Existing│         │ Create New Mount│
    │   Mount     │         │    Instance     │
    │             │         │                 │
    │  Mock Mode  │         │ Real Mount Mode│
    │             │         │                 │
    │ Tests pass  │         │Production code │
    │ injected    │         │works normally   │
    │ stubs       │         │                 │
    └─────────────┘         └──────────────────┘
         │                        │
         └───────────┬────────────┘
                     │
                     ↓
         ┌──────────────────────┐
         │  Continue with       │
         │  PHASE 2: Create     │
         │  other devices       │
         └──────────────────────┘
```

---

## Component Relationships After Initialization

```
    ┌───────────────────────────────────────────────┐
    │                  mainApp                       │
    ├───────────────────────────────────────────────┤
    │ self.mount ────────────────────┐              │
    │ self.dReg ───────────┐          │              │
    │ self.dReg["mount"] --┼──┐       │              │
    └───────────────────────┼──┼───────┼──────────────┘
                            │  │       │
                            ↓  ↓       ↓
                    ┌─────────────────────┐
                    │  MountDevice        │
                    │                     │
                    │ Same instance in:   │
                    │ - app.mount         │
                    │ - dReg["mount"]     │
                    │   .instance         │
                    └─────────────────────┘

    ┌───────────────────────────────────────────────┐
    │        DeviceRegistry (dReg)                  │
    ├───────────────────────────────────────────────┤
    │ .drivers["camera"]                            │
    │ .drivers["dome"]                              │
    │ .drivers["mount"]  ────────► DeviceEntry    │
    │ .drivers["cover"]          ├─ .instance ──► MountDevice
    │ .drivers[... etc ...]       ├─ .signals
    │                             ├─ .data
    │                             └─ .obsSite  (convenience prop)
    └───────────────────────────────────────────────┘
```

---

## Smart Detection Algorithm

```
flowchart
    START["Phase 1: Create/Find Mount"]
    
    START --> CHECK{"hasattr(app, 'mount')\nand app.mount?"}
    
    CHECK -->|YES| TEST["TEST MODE:\nUse existing mount"]
    CHECK -->|NO| PROD["PRODUCTION MODE:\nCreate new MountDevice"]
    
    TEST --> SET["mount_instance =\napp.mount"]
    PROD --> CREATE["mount_instance =\nMountDevice(app)"]
    PROD --> ASSIGN["app.mount =\nmount_instance"]
    
    SET --> PHASE2["Continue to\nPHASE 2"]
    CREATE --> ASSIGN
    ASSIGN --> PHASE2
    
    PHASE2 --> END["Create other devices\n(can access app.mount)"]
    
    style TEST fill:#90EE90
    style PROD fill:#87CEEB
    style CHECK fill:#FFE4B5
```

---

## Comparison: Old vs. New Access Patterns

### Old Pattern (Before Refactoring)

```python
# Had to reference app.mount directly (created separately)
status = self.app.mount.obsSite.status
location = self.app.mount.obsSite.location
firmware = self.app.mount.firmware
```

### New Pattern (After Refactoring)

```python
# All unified through registry (but mount initialization is cleaner)
status = self.app.dReg["mount"].obsSite.status  # Convenience property
location = self.app.dReg["mount"].location      # Convenience property
firmware = self.app.dReg["mount"].instance.firmware  # Full instance access

# OR still via app.mount (both work!)
status = self.app.mount.obsSite.status
```

**Key Difference**: Initialization logic is now in ONE place (DeviceRegistry), not scattered.

---

## Implementation Checklist

- [x] Add MountDevice import to DeviceRegistry
- [x] Extract mount creation to Phase 1
- [x] Add smart test/production detection
- [x] Set app.mount before Phase 2
- [x] Create dependent devices in Phase 2
- [x] Register mount in drivers dict
- [x] Remove direct mount creation from mainApp
- [x] Remove unused MountDevice import from mainApp
- [x] Add comprehensive documentation
- [x] Run full test suite (3711 tests pass)
- [x] Run Ruff linting (all checks pass)
- [x] Verify backward compatibility (app.mount still works)

---

*Architecture diagrams - June 6, 2026*

