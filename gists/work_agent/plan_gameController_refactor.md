# Plan: Refactor GameController as a Registered Device

## Goal

Refactor `GameController` from scattered, GUI-mixed code into a proper
logic-layer device registered in `DeviceRegistry` — following the
`SeeingWeather` single-framework pattern — with a `discoverDevices()` method
compatible with the `DevicePopup` discovery protocol (same as INDI/Alpaca),
compliant worker naming, proper `startCommunication()`/`stopCommunication()`
lifecycle methods, and a richer config that includes an `autoStart` flag and
enable/disable flags for `moveRaDec`, `moveAltAz`, and `tracking`.

Device discovery is handled exclusively inside `DevicePopup` (already
prototyped there). `tabSettGui` retains **zero** coupling to the game
controller. The `DeviceRegistry` is the single source of truth for config
persistence. No separate `TabSettGameController` GUI mixin is created; instead
`GameController` is integrated into `tabSettDevice` like every other device.

---

## Context

### Current state (problems)

| Location | Problem |
|---|---|
| `src/mw4/logic/gameController/gameController.py` | Module-level functions using `self` — not a proper class. `Worker` imported nowhere. Nested function inside `startGameController` (indentation bug). References GUI element `self.ui`. |
| `src/mw4/gui/extWindows/setting/tabSettGui.py` | Contains all gamepad business logic: HID enumeration, data conversion, polling worker, signal dispatch. Violates GUI/logic separation. Saves game-controller UI state in its own `SettingGui` config section. |
| `src/mw4/gui/mainWaddon/tabSett_Misc.py` | Duplicate copy of the same logic. |
| `src/mw4/base/deviceRegistry.py` | `GameController` is not a registered device. |

### Reference patterns

| Pattern | Used for |
|---|---|
| `SeeingWeather` | Single-framework device: `framework = "hid"`, `run = {"hid": self}`, device is its own runner. |
| `Remote` | Self-contained device with only one framework key. |
| `IndiClass.discoverDevices(deviceType, host, port)` | Framework-level `discoverDevices` method called by `DevicePopup.discoverDevices`. |
| `AlpacaClass.discoverDevices(deviceType, host, port)` | Same pattern; non-indi/alpaca path skips host/port. |
| `DeviceRegistry.addDevices` | Declarative one-row device registration. |
| `tabSettDevice.deviceUi` | Maps device names to `uiDropDown` + `uiSetup` widgets. |
| `DevicePopup.discoverDevices` | Calls `dReg[device].run[framework].discoverDevices(deviceType)` for HID (no host/port). |

---

## Files Changed

### Created

| File | Purpose |
|---|---|
| `tests/unit_tests/logic/gameController/__init__.py` | Test package marker. |
| `tests/unit_tests/logic/gameController/test_gameController.py` | 100 % coverage for the logic class. |

### Modified

| File | Change summary |
|---|---|
| `src/mw4/logic/gameController/gameController.py` | Complete rewrite as a proper `GameController` class. |
| `src/mw4/base/deviceRegistry.py` | Import `GameController`; add one row to `deviceSpec`. |
| `src/mw4/gui/extWindows/devicePopupW.py` | Fix `discovers["hid"]`: add `"button"` key, replace placeholder `AlpacaClass` with `GameController`. Align `framework2gui["hid"]["deviceName"]` to use the same widget as `discovers["hid"]["deviceList"]`. |
| `src/mw4/gui/extWindows/setting/tabSettDevice.py` | Add `"gameController"` entry to `deviceUi`. |
| `src/mw4/gui/extWindows/setting/tabSettGui.py` | Remove **all** game-controller code and now-unused imports. |
| `tests/unit_tests/gui/extWindows/setting/test_tabSettGui.py` | Remove all game-controller tests. |
| `tests/unit_tests/gui/extWindows/test_devicePopupW.py` | Add / update tests for the HID discover path. |
| `tests/unit_tests/gui/extWindows/setting/test_tabSettDevice.py` | Add test for `gameController` entry in `deviceUi`. |
| `src_add/widgets/setting.ui` | ~~Already done~~ — `gameControllerDevice` (QComboBox) and `gameControllerSetup` (QPushButton) are in place; `gameControllerGroup`/`gameControllerList` removed. No further action needed. |

---

## Detailed Changes

### 1. `src/mw4/logic/gameController/gameController.py` — Complete Rewrite

#### 1.1 `DeviceConfigGameController` (dataclass)

