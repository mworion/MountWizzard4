# Update plan: alignment-state feedback reconstruction

## Layer ownership update

The numerical API, dataset handling and immutable types now live under
`src/mw4/logic/controllers/analyse` with mirrored logic tests. Its
`analyseController.py` owns worker orchestration, revisions and result
publication; `analyseW.py` and `*Plots.py` own rendering and controls. The
controller takes the thread pool explicitly and does not depend on GUI types.
These paths supersede the earlier GUI calculation locations in this document.
See `work_agent/PLAN_analysis_layer_split.md`.

## Code naming update

The analysis API uses geometry-based terminology rather than report symbols:
`pointingRotation` / `polarAxisRotation`, `declinationOffset`,
`orthogonalityAngle`, and `reverseOrthogonality` replace tsa/tra, c3/c4 and
flipC4. The helpers are `applyOrthogonalityRotation()` and
`reframeEquatorialAlignment()`. Earlier symbol names below describe historical
evidence, not current API names. Diagnostics describe numerical limitations
without referencing disassembly reports or version-specific algorithm claims.
The saved `firmware` metadata key and its consistency check remain unchanged.

## Scope and implementation baseline

Apply `polar_ortho_align_analysis_report_new2.md` §§10.3/11/12/13 to
`work_agent/spec_model.md` and `work_agent/PLAN_model_analysis.md`. This revision
updates documentation and proposes runtime work; it does not implement it.
References below are relative to the repository root.

The semantic correction delivered on 2026-11-03 remains the baseline:
`ResidualAlignmentDiagnostics` exposes local MA/ME magnitude and signed NP
diagnostics separately from mount feedback. Both shared and split feedback
comparisons retain recorded targets and expected sources but remain unavailable.
The existing local SVD fit, worker integration, plots, protocol rounding,
recorded 11/22 primary setup and residual/RMS comparisons remain unchanged.

This task supports equatorial GM mounts only. Use pole flag `1` and HA/Dec
geometry with explicit scope provenance; a missing firmware type ID alone
does not block that choice. Explicit AZ/altaz metadata is unsupported.
Do not add an altaz solver, GUI presentation, error sphere, binary extraction,
mount access or calibration procedures.

## Evidence delta

Compared with `_new.md`, the updated report adds §§12 and 13. The second
in-place update additionally revises §12.3 and appends §13; §§1–11 are unchanged.

| Topic | New evidence | Consequence |
|-------|--------------|-------------|
| Application order, §12.1 | D wrap → unit vector → `tsa` rotation → nonlinear `c4` → geometric fallback if needed → pole reframe → D normalization → `c3` → encoder output | Implement independently testable stages, not another additive NP term |
| `c4` law, §12.2 | Explicit formulas and domain; application angle is `phi = ±c4` | The forward law is no longer an open question; parameter recovery and operational sign still require a contract |
| Pole convention, §§12.3/13 | GM-equatorial scope fixes pole flag `1`, D range `[-90,270]` degrees and reframe `D+pi`, `pi/2-C` | No need to build a generic mount-type/altaz analysis framework |
| Predicate constant | D/C predicate uses `5 degrees`, not an undecoded constant | Record `pi/36`, but do not invent operands, comparison direction or equality behavior |
| Setter map, §13.1 | IDs `{0,1,4,5,6}` set true; `{2,7,8,14}` set false; `{3,9,11,12,13}` leave unchanged | Supersedes §12.3's “else zero”; ID 10 is unspecified |
| Fit loop, §12.4 | Add term → quality → SVD → correlation → erase on failed gate | Plan named-term acceptance separately from singular-direction truncation |
| Fit thresholds | SVD `0.02`, correlation `0.99` / `0.9999` | Record exact values and provenance; do not blindly replace local `rcond=1e-10` |
| Feedback, unchanged §11 | F3 reads `tra` third column; F5 reads signed `c4` radians | Local MA/ME and NP proxies remain diagnostics, not feedback |

Two internal report qualifications matter. First, `0.02` is not equal to the
stated TPoint default `1e-2`; retain the explicit binary-reported number without
claiming equivalence. Second, §13.2 summarizes the equatorial branch as “sign
flipped”, but §§12.3/12.5/13.3 retain a runtime-dependent four-state predicate
and operational-sign uncertainty. Do not convert that summary into an
unconditional `phi = -c4`.

The report's general statements about poles and pointing models are not used
to redefine astronomy or expand scope: an altaz pointing model is possible,
but it is outside this GM-equatorial reconstruction.

## 1. Implement the newly specified forward helpers

**Files:** `src/mw4/logic/controllers/analyse/analyseModel.py`, `analyseTypes.py`;
mirrored numerical tests under `tests/unit_tests/logic/controllers/analyse/`.

