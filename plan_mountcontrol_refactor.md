# Plan: Refactor `mountcontrol` Module

**Date:** 2026-05-28  
**Scope:** `src/mw4/mountcontrol/` – all 15 Python source files  
**Goal:** Improve Pythonicity, eliminate redundancy, add missing annotations, simplify unnecessary
guards, fix real bugs, and improve consistency – without adding any new features.

---

## Progress

| File | Status |
|------|--------|
| `connection.py` | ✅ Done |
| `convert.py` | ✅ Done |
| `model.py` | ✅ Done |
| `modelStar.py` | ✅ Done |
| `mount.py` | 🔄 In progress (item 5 done; items 1, 3 pending) |
| `firmware.py` | ⬜ Pending |
| `dome.py` | ⬜ Pending |
| `setting.py` | ⬜ Pending |
| `satellite.py` | ⬜ Pending |
| `obsSite.py` | ⬜ Pending |
| `geometry.py` | ⬜ Pending |
| `progStar.py` | ⬜ Pending |
| `tleParams.py` | ⬜ Pending |
| `trajectoryParams.py` | ⬜ Pending |
| `jdMixin.py` (new) | ⬜ Pending |

---

## Summary of Findings per File

### connection.py ✅

| # | Issue | Type | Status |
|---|-------|------|--------|
| 1 | `COMMANDS` list contains duplicate entries (`:Sev` and `:Sg` appear twice, lines 147–150) | Bug/Redundancy | ✅ Fixed |
| 2 | `COMMANDS`, `COMMAND_A`, `COMMAND_B` are `list`; `validCommand` and `analyseCommand` call `sorted(…, reverse=True)` on every invocation (O(n log n) per call) | Performance | ✅ Fixed |
| 3 | `closeClientHard`: final `return` after `self.log.warning(…)` is unreachable / redundant | Cleanup | ✅ Fixed |
| 4 | `communicateRaw`: variable `sucRec` is set in except branches but the `else` branch only sets it conditionally after both except branches – technically fine but confusing; the `else` after try/except/else should set `sucRec = True` explicitly | Clarity | ✅ Fixed |
| 5 | `receiveData`: complex Boolean condition in while-loop is hard to read; extract to local variable or helper | Clarity | ✅ Fixed |

**Actions:**
- ✅ Remove duplicate entries from `COMMANDS`.
- ✅ Pre-sort `COMMAND_A` and `COMMAND_B` at class-definition time (assign sorted tuples as class
  attributes) so runtime sorting is eliminated.
- ✅ Remove the trailing redundant `return` in `closeClientHard`.
- ✅ Clarify `communicateRaw` control flow (assign `sucRec = True` in `else` block explicitly,
  document the `sucRec` variable).
- ✅ Extract the receive-completion condition in `receiveData` into a named local Boolean for
  readability.

---

### convert.py ✅

| # | Issue | Type | Status |
|---|-------|------|--------|
| 1 | `stringToAngle` and `valueToAngle` both use an `if/else` block to choose between `Angle(degrees=…)` and `Angle(hours=…)` – this pattern is identical in both functions | Redundancy | ✅ Fixed |
| 2 | `parseRaToAngleString` and `parseDecToAngleString` are structurally identical; they differ only in the regex patterns and the literal strings `H` vs `Deg` | Redundancy | ✅ Fixed |
| 3 | `convertRaToAngle` and `convertDecToAngle` share the same `isSexagesimal/isFloat/elements` dispatch pattern | Redundancy | ✅ Fixed |
| 4 | `formatLatToText` and `formatLonToText` unpack `frac` from `sexagesimalizeToInt` but never use it | Cleanup | ✅ Fixed |
| 5 | `stringToDegree`: `elif len(value) == 2:` branch is followed by `else: return 0` – the `else` is cleaner as a final guard rather than a branch in an `if/elif/else` chain | Pythonic | ✅ Fixed |
| 6 | Early returns in `stringToDegree` return integer `0`, not `float` – the annotation says `-> float` | Annotation | ✅ Fixed |

**Actions:**
- ✅ Extracted `angleFromValue(value, preference)` helper; eliminates duplicated
  `if preference == "degrees": Angle(degrees=…) else: Angle(hours=…)` idiom.
- ✅ Merged `parseRaToAngleString` and `parseDecToAngleString` into
  `parseCoordToAngleString(value, coordType)` using `rf"..."` regex with interpolated `coordType`.
- ✅ Refactored `convertRaToAngle` and `convertDecToAngle` to use the unified parser helper.
- ✅ Replaced unused `frac` variable with `_` in `formatLatToText` and `formatLonToText`.
- ✅ Changed early `return 0` → `return 0.0` in `stringToDegree`.
- ✅ Simplified chained `elif/else` to early-return style.