```python
@dataclass
class DeviceConfigGameController:
    deviceName: str  = field(default="")
    autoStart:  bool = field(default=False)
    moveRaDec:  bool = field(default=True)
    moveAltAz:  bool = field(default=True)
    tracking:   bool = field(default=True)
```

- `deviceName` — HID product string of the selected controller.
- `autoStart` — if `True` the device starts automatically at app launch.
  `startCommunication()` returns early when `False`.
- `moveRaDec` / `moveAltAz` / `tracking` — feature-enable flags consumed by
  mount-control GUI tabs that receive the game-controller signals.
- `vendorId` / `productId` are **not** stored in config; they are resolved at
  runtime in `runnerGameController()` by re-enumerating HID devices.

#### 1.2 `GameControllerSignals`

Inherits from `mw4.base.signalsDevices.Signals`.
No extra signals needed — `app.gameABXY`, `app.gamePMH`, `app.gameDirection`,
`app.gameSL`, `app.gameSR` are kept as-is.

```python
class GameControllerSignals(Signals):
    pass
```

#### 1.3 `GameController` class

Class-level attributes:
```
DEVICE_TYPE = "hid"
log         = logging.getLogger("MW4")
```

**`__init__(self, app: Any) -> None`**
```
self.app                              = app
self.threadPool                       = app.threadPool
self.signals                          = GameControllerSignals()
self.data: dict[str, Any]             = {}
self.framework: str                   = "hid"
self.run: dict[str, Any]              = {"hid": self}
self.config                           = DeviceConfigGameController()
self.workerGameController: Worker | None = None
self.running: bool                    = False
```

**`isValidGameControllers(name: str) -> bool`** — *static method*
Returns `True` when `"Controller"` or `"Game"` appears in `name`.

