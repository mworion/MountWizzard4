# Refactoring Summary: Convenience Properties for Device Registry

## Overview
Replaced all verbose usages of `dReg["mount"].instance.<property>` with the shorter convenience properties defined in `deviceRegistry.py`.

## Changes Made

### Properties Refactored
1. **`.obsSite`** - Convenience property for `instance.obsSite`
   - 91 occurrences replaced across the codebase
   - Files affected: GUI modules, logic modules

2. **`.setting`** - Convenience property for `instance.setting`
   - 23 occurrences replaced across the codebase

3. **`.location`** - Convenience property for `instance.obsSite.location`
   - Automatically covered by `.obsSite` replacements

4. **`.timeJD`** - Convenience property for `instance.obsSite.timeJD`
   - Automatically covered by `.obsSite` replacements

## Files Modified

### Logic Layer (src/mw4/logic/)
- buildData/buildpoints.py
- buildData/hipparcos.py
- modelBuild/modelRun.py
- dome/dome.py
- plateSolve/plateSolve.py
- databaseProcessing/dataWriter.py
- measure/measure.py
- environment/seeingWeather.py

### GUI Layer (src/mw4/gui/)
- mainWaddon/tabMount.py
- mainWaddon/tabMount_Move.py
- mainWaddon/tabMount_Sett.py
- mainWaddon/tabModel.py
- mainWaddon/tabModel_BuildPoints.py
- mainWaddon/tabModel_Manage.py
- mainWaddon/tabSat_Track.py
- mainWaddon/tabAlmanac.py
- mainWaddon/tabEnviron_Seeing.py
- mainWaddon/astroObjects.py
- mainWaddon/slewInterface.py
- extWindows/satelliteMapW.py
- extWindows/image/imageW.py
- extWindows/simulator/buildPoints.py
- extWindows/simulator/telescope.py
- extWindows/bigPopupW.py
- extWindows/satelliteHorW.py
- extWindows/hemisphere/hemisphereW.py
- extWindows/hemisphere/horizonDraw.py
- extWindows/hemisphere/hemisphereDraw.py

## Example Transformations

```python
# Before
self.app.dReg["mount"].instance.obsSite.timeJD
self.app.dReg["mount"].instance.obsSite.location.latitude.degrees
self.app.dReg["mount"].instance.setting.horizonLimitHigh
self.app.dReg["mount"].instance.obsSite.stopMoveAll()
self.app.dReg["mount"].instance.obsSite.moveNorth()

# After
self.app.dReg["mount"].timeJD
self.app.dReg["mount"].location.latitude.degrees
self.app.dReg["mount"].setting.horizonLimitHigh
self.app.dReg["mount"].obsSite.stopMoveAll()
self.app.dReg["mount"].obsSite.moveNorth()
```

## Important Notes
- Methods on the instance (e.g., `instance.startMountTimers()`, `instance.stopAllMountTimers()`) were correctly left unchanged as they are not convenience properties
- The 3 remaining `.instance.obsSite` references are in the property definitions within `deviceRegistry.py` itself, which is correct

## Verification Results
- ✅ All syntax checks passed (Python files compile without errors)
- ✅ 91 occurrences of `.obsSite` convenience property now used
- ✅ 23 occurrences of `.setting` convenience property now used
- ✅ 0 remaining `.instance.setting` references outside of definitions
- ✅ 3 remaining `.instance.obsSite` references are in property definitions (expected and correct)

