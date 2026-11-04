# Implementation plan: local model reconstruction and validation

## Objective and boundaries

Implement `spec_model.md`: automatically rebuild and evaluate a model after
loading its `.model` file in the analysis window. Produce a dedicated typed
result for later GUI presentation, including TPoint coefficients, per-point
correction contributions, and comparisons with the mount's recorded results.
This includes reconstructing the alignment-state polar and orthogonality
feedback and comparing it with `modelPolarError` and `modelOrthoError`.
The separate physical/calibration procedures remain outside this implementation;
their exclusion does not exclude this model-derived feedback.

**Evidence update (2026-11-04):** use
`../polar_ortho_align_analysis_report_new2.md` §§10.3/11/12/13 in preference to older
descriptions. Sections 12/13 are the delta from `_new.md`: §12 supplies the
nonlinear `c4` law, application order, mount-type pole-flag mapping and fit-gate
thresholds. F3 still reads `tra_inverse_transf_default`, while application uses
`tsa_inverse_transformation`; F5 still reads signed `c4` radians. Neither the
local `hypot(MA, ME)` nor `NP` mapping is a firmware-feedback definition.
Section 13 fixes this task to equatorial GM mounts (pole flag `1`), refines the
mount-ID setter map, and decodes the predicate threshold as `5 degrees`.
The detailed migration and its implementation status are in `../update_plan.md`.
The semantic correction is implemented; state recovery remains evidence-gated.

All numerical calculations live in `../src/mw4/gui/extWindows/analyse/analyseModel.py`.
`AnalyseData` remains in `analyseData.py` for file reading and plotting datasets.
Do not communicate with the mount, change its model, modify the input file,
add report rendering, or edit generated widgets.
Do not implement an altaz analysis path: use the documented GM-equatorial
scope, expose its provenance and reject explicit conflicting geometry metadata.
Missing firmware type ID alone is not a blocker to the equatorial reframe.

## Findings from the current code

- Both `AnalyseWindow.loadModel()` and `showAnalyse()` call `processModel()`.
  This is the common integration point for automatic reconstruction.
- `processModel()` currently reads and validates JSON, writes existing GUI
  fields, generates plotting arrays, and calls `drawAll()`.
- There is currently no SVD implementation in `analyseData.py`; the solver
  now lives in `analyseModel.py` (`designMatrix()` / `fitCandidate()`).
- `analyseTypes.py` and the worker integration already exist. The work below
  extends them, rather than adding a second solver or execution path.
- `deriveAlignmentFeedback()` now retains `ResidualAlignmentDiagnostics`
  separately from mount feedback. Both shared and split feedback comparisons
  remain unavailable with expected source and specific reconstruction reasons.
  Diagnostics acknowledge the known `c4` law while retaining the unresolved
  operational sign and constrained state-recovery limitation.
- Pure forward helpers, `AlignmentState` and `AlignmentTransform` now implement
  the explicit-input c4/GM application stages. Candidates expose empty recovered
  state; these helpers do not infer A/B/C or either matrix from saved records.
- `modelRunSupport.writeRetrofitData()` records the mount's `modelTerms`,
  `modelErrorRMS`, polar/orthogonality errors, and per-point residuals.
- `errorRA` and `errorDEC` are derived from the mount's reported residual
  magnitude and position angle. They are comparison targets, not fitting inputs.
  Their storage uses `Angle` wrappers; verify numerical units from the complete
  producer/serialization path rather than relying on the wrapper's name.
- `errorRA_S` and `errorDEC_S` originate from coordinate differences in image
  processing. Do not assume they are already tangent-plane arcsecond residuals.
- The referenced `m-2025-12-14-16-39-42-build.model` was not found in the
  workspace. Existing fixtures are available under `../tests/testData`, but their
  applicability to the stated acquisition conditions must be established.
- Section 12 now supports isolated application helpers, not just feedback-source
  identification. It does not specify the complete runtime sign predicate,
  the relationship of `tsa` to `tra`, or all fit-metric/constraint definitions
  needed for a unique local reconstruction. Earlier term formulas remain
  uncertain; a forward transform and acceptance thresholds alone do not
  establish the complete estimation algorithm.


