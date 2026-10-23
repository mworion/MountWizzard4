# MountWizzard4 – Code Review (2026-10-20)

Scope: `../src/mw4` (excluding generated `gui/widgets`), tests, tooling, repo hygiene.
Revision: `3ec18a381`, version `4.0.0b36`. Re-run after roadmap items 1–8 and the test-layout
alignment (2026-10-20, second pass).
Method: static inspection and metrics (ruff, pyrefly, AST scan, grep counts, coverage run).
Update 2026-10-22: A4 (layering contracts), A5 (tab controllers), M3 (`DeviceFacade`) and M4 (driver layout) done; the
suite now has 5226 passed / 38 skipped at 100 % line and branch coverage, `pyrefly` 0 errors,
`lint-imports` 7 contracts kept. Figures below are from the 2026-10-20 run unless stated.
The full unit suite **was** re-run: 5108 passed, 38 skipped, 100 % line and branch coverage
(18365 statements, 3666 branches); `ruff check src` clean, `pyrefly check` 0 errors.

## 1. Summary

The project is in good shape for a 12k-commit, ~46k LOC hobby/pro-am desktop
application. The latest refactoring wave is clearly visible: `AppProtocol`,
`DeviceRegistry`/`DeviceEntry`, `TabAddon` base class, central `Worker`/`setupWorker`,
type annotations nearly everywhere, ruff and pyrefly in the toolchain and 100 % coverage.

Main remaining weaknesses are **structural**: a very large, stringly-typed `app` god-object
surface, raw-dict configuration spread over the whole code base, GUI/logic separation that is
good but not clean (Qt leaks into logic), and a handful of oversized functions and
data-as-code files.

| Area            | Rating | Comment (re-rated 2026-10-23; was Architecture B, Maintainability B) |
|-----------------|--------|---------|
| Architecture    | A-     | Layers enforced by import-linter, role protocols, typed registry, controllers; raw-dict configuration remains (A3) |
| Pythonic style  | B+     | Modern 3.12 typing, dataclasses, generators; some `hasattr`/dict plumbing |
| Maintainability | A-     | Consistent conventions, shared `DeviceFacade`, tab controllers; ~12 long functions and docstring quality remain |
| Quality         | A-     | ruff clean, pyrefly 0 errors, 100 % coverage, few broad excepts (all justified), shared HTTP helper (Q3); thread-safety rule undocumented (Q5) |
| Testability     | A-     | 5.1k tests, strict 1:1 test-per-module layout (verified); heavy Qt/app stubbing, stress tests not in CI scope |
| Readability     | B+     | camelCase consistent, short methods; a few outliers; origin visible in log format (R2 closed) |

## 2. Key figures

| Metric | Value |
|--------|-------|
| Python modules in `../src/mw4` | 216 (excl. `__init__`, widgets) |
| LOC `gui` / `logic` / `mountcontrol` / `base` | 15.2k (excl. generated widgets) / 7.9k / 3.5k / 2.1k |
| Test files / tests | 216 / 5108 passed + 38 skipped (strict 1:1 `src/mw4/x/y.py` → `tests/unit_tests/x/test_y.py`, verified by script: 0 modules without a test) |
| `ruff check src` | clean (E, T2, UP, I, C, LOG, W, SIM, A, RUF, B, BLE; mccabe ≤ 10) |
| `pyrefly check` | 0 errors, **54 suppressed**, 28 warnings hidden |
| Functions with return annotation | 2043 / 2043 (100 %) |
| `except Exception` | 4 (all at documented driver/worker boundaries) |
| `# noqa` / `TODO` / `print(` | 0 / 0 / 0 (live code) |
| `type: ignore` | 3 |
| `self.app.` references in `gui` | 840 |
| `dReg["…"]` string-key lookups | 521 → **0** (typed `dReg.<device>`, A2) |
| `config[…]` / `config.get(…)` accesses | 438 (unchanged, A3) |
| `hasattr` / `getattr` | 50 (was 48) |
| `platform.system()` call sites | 1 (`base/platformInfo.py`) |
| Class-level `log = logging.getLogger(...)` | 56 classes (72 `getLogger` calls) |
| f-string in `log.*(...)` | 173 → **0** (done, enforced by `G004`) |
| Functions > 50 lines (excl. data file) | 16 (was 25; largest 91 L, was 293 L) |
| Files | largest `alignstars.py` 830 lines (data constant); QSS now in `assets/styles/*.qss`, `gui/styles/styles.py` 150 lines |
| Largest tabs | `tabImage_Manage.py` 430 L, `tabSat_Track.py` 373 L, `tabMount_Sett.py` 301 L (was 504 / 477 / 436) |
| Repository | `.git` 1.2 GB (2026-10-22; 1.4 GB on 2026-10-20), 908 tracked files in `HEAD`, `gists/`, `../work`, `log/` untracked |

