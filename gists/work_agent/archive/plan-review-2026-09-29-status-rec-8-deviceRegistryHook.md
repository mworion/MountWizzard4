# Plan – Rec 8: Remove the Test Hook in `DeviceRegistry`

**Date:** 2026-09-30
**Source:** [2026-09-29-status-review.md](2026-09-29-status-review.md), rec 8
(Sep rec 10, A3)
**Scope:** `src/mw4/base/deviceRegistry.py` and the tests that build a registry.
**Out of scope (by definition):** the `test: int = 0` argument of
`MountWizzard4` in `mainApp.py` (N5) stays unchanged.

---

## 1. Current State

`DeviceRegistry.__init__` (`deviceRegistry.py:44-63`):

```python
if hasattr(app, "mount") and app.mount is not None:
    # Test only: tests inject mock mounts before calling registry
    mount_instance = app.mount
else:
    mount_instance = MountDevice(app, verbose=True)
    app.mount = mount_instance
```

Problems:

1. Production code contains a branch that exists only for tests. It looks up
   an attribute (`app.mount`) that is not part of `AppProtocol`.
2. In production the registry writes `app.mount` back into the app. Nothing in
   `src/mw4` reads `app.mount` (all access goes through `app.dReg["mount"]`),
   so the write-back is a hidden side effect without a consumer.
3. Any app object with a truthy `mount` attribute silently replaces the real
   mount – e.g. a `MagicMock` app in `test_deviceEntry.py` gets a `MagicMock`
   mount without asking for it.

Users of the hook (all tests):

| File                                                  | Use                                                  |
|-------------------------------------------------------|------------------------------------------------------|
| `tests/unit_tests/unitTestAddOns/baseTestApp.py:152,180` | `self.mount = Mount()` (stub), then `DeviceRegistry(self)` picks it up. Used by almost all GUI/logic tests via `app.dReg["mount"]`. |
| `tests/unit_tests/base/test_deviceRegistry.py`        | Fixture `registry` and 8 direct `DeviceRegistry(app)` calls (lines 29, 240, 260, 282, 307, 337, 361, 379); 3 tests assert the hook itself (`test_initPhase2MountAccessibleDuringAddDevices`, `test_initProductionCreatesNewMount`, `test_initTestModeMountsInjected`). |
| `tests/unit_tests/base/test_deviceEntry.py:31`        | `DeviceRegistry(MagicMock())` – gets a `MagicMock` mount via the hook. |

`app.mount` is also read directly by some tests (e.g. `test_satelliteHorW.py`,
`test_mountTime.py`). These read the stub attribute of `App`, not the registry
write-back, and are not affected.

---

## 2. Target Design

Explicit constructor injection with a production default:

```python
def __init__(self, app: AppProtocol, mount: MountDevice | None = None) -> None:
    super().__init__()
    self.app = app
    self.signalsToName: dict[int, str] = {}
    if mount is None:
        mount = MountDevice(app, verbose=True)
    self.d: dict[str, DeviceEntry] = {
        "mount": DeviceEntry(
            name="mount",
            instance=mount,
            deviceType="10micron",
            isConfigurable=False,
        ),
    }
```

- No `hasattr`, no read of `app.mount`, no write-back to `app.mount`.
- `mainApp.py:96` stays `DeviceRegistry(self)` – production behaviour is
  unchanged (the registry creates the real `MountDevice`).
- The parameter is a normal dependency-injection seam, not a test flag: it
  documents that the mount is a dependency of the registry.
- `mount_instance` (snake_case) disappears; naming follows camelCase.
- Typing: the stub `Mount` in the tests is not a `MountDevice`. No type checker
  runs in CI (P4), so the annotation stays `MountDevice | None`, which describes
  the production contract.

---

## 3. Steps

### Step 1 – `src/mw4/base/deviceRegistry.py`

- Add the `mount: MountDevice | None = None` parameter.
- Replace the `hasattr` block as shown in section 2.

### Step 2 – `tests/unit_tests/unitTestAddOns/baseTestApp.py`

- Line 180: `self.dReg = DeviceRegistry(self, mount=self.mount)`.
- `self.mount = Mount()` stays, so `app.mount` and `app.dReg["mount"].instance`
  remain the same stub object (current behaviour for all dependent tests).

### Step 3 – `tests/unit_tests/base/test_deviceEntry.py`

- Fixture `registry`: `DeviceRegistry(app, mount=mock.MagicMock())`, so the
  fixture keeps its lightweight mock mount explicitly instead of via the hook.

### Step 4 – `tests/unit_tests/base/test_deviceRegistry.py`

- Fixture `registry` and the generic construction tests (lines 29, 240, 260,
  361, 379): pass `mount=app.mount` to keep today's stub mount.
- Replace the three hook tests:
  - `test_initPhase2MountAccessibleDuringAddDevices` → build with
    `mount=app.mount`, assert `dReg["mount"].instance is app.mount` before and
    after `addDevices`.
  - `test_initProductionCreatesNewMount` → `DeviceRegistry(app)` without
    `mount`: assert `isinstance(dReg["mount"].instance, MountDevice)` and that
    `app.mount` is **still the stub** (no write-back).
  - `test_initTestModeMountsInjected` → rename to `test_initInjectedMount`:
    pass a sentinel object as `mount`, assert it is used as the instance and
    that `app.mount` is unchanged.
  - New `test_initIgnoresAppMountAttribute`: an app with a non-`None`
    `app.mount` and no `mount` argument still gets a new `MountDevice`
    (proves the hook is gone).

### Step 5 – Verification

1. `grep -rn "hasattr(app, \"mount\")\|app.mount =" src/mw4` → no match.
2. `uv run ruff format src tests` and `uv run ruff check src tests` → clean.
3. `uv run pytest tests/unit_tests/base -n auto` → green.
4. `uv run pytest tests/unit_tests -n auto --cov=mw4 --cov-report=term-missing`
   → all passed, coverage 100 %.

### Step 6 – Documentation

- `2026-09-29-status-review.md`: rec 8 → ✅ Done (`DeviceRegistry` part;
  `MountWizzard4.test` kept by definition), Sep rec 10 and A3 → ✅ Fixed, N5 →
  ⏸ Kept; add a row to section 7 and a decision row to section 8
  ("`test` argument of `MountWizzard4` stays").

---

## 4. Risks

| Risk | Mitigation |
|------|------------|
| A test builds `App()`-like objects without passing `mount` and now gets a real `MountDevice` (slower, real timers/sockets not started) | Only the files in section 1 call `DeviceRegistry(`; all are updated. The full suite run in step 5 catches any remaining case. |
| Hidden production consumer of `app.mount` | `grep` over `src/mw4` shows none; `AppProtocol` has no `mount` member. |
| `MagicMock` app in `test_deviceEntry` would create a real `MountDevice` from a mock app | Step 3 injects a `MagicMock` mount explicitly. |

---

## 5. Effort

Small (S): 1 source file (≈ 8 lines), 3 test files, 4 tests rewritten/added.