Add pure, typed camelCase numerical helpers within `analyseModel.py`. Keep
dataclasses/status types in `analyseTypes.py`; do not add a worker or widget
dependency. These helpers can be delivered before the full inverse fit.

For a valid `tsa`-rotated unit vector `v` and explicitly resolved phi, implement
the reported law in radians:

```text
x = v2 / cos(phi)
if abs(x) <= 1:
    C = asin(x)
    s = sqrt(1 - x*x)
    r0 = v0*s*cos(phi) + v1*sin(phi)
    r1 = v1*s*cos(phi) - v0*sin(phi)
    D = 0 if r0 == 0 and r1 == 0 else atan2(r1, r0)
else:
    use the ordinary vector decomposition
```

Return an explicit applied/fallback status alongside coordinates. Domain
rejection is a normal geometric fallback, not an exception or failed fit.
Do not clamp x into range or silently return identity. Reject malformed or
nonfinite vectors explicitly; define and test undefined arithmetic and
near-zero cos(phi) separately from a valid out-of-domain fallback.

Apply the GM reframe `D+pi`, `pi/2-C`, normalize D to the reported
`[-pi/2, 3*pi/2]` range with verified endpoint rules, then add `c3`. Initial
`A-B` wrapping is a separate `[-pi,pi]` operation. Do not mix these ranges.
The encoder scale `410619.75` and O1/O2 offsets document a downstream stage;
do not apply them to arcsecond sky residuals.

Test zero/positive/negative phi, x below/equal/above both domain limits,
zero r0/r1, fallback, wrap endpoints, c3 order and explicit GM provenance.
Use independent expected values rather than only round trips.

**Acceptance:** the specified forward operations work for explicit valid
inputs without claiming the missing runtime predicate or state estimator exists.

## 2. Resolve and represent only the remaining state context

**Prerequisite for full reconstruction, not for step 1's isolated helpers.**

- Map saved JNow mount/solved coordinates and LST to the report's A/B/C,
  unit-vector and plain-decomposition conventions. Acquisition already applies
  coarse polar/ortho calibration; do not apply it twice.
- Keep application `tsa_inverse_transformation` and feedback
  `tra_inverse_transf_default` distinct. Establish their relationship from
  transform/fit definitions or independent reference cases; the report does
  not establish equality, transpose/inverse equivalence or how one is recovered
  from the other.
- Retain the GM pole flag independently from hemisphere, pier side and runtime
  sign mode. Missing firmware ID does not mean missing GM scope. Do not infer
  firmware IDs from numeric model names; §13 shows some such codes map to AZ.
- Resolve predicate `0x804d990`: other runtime flags, four-state `0..3` mode,
  which D/C operands are compared with `pi/36`, inequality direction and
  equality cases. A known mount class alone does not supply these values.
- Represent known/unknown sign context explicitly. The helper can accept phi
  for independent numerical tests, but production must not supply a guessed
  sign or choose one using recorded polar/ortho targets.
- Add immutable optional state for the two matrices, c3/c4 radians, geometry
  provenance, sign context, identifiable parameters and per-point transform
  status. Validate matrices as finite proper rotations without normalizing
  invalid input into an apparently valid result.

`writeRetrofitData()` currently stores summary feedback, not these matrices or
runtime predicate flags. Inventory any other saved metadata before deciding
which context is recoverable. Optional future producer metadata needs a
compatible schema and serialization tests; do not make binary extraction or
new mount queries prerequisites for offline analysis.

## 3. Add constrained recovery and firmware-style gates

**Prerequisites:** coordinate/state contract from step 2 and verified metric
semantics; the isolated transform helpers do not establish an inverse solver.

- Establish where the residual term blocks act relative to `tsa`, c4 and c3,
  which parameters are jointly/staged fitted, and the actual term order.
  Do not treat §12.1's application pipeline as a complete estimation recipe.
- Preserve the tested MA/ME rotational-degeneracy guard. An arbitrary gauge
  or rigid fit followed by free MA/ME refitting can reproduce observations
  without uniquely recovering the reported polar state.
- Establish the quality metric, SVD scaling/normalization, correlation
  definition, choice between `0.99` and `0.9999`, comparison equality behavior,
  and whether/how a rejected term is reconsidered. Numerical threshold values
  alone do not supply these definitions.
- Implement add/quality/SVD/correlation/erase with per-term acceptance and
  rejection provenance once those rules are defined. Do not merely change
  `np.linalg.lstsq(rcond=...)`; singular-vector truncation is not term removal.
- Retain the current local baseline and expose algorithm provenance separately
  from the recorded 11/22 setup. Do not silently replace established predictions
  or make algorithm selection depend on which feedback target matches.
