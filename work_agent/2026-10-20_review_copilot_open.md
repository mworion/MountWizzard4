# MountWizzard4 – Code Review, open items only (2026-10-20)

Condensed from `2026-10-20_review_copilot.md` (second pass, revision `3ec18a381`, version
`4.0.0b36`). Only findings and roadmap items that are **not yet done** are listed.
Done items (A1, A2, A4, A5, A6, P1, P2, P4, P5, R3, R4, R5, P8, M2, M3, M4, M5, M6, M8, Q1, T3, T6, T8, H2, H4, H5, roadmap 1–8
and the first round of M1, T1) are omitted.

State at re-run (2026-10-23): 5275 tests passed / 38 skipped, 100 % line and branch coverage,
`ruff check src` clean, `pyrefly` 0 errors, `lint-imports` 7 contracts kept.

Priority: **H** high, **M** medium, **L** low. ◐ = partly done.

## 1. Summary of what remains

The structural weaknesses are now concentrated in two areas: **untyped configuration**
(A3) and **repository weight** (H1). Layering (A4) is done and enforced in CI. Everything else is
incremental cleanup.

| Area            | Rating | Remaining weakness |
|-----------------|--------|--------------------|
| Architecture    | A-     | raw-dict config (A3) |
| Pythonic style  | A-     | `data` carriers stay `dict[str, Any]` by design; type suppressions (P7) |
| Maintainability | A-     | long functions, docstring quality |
| Quality         | A-     | thread-safety rule undocumented (Q5) |
| Testability     | A-     | god-object stubbing, stress tests not in CI, `../tests/work` pollution |
| Readability     | A-     | docstring style (M7), camelCase not enforced (R1) |

## 2. Open findings

### Architecture
| # | Pri | Open point | Recommendation |
|---|-----|-----------|----------------|
| A3 | H | Configuration is an untyped nested dict (438 `config[…]`/`.get` accesses); schema, defaults and migration are implicit. | Per-component `@dataclass` configs with `from_dict`/`to_dict`, defaults in one place, a schema version and one migration hook. |
| A7 | L | `MountWizzard4.__init__` ordering is encoded only by line order. | Split into `setup*` steps with docstrings stating dependencies. |

### Pythonic style
| # | Pri | Open point | Recommendation |
|---|-----|-----------|----------------|
| P3 | L | ◐ `run` typed (`FrameworkDriver` + per-family protocols); `ProfileConfig` alias for A3; camera `data` keys are constants (`base/cameraKeys.py`). `data` stays `dict[str, Any]` by design (dynamic keys). Open: key constants for other device families, record dicts (`SolveResult`, model points). | Optional, see `plan_P3_typed_carriers.md`. |
| P6 | L | Magic-value instance attributes, underscore attributes with property wrappers. | Small dataclasses (`SubFrame`, `Binning`). |
| P7 | L | 3 × `type: ignore`, 54 pyrefly suppressions, 28 hidden warnings, `mountcontrol` relaxations. | Tighten per file over time. |

### Maintainability
| # | Pri | Open point | Recommendation |
|---|-----|-----------|----------------|
| M1 | L | ◐ Reduced to 6 functions > 50 lines (2026-10-23): `qtMessageDialog.__init__` 65 L, `mainWindow.__init__` 61 L, `tabSat_Track.__init__` 61 L, `geometry.calcAxisTransforms` 55 L, `simulator/dome.create` 54 L, `simulator/telescope.createOta` 51 L; mostly declarative builders. A5 follow-up controllers (almanac, model) exist. | Optional: `calcAxisTransforms` split; decide on a lower global `PLR0915` budget. |
| M7 | L | Docstring style and language quality vary. | One style, limited ruff `D` rules for public APIs. |

### Quality and robustness
| # | Pri | Open point | Recommendation |
|---|-----|-----------|----------------|
| Q2 | M | Keep a regression test per classification branch of `handleDeviceError`. | – |
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

### Repository hygiene
| # | Pri | Open point | Recommendation |
|---|-----|-----------|----------------|
| H1 | H | ◐ **Decision 2026-10-23: no history rewrite (`git filter-repo`) – rejected due to broken hashes/forks/PRs/tags; history stays as is.** `.git` is 1.2 GB (measured 2026-10-22), almost all of it history (generated `mw4/resource/resources.py` ×hundreds, `support/`, `whl/`, `hip_main.dat`); `gists/`, `../work`, `log/` are no longer tracked (`gists/` should go into `.gitignore`). In `HEAD`: 4 test images × 17.5 MB, runtime data duplicated in `tests/testData` (6.5 MB). | See `plan_H1_repository_slimming.md`: `.gitignore` + large-file CI check, deduplicate test data, crop/compress test images, data-asset policy, partial/shallow clones; no `git filter-repo` (rejected 2026-10-23). |
| H3 | M | Exact pins on core packages. | Fine for an application; keep Renovate/Dependabot, document the pin policy. |

## 3. Remaining roadmap

**Follow-ups (first round of items 5–8 is done)**
1. Repair `../tests/stress_tests` (they fail with `AttributeError` on the UI layer) so the nightly job is green.

**Strategic**
2. A3 – typed, versioned configuration dataclasses with migration.
3. H1 – repository slimming and data-asset policy.

