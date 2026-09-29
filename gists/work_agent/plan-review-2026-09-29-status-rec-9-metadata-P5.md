# Plan – Status Review 2026-09-29, Rec 9 (P1, P2, P7, R4, R5) and P5

Scope: findings P1, P2, P5, P7, R4, R5 of
[2026-09-29-status-review.md](2026-09-29-status-review.md).

| #  | Change |
|----|--------|
| P1 | `pyproject.toml` (`>=3.12,<3.15`) is the source of truth. `README.rst` and `.github/copilot-instructions.md` are aligned to Python 3.12–3.14. |
| P2 | Classifier `Production/Stable` is kept (decision). |
| P7 | `pyproject.toml` header: "GUI with PyQT5 for python" → "GUI with PySide". |
| R4 | The 6 tracked `.DS_Store` files are removed from the index (`git rm --cached`); `.gitignore` already contains `.DS_Store`. |
| R5 | Artefacts in the working tree are accepted (decision). |
| P5 | The 29 functions without a return annotation (Ruff `ANN201`, `ANN204`, excl. `gui/widgets`) get one: 26 × `-> None`, `telescope.create -> bool`, `measureAddons.dataPlots -> dict[str, dict]`, `Styles.generateCMaps -> list[pg.ColorMap]`. No behaviour change. |

Finish: Ruff format/check, `ruff check --select ANN201,ANN202,ANN204,ANN205,ANN206`
clean, full unit test run with 100 % coverage, status review updated.

## Status (2026-09-29)

| #  | Status |
|----|--------|
| P1 | ✅ Done – `README.rst` 3.12-3.14; Copilot instructions 3.12–3.14 / 3.12 features |
| P2 | ⏸ Kept – decision in section 8 of the status review |
| P7 | ✅ Done – header "GUI with PySide" |
| R4 | ✅ Done – 6 `.DS_Store` files removed from the index (staged, not committed) |
| R5 | ⏸ Kept – decision in section 8 of the status review |
| P5 | ✅ Done – 29 annotations added; `ANN20x` check clean |

Verification: Ruff format/check clean, 4652 passed, 38 skipped (`-n auto`),
coverage 100 % (18,574 statements). Status review updated (section 3.3, 5, 7, 8).