## 3. Strengths

1. **Explicit app contract** – `base/appProtocol.py` is a `runtime_checkable` Protocol with
   type-only imports; avoids import cycles, lets tests use a stub `App` without inheritance.
2. **Device registry** – `DeviceRegistry` + `DeviceEntry` dataclass, data-driven
   `deviceSpec` list, mapping protocol (`in`, `[]`, iteration), generators for
   `configurable()` / `realDrivers()`. Adding a device is a one-line change.
3. **Consistent device pattern** – every logic device (`Camera`, `Dome`, …) owns `signals`,
   `framework`, a `run` dict of framework back-ends (INDI / Alpaca / SGPro / ASCOM) and the
   Windows-only back-ends are guarded with `platform.system()`.
4. **Worker infrastructure** – `base/tpool.py` centralises thread-pool use, busy-lock,
   slow-worker warning, traceback formatting and guarantees `finished` is always emitted.
5. **Lifecycle contract for tabs** – `TabAddon` replaces `hasattr` dispatch with no-op hooks
   (`initConfig`, `storeConfig`, `setupIcons`, `updateColorSet`, `shutdown`).
6. **Tooling discipline** – ruff with a sensible rule set and complexity cap, pyrefly with
   per-path relaxations, `../uv.lock`, pinned numeric stack, coverage with a conditional plugin
   for Windows-only code, per-OS CI workflows, markers for test categories.
7. **Quality gates met** – no leftover `print`, `TODO`, `# noqa`, no leading-underscore
   functions (only 2 `def _x` hits, and attribute-level `_binning`/`_subFrame`).
8. **Directory/package layout** is easy to navigate: `base`, `logic/<device>`, `mountcontrol`,
   `gui/{mainWaddon,extWindows,mainWindow,styles,utilities}`.

## 4. Findings and recommendations

Priority: **H** high value, **M** medium, **L** low / cosmetic.

### 4.1 Architecture