## 1. Establish the numerical contract and reference cases

Before implementing the fit, trace saved measurements from the coordinates
submitted during model building through to the recorded mount results.

- Establish the coordinate frame, epoch, sign, angular unit, and pier-side
  convention for every input and comparison field.
- Use the matching mount/solved coordinate pairs and sidereal time to reconstruct
  the observations. Verify hour-angle wrapping and the RA-to-sky projection.
- Reproduce `Model.programModelFromStarList()` input rounding using the shared
  `sexagesimalizeToInt()` helper: both RAs to 0.1 seconds of time, both Decs to
  0.1 arcseconds, and LST to 0.01 seconds of time. Work from the values actually
  transmitted to the mount, rather than the file's higher-precision values.
- Define the residual-vector direction and overall RMS formula explicitly;
  distinguish sky RMS from per-axis RMS and degrees-of-freedom statistics.
- Use a two-component tangent-plane observation vector per point, with
  arcsecond residuals and radian trigonometric inputs. Resolve the sign change
  between RA and HA explicitly rather than copying the extraction report's
  abbreviated residual notation.
- Confirm treatment of apparent/topocentric coordinates and refraction in the
  saved build inputs. Reuse the saved frame rather than reapplying astrometry
  or refraction without evidence that it is needed.
- Account for the acquisition condition: pointing corrections were cleared,
  but polar and orthogonal alignment corrections remained applied. Do not
  apply those corrections twice or claim an absolute alignment quantity can be
  recovered when the saved information supports only a relative correction.
- Trace `modelPolarError` and `modelOrthoError` through `parseNumberStars()`,
  `writeRetrofitData()`, and serialization. Determine whether unavailable
  protocol values were converted to zero, and record that ambiguity when
  it cannot be resolved from the file.
- Reconstruct the matrix-derived F3 and `c4`-derived F5, not a coefficient
  norm and assumed NP readback. Establish the matrix's frame, mapping direction,
  reference pole, sign branch, gates, and separation from residual MA/ME.
  Resolve the report's shifted-elevation notation against independent identity
  and known-rotation cases before translating its equations.
- Adopt §12.2's nonlinear `c4` law as the reported application definition,
  with an explicitly resolved input angle `phi = ±c4`. Preserve its geometric
  fallback and distinguish signed stored `c4` from per-star application sign.
  Do not map the local NP/CH coefficient directly to `c4`.
- Map saved coordinates to §12.1's A/B/C and unit-vector convention. Establish
  how the application `tsa` rotation produces or relates to the feedback `tra`
  rotation. This is a separate open question, not resolved by matrix naming.
- Use §13's equatorial pole flag `1`, reframe and D range for this GM-only
  task. Preserve scope provenance without inventing a firmware type ID.
  Do not implement §12.3's earlier "else zero" shorthand: §13.1 has explicit
  true/false sets and unchanged IDs, and does not specify ID `10`.
  Resolve the per-star sign predicate's four-state mode, other flags and D/C
  comparisons with `5 degrees` (`pi/36`), including equality behavior.
  The equatorial branch does not resolve its runtime sub-branches. Treat
  §13.2's "sign flipped" as a branch summary, not proof of unconditional
  `phi = -c4`, since §§12.5/13.3 still require operational-sign confirmation.
- Expose residual-basis diagnostics per side, but reconstruct the single
  model-level matrix and `c4` for feedback. The report sums only the split
  term counts, not polar/ortho errors. Do not invent W/E aggregation or use the
  shared candidate as a replacement. Until their respective prerequisites are
  verified, both shared and split feedback comparisons remain unavailable.
- Determine whether a rigid orientation fit and the reported five-parameter
  refinement are required to reproduce mount results. Establish their inputs,
  order, and identifiable parameters before implementing them; do not add a
  second representation of the same geometrical correction.
- Verify TPoint basis functions against `../TPoint.pdf` and authoritative
  definitions where needed. Resolve the actual 11-term repertoire and pier-side
  transformations; do not substitute approximate flexure or collimation laws.
