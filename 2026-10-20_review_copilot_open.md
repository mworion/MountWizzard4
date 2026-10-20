# MountWizzard4 – Code Review, open items only (2026-10-20)

Condensed from `2026-10-20_review_copilot.md` (second pass, revision `3ec18a381`, version
`4.0.0b36`). Only findings and roadmap items that are **not yet done** are listed.
Done items (A1, A2, P4, P5, P8, M5, M6, Q1, T2, T8, H4, H5, roadmap 1–8) are omitted.

State at re-run: 5108 tests passed / 38 skipped, 100 % line and branch coverage,
`ruff check src` clean, `pyrefly` 0 errors (54 suppressed, 28 warnings hidden).

Priority: **H** high, **M** medium, **L** low. ◐ = partly done.

## 1. Summary of what remains

The structural weaknesses are now concentrated in three areas: **untyped configuration**
(A3), **duplication / layering of the driver code** (M3, M4, A4) and **repository weight**
(H1). Everything else is incremental cleanup.

| Area            | Rating | Remaining weakness |
|-----------------|--------|--------------------|
| Architecture    | B+     | raw-dict config, `app.mainW` in `base`, big GUI tabs |
| Pythonic style  | B+     | `hasattr`/dict plumbing, `dict[str, Any]` carriers |
| Maintainability | B+     | back-end duplication, `base` mixes infra and drivers |
| Quality         | A-     | no shared HTTP helper, thread-safety rule undocumented |
| Testability     | A-     | god-object stubbing, stress tests not in CI, `tests/work` pollution |
| Readability     | B+     | class-level loggers, docstring quality |

## 2. Open findings

### Architecture
| # | Pri | Open point | Recommendation |
|---|-----|-----------|----------------|
| A3 | H | Configuration is an untyped nested dict (438 `config[…]`/`.get` accesses); schema, defaults and migration are implicit. | Per-component `@dataclass` configs with `from_dict`/`to_dict`, defaults in one place, a schema version and one migration hook. |
| A4 | M | ◐ `logic`/`mountcontrol` no longer import `gui`. Remaining: `base/audioManager.py` uses `app.mainW`; 22 `logic` + 8 `mountcontrol` files import PySide6. | Pass a parent/handle into `AudioManager`; limit Qt in `logic` to `QObject`/`Signal`; add an import-linter contract (`gui → logic → base`) in CI. |
| A5 | M | ◐ Calculations were extracted, but big tabs remain: `tabMount_Sett.py` 504 L, `tabImage_Manage.py` 477 L, `tabSat_Track.py` 436 L. | Move remaining calculations/state transitions into plain `logic` classes; prefer composition (tab owns a controller). |
| A6 | M | Global signals give loose coupling in code but tight coupling in behaviour. | Document emitter/listener ownership per signal group in `base/appSignals.py`. |
| A7 | L | `MountWizzard4.__init__` ordering is encoded only by line order. | Split into `setup*` steps with docstrings stating dependencies. |

### Pythonic style
| # | Pri | Open point | Recommendation |
|---|-----|-----------|----------------|
| P1 | M | 50 × `hasattr`/`getattr` (e.g. `deviceRegistry.py` lines 79, 267, 284). | Runtime-checkable protocol (`HasSignals`, `HasConfig`) or default attributes. |
| P2 | M | Repeated `self.d[device].run[framework].config` chains in `collectConfigFromSingleDevice`. | Local variables, `dataclasses.asdict`. |
| P3 | M | `dict[str, Any]` carriers (`Camera.data`, `run`, `config`). | `TypedDict`/dataclasses; `run: dict[str, FrameworkDriver]`. |
| P6 | L | Magic-value instance attributes, underscore attributes with property wrappers. | Small dataclasses (`SubFrame`, `Binning`). |
| P7 | L | 3 × `type: ignore`, 54 pyrefly suppressions, 28 hidden warnings, `mountcontrol` relaxations. | Tighten per file over time. |

### Maintainability
| # | Pri | Open point | Recommendation |
|---|-----|-----------|----------------|
| M1 | M | ◐ 16 functions > 50 lines (largest `measureAddons.dataPlots` 91 L, `createWindowTable` 87 L, `createDeviceTable` 79 L, `showTiltSquare` 76 L). | Builder helpers / table-driven widget creation; decide on a lower global `PLR0915` budget. |
| M2 | M | Two functions with 8 parameters (`calcTrajectoryData`, `tabSat_Search.calcSat`). | Parameter objects or keyword-only args. |
| M3 | M | Likely copy-paste across `deviceIndi/Alpaca/SGPro/Ascom` wrappers. | Run a duplication scan; extract common bases/mixins. |
| M4 | M | `base/` mixes infrastructure with driver-protocol classes (`ascomClass`, `sgproClass`, `indiClass`, …). | Move to `logic/drivers/`. |
| M7 | L | Docstring style and language quality vary. | One style, limited ruff `D` rules for public APIs. |
| M8 | L | `DeviceRegistry.addDevices(app)` has a redundant parameter; placeholder `refraction` lambda entry. | Remove parameter; model "no instance" explicitly. |

