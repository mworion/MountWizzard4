# Model error analysis report

## Goal

**Layering update:** calculations, file/dataset handling and immutable result
types live in `src/mw4/logic/controllers/analyse`. Its `analyseController.py` owns Qt
worker orchestration; `analyseW.py` and the plot components own presentation.
This supersedes earlier instructions below to keep calculations in the GUI
`analyseModel.py`. See `../PLAN_analysis_layer_split.md`.

Add a local analysis routine that checks a mount model built from a model file
and produces structured analysis data describing the model's corrections and
errors. The data will be presented in a GUI in a later step; this work should
not implement that presentation. The goal is to verify that the application's
model optimization reproduces the mount's calculation for individual points
and for the overall RMS.

## Input and scope

- Analyze a model file such as
  `m-2025-12-14-16-39-42-build.model`; do not retrieve data from the mount.
- Reuse the model-file reading and analysis data already handled by
  `analyseW.py`, `analyseData.py` and `analyseModel.py`.
- When `analyseW.py` loads a model and its data has been read, automatically
  invoke the model rebuild and evaluate the rebuilt model. This should happen
  as part of the existing load/analysis flow, without a separate user action.
- During model-file construction, the pointing correction model has been
  cleared. Polar and orthogonal alignment corrections are still applied.
  Account for that starting condition when deriving and explaining errors.
- The polar-align and ortho-align calibration procedures are separate from
  model building and are not included in this implementation. However, the
  resulting alignment state is reflected in the mount's feedback as
  `modelPolarError` and `modelOrthoError`; reconstructing and checking that
  feedback is in scope. These are not interchangeable with residual TPoint
  coefficients.
- Use `../TPoint.pdf` as the algorithm reference and
  `modeling_analysis_report.md`, `model_extract_analysis_report.md`, and
  `../polar_ortho_align_analysis_report_new2.md` as background on the mount's
  pointing model and alignment state. Sections 10.3, 11, 12 and 13 supersede older
  report versions and earlier sections where their descriptions conflict.
  Distinguish reported binary evidence from inferences and independent
  validation; unresolved formulas are not implementation definitions. The new
  evidence covers firmware 3.3.4/3.4, not automatically older firmware.
- This reconstruction targets equatorial GM mounts only (§13): pole flag `1`,
  equatorial HA/Dec processing and the equatorial reframe. Record that explicit
  scope assumption in the result; do not require a missing firmware type ID to
  rediscover the supported geometry. Explicit contradictory AZ/altaz metadata
  is unsupported, not silently coerced to GM. Altaz fitting and error-sphere
  rendering are not added by this update.
- Reconstruct locally from the saved observations (the extraction report's
  local-refit approach), not from firmware binary alignment files. Binary
  extraction, mount calibration, PEC reconstruction, and error-sphere rendering
  are outside this change.

## Analysis requirements

- Perform all model-analysis calculations in `analyseModel.py`, adding an
  SVD-based least-squares implementation.
- Return the processed results in a dedicated typed result model, suitable for
  later GUI presentation; do not generate or render the GUI report in this
  change.
- Report the polar-alignment corrections, orthogonal-alignment corrections,
  and pointing-model corrections, retaining per-point values and each term's
  contribution.
