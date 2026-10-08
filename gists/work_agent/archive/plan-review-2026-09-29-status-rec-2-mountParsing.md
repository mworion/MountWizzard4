# Plan – Status Review 2026-09-29, Recommendation 2: Harden Mount Response Parsing

**Date:** 2026-09-29
**Source:** `2026-09-29-status-review.md`, rec 2
(findings M1, M2, M3, M4, M5, M7, N2)
**Scope:** `src/mw4/mountcontrol/connection.py`, `obsSite.py`, `firmware.py`
and the mirrored tests in `tests/unit_tests/mountcontrol/`.

## Goal

A truncated, garbled or non-ASCII mount answer must never raise inside a
poll worker. The parsers return `False` and log the bad response. Socket
errors are caught by their concrete types, so programming errors are no longer
hidden as "socket error".

## Changes

### 1. `Connection` (M4, M5, M7, N2)

| Location           | Today                                         | New                                                    |
|--------------------|-----------------------------------------------|--------------------------------------------------------|
| `closeClientHard`  | `except (OSError, Exception)`                 | `except (OSError, RuntimeError)`                       |
| `buildClient`      | `except (OSError, ValueError, TypeError, Exception)` | `except (OSError, RuntimeError, TypeError, ValueError)` |
| `sendData`         | `except (OSError, Exception)`                 | `except (OSError, RuntimeError)`                       |
| `receiveData`      | `except (OSError, Exception)`; strict `decode("ASCII")` in `else` | `except (OSError, RuntimeError)`; `decode("ASCII", errors="replace")` |
| `communicateRaw`   | `except (OSError, Exception)`; strict decode; returns literal `"Exception"` | `except (OSError, RuntimeError)`; tolerant decode; returns `f"Error: {e}"` |

`RuntimeError` is what PySide6 raises when the C++ socket is already deleted.
`TypeError` / `ValueError` in `buildClient` come from `int(self.host[1])`.
With `errors="replace"` a bad byte becomes `U+FFFD`, and the parsers then
reject the value.

### 2. `ObsSite`

- `parsePointing` (M1): after the chunk count check, check that `response[3]`
  has at least 8 comma fields and `response[4]` at least 5. Otherwise log a
  warning and return `False`. Nothing is assigned before the checks pass.
- `parseSetTargetResponse` (M2): first check `len(response) == 4` and
  `len(response[0]) >= 3`, then check the two set results (`response[0][0:2]`).
- `syncPositionToTarget` (M3, `obsSite.py:734`): check `len(response) >= 2`
  before `response[1]`.

### 3. `Firmware.parse` (M3)

- `Version(response[1])` raises `InvalidVersion` for a garbled answer. Parse
  the version first, catch `InvalidVersion`, log a warning, return `False`, and
  leave all fields unchanged.

## Tests (`../../tests/unit_tests/mountcontrol`)

- `test_connection.py`: change the generic `Exception` side effects to
  `OSError` / `RuntimeError`. Add tests for non-ASCII bytes in `receiveData`
  and `communicateRaw` (no exception, replacement char), the new error text of
  `communicateRaw`, and an unexpected exception (e.g. `AttributeError`) that
  is no longer swallowed.
- `test_obsSite.py`: `parsePointing` with too few fields in `response[3]` and in
  `response[4]`; `parseSetTargetResponse` with a short `response[0]`, a wrong
  length, and an empty list; `syncPositionToTarget` with a one-element response.
- `test_firmware.py`: `parse` with an invalid version string.

## Out of Scope

- A persistent connection (M6, rec 15).
- Setter-level validation (e.g. `timeJD` with a non-numeric value). This is
  noted as a follow-up in the review.
- Other parsers in `mountcontrol` that are not listed in rec 2.

## Done Criteria

Ruff clean, the full suite passes serially and with `-n auto`, and coverage is 100 %.