- Record §12.4's SVD cutoff `0.02` and correlation cutoffs `0.99` / `0.9999`
  with binary-source provenance. The report's claim that `0.02` matches the
  `1e-2` TPoint default is numerically inconsistent; use the explicit reported
  value, not that equivalence. Establish metric definitions, scaling, term
  order, which correlation threshold applies, and equality behavior before
  reproducing the add/gate/erase loop. Keep the existing `rcond=1e-10` baseline
  separate; do not replace it blindly with `0.02`.
  Use the recorded `modelTerms` as the authoritative mount setup, not an
  independently inferred replacement. In particular, a recorded 22 requires
  the split reconstruction as the primary result.
- Obtain offline reference cases with recorded 11-term and 22-term mount
  results. Confirm consistent metadata across records and which points
  participated in the recorded fit.

**Gate:** do not guess missing formulas or tune thresholds to force agreement.
The exact firmware selection rule is not required for the local consistency
check: fit both supported candidates and compare their RMS with the recorded
overall RMS. Do not claim that this reproduces the firmware's selection
algorithm. Missing formulas or reference data remain explicit limitations on
the reconstruction and its validation.

## 2. Define the typed analysis result

Extend the existing `analyseTypes.py` alongside the analysis modules, containing
typed dataclasses and status types only; keep calculations in `analyseModel.py`.
Use camelCase field names and ordinary Python/NumPy data without widget objects.

The result should expose:

- Source identity, analysis status, units/conventions, usable/excluded point
  counts, excluded-point reasons, firmware version, and diagnostics.
- Named TPoint coefficients, physical correction group, unit, applicable pier
  side or shared scope, and active/dropped/unidentifiable state.
- Every source point's identity and pier side, input residual, per-term and
  polar/orthogonal/remaining-model contributions, total correction, resulting
  residual, recorded mount residual, component differences, and agreement status.
- Both candidate setups, where identifiable: coefficients, rank/conditioning,
  residual statistics, and distance from the mount's recorded overall RMS.
- Authoritative recorded mount term count and primary reconstruction setup,
  separately from the locally better-matching candidate and a
  consistent/disagreement/inconclusive comparison.
- Rebuilt and recorded overall RMS, their difference, numerical tolerances,
  and comparison status.
- Three separate concepts: recorded polar/ortho summaries, local per-scope
  residual `ME`/`MA`/`NP` diagnostics, and reconstructed model-level feedback.
  Include the reconstructed rotation (with frame/direction), `c4` in radians,
  state/branch availability, reconstruction provenance, firmware applicability,
  and identifiability. Preserve signed differences where applicable,
  tolerances and independent polar/ortho comparison statuses. A successful
  pointing fit does not imply a verified alignment-state reconstruction.
- Distinct application `tsa` and feedback `tra` matrices; optional mount-type ID,
  explicit GM scope and pole flag `1`, known/unknown runtime sign context, `c3`/`c4` radians,
  and per-point applied/fallback/unavailable transform status. Fit-policy
  provenance must distinguish the local baseline from a firmware-style
  candidate and record accepted/rejected terms and gate reasons.

Unavailable or unidentifiable quantities must remain explicitly unavailable,
not zero-valued successful results. Preserve every original point, including
points excluded from fitting, so a later GUI can explain the complete analysis.

## 3. Implement numerical reconstruction in `analyseModel.py`

Add small, typed numerical functions or static methods that can be exercised
without constructing a window.

- Normalize validated source values into float64 calculations, independently of
  the existing float32 plotting arrays and tolerant zero-fill conversion.
- Validate finite values, required coordinates, point identities, pier sides,
  and consistent mount metadata. Do not silently fill missing fitting data.
- Build the verified TPoint design matrix and solve using NumPy's SVD-based
  least-squares facilities, with the established conditioning/selection rules.
- For N usable points and P coefficients, assemble a `(2 * N, P)` matrix and
  matching `2 * N` observation vector. Do not copy the extraction report's
  illustrative `(N, 2 * P)` assembly, which does not match that vector.
