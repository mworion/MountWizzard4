# Photometry Architecture Refactor Plan

## Goal

Complete the core/adapter split that was started for source detection. Move the
remaining **pure analysis math** out of the Qt adapter (`photometry.py`) **and
out of the tilt display methods in `imageTabs.py`** into the pure numeric layer,
so that HFR maps, tilt values, roundness maps, background maps and tilt metrics
become independently testable and reusable without Qt. The Qt adapter is reduced
to orchestration + state storage + signal emission; the GUI methods are reduced
to drawing + label text.

External interfaces consumed by `imageTabs.py` stay unchanged (same attribute
names, same signals), so no GUI rendering code needs to change.

## Current situation

- `photometry_core.py` — pure: `Background`, `Sources`, `ExtractCounts`,
  `estimateBackground`, `extractSources`. Only covers background + extraction.
- `photometry.py` — Qt adapter that **also** performs all derived-analysis
  math (`baseCalcs`, `runnerGetHFR`, `runnerCalcTiltValuesSquare`,
  `runnerCalcTiltValuesTriangle`, `runnerGetRoundness`,
  `calcAberrationInspectView`, `calcBackground`, `calcBackgroundRMS`) and emits
  the Qt signals in the same methods (compute-and-emit coupling).
- `imageTabs.py` — reads ~25 flat attributes and renders.

## Problems addressed

1. Pure analysis math is trapped inside a `QObject`; cannot be tested/reused
   headless.
2. Each `runnerX` computes and emits in one step (math welded to Qt).
3. `signals.aberration` drives two slots (`showAberrationInspect` and
   `showImageSources`); sources rendering piggybacks on the aberration signal.
4. `SEP` / `sepThreshold` and core docstrings still reference the removed
   `sep` library.

## Design

### New pure module: `../../src/mw4/logic/photometry/photometry_analysis.py`

No Qt imports. Pure functions operating on flat arrays + image + background,
returning dataclasses. All math is moved verbatim (same formulas) from the
adapter; only the `self.signals.*.emit()` calls are dropped.

Dataclasses:

```
@dataclass
class GridGeometry:          # from baseCalcs
    h: int
    w: int
    filterConstW: int
    filterConstH: int
    xm: np.ndarray
    ym: np.ndarray

@dataclass
class HFRResult:
    grid: np.ndarray
    hfrMin: float
    hfrMax: float
    percentile: float
    median: float
    inner: float
    outer: float

@dataclass
class TiltSquareResult:
    segHFR: np.ndarray       # (3,3)

@dataclass
class TiltTriangleResult:
    segHFR: np.ndarray       # concatenated (72,)

@dataclass
class RoundnessResult:
    grid: np.ndarray
    roundnessMin: float
    roundnessMax: float
    percentile: float

@dataclass
class BackgroundResult:
    background: np.ndarray
    backgroundMin: float
    backgroundMax: float

@dataclass
class BackgroundRMSResult:
    backgroundRMS: np.ndarray
```

Pure functions (signatures illustrative, all return the dataclasses above):

```
def computeGridGeometry(image, filterScale) -> GridGeometry
def computeHFR(geom, xCoord, yCoord, hfr) -> HFRResult
def computeTiltSquare(geom, xCoord, yCoord, hfr) -> TiltSquareResult
def computeTiltTriangle(geom, xCoord, yCoord, hfr) -> TiltTriangleResult
def computeRoundness(geom, xCoord, yCoord, elongation) -> RoundnessResult
def computeAberrationImage(image, aberrationSize) -> np.ndarray
def computeBackground(geom, backSignal, globalback) -> BackgroundResult
def computeBackgroundRMS(geom, backRMS) -> BackgroundRMSResult
```

Note: `baseCalcs` currently computes both grid geometry (xm/ym/filterConsts)
and HFR inner/outer/percentile/median. These are split: geometry →
`computeGridGeometry`; the HFR scalars fold into `computeHFR` (it already has
the needed inputs). This keeps each function single-purpose.

### Adapter: `photometry.py`

Keeps all public attributes and all 8 signals exactly as today. Each `runnerX`
method becomes a thin wrapper: call the pure function, unpack the dataclass into
the existing `self.*` attributes, then emit the corresponding signal. Example:

```
def runnerGetHFR(self) -> None:
    res = computeHFR(self.geom, self.xCoord, self.yCoord, self.hfr)
    self.hfrGrid = res.grid
    self.hfrMin = res.hfrMin
    self.hfrMax = res.hfrMax
    self.hfrPercentile = res.percentile
    self.hfrMedian = res.median
    self.hfrInner = res.inner
    self.hfrOuter = res.outer
    self.signals.hfr.emit()
```

`runCalcs` orchestrates as today (compute geometry once, then call each runner
in sequence). The `self.h/self.w/self.xm/self.ym/self.filterConstW/H` attributes
remain populated (from `GridGeometry`) because `imageTabs` reads `w`/`h`.

