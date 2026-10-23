# Plan Q3 + R2 – shared HTTP helper and module-level loggers (roadmap item 5)

Source: `2026-10-20_review_copilot_open.md`, findings Q3 and R2.
Status: **plan only – nothing of this is executed.**
The two parts are independent; each can be delivered as its own change.

---

## Part A – Q3: shared HTTP helper

### Current state (measured)

`requests` is used directly in 6 modules, all with a timeout (`S113` enforced):

| Module | Call | Timeout |
|--------|------|---------|
| `logic/drivers/environment/sensorWeatherOnline.py:100` | `get` | 30 literal |
| `logic/drivers/environment/seeingWeather.py:73` | `get` | 30 literal |
| `logic/drivers/powerswitch/kmRelay.py:83` | `get` + auth | `self.TIMEOUT` |
| `logic/drivers/frameworks/sgproClass.py:54,60` | `post`, `get` | see file |
| `gui/extWindows/downloadPopupW.py:87` | `get(stream=True)` | `TIMEOUT_SOURCE` |
| `gui/extWindows/uploadPopupW.py:135,175` | `get`, `post(files=)` | `TIMEOUT_UPLOAD`, 10 literal |

Each site has its own try/except and its own error reporting; no retry, no common policy.

### Design

New module `src/mw4/base/httpClient.py` (lowest layer, no Qt, so `gui` and `logic` may both
import it; allowed by the `gui → logic → mountcontrol → base` contract):

- `DEFAULT_TIMEOUT` constant; per-call override.
- `get(url, *, timeout=None, **kw) -> Response | None`, `post(...)`, same for
  `stream=True`; optional `retries` (default 0, idempotent GET only) with small back-off.
- One error policy: catches `requests.RequestException`, logs once via `log`, returns
  `None` (or a small `HttpResult` dataclass with `ok`, `status`, `response`, `error`) –
  decision in step 1.
- No Qt signals in the helper: callers keep emitting their own signals from the result
  (keeps `base` Qt-free and the "workers return data via signals" rule, Q5).

### Steps

1. **Decide the return contract** (`Response | None` vs `HttpResult`) by reading the six call
   sites; choose the one that removes most try/except code. Document in the module docstring.
2. **Implement `base/httpClient.py`** with full type annotations; unit tests in
   `tests/unit_tests/base/test_httpClient.py` (mock `requests`): success, timeout,
   connection error, HTTP error status, retry count, streaming, auth, files.
3. **Migrate call sites one module at a time**, keeping behaviour and user-visible messages.
   Update each module's tests to mock `httpClient` instead of `requests`.
4. **Enforce.** Add `requests` to ruff `TID251` banned imports (like `QtWidgets`), with
   per-file ignore for `base/httpClient.py` only; add an `import-linter` contract if useful.
5. **Document** the policy (timeouts, retries, error handling) in the module docstring and
   the developer docs.

### Risks

- `downloadPopupW` streams large files and reports progress → helper must expose the raw
  streaming response, not wrap/consume it.
- `sgproClass` / `kmRelay` rely on specific exceptions for status → verify in tests that the
  mapping stays identical.
- Windows-only paths are not involved; no coverage guard needed.

---

## Part B – R2: module-level loggers

### Current state (measured)

- 49 classes with `log = logging.getLogger("MW4")` at class level, 2 with
  `self.log = logging.getLogger("MW4")`, 3 more `log` variants.
- Root config in `base/loggerMW.py`: `basicConfig` with
  `[%(filename)20.20s][%(lineno)4s]`, handler on the root logger, level set on `"MW4"`,
  noisy libs (`urllib3`, `requests`, `astropy`, `PySide6`, `keyring`) set to WARNING.

Because every logger is the single named logger `"MW4"`, the log format already carries
file and line; a hierarchical `__name__` logger would add per-module level control.

### Decision (step 1)

Option 1 (recommended): **module-level `log = logging.getLogger(__name__)`** with all
modules living under the `mw4` package; set level on the `"mw4"` logger instead of `"MW4"`
and add `%(name)s`-free format (filename/line stay). Gains per-module level control.
Option 2: keep the `"MW4"` logger, only move it to module level (pure mechanical).
Option 3: keep as is, add `%(module)s` (review's fallback) – no code change.

### Steps

1. **Pick option** with the maintainer; record it here.
2. **Mechanical refactor** in `src/mw4` (excluding `gui/widgets`): move the class attribute
   to module level directly below the imports; replace `self.log` / `ClassName.log` uses.
   Do it package by package (`base`, `mountcontrol`, `logic`, `gui`, `mainApp`) in separate
   commits.
3. **Logging setup** (`base/loggerMW.py`): for option 1 change `getLogger("MW4").setLevel`
   to the `"mw4"` logger and check that file handler, `LoggerWriter` and the level switch
   in the GUI (debug/info toggle) still affect all modules.
4. **Tests.** Tests that use `caplog` / patch `log` by `Class.log` need updating to the
   module attribute; add one test that the level toggle reaches a module logger.
5. **Enforce.** Add a ruff rule or a pre-commit grep that rejects class-level
   `getLogger` (e.g. `grep -rn "^    log = logging"`), and keep `LOG` ruff rules enabled.

### Risks

- Tests patching `Class.log` break → grep tests first (`rg "\.log\b" tests`).
- Third-party code logging to `"MW4"` (none known) would be dropped from the filter → check
  `rg 'getLogger\("MW4"\)'` outside `src/mw4`.
- Log volume changes if level handling differs → verify with a manual debug-level run.

---

## Verification (both parts)

- `uv run pytest` full suite, 100 % line and branch coverage.
- `uv run ruff check src`, `uv run ruff format`, `uv run lint-imports`, pyrefly.

## Done when

- No direct `requests` call outside `base/httpClient.py`; ban enforced by ruff.
- No class-level logger in `src/mw4`; level control verified.
