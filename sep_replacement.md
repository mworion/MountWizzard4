# Plan: Replacing `sep` with `photutils`

## 1. Goal

Replace the `sep` (Source Extraction and Photometry, SEP) library with the
Astropy-affiliated `photutils` library in the photometry logic, while keeping
the existing feature set (background estimation, source extraction, ellipse
parameters, Kron flux, half-flux radius / HFR, roundness, tilt and background
visualisation) as close to identical as possible.

## 2. Scope

`sep` is used in exactly one production module:

- `src/mw4/logic/photometry/photometry.py`

and referenced in one test module:

- `tests/unit_tests/logic/photometry/test_photometry.py`

and declared as a dependency in:

- `pyproject.toml` (`"sep==1.4.1"`)

No other production code imports `sep`. This makes the replacement local and
well contained.

## 3. Current `sep` usage (API inventory)

All calls live in `runnerCalcPhotometry()`, plus a few attribute accesses in
`calcBackground()`.

| # | `sep` call / attribute | Purpose | Result used as |
|---|------------------------|---------|----------------|
| 1 | `sep.Background(image, bw=32, bh=32)` | 2D background model | `self.bkg` |
| 2 | `image - self.bkg` | background subtraction (operator overload) | `image_sub` |
| 3 | `bkg.rms()` | 2D background RMS map | `self.backRMS` |
| 4 | `bkg.back()` | 2D background map | `self.backSignal` |
| 5 | `bkg.globalback` | scalar median background | normalisation in `calcBackground()` |
| 6 | `bkg.globalrms` | scalar median RMS | only in commented-out SN variant |
| 7 | `sep.extract(image_sub, thr, err=backRMS, filter_kernel=None, minarea=7)` | source detection/segmentation | `objs` (fields `x, y, a, b, theta`) |
| 8 | `sep.kron_radius(...)` | Kron radius per source | `kronRad`, `krFlag` |
| 9 | `sep.sum_ellipse(...)` | elliptical aperture flux (FLUX_AUTO) | `flux`, `fluxErr`, `flag` |
| 10 | `sep.sum_circle(...)` | circular aperture flux (small-source fallback) | `cFlux`, ... |
| 11 | `sep.flux_radius(..., [0.5, 1.0], normflux=flux)` | flux-fraction radii | `radius[:,0]` (HFR), `radius[:,1]` (SN) |

Downstream, the module only relies on `self.objs` being indexable by the field
names `x`, `y`, `a`, `b`, `theta` and on `self.hfr` being a 1-D array of
half-flux radii. Keeping that contract intact means the many `runner*` /
`calc*` methods need **no** changes.

## 4. Target `photutils` mapping (v3.0.0)

`photutils==3.0.0` requires `numpy>=2.0`, `scipy>=1.13`, `astropy>=6.1.4` — all
satisfied by the current pins (numpy 2.5.3, scipy 1.18.1, astropy 8.0.1). No
dependency conflicts expected.

| `sep` feature | `photutils` replacement |
|---------------|-------------------------|
| `sep.Background(bw, bh)` | `photutils.background.Background2D(data, box_size=(32, 32), bkg_estimator=SExtractorBackground(), bkgrms_estimator=StdBackgroundRMS())` |
| `bkg.back()` | `bkg.background` (2D `ndarray`) |
| `bkg.rms()` | `bkg.background_rms` (2D `ndarray`) |
| `bkg.globalback` | `bkg.background_median` |
| `bkg.globalrms` | `bkg.background_rms_median` |
| `image - bkg` | `image - bkg.background` |
| `sep.extract(err=rms, thr, minarea=7)` | `threshold = thr * bkg.background_rms`; `segm = detect_sources(image_sub, threshold, npixels=7)`; optionally `deblend_sources(...)`; then `cat = SourceCatalog(image_sub, segm, background=bkg.background, error=rms)` |
| `objs['x'] / ['y']` | `cat.xcentroid` / `cat.ycentroid` |
| `objs['a'] / ['b']` | `cat.semimajor_sigma.value` / `cat.semiminor_sigma.value` |
| `objs['theta']` | `cat.orientation.to(u.rad).value` |
| `sep.kron_radius` + `sep.sum_ellipse` (FLUX_AUTO) | `cat.kron_radius`, `cat.kron_flux`, `cat.kron_fluxerr` (built-in FLUX_AUTO equivalent, already includes the min-radius circular fallback logic) |
| `sep.sum_circle` fallback | handled internally by `kron_flux`; or `CircularAperture` + `aperture_photometry` if explicit control is needed |
| `sep.flux_radius(0.5)` (HFR) | `cat.fluxfrac_radius(0.5).value` |
| `sep.flux_radius(1.0)` (SN denominator) | `cat.fluxfrac_radius(0.9).value` (see deficit note) or Kron aperture radius |