- Distinguish SVD truncation of singular directions from removal of individual
  named terms. Reproduce the established stepwise term-selection behavior
  explicitly rather than labelling every truncated direction a dropped term.
- Evaluate a shared 11-term candidate and, where supported, two independent
  pier-side candidates totaling 22 terms.
- Handle insufficient points, missing pier-side coverage, duplicate observations,
  rank deficiency, and numerical failures explicitly.
- Select the primary reconstruction using the recorded term count: 22 means
  two pier-side-specific 11-term models. Compute both candidate fits from the
  observations independently of the recorded residuals and RMS; only use the
  recorded RMS afterward to evaluate their agreement.
- Evaluate coefficients through the same verified basis used for fitting.
  Retain every term's per-point contribution and separate correction groups
  without double-counting polar/orthogonal alignment.
- Separate residual-basis diagnostics from firmware feedback in
  `deriveAlignmentFeedback()`. Initially retain the diagnostics but disable
  direct proxy comparisons for shared and split fits.
- Add pure, typed state reconstruction and feedback evaluation in
  `analyseModel.py` once the rotation/`c4` mapping is verified. Jointly fit or
  otherwise constrain the decomposition using established firmware ordering;
  do not fit a rigid rotation and then freely refit the same rotational modes
  as MA/ME. Check rank/identifiability for the complete parameterization.
- Implemented pure explicit-input application helpers: unit-vector
  conversion and `tsa` application, `c4` correction with explicit phi and
  plain-decomposition fallback, GM-equatorial reframe, wrapping and
  `c3` offset. Implement the supported helper domain without waiting for the
  unresolved full fitter. Do not invent the sign predicate; expose unknown
  context through typed availability. Encoder scaling and O1/O2 do not belong
  in sky-residual units.
- Add firmware-style term acceptance only once the quality/SVD/correlation
  definitions are verified. Preserve the local baseline for regression and
  label algorithms separately; recorded 11/22 still governs primary setup,
  not which experimental algorithm happens to fit best.
- Evaluate F3 from the reconstructed second matrix's axis/pole geometry and
  F5 from reconstructed `c4 * 180 / pi`, with independent state gates.
  Keep those operations separate from executing physical alignment procedures.
  Use the authoritative recorded setup for the primary comparison.

## 4. Validate against the mount's recorded result

- Preserve `modelTerms` as the exact mount setup fact: shared 11 versus
  pier-side-specific 22. A better-matching alternative must not overwrite it.
- Compare each candidate's overall RMS with recorded `modelErrorRMS`. Mark
  disagreement when the alternative's absolute RMS difference is smaller than
  the authoritative setup's difference beyond the documented tolerance.
  Retain both differences; treat indistinguishable differences or insufficient
  data as inconclusive. Do not choose solely by lowest fitted RMS.
- Compare rebuilt residual components with `errorRA` and `errorDEC`, retaining
  the signed differences for every comparable point.
- Compare rebuilt overall RMS with `modelErrorRMS`; also retain the recorded
  per-point `errorRMS` and `errorAngle` for diagnostic consistency checks.
- Compare reconstructed F3/F5 with `modelPolarError` / `modelOrthoError`
  independently. Preserve recorded values as targets, never fitting inputs
  or a means of choosing a pole branch or NP/CH mapping. Keep local coefficient
  diagnostics out of these comparisons. Missing or non-identifiable state is
  a specific reconstruction limitation, not an inherent exclusion from scope.
- Select and document tolerances using coordinate precision, residual-magnitude
  precision, position-angle quantization, and numerical conditioning.
  Keep precision allowances distinct from algorithmic disagreement.
- Use the report's `:getain#` formatting evidence as a starting point for
  precision checks: RMS has one decimal place, polar error four, and ortho
  error two. Verify those precisions and units against each fixture's firmware
  and producer before choosing tolerances; never infer protocol precision
  from JSON's number of digits.
- Represent metadata conflicts, unsupported recorded term counts, unavailable
  reference values, and actual numerical mismatches distinctly.
