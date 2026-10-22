# MountWizzard4 – Code Review, open items only (2026-10-20)

Condensed from `2026-10-20_review_copilot.md` (second pass, revision `3ec18a381`, version
`4.0.0b36`). Only findings and roadmap items that are **not yet done** are listed.
Done items (A1, A2, P2, P4, P5, P8, M2, M5, M6, M8, Q1, T3, T6, T8, H2, H4, H5, roadmap 1–8 and the first
round of A4, A5, M1, P1, T1) are omitted.

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
| A4 | L | ◐ `AudioManager` is decoupled from `app.mainW`; import-linter contract (`base`/`logic`/`mountcontrol` ↛ `gui`) runs in the ubuntu lint job. Remaining: 22 `logic` + 8 `mountcontrol` files import PySide6; `base` ↔ `logic` is circular. | Limit Qt in `logic` to `QObject`/`Signal`; extend the contract with `base ↛ logic`. |
| A5 | M | ◐ Pass-text, age-colour, trajectory, list-pick, filter-range and tracking-mode logic extracted. Tabs are still large (`tabMount_Sett.py` ~490 L, `tabImage_Manage.py` ~460 L, `tabSat_Track.py` ~400 L), mostly dialog/GUI code. | Move remaining calculations/state transitions into plain `logic/controllers/<GUI area>/` classes (see `plan_A5_tab_logic_extraction.md`); prefer composition (tab owns a controller). |
| A6 | M | Global signals give loose coupling in code but tight coupling in behaviour. | Document emitter/listener ownership per signal group in `base/appSignals.py`. |
| A7 | L | `MountWizzard4.__init__` ordering is encoded only by line order. | Split into `setup*` steps with docstrings stating dependencies. |

### Pythonic style
| # | Pri | Open point | Recommendation |
|---|-----|-----------|----------------|
| P1 | L | ◐ `HasSignals`/`HasDriverConfig` (`base/driverProtocol.py`) replace the `hasattr` checks in `deviceRegistry`, `tabSettDevice`, `devicePopupW`. Remaining `getattr` calls are mostly dynamic UI-name lookups. | Review the rest case by case. |
| P3 | M | `dict[str, Any]` carriers (`Camera.data`, `run`, `config`). | `TypedDict`/dataclasses; `run: dict[str, FrameworkDriver]`. |
| P6 | L | Magic-value instance attributes, underscore attributes with property wrappers. | Small dataclasses (`SubFrame`, `Binning`). |
| P7 | L | 3 × `type: ignore`, 54 pyrefly suppressions, 28 hidden warnings, `mountcontrol` relaxations. | Tighten per file over time. |

### Maintainability
| # | Pri | Open point | Recommendation |
|---|-----|-----------|----------------|
| M1 | L | ◐ `createWindowTable`, `createDeviceTable`, `showTiltSquare` reworked. ~12 functions > 50 lines remain (largest `measureAddons.dataPlots` 91 L, purely declarative; `createFramework2gui` 63 L, `extractSources` 61 L, `astrometry.solve` 57 L). | Builder helpers where it helps; decide on a lower global `PLR0915` budget. |
| M3 | M | Likely copy-paste across `deviceIndi/Alpaca/SGPro/Ascom` wrappers. | Run a duplication scan; extract common bases/mixins. |
| M4 | M | `base/` mixes infrastructure with driver-protocol classes (`ascomClass`, `sgproClass`, `indiClass`, …). | ✅ Done: driver classes now in `logic/drivers/frameworks/`; `measure`/`keypad` in `logic/drivers/`. |
| M7 | L | Docstring style and language quality vary. | One style, limited ruff `D` rules for public APIs. |

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
| T1 | M | ◐ `makeApp(**overrides)` fixture exists (`tests/conftest.py`). Remaining: tests still build `App()` directly. | Migrate tests gradually; use narrow protocols (A1). |
| T2 | – | Remaining idea: mutation testing (`mutmut`) on `mountcontrol` and `logic/modelBuild`. | Optional. |
| T4 | M | Heavy `unittest.mock` use for GUI tabs. | In-memory fakes for devices; `qtbot.waitSignal`. |
| T5 | M | Windows-only code validated only on the Windows workflow. | Contract tests against a fake `win32com`. |
| T7 | L | No property-based tests. | `hypothesis` round-trips for `base/transform.py`, `mountcontrol/geometry.py`, `convert.py`. |

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
| H3 | M | Exact pins on core packages. | Fine for an application; keep Renovate/Dependabot, document the pin policy. |

## 3. Remaining roadmap

**Follow-ups (first round of items 5–8 is done)**
1. Repair `tests/stress_tests` (they fail with `AttributeError` on the UI layer) so the nightly job is green.
2. A5/M1 – continue tab logic extraction and the remaining ~12 long functions.
3. T1 – migrate tests to `makeApp`; extend the import-linter contract (`base ↛ logic`).

**Strategic**
4. A3 – typed, versioned configuration dataclasses with migration.
5. M3 – duplication analysis of device back-ends (M4 done).
6. H1 – repository slimming and data-asset policy.
7. Q3 – shared HTTP helper; R2 – module-level loggers.