**`discoverDevices(self, deviceType: str) -> list[str]`**
`DevicePopup` compatible discovery method (called without host/port for the
`"hid"` framework path in `DevicePopup.discoverDevices`):
```
result = []
for device in hid.enumerate():
    name = device["product_string"]
    if self.isValidGameControllers(name) and name not in result:
        result.append(name)
return result
```
- `deviceType` is received as `"hid"` (the class's `DEVICE_TYPE`) but is
  not used; it is accepted for API compatibility with the DevicePopup protocol.
- Returns a deduplicated list of product-string names.
- Has **no side effects** on `self.config`.

**`isNewerData(act: list, old: list) -> bool`** — *static method*
Unchanged logic from the current implementation.

**`convertData(self, name: str, iR: list) -> list`**
Unchanged logic; uses `self.log`.

**`sendGameControllerSignals(self, act: list, old: list) -> None`**
Unchanged dispatch logic; emits via `self.app.gameABXY`, `self.app.gamePMH`,
`self.app.gameDirection`, `self.app.gameSL`, `self.app.gameSR`.

**`readGameController(self, gamepad: hid.device) -> list`**
Unchanged read logic; uses `self.log`. On exception sets
`self.running = False` and returns `[]`.

**`runnerGameController(self) -> None`**
Polling loop (run inside `threadPool` worker). Looks up `vendorId`/`productId`
at startup by re-enumerating HID devices:
```
vendorId = productId = 0
for device in hid.enumerate():
    if device["product_string"] == self.config.deviceName:
        vendorId = device["vendor_id"]
        productId = device["product_id"]
        break
if not vendorId:
    self.log.warning(f"HID device [{self.config.deviceName}] not found")
    self.running = False
    self.signals.deviceDisconnected.emit(self.config.deviceName)
    return

gameControllerDevice = hid.device()
gameControllerDevice.open(vendorId, productId)
gameControllerDevice.set_nonblocking(True)
self.log.debug(f"GameController: [{self.config.deviceName} ...]")
self.app.msg.emit(1, "System", "GameController",
                  f"Starting {[self.config.deviceName]}")
reportOld = [0] * 16
while self.running:
    time.sleep(0.1)   # standard time.sleep — NOT mainThreadSleep
    report = self.readGameController(gameControllerDevice)
    if not self.isNewerData(report, reportOld):
        continue
    report = self.convertData(self.config.deviceName, report)
    self.sendGameControllerSignals(report, reportOld)
    reportOld = report
gameControllerDevice.close()
```
**`mainThreadSleep` must not be called from a background thread** —
replaced by `time.sleep(0.1)`.

**`startCommunication(self) -> None`**
```
if not self.config.autoStart:
    return
self.running = True
self.workerGameController = Worker(self.runnerGameController)
self.threadPool.start(self.workerGameController)
self.signals.deviceConnected.emit(self.config.deviceName)
```

**`stopCommunication(self) -> None`**
```
self.running = False
self.signals.deviceDisconnected.emit(self.config.deviceName)
```

---

### 2. `src/mw4/base/deviceRegistry.py` — Add GameController

Add import (alphabetical order):
```python
from mw4.logic.gameController.gameController import GameController
```

Add one row to `deviceSpec` (between `"focuser"` and `"lightPanel"`):
```python
("gameController", GameController, "hid", True),
```

No further changes needed — the registry pipeline restores all
`DeviceConfigGameController` fields and calls `startCommunication()`
on app start.

---

### 3. `src/mw4/gui/extWindows/devicePopupW.py` — Fix HID Prototype

The prototype already adds the `"hid"` entries but has two issues to fix:

**Fix `discovers["hid"]`** — add missing `"button"` key and correct `"class"`:
```python
"hid": {
    "deviceList": self.ui.hidDeviceList,
    "button":     self.ui.hidDiscover,
    "class":      GameController,
},
```
Update import: replace `from mw4.logic.gameController import GameController`
with the correct path:
```python
from mw4.logic.gameController.gameController import GameController
```

**Align `framework2gui["hid"]["deviceName"]`** — must reference the same
widget as `discovers["hid"]["deviceList"]` so the discovered names flow into
the stored device name (same pattern as INDI where
`framework2gui["indi"]["deviceName"] == discovers["indi"]["deviceList"]`):
```python
"hid": {
    "deviceName": self.ui.hidDeviceList,
},
```

No changes needed to `discoverDevices()` — the prototyped `else` branch
already calls `deviceInstance.discoverDevices(deviceType)` (no host/port).

---

### 4. `src/mw4/gui/extWindows/setting/tabSettDevice.py` — Add GameController

Add `"gameController"` to the `deviceUi` dict (alphabetical order between
`"focuser"` and `"lightPanel"`):
```python
"gameController": {
    "uiDropDown": self.ui.gameControllerDevice,
    "uiSetup":    self.ui.gameControllerSetup,
},
```

The UI widgets `gameControllerDevice` (QComboBox) and
`gameControllerSetup` (QPushButton) are already present in the generated
`src/mw4/gui/widgets/setting_ui.py`. No UI source changes are required.

---

### 5. `src/mw4/gui/extWindows/setting/tabSettGui.py` — Full Cleanup

**Remove** all of the following:

*Imports no longer needed:*
- `import hid`
- `from mw4.base.threadUtils import mainThreadSleep`
- `from mw4.base.tpool import Worker`

*Instance attributes in `__init__`:*
- `self.gameControllerList: dict`
- `self.gameControllerRunning: bool`
- `self.worker: Worker | None`

*Signal connection in `__init__`:*
- `self.ui.gameControllerGroup.clicked.connect(self.switchStatusGameController)`

*Methods (entire bodies deleted):*
- `isValidGameControllers()`
- `populateGameControllerList()`
- `switchStatusGameController()`
- Any of: `workerGameController`, `readGameController`,
  `sendGameControllerSignals`, `convertData`, `isNewerData`,
  `startGameController`

*`initConfig()` lines to remove:*
- `self.ui.gameControllerGroup.setChecked(...)`
- `self.ui.gameControllerList.setCurrentIndex(...)`
- `self.populateGameControllerList()`

*`storeConfig()` lines to remove:*
- `config["gameControllerGroup"] = ...`
- `config["gameControllerList"] = ...`

---

## Config Persistence Flow

```
App start
  └─ DeviceRegistry.initConfig()
       ├─ writeConfigToAllDevices()
       │    └─ restores: config.deviceName, .autoStart,
       │                 .moveRaDec, .moveAltAz, .tracking
       └─ startDevices()
            └─ startDevice("gameController")
                 ├─ framework == "hid"            ✓ (always set in __init__)
                 ├─ config.deviceName != ""       ← only if previously saved
                 └─ GameController.startCommunication()
                      └─ config.autoStart guard   ← returns if False

User opens Settings → Device tab → clicks gameControllerSetup
  └─ tabSettDevice.callPopup("gameController")
       ├─ dReg.stopDevice("gameController")
       ├─ DevicePopup.configure(...)
       │    └─ HID tab: user clicks Search
       │         └─ DevicePopup.discoverDevices("hid")
       │              └─ GameController.discoverDevices("hid") → list[str]
       │         → hidDeviceList populated
       │    └─ user selects device, clicks OK
       │         └─ DevicePopup.storeConfig()
       │              └─ data["hid"]["deviceName"] = selected name
       │              └─ data["framework"] = "hid"
       └─ tabSettDevice.processPopupResults(returnValues)
            ├─ dReg.writeConfigToSingleDevice("gameController", data)
            │    └─ config.deviceName = selected name
            │    └─ config.autoStart set from data
            └─ app.startDevice.emit("gameController")
                 └─ GameController.startCommunication() (if autoStart=True)

App stop
  └─ DeviceRegistry.storeConfig()
       └─ collectConfigFromAllDevices()
            └─ saves framework + all DeviceConfigGameController fields
               under SettingDevice / gameController / hid /
```

---

## Tests — `test_gameController.py` (new, 100 % coverage)

**Pytest scope:** `module`

| Test group | Cases |
|---|---|
| `DeviceConfigGameController` | Default values for all 5 fields. |
| `GameControllerSignals` | Instantiable; inherits `deviceConnected` / `deviceDisconnected`. |
| `GameController.__init__` | All attributes present; `run["hid"] is instance`; `framework == "hid"`; `DEVICE_TYPE == "hid"`. |
| `isValidGameControllers` | `"Pro Controller"` → True; `"SomeDevice"` → False; `"Game Pad"` → True; `"Controller X"` → True. |
| `discoverDevices` | Empty HID list → `[]`; mixed valid/invalid → only valid names; duplicates deduplicated; `deviceType` arg is accepted and ignored. |
| `isNewerData` | Empty list → False; equal lists → False; one element differs → True. |
| `convertData` | Empty `iR` → `[0]*7`; `"Pro Controller"` layout; `"Controller (XBOX 360 For Windows)"` — all five direction branches. |
| `sendGameControllerSignals` | Each of the 5 signal groups emits exactly when its index changes; no emit when unchanged. |
| `readGameController` | Non-empty read → returns data; empty read → returns `[]`; exception → sets `running=False`, returns `[]`. |
| `runnerGameController` — device not found | HID enumerate returns no match → `running=False`, `deviceDisconnected` emitted, returns without opening device. |
| `runnerGameController` — normal run | Opens device; loops while `running`; calls `convertData` and `sendGameControllerSignals` on new data; skips on unchanged data; closes device after loop exits. |
| `startCommunication` — `autoStart=False` | Returns early; `running` stays `False`; no worker; no signal emitted. |
| `startCommunication` — `autoStart=True` | `running=True`; `workerGameController` created; `threadPool.start` called; `deviceConnected` emitted. |
| `stopCommunication` | `running` set to `False`; `deviceDisconnected` emitted. |

---

## Tests — `test_tabSettGui.py` (update)

Remove all tests and fixture setup related to game-controller:
- Remove `gameControllerGroup` / `gameControllerList` mock setup from fixture.
- Remove tests for: `sendGameControllerSignals`, `readGameController`,
  `convertData`, `isNewerData`, `workerGameController`,
  `isValidGameControllers`, `startGameController`,
  `populateGameControllerList`, `switchStatusGameController`,
  and any `initConfig`/`storeConfig` assertions about game-controller keys.

---

## Tests — `test_devicePopupW.py` (add/update)

Add tests for:
- `discoverDevices("hid")` path: calls `GameController.discoverDevices`,
  populates `hidDeviceList`, updates `self.framework`.
- `discoverDevices("hid")` with empty result: emits msg, does not update list.

---

## Tests — `test_tabSettDevice.py` (update)

Add test: `"gameController"` key exists in `deviceUi` with non-None
`uiDropDown` and non-None `uiSetup`.

---

## Implementation Order

1. Rewrite `src/mw4/logic/gameController/gameController.py`.
2. Add `GameController` to `src/mw4/base/deviceRegistry.py`.
3. Fix `src/mw4/gui/extWindows/devicePopupW.py` (button key, class, widget alignment).
4. Add `"gameController"` to `tabSettDevice.py`.
5. Clean `src/mw4/gui/extWindows/setting/tabSettGui.py`.
6. Create `tests/unit_tests/logic/gameController/__init__.py`.
7. Create `tests/unit_tests/logic/gameController/test_gameController.py`.
8. Update `tests/unit_tests/gui/extWindows/setting/test_tabSettGui.py`.
9. Update `tests/unit_tests/gui/extWindows/test_devicePopupW.py`.
10. Update `tests/unit_tests/gui/extWindows/setting/test_tabSettDevice.py`.
11. Run `pytest` with coverage — iterate until 100 %.
12. Run `ruff check` / `ruff format` — resolve all findings.
13. Run the full test suite to confirm no regressions.