### Quality and robustness
| # | Pri | Open point | Recommendation |
|---|-----|-----------|----------------|
| Q2 | M | Keep a regression test per classification branch of `handleDeviceError`. | – |
| Q3 | M | ◐ `S113` enforced, all `requests` calls have a timeout. No shared helper, retry or error-to-signal policy. | One HTTP helper with default timeout and shared error handling. |
| Q4 | L | `ascomClass.py` composes a Python snippet string for a subprocess. | Security review: never include user-controlled input (Windows only). |
| Q5 | L | Workers and GUI thread both mutate shared state. | Document "workers return data via signals" and test it. |

### Testability
| # | Pri | Open point | Recommendation |
|---|-----|-----------|----------------|
| T1 | H | Each test stubs a large `app` surface; no `makeApp(**overrides)` factory in `tests/conftest.py`. | Narrow protocols are available (A1), add the factory. |
| T2 | – | Remaining idea: mutation testing (`mutmut`) on `mountcontrol` and `logic/modelBuild`. | Optional. |
| T3 | M | `tests/stress_tests` are not run by CI and carry no markers. | Mark `slow`/`integration`, nightly job or documented as manual. |
| T4 | M | Heavy `unittest.mock` use for GUI tabs. | In-memory fakes for devices; `qtbot.waitSignal`. |
| T5 | M | Windows-only code validated only on the Windows workflow. | Contract tests against a fake `win32com`. |
| T6 | L | Test runs modify/delete tracked files in `tests/work/` (`config/profile`, `build.hpts`, `m51.fit`); `.gitignore` covers only `/work/`. | Generate into `tmp_path` or ignore/untrack generated files. |
| T7 | L | No property-based tests. | `hypothesis` round-trips for `base/transform.py`, `mountcontrol/geometry.py`, `convert.py`. |
| T8 | L | Mapping is 1:1 today but not enforced. | Meta-test or CI script that fails on a module without `test_<module>.py`. |

### Readability
| # | Pri | Open point | Recommendation |
|---|-----|-----------|----------------|
| R1 | M | camelCase is a deliberate deviation; no tool enforces it. | Pre-commit grep for `snake_case` defs if drift appears. |
| R2 | M | 56 classes with a class-level `log = logging.getLogger("MW4")`. | Module-level `logging.getLogger(__name__)` or print `%(module)s`. |
| R3 | L | Long section banners remain. | Optional cleanup. |
| R4 | L | Mixed English in docstrings/comments. | Proof-reading pass. |
| R5 | L | Module header differs from the project banner. | Cosmetic. |

### Repository hygiene
| # | Pri | Open point | Recommendation |
|---|-----|-----------|----------------|
| H1 | H | ◐ `.git` is 1.4 GB; `work/`, `log/` untracked now, 149 files in `gists/` still tracked; large binaries in history. | Move `gists/` out; `git lfs` or download-on-first-start for big data; `git filter-repo` only with maintainer agreement. |
| H2 | M | `.idea/` is untracked but not in `.gitignore`. | Add `.idea/` to `.gitignore`. |
| H3 | M | Exact pins on core packages. | Fine for an application; keep Renovate/Dependabot, document the pin policy. |

## 3. Remaining roadmap

**Quick wins (≤ 1 day each)**
1. H2 – add `.idea/` to `.gitignore`; T6 – stop tests polluting `tests/work/`.
2. T8 – CI/meta check for the test-per-module mapping.
3. T3 – markers and nightly run for `tests/stress_tests`.
4. P2, M8 – small `DeviceRegistry` cleanups.

**Medium (1–2 weeks)**
5. A4 – `AudioManager` without `app.mainW`, import-linter contract in CI.
6. A5 – further tab logic extraction (three tabs > 430 L).
7. M1/M2 – remaining 16 long functions and the two 8-parameter functions.
8. T1 – `makeApp(**overrides)` test factory; P1 – `HasSignals`/`HasConfig` protocols.

**Strategic**
9. A3 – typed, versioned configuration dataclasses with migration.
10. M3/M4 – duplication analysis of device back-ends, move driver classes out of `base`.
11. H1 – repository slimming and data-asset policy.
12. Q3 – shared HTTP helper; R2 – module-level loggers.