---

### dome.py ⬜

| # | Issue | Type |
|---|-------|------|
| 1 | `shutterState` and `flapState` setters share identical clamping logic (`valueToInt` then check `not in [0,1,2,3]`, reset to 0) | Redundancy |
| 2 | `slewDome`: `commandString = setAzimuth` – the intermediate `commandString` variable is not needed since `setAzimuth` is the final value | Cleanup |
| 3 | Every command method creates `conn = Connection(self.parent)` locally – consistent with rest of module, but method bodies are very repetitive | Pattern (acceptable, see note) |

**Actions:**
- Extract `clampState(value, valid=(0,1,2,3))` helper method or inline a `valueToInt`-then-range
  guard into one line using `value if value in {0,1,2,3} else 0` pattern.
- Eliminate the redundant `commandString = setAzimuth` assignment in `slewDome`.

---

### firmware.py ⬜

| # | Issue | Type |
|---|-------|------|
| 1 | `parse` is called from `poll` which sends 6 commands (`:GVD#:GVN#:GVP#:GVT#:GVZ#:GCFG#`) yielding 6 chunks, but `parse` only assigns `response[0..4]` – `response[5]` (the GCFG reply) is silently discarded. The `numberOfChunks` check passes with 6, yet only 5 slots are assigned. | Bug |
| 2 | `isHW2024()` and `isHW2012()` are methods with no arguments (only `self`) that return a `bool` – they are more naturally expressed as `@property` | Pythonic |

**Actions:**
- Investigate whether `response[5]` (`:GCFG#` reply) should be parsed into a field. If intentionally
  discarded, add an explicit comment and check `len(response) >= 5` instead of `== numberOfChunks`.
  If it should be used, add the assignment.
- Convert `isHW2024()` and `isHW2012()` to `@property` so call sites read `firmware.isHW2024`
  instead of `firmware.isHW2024()`. Check all call sites and update them.

---

### geometry.py ⬜

| # | Issue | Type |
|---|-------|------|
| 1 | `transformRotX`, `transformRotY`, `transformRotZ` are three nearly identical static methods; they only differ in which axes the `tCos`/`tSin` values are placed in a 4×4 identity matrix | Redundancy |
| 2 | `calcTransformationMatrices` accesses `ha.degrees` – a private Skyfield attribute. `ha.degrees` (without underscore) should be used for the signed version or `ha.degrees` with `preference="degrees"` should be accessed via the public interface | Correctness |
| 3 | `initializeGeometry` unpacks the geometry dict key-by-key; could use dict unpacking | Pythonic |

**Actions:**
- Merge the three rotation static methods into one `transformRot(axis, angle)` where `axis` is
  `"x"`, `"y"`, or `"z"`, using a `match` statement to build the matrix. The three original
  names can remain as thin wrappers calling the unified helper.
- Replace `ha.degrees` with `ha.degrees` or the appropriate public accessor throughout the module
  (also applies to `mount.py`).
- Replace the five individual key-by-key dict assignments in `initializeGeometry` with
  `vars(self).update(self.geometryData[mountType])` or targeted unpacking.

---

### model.py ✅

| # | Issue | Type | Status |
|---|-------|------|--------|
| 1 | `addName`: `self._nameList.insert(len(self._nameList), value)` is equivalent to `self._nameList.append(value)` but is less readable and slower | Pythonic | ✅ Fixed |
| 2 | `parseNumberNames`: checks `len(response) != numberOfChunks` AND then `len(response) != 1` with identical log message "wrong number of chunks" – the second check is redundant | Redundancy | ✅ Fixed |
| 3 | `nameList` setter: uses a three-branch if/elif/else; simplifiable to one-liner | Pythonic | ✅ Fixed |
| 4 | `delStar`: guard `value < 0 or value > len(self._starList) - 1` can be written as `not (0 <= value < len(self._starList))` | Pythonic | ✅ Fixed |
| 5 | `programModelFromStarList`: `sgn` returned by `sexagesimalizeToInt` is unpacked three times but used only once (for `dec` sign); for `ra` and `raSolve` it is silently discarded | Cleanup | ✅ Fixed |
| 6 | `programModelFromStarList`: string formatting of sexagesimal coordinates is copy-pasted 4 times; could be extracted to a small helper | Redundancy | ✅ Fixed |