### Proposed rewrite of `runnerCalcPhotometry()`

1. `bkg = Background2D(self.image, box_size=(32, 32), ...)`
2. `image_sub = self.image - bkg.background`
3. `self.backRMS = bkg.background_rms`; `self.backSignal = bkg.background`
4. Store a lightweight object exposing `.background`, `.background_rms`,
   `.globalback` so `calcBackground()` keeps working — **or** update
   `calcBackground()` to use `bkg.background_median` (preferred, cleaner).
5. `threshold = self.sepThreshold * bkg.background_rms`
6. `segm = detect_sources(image_sub, threshold, npixels=7)`; guard `segm is None`.
7. `cat = SourceCatalog(image_sub, segm, error=bkg.background_rms)`
8. Build a NumPy structured array `objs` with fields `x, y, a, b, theta`
   from the catalog columns so the existing downstream contract is preserved.
9. Compute `flux = cat.kron_flux`, `hfr = cat.fluxfrac_radius(0.5)`.
10. Apply the same masks (`r` between 0.8 and 15, S/N threshold, HFR < 10).
11. Keep the `try/except` guard around detection, returning empty arrays on
    failure (as today).

The eight `runner*` / `calc*` helper methods stay unchanged because they only
read `self.objs['x'|'y'|'a'|'b'|'theta']` and `self.hfr`.

## 5. Feature-parity assessment

### Fully covered
- 2D background map, RMS map, global/median background — `Background2D`.
- Background subtraction.
- Source detection with a minimum pixel area (`npixels` == `minarea`).
- Per-source centroids, ellipse axes and orientation.
- Kron (FLUX_AUTO) photometry — `kron_flux`/`kron_radius` are the direct
  equivalent and even encapsulate the circular-aperture fallback that the
  current code implements manually.
- Half-flux radius (HFR) — `fluxfrac_radius(0.5)`.
- All roundness / tilt / aberration / background visualisation logic (uses only
  the preserved `objs` fields and `hfr`).

### Deficits / behavioural differences to be aware of

1. **Ellipse parameter definition differs.** `sep`'s `a`/`b`/`theta` come from
   raw second moments of the isophotal footprint; `photutils`
   `semimajor_sigma`/`semiminor_sigma` are Gaussian-sigma-equivalent sizes.
   Absolute values differ by a scale factor, so the hard-coded filter limits
   `0.8 < r < 15` and `r < 10`, and the S/N constants (`SN`, `SEP`) may need
   re-tuning against real frames. This is a **calibration task**, not a missing
   feature.

2. **`flux_radius` at fraction 1.0.** `sep.flux_radius` can integrate out to an
   arbitrary multiple of `a` and return the radius enclosing 100 % of the
   measured flux; `photutils.fluxfrac_radius(1.0)` is ill-defined (100 % is only
   reached at the aperture edge / infinity). The `radius[:,1]` value feeds the
   S/N estimate only. Mitigation: use `fluxfrac_radius(0.9)` (or the Kron radius)
   as the aperture-size proxy and, if needed, re-tune `SN`. Minor.

3. **Performance.** `sep` is a compiled C extension and is very fast.
   `photutils` detection/segmentation is NumPy/SciPy based and is typically
   several times slower on large frames. Photometry already runs in a Qt worker
   thread (`runnerCalcPhotometry`), so the UI stays responsive, but total
   analysis time will increase. Acceptable, worth noting.

4. **Deblending.** `sep.extract` has a built-in deblender controlled by
   `deblend_nthresh`/`deblend_cont` (defaults active). To match blended-star
   splitting behaviour, add `photutils.segmentation.deblend_sources` after
   `detect_sources`. Optional but recommended for parity.

5. **No convolution kernel** (`filter_kernel=None`) maps cleanly to *not*
   passing a `convolved_data`/kernel to `detect_sources` — no deficit.

Overall: **no hard feature is lost.** The two real risks are (a) numeric
re-calibration of the ellipse/HFR/S-N thresholds and (b) a modest performance
regression.

## 6. Implementation steps

1. **Dependencies** — in `pyproject.toml`, replace `"sep==1.4.1"` with
   `"photutils==3.0.0"`. Regenerate `uv.lock` (`uv lock`).
2. **Rewrite `runnerCalcPhotometry()`** in
   `src/mw4/logic/photometry/photometry.py`:
   - swap imports (`import sep` → photutils imports + `astropy.units as u`);
   - implement the mapping in §4;
   - build the `objs` structured array to preserve the downstream contract.
3. **Update `calcBackground()`** to use `bkg.background_median` instead of
   `self.bkg.globalback` (or keep a small adapter object).
4. **Rename note (optional):** signal `sepFinished` and attributes
   `sepThreshold` / `SEP` reference the old library name. Keep the public signal
   name `sepFinished` to avoid touching the image window; internal-only names
   may stay for a minimal diff (per "stay close to the task" guideline).
