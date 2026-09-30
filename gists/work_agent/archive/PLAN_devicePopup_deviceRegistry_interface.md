# Plan: Simplify DevicePopup interface by using DeviceRegistry directly

## Goal

Remove the intermediate configuration `dict` that is currently handed over
between `SettDevice` (tab `tabSettDevice.py`) and `DevicePopup`
(`devicePopupW.py`).

Instead of

1. collecting config from the device registry into a `dict`,
2. passing that `dict` into the popup,
3. editing the `dict` inside the popup and
4. writing the returned `dict` back into the registry,

the popup shall read the required configuration items **directly** from
`self.app.dReg` when it opens and, when closed with **OK**, write the edited
values **directly back** into the registry `config` dataclasses.

## Review of the idea

The idea is feasible and low-risk because:

- `DevicePopup` already holds `self.app` and `self.device` and already
  accesses `self.app.dReg[self.device]` directly in `discoverDevices`,
  `checkApp`, `checkIndex` and `selectAscomDriver`. Registry access from the
  popup is therefore an established pattern.
- The dict produced by `DeviceRegistry.collectConfigFromSingleDevice` is a
  1:1 snapshot of the per-framework `config` dataclasses
  (`run[framework].config`). Iterating the live dataclass `fields()` yields
  exactly the same element set, so **no behavioural change** results from
  reading directly.
- Writes only happen in `storeConfig` (the OK path). Cancel never writes.
  Reading/writing live registry values therefore keeps the current
  "cancel = no change" semantics, since nothing is written on cancel.
- `collectConfigFromSingleDevice` / `writeConfigToSingleDevice` must **stay**
  in `DeviceRegistry`: they are still used by the `...AllDevices` variants for
  persistence to `app.config` (`initConfig` / `storeConfig`). Only their usage
  from the popup flow is removed.

### Naming mismatch to correct (config dataclasses are the master)

`framework2gui["indi"]` uses keys `hostaddress` and `messages`, while the
`DeviceConfigIndi` dataclass fields are `hostAddress` and `showMessage`. Because
both the current dict flow and the new registry flow match widgets via
`framework2gui[framework].get(element)` keyed on the dataclass field name, the
INDI host address and "show message" checkbox are **silently skipped today**
(neither populated on open nor read back on OK).

The config dataclasses are the single source of truth, so the popup keys must
be aligned to the field names. This is corrected as part of this task.

A full audit of every framework against its config dataclass shows the INDI tab
is the **only** mismatch:

| framework | config dataclass fields (master) | framework2gui keys | status |
|---|---|---|---|
| indi | deviceName, hostAddress, port, protocol, loadConfig, showMessage | hostaddress, port, deviceName, messages, loadConfig | **fix** `hostaddress`→`hostAddress`, `messages`→`showMessage` |
| alpaca | deviceName, hostAddress, port, protocol, loadConfig, apiVersion, number | hostAddress, port, deviceName | ok |
| sgpro | deviceName, hostAddress, port | hostAddress, port, deviceName | ok |
| ascom | deviceName | deviceName | ok |
| boltwood | deviceName, filePath | filePath | ok |
| astrometry | deviceName, searchRadius, timeout, appPath, indexPath, apiKey | deviceName, searchRadius, timeout, appPath, indexPath | ok |
| astap | deviceName, searchRadius, timeout, appPath, indexPath | (same) | ok |
| watney | deviceName, searchRadius, timeout, appPath, indexPath | (same) | ok |
| online | deviceName, hostAddress, apiKey | apiKey, hostAddress | ok |
| seeing | deviceName, apiKey, hostAddress | apiKey, hostAddress | ok |
| relay | deviceName, hostAddress, user, password | hostAddress, user, password | ok |
| hid | deviceName, moveRaDec, moveAltAz, tracking, parkStop, dome | deviceName | ok |

Fields that legitimately have **no widget** (e.g. `protocol`, `apiVersion`,
`number`, the hid boolean flags) stay absent from `framework2gui`; the
`.get(element)` lookup returns `None` and they are skipped, which is correct.