**Actions:**
- ✅ Replaced `insert(len(…), value)` with `append(value)` in `addName`.
- ✅ Rewrote `parseNumberNames` to check only `len(response) != 1`.
- ✅ Simplified `nameList` setter to one-liner with `isinstance`/`all` guard.
- ✅ Changed `delStar` guard to `if not (0 <= value < len(self._starList))`.
- ✅ Extracted `@staticmethod` helpers `formatSexagesimalRA`, `formatSexagesimalDec`,
  and `formatSexagesimalSidereal`; refactored `programModelFromStarList` to use them.

---

### modelStar.py ✅

| # | Issue | Type | Status |
|---|-------|------|--------|
| 1 | Imports `numpy` as `numpy` – project convention is `import numpy as np` | Convention | ✅ Fixed |
| 2 | `errorRA` and `errorDEC` methods are missing return type annotations | Annotation | ✅ Fixed |
| 3 | Mutable dataclass defaults for `coord`, `errorAngle`, `alt`, `az` – confirmed by user that Skyfield `Angle` objects are immutable, so `field(default_factory=...)` is not needed | Correctness | ✅ Confirmed safe |

**Actions:**
- ✅ Changed `import numpy` to `import numpy as np`; updated `numpy.sin/cos` → `np.sin/np.cos`.
- ✅ Added `-> Angle` return type annotations to `errorRA` and `errorDEC`.
- ✅ Confirmed Skyfield `Angle` immutability – no `field(default_factory=...)` needed.

---

### mountSignals.py ✅

No issues found. File is clean, well-structured, and concise.

---

### mount.py 🔄

| # | Issue | Type | Status |
|---|-------|------|--------|
| 1 | `workerProgTrajectory` is a method name in violation of the project naming convention: worker *methods* should be named `runner{Name}`, not `worker{Name}` (which is reserved for the Worker instance attribute) | Convention | ⬜ Pending |
| 2 | `collectData` and `resetAfterStart` access `self.obsSite.raJNow.degrees` – private Skyfield attribute | Correctness | ⬜ Omitted (per user request) |
| 3 | `cycleDome` is the only cycle method that does **not** use a mutex guard, while all other cycle methods (`cyclePointing`, `cycleSetting`, `cycleClock`) do | Bug | ⬜ Pending |
| 4 | `checkMountIsUp`: `client.shutdown(socket.SHUT_RDWR)` is called inside the `try` block (on the success path in the `else` branch of `connect`) without being guarded; if `shutdown` itself raises, `client.close()` in `finally` still runs (fine), but there is also a missing `client.close()` on the success path before `finally`. Actually reviewing: `finally: client.close()` does the close. But the success path calls `shutdown` and then `finally` calls `close` – this is correct actually. | OK | ✅ No action needed |
| 5 | `clearCyclePointing`: the `statusSlew` tracking logic can be simplified | Cleanup | ✅ Fixed |

**Actions:**
- ⬜ Rename `workerProgTrajectory` method to `runnerProgTrajectory` and update the `Worker(…)` call
  in `progTrajectory` accordingly.
- ⬜ Omitted (point 2, per user request): Replace `self.obsSite.raJNow.degrees` with the public
  accessor.
- ⬜ Add `mutexCycleDome` usage to `cycleDome` / `clearDome` (matching the pattern of the other
  cycle methods).
- ✅ Simplified `clearCyclePointing` slew-tracking block:
  ```python
  if not self.obsSite.statusSlew and self.statusSlew:
      self.settlingWait.start(settleWait)
  self.statusSlew = self.obsSite.statusSlew
  ```

---

### obsSite.py ⬜

| # | Issue | Type |
|---|-------|------|
| 1 | `setTargetAltAz` and `setTargetRaDec` are near-duplicate methods (identical boilerplate for response validation and target assignment); differ only in how they format the command string | Redundancy |
| 2 | `status` setter validates against a literal list `[0,1,2,…,98,99]` – should be a `frozenset` for O(1) lookup | Performance |
| 3 | `pollSyncClock`: `platform.system() == "Windows" or platform.system() == "Linux"` – should be `platform.system() in ("Windows", "Linux")` | Pythonic |
| 4 | `timeJD` getter: `if … return … else: return …` is the anti-pattern where `else` after `return` is unnecessary | Pythonic |
| 5 | `timeDiff` setter: the setter does nothing (just `return`) but it exists. A no-op setter is unusual; either remove the setter and document why direct assignment is forbidden, or replace it with `pass` and a comment | Clarity |
| 6 | `parseLocation`: sign inversion for longitude is done by two conditional string `.replace()` calls – fragile if both `+` and `-` are absent | Correctness/Clarity |
| 7 | `startSlewing`: builds `slewTypes` dict then mutates it by adding the `"keep"` entry; mutating a freshly created local dict is unnecessary complexity | Pythonic |
| 8 | `statusText`: `else: return text + " - settle" if self.statusSlew else text` – the `else` after `return` is unnecessary | Pythonic |
| 9 | Multiple `raJNow`, `decJNow`, `angularPosRA`, etc. setters all share the identical pattern: `if isinstance(value, Angle): self._x = value; return; self._x = valueToAngle/stringToAngle(value)` – significant boilerplate | Redundancy |