5. **Update tests** in
   `tests/unit_tests/logic/photometry/test_photometry.py`:
   - replace `import sep` and the two `sep.Background(...)` fixtures with
     `Background2D` (or mock `bkg` with `background`/`background_rms`
     attributes);
   - replace `mock.patch.object(sep, "extract", ...)` with a patch of
     `detect_sources` in the module namespace to drive the error path;
   - keep asserting the same public behaviour (`objs`, `hfr`, `bkg` set).
6. **Coverage** — keep 100 % coverage for the module (project requirement),
   including the detection-failure branch and the empty-`segm` branch.
7. **Lint/format** — run `ruff` and resolve all findings.
8. **Validate** — run the photometry unit tests, then the full suite.

## 7. Effort & risk

- **Code churn:** one production method rewrite + small background helper + test
  updates. Single-module change, low structural risk.
- **Main risk:** numeric re-tuning of detection/selection thresholds against
  real FITS frames (item 5.1). Recommend validating against a known test frame
  in `tests/testData/` and comparing detected star counts / median HFR before
  and after.
- **Recommendation:** proceed. `photutils` covers all required features; the
  only true costs are threshold re-calibration and a modest speed reduction.

## 8. Simplification opportunities (recommended)

Moving to `photutils` is not just a 1:1 swap — `SourceCatalog` lets us delete a
large amount of manual aperture bookkeeping. Concentrating on the main topics:

### 8.1 One `SourceCatalog` replaces four chained calls
Today `runnerCalcPhotometry()` manually chains
`kron_radius → sum_ellipse → sum_circle (fallback) → flux_radius`
(~40 lines, several intermediate arrays, `PHOT_AUTOPARAMS`, `PHOT_FLUXFRAC`,
`r_min`, `useCircle` masking). All of it collapses into a single catalog:

```python
cat = SourceCatalog(image_sub, segm, error=bkg.background_rms)
flux = cat.kron_flux          # FLUX_AUTO (circular fallback handled internally)
hfr  = cat.fluxfrac_radius(0.5)   # half-flux radius
```

The small-source circular-aperture fallback (`sum_circle`, `r_min`, `useCircle`)
is built into `kron_flux`, so that entire branch disappears.

### 8.2 Use the catalog's own error for S/N — drop the manual loop
The current code samples the background per source in a Python `for` loop and
then applies a custom S/N formula:

```python
b = []
for x, y in zip(objs["x"], objs["y"]):
    b.append(self.backSignal[int(y)][int(x)])
sn = flux / np.sqrt(np.abs(b * radius[:, 1] ** 2 * np.pi))
```

With `error=bkg.background_rms` passed to `SourceCatalog`, this becomes a single
vectorised, physically standard SNR:

```python
sn = cat.kron_flux / cat.kron_fluxerr
```

This removes the loop, the `radius[:, 1]` term, and the second `flux_radius`
fraction (`1.0`) entirely — which also **eliminates deficit 5.2** (the
ill-defined `fluxfrac_radius(1.0)`). Net: the S/N path gets both simpler *and*
more correct.

### 8.3 Roundness/elongation come for free
`runnerGetRoundness()` computes `max(a/b, b/a)` by hand. `photutils` exposes
`cat.elongation` (= a/b) and `cat.ellipticity` directly. If we let
`runnerGetRoundness()` read a precomputed `self.elongation` array, the a/b math
leaves the module. (Optional — only worth it if we relax the strict "keep
`objs` fields untouched" contract.)

### 8.4 `npixels` replaces the size heuristics
`detect_sources(npixels=7)` already enforces a minimum footprint, and
segmentation naturally rejects noise blobs. The manual ellipse filter
`(r < 15) & (r > 0.8)` can likely be reduced to a single upper-size cut (or
dropped), since its lower bound was mostly a noise guard that `npixels` now
covers.

### 8.5 Trade-off: two design options
There are two levels of change; pick one up front:

- **Option A – minimal diff (lowest risk):** keep building the `objs`
  structured array so all `runner*`/`calc*` helpers stay byte-for-byte
  unchanged. Apply only 8.1 and 8.2 inside `runnerCalcPhotometry()`.
  Smallest, safest change; still deletes ~half the method.
- **Option B – simplest end state:** feed the `SourceCatalog` (or a slim
  wrapper) through to the helpers and use `cat.elongation` etc. directly
  (adds 8.3). Slightly more edits across the module, but removes the
  structured-array shim and the duplicated a/b math for good.

**Recommendation:** implement **Option A + items 8.1, 8.2** first (big
simplification, minimal risk, fixes deficit 5.2), validate against a real frame,
then optionally adopt 8.3/8.4 (Option B) as a follow-up cleanup.