**Correction (in `framework2gui["indi"]`):**
```python
"indi": {
    "hostAddress": self.ui.indiHostAddress,   # was "hostaddress"
    "port": self.ui.indiPort,
    "deviceName": self.ui.indiDeviceList,
    "showMessage": self.ui.indiMessages,      # was "messages"
    "loadConfig": self.ui.indiLoadConfig,
},
```
After this correction the INDI host address (`QLineEdit`) and the show-message
checkbox (`QCheckBox`) are populated on open and written back on OK.

## Affected files

1. `../../src/mw4/gui/extWindows/devicePopupW.py` (class `DevicePopup`)
2. `../../src/mw4/gui/extWindows/setting/tabSettDevice.py` (class `SettDevice`)
3. Tests:
   - `../../tests/unit_tests/gui/extWindows/test_devicePopupW.py`
   - `../../tests/unit_tests/gui/extWindows/setting/test_tabSettDevice.py`

`../../src/mw4/base/deviceRegistry.py` stays **unchanged** (collect/write single
methods remain for persistence).

## Detailed changes

### A. `devicePopupW.py`

Add helper import:
```python
from dataclasses import fields
```

#### 0. Correct the INDI `framework2gui` keys

Align the mapping keys with the `DeviceConfigIndi` field names (see the
mismatch table above): `hostaddress` → `hostAddress`, `messages` →
`showMessage`. No other framework needs changes.
#### 1. Constructor signature

- Change `__init__(self, parentWidget, device, data)` to
  `__init__(self, parentWidget, device)`.
- Remove `self.data = data`.
- Derive framework from the registry:
  `self.framework = self.app.dReg[device].framework`.
- Add a small helper to enumerate frameworks that own a `config` dataclass:
  ```python
  def frameworksWithConfig(self) -> list[str]:
      run = self.app.dReg[self.device].run
      return [fw for fw in run if hasattr(run[fw], "config")]
  ```
- Add a helper to read a framework config dataclass:
  ```python
  def frameworkConfig(self, framework: str) -> Any:
      return self.app.dReg[self.device].run[framework].config
  ```

#### 2. `populateTabs`

Replace iteration over `self.data` with iteration over
`frameworksWithConfig()`; read values via `getattr(config, field.name)`:
```python
def populateTabs(self) -> None:
    for framework in self.frameworksWithConfig():
        config = self.frameworkConfig(framework)
        for f in fields(config):
            element = f.name
            ui = self.framework2gui[framework].get(element)
            value = getattr(config, element)
            if isinstance(ui, QComboBox):
                ui.clear()
                ui.setView(QListView())
                ui.addItem(getattr(config, "deviceName"))
            elif isinstance(ui, QLineEdit):
                ui.setText(f"{value}")
            elif isinstance(ui, QCheckBox):
                ui.setChecked(value)
            elif isinstance(ui, QDoubleSpinBox):
                ui.setValue(value)
```

#### 3. `selectTabs`

Replace `objectName() in self.data` with membership in
`frameworksWithConfig()`:
```python
def selectTabs(self) -> None:
    tabIndex = getTabIndex(self.ui.tab, self.framework)
    self.ui.tab.setCurrentIndex(tabIndex)
    frameworks = self.frameworksWithConfig()
    for index in range(self.ui.tab.count()):
        isVisible = self.ui.tab.widget(index).objectName() in frameworks
        self.ui.tab.setTabVisible(index, isVisible)
```

#### 4. `initConfig`

Replace `framework = self.data.get("framework", "")` with
`framework = self.framework` (already read from the registry).

#### 5. `configure` classmethod

Change signature to `configure(cls, parentWidget, device)` and drop the `data`
argument.

#### 6. `readTabs`