**Actions:**
- Extract `parseSetTargetResponse(response)` helper to share validation/assignment logic between
  `setTargetAltAz` and `setTargetRaDec`.
- Change `_STATUS_VALID = frozenset({0,1,2,3,4,5,6,7,8,9,10,11,98,99})` class attribute and use
  it in the `status` setter.
- Simplify platform check to `platform.system() in ("Windows", "Linux")`.
- Remove the `else` in `timeJD` getter.
- Add a comment to the no-op `timeDiff` setter explaining why it exists (or delete it and make
  the attribute read-only via other means).
- Rewrite `parseLocation` longitude sign-flip using numeric arithmetic or a clear ternary:
  `lon = response[1].replace("-", "+") if "-" in response[1] else response[1].replace("+", "-")`
  (already this way – but add a comment explaining the LX200 protocol inversion).
- In `startSlewing`, compute `keepSlewType` inline rather than post-mutating the dict.
- Remove unnecessary `else` after `return` in `statusText`.
- Consider defining a helper `setAngleAttr(value, preference)` to reduce the repetitive
  `isinstance(value, Angle)` setter guard (optional – low priority, many usages).

---

### progStar.py ⬜

| # | Issue | Type |
|---|-------|------|
| 1 | `@dataclass` declares both `pierside: str` (positional field) AND `_pierside: str = "E"` (also a dataclass field) AND a `@property` named `pierside` – this triple definition is a known dataclass anti-pattern. The `__init__` generated by `@dataclass` will conflict with the property descriptor. | Bug |
| 2 | `log = logging.getLogger("MW4")` inside `@dataclass` becomes a dataclass field descriptor, not a class attribute, causing unexpected behaviour | Bug |
| 3 | `pierside` property getter and setter are missing type annotations | Annotation |

**Actions:**
- Refactor `ProgStar` to a regular class (not `@dataclass`) or use `@dataclass` correctly with
  `field(init=False)` and `__post_init__`, explicitly excluding the property from dataclass field
  collection.
- Move `log` out of the dataclass body using `ClassVar[logging.Logger]`:
  ```python
  from typing import ClassVar
  log: ClassVar[logging.Logger] = logging.getLogger("MW4")
  ```
- Add return type `-> str` to the `pierside` getter.
- Add `-> None` to `pierside` setter and add `: str` to the parameter.

---

### satellite.py ⬜

| # | Issue | Type |
|---|-------|------|
| 1 | `__init__` is missing type annotation for `parent` parameter | Annotation |
| 2 | `parseCalcTLE`: checks `len(response) != numberOfChunks` then immediately checks `len(response) != 3` with the same "wrong number of chunks" message – the second check is redundant when the command always returns exactly 3 chunks | Redundancy |
| 3 | `parseStatTLE`: same double-check pattern – checks `!= numberOfChunks` and then `!= 1` | Redundancy |
| 4 | `addTrajectoryPoint`: `return all(response[i] != "E" for i in range(0, len(az)))` can be simplified to `all(r != "E" for r in response)` | Pythonic |
| 5 | `setTrackingOffsets`: the for/else loop `for res in response: if res == "E": break else: return True; return False` should be `return all(res != "E" for res in response)` | Pythonic |
| 6 | `setTrackingFirst`, `setTrackingSecond`, `setTrackingFirstCorr`, `setTrackingTime`, `addTrackingFirst`, `addTrackingSecond`, `addTrackingFirstCorr`, `addTrackingTime` – 8 single-expression methods using `:TROFFSET{N}` or `:TROFFADD{N}`, all trivially identical in structure | Redundancy |

**Actions:**
- Add `parent: Any` type annotation to `__init__`.
- In `parseCalcTLE` and `parseStatTLE`, keep only the most specific length check (`!= 3` / `!= 1`)
  since those values fully imply the `numberOfChunks` check.
- Simplify `addTrajectoryPoint` response check with `all(r != "E" for r in response)`.
- Simplify `setTrackingOffsets` for/else to `return all(res != "E" for res in response)`.
- Merge the 8 tracking-offset methods into two parameterised methods:
  `setTrackingOffset(index, value)` and `addTrackingOffset(index, value)`, with the public API
  preserved via thin wrappers or by updating call sites to use the parameterised form.

