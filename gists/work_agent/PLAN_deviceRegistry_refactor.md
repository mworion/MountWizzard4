# Plan: Simplify `DeviceRegistry` with typed entries and iterators

## Context

`src/mw4/base/deviceRegistry.py` exposes a single nested dict
`drivers[name] -> {"class", "deviceType", "stat"}`. Consumers across
`gui/mainWaddon/tabSett_Device.py`, `logic/measure/measure.py`,
`gui/mainWindow/mainWindow.py`, `mainApp.py` and `base/loggerMW.py`
read/write this structure with stringly-typed keys and repeat the same
filtering boilerplate (notably `if driver in ["mount"] or ...["class"]
is None: continue`).

## Goals

1. Replace the nested-dict entry with a typed `DeviceEntry` dataclass.
2. Provide iterators on `DeviceRegistry` so call sites express intent
   (`configurable()`, `withFramework(...)`, `measureSources()`) instead
   of inline filtering with `continue`.
3. Encapsulate state mutations (`setStat`).
4. Remove duplicated guards across `tabSett_Device.py` (5 occurrences of
   the mount/None filter).
5. Keep public surface stable enough for an incremental migration.
6. Maintain 100 % unit test coverage; pass Ruff lint/format.

## Non-goals (this iteration)

- Removing the `"refraction"` virtual entry (tracked as v2 cleanup).
- Moving `mount` out of the registry (tracked as v2 cleanup).

## Design

### `DeviceEntry`

```python
from dataclasses import dataclass
from typing import Any

@dataclass
class DeviceEntry:
    name: str
    instance: Any | None        # device class instance (None for refraction)
    deviceType: str | None
    isConfigurable: bool        # False for mount / refraction
    stat: bool | None = None
```

`isConfigurable` captures the existing implicit rule
"`driver not in ['mount'] and class is not None`".

### `DeviceRegistry` API

```python
class DeviceRegistry:
    def __init__(self, app: Any) -> None: ...
    def __iter__(self) -> Iterator[DeviceEntry]: ...
    def __getitem__(self, name: str) -> DeviceEntry: ...
    def __contains__(self, name: str) -> bool: ...

    # Selectors
    def configurable(self) -> Iterator[DeviceEntry]:
        """Entries the user can configure (excludes mount/refraction)."""

    def withFramework(self, *names: str) -> Iterator[DeviceEntry]:
        """Configurable entries whose current framework is in names."""

    def measureSources(self) -> Iterator[DeviceEntry]:
        """Configurable entries listed in `measure` mapping."""

    # Mutators
    def setStat(self, name: str, value: bool | None) -> None: ...
```

For backwards-compat during migration, also expose
`self.drivers` as a `dict[str, _LegacyView]` where `_LegacyView`
implements `__getitem__("class"|"deviceType"|"stat")` proxying to the
`DeviceEntry`. This lets us migrate call sites file-by-file.

## Migration steps

1. **Add `DeviceEntry` + iterators**, keep legacy dict view; update
   `tests/unit_tests/base/test_deviceRegistry.py`.
2. **Migrate `tabSett_Device.py`** — biggest win, replace 7 manual loops:
   - `stopDrivers`, `addMissingDefaultData`, `copyConfig`,
     `startDrivers`, `manualStartAllAscomDrivers`,
     `manualStopAllAscomDrivers` → use `configurable()` /
     `withFramework("ascom", "alpaca")`.
3. **Migrate `logic/measure/measure.py`** — use `measureSources()`,
   drop `isinstance(driver, dict)` defensive code.
4. **Migrate `mainApp.py`, `gui/mainWindow/mainWindow.py`,
   `base/loggerMW.py`** to attribute access (`registry["mount"].instance`,
   `registry.setStat("refraction", True)`).
5. **Remove the legacy dict view** once no consumer uses it.
6. **Run** `ruff check --fix`, `ruff format`, full `pytest --cov`
   ensuring 100 % coverage.

## Expected impact

- `tabSett_Device.py`: ~30 LOC removed, intent visible at a glance.
- Call sites become type-checked (entry attributes vs. dict keys).
- Single place defines what "configurable" means.

## Risks

- Hidden coupling on the dict layout in tests / popup classes — handled
  by keeping the legacy view during migration.
- Behaviour change if any caller relied on iterating *all* drivers
  including `mount`; audited usage shows none rely on this except direct
  lookups by name (`drivers["mount"]`), which stay valid via
  `registry["mount"]`.

## Acceptance

- All consumers migrated; legacy dict view removed.
- `ruff` clean; `pytest --cov` reports 100 % for `deviceRegistry.py`
  and the touched modules.