- Distinguish the coarse polar/orthogonal alignment already applied during
  acquisition, any identifiable rigid orientation, and the fitted residual
  polar (`ME`/`MA`) and non-perpendicularity (`NP`) corrections. Derive the
  corresponding mount feedback from reconstructed alignment state as follows:
  - `modelPolarError` (F3) is derived from the third column of
    `tra_inverse_transf_default`, the second rigid-rotation matrix, not directly
    from `hypot(MA, ME)`. Reconstruct that orientation from saved observations
    only where its frame, direction, pole/sign branch, and separation from
    residual pointing terms are identifiable. Use angular deviation from the
    appropriate pole reference, converted from radians to degrees. Validate the
    report's intermediate elevation offsets before coding them; its remaining
    operational sign branch is not fully specified by the new evidence.
    The application pipeline uses `tsa_inverse_transformation`, whereas F3
    reads `tra_inverse_transf_default`. Establish their relationship before
    using a fitted application matrix as the feedback matrix; do not assume
    identity, equality or transpose/inverse equivalence.
  - `modelOrthoError` (F5) is the single alignment-state coefficient `c4`
    (`0x8281b10` in the analysed binary), converted from radians to degrees.
    Section 12.2 now supplies its nonlinear application law, after the `tsa`
    rotation and before pole reframing and the `c3` offset. Use this law to
    reconstruct `c4`, not an assumed additive local NP/CH coefficient. Its
    application angle is `phi = -c4` when the runtime pole predicate is true,
    otherwise `phi = c4`. F5 still reports signed `c4`, not the per-star `phi`.
  - Preserve the local `hypot(MA, ME) / 3600` and signed `NP / 3600` values only
    as explicitly labelled residual-basis diagnostics in degrees. They must
    not produce firmware-feedback match/mismatch statuses without a verified
    mapping, including for the shared 11-term candidate.
  Any unresolved state reconstruction or mapping is an implementation
  limitation, not an inherent exclusion of feedback from scope.
- For a 22-term setup, expose residual-basis diagnostics separately for each
  pier side. The updated report identifies one matrix-derived F3 and one `c4`
  F5; only the term count is explicitly summed across the two term blocks.
  Do not assume feedback is an average or norm of W/E terms. Reconstruct the
  model-level state, verifying how both sides feed it; until then leave the
  affected comparison unavailable. Do not substitute the 11-term candidate.
- Implement the reported application stages as separately testable numerical
  operations: wrap `D = A - B`, form the unit vector, apply the `tsa` rotation,
  apply the nonlinear `c4` helper, use ordinary vector decomposition only on
  its geometric fallback, then pole-reframe, normalize D and add `c3`.
  Establish the mapping from saved RA/Dec/LST to A/B/C and the helper's vector
  conventions before claiming an end-to-end reconstruction. Encoder scaling
  (`410619.75`) and O1/O2 offsets are downstream reference information, not
  units or fitting targets for the sky-residual comparison.
- Preserve the `c4` helper's domain `abs(v2 / cos(phi)) <= 1`, including the
  boundary and its zero-r0/zero-r1 D=0 branch. Domain rejection triggers the
  reported plain-decomposition fallback; it must not be silently clamped to
  a corrected value or treated as a failed fit. Distinguish that valid geometric
  fallback from malformed vectors, nonfinite values and undefined arithmetic.
- Use the GM pole-flag-true reframe `D + pi`, `pi/2 - C`, normalize D to
  `[-pi/2, 3*pi/2]` and then add `c3`; verify endpoint handling. This flag is
  neither hemisphere nor pier side. Section 13.1 refines §12.3: firmware IDs
  `{0,1,4,5,6}` set it true, `{2,7,8,14}` set it false, and
  `{3,9,11,12,13}` leave it unchanged. ID `10` is not specified by that table.
  Do not implement an "else false" mapping or guess IDs from model numbers.
  The equatorial scope resolves the reframe, not the full per-star `c4` sign:
  the predicate also uses runtime flags, a four-state mode and D/C against a
  decoded `5 degrees` (`pi/36`) constant. Comparison operands, branch direction
  and equality rules still need definition. Sections 12.3/12.5/13.3 retain
  operational-sign uncertainty despite §13.2's shorthand "sign flipped".
  Missing predicate context remains explicitly unavailable; do not assume an
  unconditional negative sign or select a sign using recorded feedback.