- Recover model-level state together with shared or W/E residual blocks using
  the verified constraints. No W/E average or 11-term substitution is justified.

Test named-term rejection and gate boundary behavior using independently
defined metrics, plus identifiability, conditioning, missing branch context and
distinct W/E residuals. Keep both supported setup candidates and the recorded
setup as primary.

## 4. Enable feedback only from recovered state

**Prerequisites:** independently identified state and applicable firmware
conventions for the quantity being compared.

- F3 uses the third column of recovered `tra`, not automatically fitted `tsa`.
  Verify the §11 elevation offsets/reference pole and operational sign.
  Known-tilt and identity matrices must agree with independent angular
  separation `atan2(norm(cross(u,p)), dot(u,p))` in the established frame.
- F5 is `c4 * 180/pi`, preserving the signed stored coefficient. The per-point
  application phi may have the opposite sign; do not report phi as F5.
- Keep F3/F5 state gates independent. `N > 0` and the protocol's three-star
  minimum do not alone prove c4 recovery. Do not force polar availability
  from successful c4 recovery or vice versa.
- Recorded summaries and RMS remain validation targets, never constraints for
  fitting state, identifying matrix relationships or selecting signs.
- Preserve legacy-zero ambiguity, excluded-sample diagnostics and source
  provenance. Recorded summaries are already degrees; the local diagnostics
  are separately converted from arcsecond coefficients.
- Retain protocol half-step allowances `0.00005` / `0.005` degrees with the
  existing roundoff margin. Establish additional reconstruction uncertainty
  independently rather than expanding tolerances to force agreement.

Until these gates pass, retain unavailable calculated feedback/differences.
Update current runtime diagnostics in the next implementation: “c4 correction
law unknown” is obsolete; “operational predicate/state recovery unverified” is
the accurate remaining limitation.

## 5. Integrate and validate

Keep the existing `processModel()` / analysis worker / stale-result publication
path. No generated widgets or extra GUI are needed. Update
`doc/workflows/modeling/model_build.rst` together with runtime behavior.

Use module-scoped tests in the mirrored analysis test directory. Include
contradictory geometry metadata, independent matrix/c4 availability, zero and
nonzero state, sign ambiguity, recorded-target independence and shared/split
setup behavior. Preserve local residual/RMS regression against the 2.16.11
fixture without claiming that it validates the new 3.3.4/3.4 state model.
Obtain independent offline equatorial reference cases for actual state/branch
validation; live dummy tests are optional future evidence, not actions in this
offline task.

Follow `work_agent/PLAN_model_analysis.md` §7: focused coverage, Ruff format/lint,
type and import-contract checks, then overall package tests with 100% coverage
under existing platform rules. No coverage exclusions.

## Delivery order

The first runtime change should deliver step 1, typed transform statuses and
accurate limitation wording. Do not keep the now-specified forward law blocked
by unresolved full-state recovery. Then complete coordinate/matrix/sign context,
constrained fitting and metric semantics, and finally enable each independently
validated feedback comparison.

Resolved by the latest report: nonlinear c4 law and ordering, GM geometry and
reframe, the 5-degree predicate constant, and fit threshold values. Still open:
complete operational predicate, tsa/tra relationship, saved-coordinate mapping,
unique fit decomposition and metric semantics, actual 11-term repertoire and
older-firmware applicability. The additional evidence substantially narrows the
work but is not by itself a complete from-scratch fitter.

## Implementation status (2026-11-04)

Step 1's forward numerical API and the typed state/status portion of step 2
are implemented in `analyseModel.py` / `analyseTypes.py`.
`applyC4Rotation()` evaluates the reported law for explicit phi and preserves
geometric fallback. `applyAlignmentTransform()` composes an explicitly supplied
proper tsa rotation, signed c4 application, GM reframe/wrap and c3 offset.
It does not interpret saved RA/Dec as the report's A/B/C.
Unknown sign or missing state and unsupported geometry remain unavailable.
Invalid numerical inputs raise explicit errors.

`AlignmentState` keeps tsa and tra separate and defaults to no recovered
matrices/coefficients/sign context. Every fit exposes this state without
claiming recovery. In-range angular endpoints are preserved; out-of-range turns
map to a half-open interval. This is a documented local endpoint policy, not
verified firmware equality semantics. Numerical singularity is explicitly
rejected at `abs(cos(phi)) <= float64 epsilon`; a finite nonsingular quotient
outside the helper domain takes geometric fallback.

Runtime diagnostics and user documentation now acknowledge that the c4 law is
known, distinguishing it from unresolved state recovery and operational sign.
The existing local fit cutoff and residual/RMS behavior remain unchanged.
Full state recovery, firmware-style term gates and enabled feedback comparisons
remain blocked by the specific evidence requirements in steps 2–4.