`baseCalcs` is replaced by a single call storing `self.geom = computeGridGeometry(...)`
plus assigning `self.h/self.w/...` from it and folding the HFR scalars into
`runnerGetHFR`.

### Signal cleanup (item 4, INCLUDED)

Add a dedicated `sources = Signal()` and connect `showImageSources` to it in
`imageTabs.__init__`, emitted right after extraction. `aberration` is bound only
to `showAberrationInspect`.

### Naming cleanup (item 5, INCLUDED)

Rename `SEP` → `THRESHOLD_FACTORS` and `sepThreshold` → `thresholdFactor` in the
adapter and its tests. Also drop the residual "sep" mentions in the
`photometry_core.py` `Background`/`Sources` docstrings.

### Pure calculations moved out of `imageTabs.py` (added scope)

The two tilt display methods currently interleave pure numeric work with
pyqtgraph drawing. The numeric parts move into `photometry_analysis.py` as pure
functions returning dataclasses; the pyqtgraph item creation (lines, ellipses,
text) stays in `imageTabs.py` and consumes the returned values.

`showTiltSquare` — extract:
- `corners` (from `segHFR`) and `vectors` (geometry constants)
- `best`/`worst` = min/max(corners)
- `points` = `vector * corner / worst + centre`
- `tiltDiff`, `tiltPercent`
- `offAxisDiff` (= `hfrOuter - segHFR[1][1]`), `offAxisPercent`
→ `TiltSquareView(points, best, worst, tiltDiff, tiltPercent, offAxisDiff, offAxisPercent)`

`showTiltTriangle` — extract:
- `segData` (means of `segHFR` slices, indexed by `offsetTiltAngle`)
- `vectors`/`points` geometry
- `best`/`worst`, `tiltDiff`, `tiltPercent`
- `offAxisDiff` (= `hfrOuter - hfrInner`), `offAxisPercent`
→ `TiltTriangleView(segData, points, best, worst, tiltDiff, tiltPercent, offAxisDiff, offAxisPercent)`

Shared pure helper:
- `def tiltHint(tiltPercent, tiltTable) -> str` — maps a tilt percentage to its
  label (the `for tiltHint in self.TILT` selection loop), returning the chosen
  key. GUI keeps the f-string formatting and `setText` calls.

Trade-off / boundary: the per-segment **drawing** geometry (ring radii, line
endpoints at `r25..r`, text anchor positions at `r62`, the `angleSep`/
`angleText` trig) stays in `imageTabs.py`, because it exists only to place Qt
items. Only the values that feed the *reported metrics* and the *tilt vector
polygon* (`points`) are extracted. This means a small amount of angle trig is
computed in both places (GUI for drawing, pure fn for `points`); accepted to
keep a clean Qt/no-Qt boundary. `links` (which points to connect) are drawing
constants and stay in the GUI.

After extraction, `showTiltSquare`/`showTiltTriangle` call the pure function
once, then only build pyqtgraph items and set label text from the returned
dataclass.

## Files changed

- **new** `../../src/mw4/logic/photometry/photometry_analysis.py` — pure functions +
  dataclasses (math moved from adapter **and** from the imageTabs tilt methods).
- **modify** `../../src/mw4/logic/photometry/photometry.py` — runners become thin
  wrappers; import from `photometry_analysis`; `baseCalcs` replaced by geometry
  call.
- **modify** `../../src/mw4/gui/extWindows/image/imageTabs.py` — tilt methods reduced
  to drawing + label text using `TiltSquareView`/`TiltTriangleView`/`tiltHint`;
  plus the sources signal split if approved.
- **new** `../../tests/unit_tests/logic/photometry/test_photometry_analysis.py` —
  direct pure-function tests (no Qt fixture needed), including the tilt-view and
  `tiltHint` functions.
- **modify** `../../tests/unit_tests/logic/photometry/test_photometry.py` — adapter
  tests now patch/verify the analysis functions and signal emission.
- **modify** `../../tests/unit_tests/gui/extWindows/image/test_imageTabs.py` — tilt
  tests updated for the new drawing-only methods; sources signal split if
  approved.

## Verification

- 100% coverage on `photometry.py`, `photometry_core.py`,
  `photometry_analysis.py`.
- Full image GUI test suite green.
- `uv run ruff check` / `format` clean.
- Behavioural equivalence: same attribute values produced for a given image
  (spot-check against current output on `../../tests/testData/m51.fit`).

## Out of scope (not in this pass)

- Grouping the ~25 `imageTabs` attributes into result objects exposed on the
  adapter (would require rewriting many `imageTabs` reads). Can be a follow-up.
- Any change to the numeric algorithms or photutils tuning.
- Performance changes.
