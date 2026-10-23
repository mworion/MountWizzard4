# Plan P3 – typed carriers instead of `dict[str, Any]`

**Status 2026-10-23: wave 1 implemented** (`run` typed via `FrameworkDriver` + per-family
protocols in `logic/drivers/frameworks/driverProtocols.py`, `DeviceFacade[AppT, DriverT]`,
`ProfileConfig` alias; conformance tests; 5273 passed, 100 % coverage, pyrefly 0 errors,
lint-imports kept). pyrefly found a real mismatch (`lightIntensity` int vs float).
`DeviceEntry.run` stays `Any` (GUI uses driver-specific attributes through it).
**Wave 2 implemented (2026-10-23):** camera data keys are constants in `base/cameraKeys.py`
(27 keys, used by the camera back-ends, `cameraCalculations`, `fitsFunction`, `measureAddOns`,
`tabImage_*`); 5275 passed, 100 % coverage. **Decided against** `TypedDict`s for `data`:
measure keys are built dynamically, weather `data` is shared through `DeviceFacade.data`,
and dotted INDI names would need the functional syntax for little gain. Key constants for the
other device families (power, dome, light panel, weather, filter) were not done; add the same
way if needed. Record `TypedDict`s (step 6) remain optional.

Goal: P3 of `2026-10-20_review_copilot_open.md` ("`dict[str, Any]` carriers: `Camera.data`,
`run`, `config`"). 93 `dict[str, Any]` annotations in `src/mw4` (excl. `gui/widgets/`).
Behaviour must not change. `config` is covered by A3 (typed configuration) and is only
prepared here.

## 1. Findings

| Carrier | Where | What it really is | Verdict |
|---------|-------|-------------------|---------|
| `run` | `DeviceFacade.run` + 7 device classes (`measure`, `plateSolve`, `remote`, `hid`, `kmRelay`, `seeing`, `directWeather`, `mount`), 61 `.run[…]` accesses, `DeviceEntry.run -> Any` | `framework name -> backend driver`; every backend has `startCommunication`, `stopCommunication`, `config` | **Type it.** Clear win, low risk. |
| `data` (`Camera.data`, all devices) | `DeviceFacade.data`, 12 device classes, `DriverData`, GUI reads (`tabImage_Manage` 33×) | Open-ended mirror of INDI/ASCOM/Alpaca properties, keys like `"CCD_GAIN.GAIN_MIN"`, filled dynamically by `storePropertyToData`; INDI cameras add arbitrary keys (e.g. `FILTER_NAME.*`). | **Partly.** A closed `TypedDict` is wrong for camera/filter/dome (open-ended). Fixed key sets exist for weather/measure/seeing. |
| `config` | `app.config` (98 accesses), `profile.py`, `qtHelpers`, `qtMain`, tab `initConfig/storeConfig` | Nested profile dict | **Defer to A3**; here only replace bare `dict`/`dict[str, Any]` by one alias `ProfileConfig = dict[str, Any]` so A3 has a single place to change. |
| Result / record dicts | plate-solve `result`, `modelBuildData`, model file records, `dataWriter` MPC records, `satOrbit` | Known keys | **Optional second wave**: `TypedDict` per record (`SolveResult`, `ModelPoint`, …). |
| GUI tables | `uiWindows`, `setButtons`, `addons` | Declarative tables | **Keep** (low value). |

## 2. Design

### 2.1 `run` (wave 1)
- New protocol in `base/driverProtocol.py`:
  ```python
  class FrameworkDriver(Protocol):
      config: Any
      def startCommunication(self) -> None: ...
      def stopCommunication(self) -> None: ...
  ```
  Only members that every backend has (verify per backend, `mountcontrol`/`remote`/`hid` use
  `self` as backend and need the same two methods or are excluded via a narrower type).
- `DeviceFacade.run: dict[str, FrameworkDriver]`; `buildBackends` typed accordingly.
- `DeviceEntry.run -> dict[str, FrameworkDriver]`.
- Device-specific calls (`self.run[self.framework].expose()`) need the concrete protocol per
  device type: `CameraDriver(FrameworkDriver)` with `expose`, `abort`, … in the device
  package, used by `Camera` via a class attribute annotation `run: dict[str, CameraDriver]`.
  Do this per device family (camera, dome, focuser, filter, cover, lightPanel, powerswitch),
  one commit each, so pyrefly findings stay reviewable.
- Layering stays intact: protocols live in `base` (generic) or next to the device in
  `logic/drivers/<device>/`; `lint-imports` must stay green.

### 2.2 `data` (wave 2, only where keys are fixed)
- Keep `dict[str, Any]` for open-ended INDI-backed devices (camera, filter, dome, cover,
  focuser, lightPanel, powerswitch) and document why on `DeviceFacade.data`.
- Fixed-key devices (`directWeather`, `sensorWeather*`, `seeingWeather`, `measure`) get
  `TypedDict(..., total=False)` in functional syntax (keys contain dots, e.g.
  `"WEATHER_PARAMETERS.WEATHER_TEMPERATURE"`), one per device; `DriverData.data` becomes
  generic over it where simple, otherwise stays untyped.
- Add accessor helpers instead of scattered `.data.get("CCD_GAIN.GAIN", False)` strings:
  string constants for the INDI keys in one module (`logic/drivers/camera/cameraKeys.py`),
  used by `cameraCalculations` and `tabImage_Manage`. This removes typo risk without a
  closed schema.

### 2.3 `config` (prep for A3)
- Add `ProfileConfig` alias in `logic/profiles/profile.py`, use it in `profile.py`,
  `qtHelpers`, `qtMain`, `mainWindow.switchProfile`, tab config helpers. No behaviour change.

## 3. Steps

1. `FrameworkDriver` protocol + `DeviceFacade.run`/`DeviceEntry.run` typing; fix pyrefly findings.
2. Per-device driver protocols (camera, dome, focuser, filter, cover, lightPanel, powerswitch,
   plateSolve, measure); the 7 stand-alone `self.run = {…: self}` classes.
3. Key constants for camera `data` + use in `cameraCalculations`, `tabImage_Manage`.
4. `TypedDict`s for weather/seeing/measure data.
5. `ProfileConfig` alias.
6. Optional: result/record `TypedDict`s (`SolveResult`, model point).
7. Update review file (P3 ◐ → done or reduced to "data of open-ended devices").

## 4. Validation

- Tests mirror `src/mw4` under `tests/unit_tests/`, module scope; protocol conformance
  tests (`isinstance` against `runtime_checkable` protocols or static pyrefly) for every
  backend; 100 % line and branch coverage, no `pragma: no cover`.
- `uv run pytest tests/unit_tests`, `ruff check/format`, `uv run pyrefly check`
  (suppression count must not grow), `uv run lint-imports`.

## 5. Risks / open decisions

- Windows backends (`ascom`, `sgpro`) are built through factories and are not type-checked
  on macOS; protocol conformance must be asserted in the Windows-only tests.
- Closing `data` schemas for INDI devices would break unknown properties; therefore only
  key constants, no closed schema.
- Wave 1 (`run`) is mechanical; wave 2 is optional and can be dropped without harming wave 1.