- Do not suppress alternative-candidate disagreement, enlarge tolerances to
  obtain agreement, or refit the recorded residuals. If the recorded setup
  cannot be fitted, report it as unavailable rather than replacing it with
  the other candidate.

## 5. Integrate automatic execution without blocking the GUI

- Initialize an analysis result/status on the window and trigger reconstruction
  from the common successful `processModel()` path after reading the records.
- Preserve existing metadata and plotting behavior; no new presentation is
  included in this implementation.
- Use the existing `startWorker()`/`app.threadPool` infrastructure, naming the
  worker `workerRebuildModel` and its numerical entry point `runnerRebuildModel`.
- Pass a stable snapshot of the loaded input to the worker. Do not read widgets
  or mutable plotting state from the worker thread.
- Publish the typed result on the GUI thread. Clear previous analysis state for
  a new load and prevent an older worker result from replacing a newer model's
  result.
- Ensure a new load is not silently discarded when a reusable worker is busy;
  serialize pending requests or otherwise use an explicit latest-load policy.
- Route expected analysis limitations into typed diagnostics and repository-standard
  logging; use the existing worker error signal for unexpected failures.
- Cover close/reopen and overlapping-load behavior without adding duplicate
  signal connections or introducing callbacks that access destroyed widgets.

## 6. Add tests and directly related documentation

Extend tests under `../tests/unit_tests/gui/extWindows/analyse`, matching the
implementation modules and using module-scoped fixtures.

- Verify individual basis functions against independently calculated reference
  values, including signs, units, hour-angle wrap, and pier-side transformations.
- Recover known coefficients from synthetic shared and split models. Use
  independent reference values so fit/evaluation mistakes cannot cancel out.
- Verify per-term sums, correction-group decomposition, residual components,
  and the exact overall RMS definition.
- Cover acquisition with pre-applied polar/ortho corrections, distinguishing
  fitted residual terms and model-derived feedback from the separate coarse
  calibration process. Verify that unavailable/ambiguous recorded summary
  fields cannot produce a false match.
- Replace proxy-as-feedback expectations with separate diagnostic and state
  tests. Test known rotations and known radian-valued `c4`, pole/sign branches,
  state gates, units, mismatches and tolerance boundaries for shared and split
  setups. Verify that no invented W/E combination or unverified mapping
  produces a successful comparison. Changing recorded feedback must not change
  reconstructed state, branch selection or derived values.
- Test the nonlinear helper independently: zero/positive/negative phi,
  `abs(x)` below/equal/above one, zero r0/r1, fallback, malformed/nonfinite
  inputs and near-zero cos(phi). Do not use blanket clipping or a broad catch.
  Test GM scope with missing type ID and explicit contradictory geometry,
  equatorial D-wrap endpoints and c3 ordering. If a metadata consistency
  mapper is necessary, cover explicit setter cases, unchanged and unspecified
  IDs without introducing an altaz solver. Unknown sign context must not
  produce a default branch; test the 5-degree boundary only once predicate
  operands and comparison direction are verified.
- Test term gates at `0.02`, `0.99`, `0.9999` boundaries once metric definitions
  are established; rejection of a named term is not singular-vector truncation.
  Keep the existing pointing residual/RMS regression as the local baseline.
- Exercise recorded 11/22 setups, alternative-candidate disagreements, ties,
  and unavailable comparisons. Changing only recorded `modelTerms` must change
  the primary setup but not either independently fitted candidate. In particular,
  recorded 22 must remain authoritative even when the shared candidate matches
  the recorded overall RMS better.
- Validate offline mount fixtures for both decisions, per-point residuals,
  and overall RMS with documented, fixed tolerances.
- Cover missing/nonfinite data, unsupported metadata, insufficient/one-sided
  samples, degenerate geometry, solver errors, and tolerance boundaries.
- Verify that both load entry points automatically trigger evaluation exactly
  once, existing charts remain functional, stale results are rejected, and
  worker failures cannot leave a previous result looking current.
- Document the data contract, numerical conventions, selection rule, tolerances,
  and any demonstrated limits next to the relevant implementation and tests.