| # | Pri | Finding | Recommendation |
|---|-----|---------|----------------|
| A1 | H | ✅ **Done 2026-10-20 (WP 6.1–6.6)**: 8 role protocols in `base/appProtocol.py`, `AppProtocol` is their composition, signals grouped in `base/appSignals.py` (`app.signals.ui/.hemisphere/.model/.system`). **`app` is a god object.** `AppProtocol` exposes ~35 members including 25 signals; 842 `self.app.` uses in the GUI. Every tab/device implicitly depends on everything. | Split the Protocol into narrow role protocols (`HasConfig`, `HasThreadPool`, `HasDevices`, `HasMessaging`, `HasSignals`) and type each consumer with the smallest one. Group the 25 signals into 3–4 sub-objects (`app.signals.hemisphere`, `.model`, `.satellite`, `.ui`), mirroring the already existing `MountSignals`. |
| A2 | H | ✅ **Done 2026-10-20 (WP 5.1–5.6): typed `dReg.<device>` properties + `Literal` overloads.** **Stringly-typed device access**: 521 × `dReg["camera"]` etc. A typo is a runtime `KeyError`, no IDE completion, no typing of the returned instance (`DeviceEntry.instance` is effectively `Any`). | Expose typed attributes (`dReg.camera: Camera`, `dReg.dome: Dome`) or a `Literal[...]` key with `@overload` on `__getitem__`. Keep the dict internally for iteration. |
| A3 | H | **Configuration is an untyped nested dict** (`app.config[...]`, 438 accesses), each tab reads/writes its own keys in `initConfig`/`storeConfig`. Schema, defaults and migration are implicit and scattered. | Introduce per-component `@dataclass` config objects (already the case for device `run[framework].config`, see `collectConfigFromSingleDevice`) with `from_dict`/`to_dict` and defaults in one place. Add a schema/version field and a single migration hook. |
| A4 | M | ✅ **Done 2026-10-22 (plan A4):** `deviceRegistry` (composition root) moved out of `base`; `lint-imports` enforces `gui > logic > mountcontrol > base`, controllers ↛ drivers, independent controller areas, Qt-free foundations/controllers (2 documented QObject workers); ruff `TID251` bans `QtWidgets`/`QtGui`/`QtCharts` outside `gui`. Earlier: (◐ re-check 2026-10-20: `logic`/`mountcontrol` no longer import `gui`; only the type-only import in `base/appProtocol.py` remains; `audioManager` still uses `app.mainW`; 22 `logic` + 8 `mountcontrol` files import PySide6) **Layer leakage.** `logic` (15 files) and `mountcontrol` (4) import PySide6 – acceptable for `Signal`/`QThreadPool`, but `base/audioManager.py` reaches into `app.mainW` (a GUI object) and `logic` imports 1 GUI module. The stated "clear separation business logic vs GUI" is therefore only approximate. | Limit Qt in `logic` to `QObject`/`Signal`; pass a parent/handle into `AudioManager` instead of `app.mainW`; remove the `logic → gui` import (move shared item to `base`). Consider a small import-linter contract (`gui → logic → base`, never the reverse). |
| A5 | M | ✅ **Done 2026-10-22 (plan A5, phases 1–3):** controllers in `logic/controllers/{mount,image,satellites}`, tabs own a controller; tabs now 301 / 430 / 373 L (`tabMount_Sett` / `tabImage_Manage` / `tabSat_Track`). Earlier: (◐ partly done: image stats, tilt geometry and satellite track calculations moved to `logic/`; other tabs have only UI wiring left) **Inheritance/mixin for GUI composition.** Tabs are mixins plus `TabAddon`; several tabs (e.g. `tabMount_Sett.py` 504 L, `tabImage_Manage.py` 477 L, `tabSat_Track.py` 436 L) hold UI wiring, state and calculations together. | Keep widget wiring in the tab, move calculations/state transitions into plain classes in `logic` (testable without Qt). Prefer composition (tab owns a controller) over adding further mixins. |
| A6 | M | **Tab → tab decoupling** is largely honoured (only `TabAddon` is imported across tabs), but communication goes through the global `app` signals (`refreshModel`, `redrawHemisphere`, …). That is loose coupling in code, tight coupling in behaviour (any tab can fire any global signal). | Document ownership of each global signal (emitter vs. listeners); see A1 for grouping. |
| A7 | L | `MountWizzard4.__init__` has strict ordering requirements (`dReg` → `audioMgr` → `initConfig` → `buildPoint` → `mainW`) but this is encoded only by line order. | Split into small `setup*` steps with docstrings stating dependencies, or a tiny builder. |

### 4.2 Pythonic style