- Retain the existing local SVD baseline (`rcond=1e-10`) separately from the
  proposed firmware-style fit. Section 12.4 reports per-term addition, quality,
  SVD and correlation gates, erasing rejected terms, with SVD cutoff `0.02`
  and correlation cutoffs `0.99` / `0.9999`. Implement these as firmware-style
  gates only after establishing normalization, metric definitions, term order,
  threshold selection and equality rules. Do not substitute `rcond=0.02` into
  the current solver and call that the firmware algorithm. `0.02` is not equal
  to the TPoint `1e-2` default, despite the report's parenthetical description.
- Fit observation differences from matching saved mount/solved coordinates,
  not the mount's post-fit residuals. Specify coordinate frames, RA versus HA
  sign, wrapping, sky projection, and units explicitly.
- Reproduce the input precision used by the existing model-programming code
  before rebuilding: RA to 0.1 seconds of time, Dec to 0.1 arcseconds, and
  sidereal time to 0.01 seconds of time. Compare per-point residuals in the
  mount's recorded position-angle direction, not an assumed opposite convention.
- Include the fitted TPoint parameters in the analysis result, with each term's
  name, coefficient, unit, and applicable correction contribution, so the
  later analysis GUI can display them.
- Check the optimized model against the mount's calculation:
  - compare calculated per-point results with the recorded `errorRA` and
    `errorDEC` values;
  - compare the calculated overall RMS with the recorded `modelErrorRMS`;
  - compare independently reconstructed matrix-derived polar error and
    `c4`-derived ortho error with the recorded `modelPolarError` and
    `modelOrthoError`, only when each quantity's prerequisites are satisfied.
- Treat the file's recorded `modelTerms` as ground truth for the mount's setup.
  In particular, `modelTerms == 22` means the mount used separate 11-term models
  for the two pier sides. Use that setup for the primary reconstruction and
  validation; never replace the recorded fact with a locally preferred setup.
- Where the data supports fitting both, also calculate the shared 11-term and
  split 22-term candidates. Retain both results and compare their overall RMS
  with the recorded `modelErrorRMS`, rather than merely choosing the candidate
  with the lowest fitted RMS. Mark disagreement if the alternative setup
  matches the recorded RMS better beyond the documented tolerance, while
  preserving the recorded mount setup as truth. Mark ties or insufficient
  data as inconclusive. This is a local consistency check, not a claim to
  reproduce the firmware's internal selection algorithm.
- Include the values being compared, their units, and any unavailable or
  unusable input data in the structured result. Use documented numerical
  tolerances when deciding whether calculated and recorded values agree.
- Account for firmware version and recorded-value precision. Missing alignment
  information is not equivalent to zero error; the report notes that the mount
  can return `E` for unavailable summaries. Establish whether the existing file
  producer preserves or loses that distinction before interpreting zero values.
  Apply feedback gates separately: polar feedback requires the appropriate
  equatorial alignment state and sign/pole branch (the report says `E` for
  altaz); ortho feedback requires an active fit (`N > 0`, protocol minimum
  three stars). Unknown flags or mount geometry must not be assumed valid.
- Recorded summaries are independent validation targets, never constraints
  for estimating the matrix, choosing its branch, identifying `c4`, or tuning
  tolerances. Retain source/mapping provenance, firmware applicability,
  identifiability, and a reason for every unavailable comparison.

## Open decisions for planning

The concrete typed result fields and numerical tolerance values should be
selected during implementation after reviewing the existing analysis patterns
and the model-file data. See `../update_plan.md` for migration of the existing
implementation and the delivered semantic correction. Firmware-state recovery
remains evidence-gated; local diagnostic proxies are no longer compared as
mount feedback.

The explicit-input forward helpers and typed `AlignmentState` /
`AlignmentTransform` are implemented. They evaluate the supplied c4 angle and
GM reframe without guessing runtime sign or recovering matrices from saved
coordinates. Candidate state remains empty until recovery is verified.
Angular wrap endpoints currently follow a documented local policy, not claimed
firmware endpoint equivalence.