- Use independently generated synthetic observations for dummy-pointing tests
  of signs, scales, and correction ordering. These are offline checks only;
  they do not prove firmware equivalence without saved mount reference cases.

## 7. Validation sequence

During implementation, run the focused analysis-module tests and coverage first,
then address relevant typing, formatting, lint, and import-contract findings.
Do not add coverage exclusions or fix unrelated existing issues.

```sh
uv run pytest tests/unit_tests/gui/extWindows/analyse \
  --cov=mw4.gui.extWindows.analyse --cov-report=term-missing
uv run ruff format --check src tests
uv run ruff check src tests
uv run pyrefly check
uv run lint-imports
```

Use Ruff to format modified Python files before the format check. As the final
implementation validation, run the overall unit-test suite and package coverage:

```sh
uv run pytest tests/unit_tests --cov=mw4 --cov-report=term-missing --cov-fail-under=100
```

Require 100% coverage under the repository's existing platform-specific rules;
report pre-existing failures or unavailable reference data explicitly.

## Completion criteria

Loading a valid model automatically produces a typed reconstruction result,
without mount access or new GUI rendering. The result exposes named TPoint
parameters and all per-point contributions. It uses the mount's recorded
11/22 setup as truth for the primary reconstruction, retains both supported
candidates, and marks any alternative-candidate disagreement based on closeness
to the recorded overall RMS. It verifies per-point residuals, overall RMS, and
model-derived polar/ortho feedback within justified tolerances. An unresolved
feedback mapping is outstanding implementation work, not an inherent exclusion
from scope. Unsupported or unidentifiable cases are explicit, not reported as
successful matches.

## Local implementation limitations

The initial implementation uses an explicitly documented local candidate basis:
`IH ID CH NP MA ME TF HCES HCEC DCES DCEC`. It does not claim that these are the
firmware's exact eleven operational terms. In particular, it does not invent
FO/DAF laws or reproduce the unverified five-parameter refinement.
`ResidualAlignmentDiagnostics` exposes `maMeMagnitude` and `npCoefficient` in
degrees for the shared scope or separately for W/E, using the local linear
mapping `hypot(MA, ME) / 3600` and signed `NP / 3600`. These values are explicitly
not firmware feedback.

Both shared and split candidates retain recorded feedback, protocol precision
allowances, expected source and specific unavailable-comparison diagnostics.
Neither exposes proxy-derived calculated feedback or signed differences.
The former shared-candidate match/mismatch comparison is disabled until
alignment state is independently reconstructed.
Unavailable fits, excluded samples and missing/inconsistent recorded feedback
remain explicit; legacy recorded zeros remain ambiguous rather than false
matches. The blanket matrix-based impossibility claim is removed.

Reconstruction of the second matrix and fitted `c4` remains outstanding.
There is no longer evidence for treating this as merely a missing W/E averaging
rule: the firmware reads single model-level state quantities. The report's
§12.2 supplies the `c4` application law and §12.1 its stage order; these are no
longer unknown. The complete operational sign predicate, application-to-feedback
matrix relationship, unique parameter decomposition and exact metric semantics
remain open, as does applicability to older firmware.
These are reconstruction limitations, not exclusions from scope. The recorded
setup remains truth, with both candidates compared against recorded overall RMS.

Prior implementation validation recorded the following for the firmware 2.16.11
fixture (not re-run for this documentation update). Reproducing
protocol rounding gives a split-model RMS of approximately 1.09663 arcsec versus
the recorded 1.1 arcsec, and all 57 available per-point comparisons agree within
the precision bounds. The mount's recorded residual direction is fitted correction
minus observation, verified against those per-point results. One point has no
recorded vector and remains explicitly unavailable for comparison. The shared
candidate's RMS is approximately 1.16230 arcsec, so the recorded split setup is
consistent with the closer overall RMS. A real 11-term reference and the
referenced newer build file are still needed to establish broader equivalence.
These residual/RMS results do not validate F3/F5 reconstruction or establish
that the new 3.3.4/3.4 evidence applies unchanged to 2.16.11.