| # | Pri | Finding | Recommendation |
|---|-----|---------|----------------|
| P1 | M | `hasattr`/`getattr` used 50 × (re-run 2026-10-20) (e.g. `hasattr(self.d[entry.name].instance, "signals")`, `hasattr(run[framework], "config")`). | Make "has signals / has config" part of a Protocol (`HasSignals`) or give every device default attributes; use `isinstance` against a runtime-checkable protocol. |
| P2 | M | Repeated `self.d[device].run[framework].config` chains in `DeviceRegistry.collectConfigFromSingleDevice` (4 evaluations per iteration). | Use local variables, and `dataclasses.asdict(config)` instead of manual field loop. |
| P3 | M | `dict[str, Any]` is the default data carrier (`Camera.data`, `run`, `config`). | Use `TypedDict` or dataclasses where keys are fixed; `run: dict[str, Any]` could be `dict[str, FrameworkDriver]` with a shared Protocol. |
| P4 | M | ✅ **Done 2026-10-20.** 173 logging calls used f-strings; all converted to lazy `%`-style, `G004` now enforced in ruff. | – |
| P5 | L | ✅ **Done 2026-10-20.** `generateAlignStars()` (825 lines) now returns a copy of the `ALIGN_STARS` constant in `logic/buildData/alignstars.py`; public API unchanged, the `PLR0915` ignore was dropped. | – |
| P6 | L | Many "constants" are instance attributes initialised to magic values (`posXASCOM`, `widthASCOM`, `exposureTime1`/`N`). Leading-underscore *attributes* (`_binning`, `_subFrame`) with property wrappers contradict the "no underscore" convention only partially. | Group into small dataclasses (`SubFrame`, `Binning`), keeping convention intact. |
| P7 | L | `# type: ignore` (3) and pyrefly `sub-config` that disables `bad-argument-type`, `bad-return`, `bad-assignment` for **all** of `mountcontrol`. | Accept as pragmatic for numpy/skyfield stubs, but track the 54 suppressed errors and tighten per-file over time (`pyrefly check --min-severity=warn` shows 30 additional warnings). |
| P8 | L | ✅ **Done 2026-10-20 (WP 8).** `base/platformInfo.py` is the only caller of `platform.system()` (was ≈60 hits); modules use `platformInfo.IS_WINDOWS` and `registerWindowsBackends`, tests patch the constants. Platform handling by `if platform.system() == "Windows":` in many modules (≈60 `platform` hits). | Centralise in `base/platform.py` (`IS_WINDOWS`) and use a back-end factory so devices don't branch inline. |

### 4.3 Maintainability

| # | Pri | Finding | Recommendation |
|---|-----|---------|----------------|
| M1 | H | ✅ **Largely done 2026-10-23:** 6 functions > 50 L remain (largest 65 L, mostly declarative builders); A5 follow-up controllers for almanac/model exist. Earlier: **Oversized functions** (✅ roadmap 7: all `PLR0915` ignores removed, largest function 293 → 91 L, 25 → 16 over 50 L; remaining are mostly data tables, global statement budget still open): `measureAddons.dataPlots` 293 L, `devicePopupW.__init__` 154 L, `simulator/materials.__init__` 140 L, `simulator/telescope.create` 122 L, `tabSettDevice.__init__` 103 L, native-Qt dialog constructors 98–99 L. 25 functions > 50 lines in total. (mccabe ≤ 10 passes because they are linear, not branchy.) | Split into builder helpers (`createPlotAxes`, `createMaterial`, …); table-drive repetitive widget creation. Add a ruff `PLR0915` (too-many-statements) budget to prevent regrowth. |
| M2 | M | **Long parameter lists** in a few places: `qtInputDialog.__init__` 12 args, `tabSat_Search.calcSat` 9, `updateListSats` 8, `astroObjects.__init__` 8. | Use dataclass parameter objects or keyword-only args (`*,`). |
| M3 | M | ✅ **Done 2026-10-22 (plan M3).** The framework back-ends were already DRY (`*AlpacaAscomBase` + 9-line shells); the copy-paste sat in the nine device facades. They now share `logic/drivers/frameworks/deviceFacade.py` (`DeviceFacade[AppT]`: signals, back-end table, start/stop), −321 net source lines. Deliberately kept as they are (own signals, custom start/stop or fixed framework): `Measure`, `PlateSolve`, `Remote`, `KMRelay`, `SeeingWeather`, `DirectWeather`, `HidController`, `Keypad`. **Duplicated framework wrappers.** Per device there is `deviceIndi`, `deviceAlpaca`, `deviceSGPro`, `deviceAscom` plus shared `*Class.py` in `base`. This is a good pattern but likely contains copy-paste across devices (camera/focuser/dome/filter/cover). | Run a duplication scan (e.g. `pylint --enable=duplicate-code` or `jscpd`) and extract common bases/mixins for connect/disconnect/poll/error handling. |
| M4 | M | ✅ **Done:** driver framework classes live in `logic/drivers/frameworks/`, device packages under `logic/drivers/`, GUI-independent logic under `logic/controllers/<GUI area>/`; `base/` keeps infrastructure. `base/` mixes infrastructure (`tpool`, `loggerMW`, `bootstrap`) with domain-ish helpers (`transform`, `timeManager`, `ascomClass`, `sgproClass`, `indiClass`). | Move driver-protocol classes to `logic/drivers/` (or `base/drivers/`) to keep `base` dependency-free. |
| M5 | M | ✅ **Done 2026-10-20 (WP 8).** QSS moved to `assets/styles/{basic,mac,nonMac}.qss` templates with placeholders, rendered by `gui/styles/styles.py`; a golden-file test (`../tests/testData/styleGolden.json`) guards the output. Styles: `gui/styles/styleSheets.py` is 691 lines of Python-embedded QSS. | Move to `.qss` templates with placeholders; makes theming testable and diffable. |
| M6 | M | ✅ **Done 2026-10-20; signals now declared once in `AppSignals` (A1)** (contract test `test_concreteAppProvidesAllProtocolMembers`). `AppProtocol` is kept manually in sync with `MountWizzard4` (signals declared twice). `drawHorizonPoints` exists only on the concrete class but nothing consumes it, so its absence from the Protocol is intended. | Longer term: derive the signal list from one place (see A1). |
| M7 | L | Docstring style/language quality varies (e.g. typos in `alignstars` docstring: "assdataets", lower-case sentence starts, mixed numpy/rst). | Pick one style (Google or NumPy) and let ruff `D`-rules (limited subset) check public APIs. |
| M8 | L | `DeviceRegistry.addDevices(app)` takes `app` although `self.app` already exists; `("refraction", lambda _app: None, None, False)` is a placeholder device entry. | Remove the redundant parameter; model "no instance" explicitly rather than with a lambda returning `None`. |