---

### setting.py ⬜

| # | Issue | Type |
|---|-------|------|
| 1 | `parseSetting` calls `response[17].split(",")` twice (also once for `[1]` and once for `[0]`) – the result should be stored in a local variable | Cleanup |
| 2 | `checkRateLunar/Sidereal/Solar` compare floats by formatting to a fixed-width string – fragile and non-idiomatic | Pythonic |
| 3 | `setSlewSpeedMax` and `setSlewSpeedHigh` are clean, but `setSlewSpeedMed` and `setSlewSpeedLow` store the command parameter in an unnecessary intermediate variable (`centerSpeed`) | Cleanup |
| 4 | In `parseSetting`, `addressWirelessMAC` (`response[13]`) is never assigned when firmware >= 3.2.5 (the GPS sync field moves from index 13 to index 26) – it is silently skipped | Correctness |

**Actions:**
- Store `response[17].split(",")` in a local variable `w17 = response[17].split(",")` and use it.
- Replace string-formatting float comparison in `checkRateLunar/Sidereal/Solar` with a small
  tolerance comparison: `abs(self.trackingRate - 62.4) < 0.1` etc.
- Remove intermediate `centerSpeed` variable in `setSlewSpeedMed` and `setSlewSpeedLow`.
- Review `addressWirelessMAC` assignment in `parseSetting` to confirm whether `response[13]`
  is correctly the MAC in both firmware versions and add explicit assignment or comment.

---

### tleParams.py / trajectoryParams.py ⬜

| # | Issue | Type |
|---|-------|------|
| 1 | Both files contain identical `jdStart` and `jdEnd` property implementations (getter returns `ts.now()` if None, setter converts to TT JD) – pure code duplication | Redundancy |
| 2 | `_jdStart` and `_jdEnd` are declared as dataclass fields with default `None`; they will appear in `__init__` as optional keyword arguments of the dataclass. This is undesirable – these are implementation details | Design |

**Actions:**
- Create a new file `jdMixin.py` (or `timeParams.py`) in `mountcontrol/` containing a
  `JdParamsMixin` dataclass mixin with the `jdStart` and `jdEnd` properties and the private
  `_jdStart`/`_jdEnd` fields declared as `field(default=None, init=False, repr=False)`.
- Inherit `TLEParams(JdParamsMixin)` and `TrajectoryParams(JdParamsMixin)` from the mixin.
- Mark `_jdStart`/`_jdEnd` with `field(default=None, init=False, repr=False)` to exclude them
  from the generated `__init__`.

---

## Cross-Cutting Issues

| # | Issue | Applies to | Status |
|---|-------|-----------|--------|
| A | `ha.degrees` private Skyfield attribute accessed – use `ha.degrees` | `mount.py`, `geometry.py` | ⬜ Pending (mount.py omitted per user; geometry.py pending) |
| B | `import numpy` vs `import numpy as np` inconsistency | `modelStar.py` | ✅ Fixed |
| C | Pattern `conn = Connection(self.parent)` repeated in every method body of every class – this is the design (one TCP connection per command), and it is acceptable as-is | All data classes | ✅ Accepted |
| D | Naming convention: `worker{X}` attribute vs `runner{X}` method | `mount.py` | ⬜ Pending |

---

## Execution Order

The changes described above should be implemented **file by file** in the following order to make
each step self-contained and testable:

1. ✅ **connection.py** – pre-sorted lists, duplicate removal
2. ✅ **convert.py** – standalone utility, no dependencies on other changed files
3. ✅ **modelStar.py** – standalone dataclass
4. ✅ **model.py** – addName, nameList setter, programModelFromStarList helpers
5. 🔄 **mount.py** – rename runner, add dome mutex (item 5 done; items 1 & 3 pending)
6. ⬜ **firmware.py** – property conversions
7. ⬜ **dome.py** – minor cleanup
8. ⬜ **setting.py** – parse cleanup
9. ⬜ **satellite.py** – annotation + redundancy removal + tracking-offset refactor
10. ⬜ **geometry.py** – private attribute access, rotation method refactor
11. ⬜ **obsSite.py** – largest set of changes; requires no upstream changes
12. ⬜ **progStar.py** – standalone dataclass fix
13. ⬜ **tleParams.py + trajectoryParams.py** → create `jdMixin.py` first, then replace duplication

After all changes: run `pytest` for 100 % coverage and `ruff check --fix` + `ruff format`.

