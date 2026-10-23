# MountWizzard4 – Code Review, open items only (2026-10-20)

Condensed from `2026-10-20_review_copilot.md` (second pass, revision `3ec18a381`, version
`4.0.0b36`). Only findings and roadmap items that are **not yet done** are listed.
Done items (A1, A2, A4, A5, P2, P4, P5, P8, M2, M3, M4, M5, M6, M8, Q1, T3, T6, T8, H2, H4, H5, roadmap 1–8
and the first round of M1, P1, T1) are omitted.

State at re-run: 5213 tests passed / 38 skipped, 100 % line and branch coverage,
`ruff check src` clean, `pyrefly` 0 errors, `lint-imports` 7 contracts kept.

Priority: **H** high, **M** medium, **L** low. ◐ = partly done.

## 1. Summary of what remains

The structural weaknesses are now concentrated in two areas: **untyped configuration**
(A3) and **repository weight** (H1). Layering (A4) is done and enforced in CI. Everything else is
incremental cleanup.

| Area            | Rating | Remaining weakness |
|-----------------|--------|--------------------|
| Architecture    | A-     | raw-dict config (A3) |
| Pythonic style  | B+     | `hasattr`/dict plumbing, `dict[str, Any]` carriers |
| Maintainability | A-     | long functions, docstring quality |
| Quality         | A-     | no shared HTTP helper, thread-safety rule undocumented |
| Testability     | A-     | god-object stubbing, stress tests not in CI, `../tests/work` pollution |
| Readability     | B+     | class-level loggers, docstring quality |

## 2. Open findings

### Architecture
| # | Pri | Open point | Recommendation |
|---|-----|-----------|----------------|
| A3 | H | Configuration is an untyped nested dict (438 `config[…]`/`.get` accesses); schema, defaults and migration are implicit. | Per-component `@dataclass` configs with `from_dict`/`to_dict`, defaults in one place, a schema version and one migration hook. |
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
| H1 | H | ◐ **Decision 2026-10-23: no history rewrite (`git filter-repo`) – rejected due to broken hashes/forks/PRs/tags; history stays as is.** `.git` is 1.2 GB (measured 2026-10-22), almost all of it history (generated `mw4/resource/resources.py` ×hundreds, `support/`, `whl/`, `hip_main.dat`); `gists/`, `../work`, `log/` are no longer tracked (`gists/` should go into `.gitignore`). In `HEAD`: 4 test images × 17.5 MB, runtime data duplicated in `tests/testData` (6.5 MB). | See `plan_H1_repository_slimming.md`: `.gitignore` + large-file CI check, deduplicate test data, crop/compress test images, data-asset policy, partial/shallow clones; no `git filter-repo` (rejected 2026-10-23). |
| H3 | M | Exact pins on core packages. | Fine for an application; keep Renovate/Dependabot, document the pin policy. |

## 3. Remaining roadmap

**Follow-ups (first round of items 5–8 is done)**
1. Repair `../tests/stress_tests` (they fail with `AttributeError` on the UI layer) so the nightly job is green.
2. M1 – the remaining ~12 long functions. Optional: same controller pattern for
   `tabModel_Manage.py`, `tabAlmanac.py`, `tabModel_BuildPoints.py` (A5 follow-up); the
   `update*Gui` tri-state button logic in `tabImage_Manage.py` could move to `logic` as well.

**Strategic**
3. A3 – typed, versioned configuration dataclasses with migration.
4. H1 – repository slimming and data-asset policy.
5. Q3 – shared HTTP helper; R2 – module-level loggers.