### 4.4 Quality, robustness, error handling

| # | Pri | Finding | Recommendation |
|---|-----|---------|----------------|
| Q1 | M | ✅ **Done 2026-10-20.** `Worker.run` now has one `except Exception` branch that logs the full `traceback.format_exc()` and emits a short error string; the manual `tb_next` walk and `formatTbFrame` are gone. | – |
| Q2 | M | Broad excepts in `alpacaAscomCommon` (3) are justified by the driver boundary and documented in `per-file-ignores` – good. Keep a regression test per classification branch of `handleDeviceError`. | – |
| Q3 | M | ✅ **Done 2026-10-23:** `base/httpClient.py` (`request` with default timeout and retry on connection errors/timeouts, `safeRequest` logs and returns `None`); all `requests` calls in `src` use it. Earlier: (◐ re-check 2026-10-20: `S113` is enforced and every `requests` call has a `timeout`; no shared helper or retry policy yet) Network/IO paths (`requests`, `websocket-client`, `astroquery`, mount TCP in `mountcontrol/connection.py`, 462 L) – verify consistent timeouts, retries and error-to-signal mapping. | Introduce one `base/ethernet.py`-style helper for HTTP with default timeout and shared error handling; forbid bare `requests.get` without `timeout=` via ruff `S113`. |
| Q4 | L | `ascomClass.py` builds a Python snippet as a string (`"print(result if result else '', end='')"`) for execution via a subprocess. | Fine as a pragmatic COM isolation; make sure the string composition never includes user-controlled input (security review recommended, Windows only). |
| Q5 | L | Thread-safety relies on `QThreadPool` max 30 and a busy lock; shared mutable state (`Camera.data`, `app.config`) is mutated from workers and GUI thread. | Document the rule "workers return data via signals, GUI thread mutates state" and test it. |

### 4.5 Testability

