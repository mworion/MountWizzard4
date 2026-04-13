# Plan: Add Missing Type Annotations to `src/mw4/mountcontrol`

**Date:** 2026-04-12  
**Scope:** All Python source files under `src/mw4/mountcontrol/`  
**Goal:** Add or correct type annotations for all functions, methods (including `__init__`, properties, and setters) per SKILL.md rule 14 (Python 3.11 style).

---

## Summary of Files and Issues

### 1. `connection.py`
| Method | Issue |
|--------|-------|
| `__init__(self, host=None)` | `host` param untyped; return type `-> None` missing |
| `validCommand(self, command)` | param `command: str` missing; return `-> bool` missing |
| `validCommandSet(self, commandString)` | param `commandString: str` missing; return `-> bool` missing |
| `analyseCommand(self, commandString)` | param `commandString: str` missing; return type missing (has it annotated but wrong – `commandString` is unannotated) |
| `closeClientHard(self, client)` | param `client: socket.socket \| None` missing; return `-> None` missing |
| `buildClient(self)` | return `-> socket.socket \| None` missing |

### 2. `convert.py`
| Function | Issue |
|----------|-------|
| `formatLatLonToAngle(value, pf)` | return type says `-> float` but actually returns `Angle` |
| `convertLatToAngle(value)` | return type says `-> float` but actually returns `Angle` |
| `convertLonToAngle(value)` | return type says `-> float` but actually returns `Angle` |
| `parseRaToAngleString(value)` | return `list[str]` is wrong in the `else` branch which returns `""` → fix to `list[str] \| str` |
| `parseDecToAngleString(value)` | same issue as `parseRaToAngleString` |

### 3. `dome.py`
| Method | Issue |
|--------|-------|
| `__init__(self, parent)` | `parent` param untyped (use `Any`); return `-> None` missing |
| property `shutterState` getter | return `-> int` missing |
| property `shutterState` setter | param untyped; return `-> None` missing |
| property `flapState` getter | return `-> int` missing |
| property `flapState` setter | param untyped; return `-> None` missing |
| property `slew` getter | return `-> bool` missing |
| property `slew` setter | param untyped; return `-> None` missing |
| property `azimuth` getter | return `-> float` missing |
| property `azimuth` setter | param untyped; return `-> None` missing |

### 4. `firmware.py`
| Method | Issue |
|--------|-------|
| `__init__(self, parent)` | `parent` param untyped (use `Any`); return `-> None` missing |
| property `vString` getter | return `-> Version` missing |
| property `vString` setter | param typed already; return `-> None` missing |

### 5. `geometry.py`
| Method | Issue |
|--------|-------|
| `__init__(self, parent)` | `parent` param untyped (use `Any`); return `-> None` missing |
| All property getters | return types missing (`-> float`) |
| All property setters | param untyped; return `-> None` missing |
| `initializeGeometry(self, mountType)` | `mountType: str` missing; return `-> bool` missing |
| `calcTransformationMatrices(...)` | `pierside="W"` missing `str` annotation; `-> tuple` too vague |

### 6. `model.py`
| Method | Issue |
|--------|-------|
| `__init__(self, parent)` | `parent` param untyped (use `Any`); return `-> None` missing |
| property `starList` getter/setter | return/param types missing |
| property `numberStars` getter | return `-> int` missing |
| property `numberStars` setter | param untyped; return `-> None` missing |
| property `nameList` getter | return `-> list` missing |
| property `nameList` setter | param untyped; return `-> None` missing |
| property `numberNames` getter | return `-> int` missing |
| property `numberNames` setter | param untyped; return `-> None` missing |
| `delStar(self, value: int)` | return `-> None` missing |
| `checkStarListOK(self)` | return `-> bool` missing |

### 7. `modelStar.py`
| Method | Issue |
|--------|-------|
| `errorRA(self)` | return `-> Angle` missing |
| `errorDEC(self)` | return `-> Angle` missing |