Write GUI values directly into the live config dataclass of the current
framework:
```python
def readTabs(self) -> None:
    config = self.frameworkConfig(self.framework)
    for f in fields(config):
        element = f.name
        ui = self.framework2gui[self.framework].get(element)
        if isinstance(ui, QComboBox):
            setattr(config, "deviceName", ui.currentText())
        elif isinstance(ui, QLineEdit):
            if isinstance(getattr(config, element), int):
                setattr(config, element, int(ui.text()))
            else:
                setattr(config, element, ui.text())
        elif isinstance(ui, QCheckBox):
            setattr(config, element, ui.isChecked())
        elif isinstance(ui, QDoubleSpinBox):
            setattr(config, element, ui.value())
```

#### 7. `storeConfig`

Also set the device framework on the instance and shrink `returnValues`:
```python
def storeConfig(self) -> None:
    self.readFramework()
    self.readTabs()
    self.app.dReg[self.device].instance.framework = self.framework
    self.returnValues["close"] = "ok"
    self.close()
```
`returnValues` now only carries `{"close": "ok"|"cancel"}`.

### B. `tabSettDevice.py`

#### 1. `callPopup`

Drop the collect step and the `data` argument:
```python
def callPopup(self, device: str) -> None:
    self.app.dReg.stopDevice(device)
    returnValues = DevicePopup.configure(self.parentW, device)
    if returnValues["close"] == "ok":
        self.processPopupResults(device)
    else:
        self.app.dReg.startDevice(device)
```

#### 2. `processPopupResults`

Read framework / deviceName from the registry (the popup already wrote them),
drop the `writeConfigToSingleDevice` call:
```python
def processPopupResults(self, device: str) -> None:
    framework = self.app.dReg[device].framework
    deviceName = self.app.dReg[device].run[framework].config.deviceName
    index = findIndexValue(self.deviceUi[device]["uiDropDown"], framework)
    itemText = f"{framework} - {deviceName}"
    self.deviceUi[device]["uiDropDown"].setCurrentIndex(index)
    self.deviceUi[device]["uiDropDown"].setItemText(index, itemText)
    self.app.dReg.startDevice(device)
```

## Behavioural equivalence check

| Concern | Before (dict) | After (registry) |
|---|---|---|
| Values shown | snapshot dict from `collectConfig` | live `config` dataclass (same source) |
| Element iteration | `data[framework]` keys = `fields(config)` | `fields(config)` |
| Tab visibility | framework in dict | framework in `frameworksWithConfig()` |
| Cancel | dict discarded, registry untouched | nothing written, registry untouched |
| OK | dict written via `writeConfigToSingleDevice` | values written directly to config + framework set |
| Persistence path | unchanged | unchanged (`collect/write ...AllDevices` kept) |

## Test impact

- `test_devicePopupW.py`: update `DevicePopup(...)` / `DevicePopup.configure(...)`
  constructions to the new signature (no `data` argument). Provide a fake
  `app.dReg[device]` whose `run[framework].config` is a real dataclass so
  `fields()` and `getattr/setattr` work. Adjust `storeConfig` assertions
  (returnValues now only has `close`; check config dataclass values instead of
  `returnValues["data"]`). Add assertions that the INDI `hostAddress` and
  `showMessage` fields are now populated on open and written back on OK
  (previously untested because they were silently skipped).
- `test_tabSettDevice.py`: `callPopup`/`processPopupResults` tests must stop
  mocking `collectConfigFromSingleDevice` / `writeConfigToSingleDevice` for the
  popup flow and instead assert on registry framework/config and dropdown item
  text. `DevicePopup.configure` mock now returns `{"close": ...}` only.
- `test_deviceRegistry.py`: unchanged (methods remain).

## Validation steps (after implementation)

1. `ruff format` + `ruff check` on changed files — resolve all findings.
2. Run affected unit tests:
   - `../../tests/unit_tests/gui/extWindows/test_devicePopupW.py`
   - `../../tests/unit_tests/gui/extWindows/setting/test_tabSettDevice.py`
   - `../../tests/unit_tests/base/test_deviceRegistry.py`
3. Ensure 100% coverage for the two changed modules.
4. Full test run as final step.

## Out of scope

- Any change to `DeviceRegistry` persistence methods.
- Any new features beyond removing the dict interface and correcting the
  INDI naming mismatch.