| # | Pri | Finding | Recommendation |
|---|-----|---------|----------------|
| T1 | H | ✅ **Done 2026-10-22 (plan T1):** all unit tests build their stub app via the session-scoped `makeApp` fixture; `test_noDirectAppImport` prevents regressions; 14 per-device start/stop delegation tests duplicating `test_deviceFacade.py` removed. Earlier: 100 % line coverage is excellent, but with `app` as a god object each test must stub a large surface (the stub `App`). Test cost grows with the surface (see A1). | Narrow protocols (A1) shrink fixtures. Offer a `makeApp(**overrides)` factory with sensible defaults in `../tests/conftest.py`. |
| T2 | M | ✅ **Done 2026-10-20** (branch coverage enabled, `fail_under = 100`, all branch gaps closed – 4987 tests, 100 % line and branch coverage). Remaining: consider mutation testing (`mutmut`) on `mountcontrol` and `logic/modelBuild` where calculations matter. | – |
| T3 | M | `../tests/stress_tests` (crash, subprocess, loader-cycle tests) are not part of `tests/unit_tests`; it is unclear whether CI runs them. | Mark them `@pytest.mark.slow/integration` and run in a nightly job, or document why they are manual. |
| T4 | M | Tests mock heavily with `unittest.mock`; risk of tests verifying mocks instead of behaviour for GUI tabs. | Prefer fakes (in-memory device back-ends) over `MagicMock` for devices; keep `pytest-qt` signal-based assertions (`qtbot.waitSignal`). |
| T5 | M | Windows-only code is excluded from non-Windows coverage via conditional plugin – good – but is only validated on the Windows workflow. | Keep Windows CI mandatory; add contract tests for ASCOM/COM wrappers against a fake `win32com` so logic is checked on every OS. |
| T6 | L | (re-check 2026-10-20: still open – after a test run, tracked files under `../tests/work` show as deleted/untracked, e.g. `config/profile`, `build.hpts`, `m51.fit`; `.gitignore` only covers `/work/`) Test data, `tests/work/*` generated assets show up as untracked files in `git status`. | Ensure `../tests/work` is in `.gitignore` or generated into `tmp_path`. |
| T8 | L | ✅ **Done 2026-10-20.** Test layout aligned 1:1 with `../src/mw4`: 19 modules lacked a matching test file. 18 were misnamed/misplaced and were renamed with `git mv` (`mainApp/test_*` → `tests/unit_tests/test_*`, `test_s_*` → `test_*` in `simulator/`, `test_driverData` → `test_driverDataClass`, `test_boltwoodWeather` → `test_sensorWeatherBoltwood`, `test_fitsFunctions` → `test_fitsFunction`, `test_qCustomTableWidgetItem` → `test_qtCustomTableWidgetItem`); `test_loader_func.py` (it tested `bootstrap`) was merged into `base/test_bootstrap.py`. `base/appSignals.py` had no test and got `base/test_appSignals.py` (100 %). | Keep the mapping enforced, e.g. a small meta-test or CI script that fails when a module has no `test_<module>.py`. |
| T7 | L | Property-based tests (`hypothesis`) would fit transformations in `base/transform.py` and `mountcontrol/geometry.py` / `convert.py`. | Add for round-trip conversions (hms/dms parsing, coordinate transforms). |

### 4.6 Readability

| # | Pri | Finding | Recommendation |
|---|-----|---------|----------------|
| R1 | M | Consistent camelCase (a deliberate, documented deviation from PEP 8; `N999` ignored). Reasonable for a Qt code base, but ruff `N`-rules cannot help enforce it. | Keep; add a tiny custom check or pre-commit grep for `snake_case` defs if drift appears. |
| R2 | M | ✅ **Closed 2026-10-23, no change:** the log format already prints file name and line number (`%(filename)20.20s`/`%(lineno)4s`), so the origin is not lost; migrating would break `setCustomLoggingLevel` on the `"MW4"` logger. Earlier: Module-level `log = logging.getLogger("MW4")` as a *class attribute* in 60 classes. | One logger per module (`logging.getLogger(__name__)`) is idiomatic and gives per-module filtering; current single-name logger loses origin unless the formatter prints `%(module)s`. |
| R3 | L | ✅ Partly done 2026-10-20: commented-out code in `keypad.py` removed. Several long section banners remain. | Optional cleanup of banners. |
| R4 | L | Mixed English quality in docstrings and a few comments. | Light proof-reading pass. |
| R5 | L | Header banner in `../pyproject.toml` (ASCII art) and per-file headers are noise-free, but the file header in modules differs from the project banner. | Cosmetic. |

### 4.7 Repository hygiene and delivery