### 8. `mount.py`
| Method | Issue |
|--------|-------|
| `__init__(self, app, host, MAC, pathToData, verbose)` | all params untyped; return `-> None` missing |
| property `MAC` getter | return `-> str \| None` missing |
| property `MAC` setter | param untyped; return `-> None` missing |
| property `waitTimeFlip` getter | return `-> float` missing |
| property `waitTimeFlip` setter | param untyped; return `-> None` missing |
| `resetAfterStart(self)` | return `-> None` missing |
| `collectData(self)` | return `-> None` missing |
| `waitAfterSettlingAndEmit(self)` | return `-> None` missing |
| `startMountTimers(self)` | return `-> None` missing |
| `stopAllMountTimers(self)` | return `-> None` missing |
| `startDomeTimer(self)` | return `-> None` missing |
| `stopDomeTimer(self)` | return `-> None` missing |
| `startMountClockTimer(self)` | return `-> None` missing |
| `stopMountClockTimer(self)` | return `-> None` missing |
| `checkMountIsUp(self)` | return `-> None` missing |
| `clearCycleCheckMountIsUp(self)` | return `-> None` missing |
| `cycleCheckMountIsUp(self)` | return `-> None` missing |
| `cyclePointing(self)` | return `-> None` missing |
| `clearCycleSetting(self, result)` | `result` untyped; return `-> None` missing |
| `cycleSetting(self)` | return `-> None` missing |
| `clearGetModel(self)` | return `-> None` missing |
| `getModel(self)` | return `-> None` missing |
| `clearGetNames(self)` | return `-> None` missing |
| `getNames(self)` | return `-> None` missing |
| `clearGetFW(self)` | return `-> None` missing |
| `getFW(self)` | return `-> None` missing |
| `clearGetLocation(self)` | return `-> None` missing |
| `getLocation(self)` | return `-> None` missing |
| `clearCalcTLE(self)` | return `-> None` missing |
| `clearStatTLE(self)` | return `-> None` missing |
| `statTLE(self)` | return `-> None` missing |
| `clearGetTLE(self)` | return `-> None` missing |
| `getTLE(self)` | return `-> None` missing |
| `bootMount(self, bAddress="", bPort=0)` | params untyped; return `-> bool` missing |
| `shutdown(self)` | return `-> bool` missing |
| `clearDome(self, result)` | `result` untyped; return `-> None` missing |
| `cycleDome(self)` | return `-> None` missing |
| `clearCycleClock(self)` | return `-> None` missing |
| `cycleClock(self)` | return `-> None` missing |
| `clearProgTrajectory(self)` | return `-> None` missing |
| `workerProgTrajectory(self, alt, az, replay=False)` | params untyped; return `-> bool` missing |
| `progTrajectory(self, start, alt, az, replay=False)` | params untyped; return `-> None` missing |
| `calcTransformationMatricesTarget(self)` | return type missing |
| `calcTransformationMatricesActual(self)` | return type missing |
| `calcMountAltAzToDomeAltAz(self, alt, az)` | params untyped; return type missing |

### 9. `obsSite.py`
| Method | Issue |
|--------|-------|
| `__init__(self, parent, verbose=False)` | params untyped; return `-> None` missing |
| All property getters (location, timeJD, timeDiff, ut1_utc, timeSidereal, raJNow, raJNowTarget, haJNow, haJNowTarget, decJNow, decJNowTarget, angularPosRA, angularPosDEC, errorAngularPosRA, errorAngularPosDEC, angularPosRATarget, angularPosDECTarget, pierside, piersideTarget, Alt, AltTarget, Az, AzTarget, status, statusSat, statusSlew) | return types missing |
| All property setters | param types and return `-> None` missing |
| `statusText(self)` | return `-> str` missing |
| `statusSatText(self)` | return `-> str` missing |
| `startSlewing(self, slewType: str = "normal")` | return `-> bool` missing |
| `stopMoveEast(self)` | return `-> bool` missing |

### 10. `setting.py`
| Method | Issue |
|--------|-------|
| `__init__(self, parent)` | `parent` param untyped (use `Any`); return `-> None` missing |
| All property getters | return types missing |
| All property setters | param types and return `-> None` missing |
| `timeToMeridian(self)` | return `-> int` missing |
| `setWOL(self, status)` | `status: bool` missing; return `-> bool` missing |

### 11. `tleParams.py`
| Method | Issue |
|--------|-------|
| `_jdStart: object = None` | should be `Time \| None = None` |
| `_jdEnd: object = None` | should be `Time \| None = None` |
| property `jdStart` getter | return `-> Time` missing |
| property `jdStart` setter | param `value: float` missing; return `-> None` missing |
| property `jdEnd` getter | return `-> Time` missing |
| property `jdEnd` setter | param `value: float` missing; return `-> None` missing |

### 12. `trajectoryParams.py`
| Method | Issue |
|--------|-------|
| `_jdStart: object = None` | should be `Time \| None = None` |
| `_jdEnd: object = None` | should be `Time \| None = None` |
| property `jdStart` getter | return `-> Time` missing |
| property `jdStart` setter | param `value: float` missing; return `-> None` missing |
| property `jdEnd` getter | return `-> Time` missing |
| property `jdEnd` setter | param `value: float` missing; return `-> None` missing |

---

## Implementation Order
1. `convert.py` – fix wrong return types, simplest changes
2. `modelStar.py` – tiny dataclass, add return types
3. `tleParams.py` – fix field types and property annotations
4. `trajectoryParams.py` – same pattern as tleParams
5. `connection.py` – add missing param/return types
6. `firmware.py` – `__init__` + property types
7. `dome.py` – `__init__` + all property types
8. `setting.py` – `__init__`, property types, `setWOL`, `timeToMeridian`
9. `geometry.py` – `__init__`, properties, `initializeGeometry`, `calcTransformationMatrices`
10. `model.py` – `__init__`, properties, `delStar`, `checkStarListOK`
11. `obsSite.py` – `__init__`, all properties, `statusText`, `statusSatText`, `startSlewing`, `stopMoveEast`
12. `mount.py` – largest file, `__init__`, properties, all methods

## Post-Implementation
- Run `ruff check --fix` and `ruff format` on the package
- Run the full unit test suite for `tests/unit_tests/` targeting `mountcontrol`