| # | Pri | Finding | Recommendation |
|---|-----|---------|----------------|
| H1 | H | (◐ re-check 2026-10-22: `gists/`, `../work` and `log/` are no longer tracked; `.git` is 1.2 GB, almost all of it old history, mainly the generated `mw4/resource/resources.py`; `HEAD` still has 70 MB test images and duplicated runtime data, see `work_agent/plan_H1_repository_slimming.md`; **Decision 2026-10-23: no history rewrite (`git filter-repo`) – rejected due to broken hashes/forks/PRs/tags; history stays as is.**) `.git` is **1.4 GB**; large binaries (ephemeris `de440_mw4.bsp`, finals data, assets 16 MB) historically committed. | Move runtime dirs (`../work`, `log/`) out of version control (`.gitignore`), keep `gists/` in a separate repo or docs. Consider `git lfs` or download-on-first-start for big data; `git filter-repo` history rewrite is rejected (decision 2026-10-23). |
| H2 | M | `../.idea` and `.coverage` present in the working tree. (re-check 2026-10-20: `.coverage` is ignored, `.idea/` is still untracked and **not** in `.gitignore`.) | Add `../.idea` to `.gitignore`. |
| H3 | M | Exact pins on core scientific packages (`numpy==2.5.4`, `astropy==8.0.2`, `pyside6==6.12.0`, `photutils==3.1.1`) – good for reproducibility, but libraries consumers of the PyPI package get over-constrained. | Fine for an application. Keep Renovate/Dependabot to bump regularly; document the pin policy. |
| H4 | L | ✅ **Done 2026-10-20.** Console scripts reduced to `mw4` and `mountwizzard4`. | – |
| H5 | L | ✅ **Done 2026-10-20.** Classifier changed to `Development Status :: 4 - Beta`. | – |

## 5. Suggested roadmap

**Quick wins (≤ 1 day each)** – ✅ all done on 2026-10-20
1. ✅ Added ruff rules `G004` (lazy logging, 167 call sites fixed), `S113` (request timeout,
   no findings) and `PLR0915` (statement budget; 7 known oversized functions listed in
   `per-file-ignores`; all 7 ignores have since been removed, see M1).
2. ✅ `generateAlignStars` returns the `ALIGN_STARS` data constant instead of 825 lines of code (P5).
3. ✅ Contract test `AppProtocol` ⇄ `MountWizzard4` (M6).
4. ✅ Branch coverage enabled and brought back to 100 % (T2); dead comment removed (R3);
   classifier and script aliases fixed (H4/H5); `Worker.run` simplified (Q1).

Next up: the open **Strategic** items below (9 and 11; 10 and 12 are done). Open decision: lowering the global
`PLR0915` budget from 50. A condensed list of everything still open is in
`2026-10-20_review_copilot_open.md`.

**Medium (1–2 weeks)**
5. ✅ Done: typed device access on `DeviceRegistry` (A2).
6. ✅ Done: `AppProtocol` split into role protocols, signals grouped (A1).
7. ✅ Done 2026-10-20: oversized functions broken up (M1: 25 → 16 over 50 L, largest 293 → 91 L,
   all `PLR0915` ignores removed); image stats, tilt geometry, asteroid MPC formatting and
   satellite track calculations extracted to `logic/` (A5, partly). `pyrefly` back to 0 errors;
   suite 5079 passed at 100 % line and branch coverage.
8. ✅ Done 2026-10-20: QSS moved to template files (M5); platform checks centralised in `base/platformInfo.py` (P8).

**Strategic**
9. Typed, versioned configuration dataclasses with migration (A3).
10. ✅ Done 2026-10-22: duplication analysis of device back-ends and shared `DeviceFacade` base (M3).
11. Repository slimming and data-asset policy (H1) – planned in `plan_H1_repository_slimming.md`.
12. ✅ Done 2026-10-22: import-linter contracts (7) for layering and Qt boundaries in CI; `deviceRegistry` moved to `mw4/deviceRegistry.py` (A4).

## 6. Conclusion

MountWizzard4 shows strong engineering discipline: layered package layout, modern typing,
strict linting, full test coverage and multi-OS CI. The investments with the highest return
now are to **type the seams** (device registry, app contract, configuration) and to
**shrink the biggest units** (a few giant functions and tabs). None of the findings is
blocking; they are all incremental, test-protected refactorings that the existing 100 %
coverage makes safe to do.
