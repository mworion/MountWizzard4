# Analyse architecture and maintainability review

Reviewed: 2026-11-03

Scope: `../src/mw4/gui/extWindows/analyse`, with targeted checks of the file
producer, worker helper, plotting implementation and analyse tests. Generated
widgets are excluded. This is a review only; no implementation changes are made.

## Implementation follow-up

The findings below describe the reviewed baseline. The subsequent implementation
adds an unloaded redraw gate, reference-view linking, direct field extraction,
strict parallel-array alignment, typed status/fit/plot contracts and fresh
revisions on public analysis start. Legacy null/NaN zero filling is retained with
warning logs because the saved reference model contains null RA/DEC residuals;
invalid conversions and infinities no longer silently become zero.
Metadata names, RMS comparison readability, combined diagnostic reasons and
test ownership have been cleaned up, and the composition plan now records only
the current architecture. Existing numerical and worker-signal guards remain.
No runtime schema framework, generic tab hierarchy or additional solver split
has been introduced.

## Open points after implementation

The original findings and line references below describe the baseline, not a
list of remaining defects. The redraw, linking, extraction, strict alignment,
start-lifecycle and readability changes are implemented. The following items
remain open:

| Priority | Open point | Required outcome |
|---|---|---|
| Medium | Preserve missing plot values | Keep per-field missing-value masks before legacy null/NaN values are filled; do not infer missingness from zero |
| Medium | Display unavailable values honestly | Where position is known independently, use a neutral gray marker and an unavailable-value tooltip; where a missing value determines position, omit the point and report the missing count |
| Medium | Exclude missing values from plot statistics | Do not let placeholder zeros affect color scales, contour interpolation, sorted error plots or distributions |
| Medium | Verify firmware alignment mapping | Local polar/ortho derivation remains explicitly unverified; retain provenance and limitations until reference evidence establishes equivalence |
| Medium | Establish 22-term aggregate feedback | Keep W/E errors separate and the combined comparison unresolved until the firmware combination rule is verified; do not invent averaging |
| Low | Further record/array typing | Consider a small record `TypedDict` and additional numerical `NDArray` annotations only where useful; runtime schema validation remains out of scope |

### Missing-value plotting proposal

This is a proposed follow-up, not implemented behavior:

- A measured zero is valid and keeps normal plot coloring. It must not be marked
  unavailable simply because its numeric value is zero.
- Preserve `None`/NaN provenance in `AnalyseData` using masks aligned with each
  affected field. Do not recover masks by testing the already filled arrays.
- For Alt/Az error maps, altitude/azimuth can still locate a point whose residual
  is unavailable. Render it as a neutral gray marker outside the numerical
  colormap, with a tooltip such as "Recorded residual unavailable."
- For encoder-error plots, a missing residual means the vertical coordinate is
  unknown. Omit it rather than positioning it at zero; expose the missing count.
  Apply the same rule to missing scale, magnitude or angle coordinates in the
  other tabs.
- Filter missing values before deriving color limits, contours, sorted errors
  and distributions. Keep masks field-specific so one unavailable component
  does not hide unrelated valid measurements.
- Add coverage for genuine zero, `None`, NaN, mixed valid/missing values and
  entirely missing fields, including alignment of indices, pier sides and
  tooltips after filtering.

The masks represent explicitly missing data in otherwise trusted app-produced
records. They are not a request to restore general file-schema validation or
accept malformed numeric values silently.

## Overall assessment

The composition architecture is appropriate and should stay:

| Component | Responsibility | Assessment |
|---|---|---|
| `AnalyseWindow` | UI, configuration and load/display orchestration | Small and explicit |
| `AnalyseData` | File reading, dataset generation and plot arrays | Correct boundary; conversion can be simpler |
| `AnalyseModel` | Background reconstruction lifecycle and results | Correct boundary; important asynchronous guards |
| Numerical functions in `analyseModel.py` | Fits, evaluation and comparisons | Mostly pure and independently testable |
| Three tab plot classes | Drawing their respective tabs | Clear ownership; no dependencies between tabs |
| `analyseTypes.py` | Immutable numerical results | Useful, not unnecessary abstraction |
| `plotHelpers.py` | Shared coloring and view linking | Suitable name and scope |

No further class hierarchy, generic tab framework, service layer or module split
is needed at this size. The highest-value improvements are a defined no-data
state, simpler view linking, less permissive plot conversion and clearer Python
types. Removing every guard would not make this design more reliable.

## Prioritized findings

### 1. Medium: redraw is reachable before any data exists

Locations:
`analyseW.py:34-41,68-73,87-89`,
`generalPlots.py:23-27,33-42`,
`analyseData.py:16-30`.

The window connects palette changes and checkbox clicks immediately, while all
plot arrays initially are empty. These paths call `drawAll()` without a loaded
model. `GeneralPlots.drawScaleImage()` then calls the scatter plot with empty
arrays. Its range calculation uses `np.min`/`np.max`
(`gui/utilities/pyqtgraph/gNormalScatter.py:20-25`), which cannot reduce an empty
array. This is a concrete exception path, not a reason to restore file-schema
validation.

Recommendation: define the unloaded state once at the window boundary. Update
widget palettes even when unloaded, but do not draw data until a model has been
loaded. Disable data-only controls or gate `drawAll()` with an explicit loaded
state. Avoid copying the same empty-data checks into every plotting method.

Add a test for a new window receiving a palette event and checkbox clicks before
loading a model, using actual plot widgets rather than mocking `drawAll()`.

### 2. Low: view linking repeatedly overwrites links

Location: `plotHelpers.py:12-21`.

The nested loop appears to link every view to every other view. PyQtGraph stores
one linked view per axis: each `setXLink()`/`setYLink()` replaces the previous
link. For four plots the loop performs twelve X-link assignments and twelve
Y-link assignments, but retains only one target per view. Repeating this on
every redraw makes the topology harder to understand and needlessly rebinds
signals.

Recommendation: use one reference view and link the remaining views to it.
Unlink every view explicitly when disabled. Preserve the existing X-only
behavior for RA/DEC and X/Y behavior for Alt/Az. Verify that panning any member
still synchronizes the group before replacing the current topology; this is a
simplification proposal, not a claim that the current links never work.

No general-purpose graph or linking manager is warranted.

### 2a. Low: tolerant plot conversion can disguise missing data

Locations: `analyseData.py:32-49`,
`generalPlots.py:47-52`, `raDecPlots.py:71-73`.

`list2array()` silently replaces `None`, NaN, unconvertible strings/objects and
overflowing integers with zero. Zero is also a legitimate residual or image
scale value. This can make unavailable data look like a real measurement.
Infinity is not handled consistently: it passes through the float conversion.

The two `zip(..., strict=False)` calls similarly allow arrays with different
lengths to be truncated without explanation.

For records trusted to be app-produced, broad fallback conversion and silent
truncation are questionable. `buildSaveData()` filters successful observations
and checks the saved/star-list lengths before writing
(`logic/controllers/model/modelRunSupport.py:81-94`).

Recommendation: establish the producer's contract for nullable numeric fields,
then simplify conversion to the supported cases. If `None` is meaningful, retain
it as an explicit missing-data policy rather than treating every conversion
failure as zero. Equal-length arrays generated from the same records should use
`strict=True`. Do not replace these fallbacks with another full-schema validator,
and do not remove legacy-null handling without checking supported saved files.

### 3. Low: dataset generation transposes fields that are never used

Location: `analyseData.py:61-81`.

`generateDataSets()` first constructs a list for every key in the first record,
including metadata, coordinates and unrelated fields. Only a fixed subset is
then used to populate plotting arrays. It also assumes every subsequent record
has every first-record key, including keys unrelated to the plots.

Recommendation: collect only the fields actually assigned, using direct list
comprehensions. Keep the explicit assignments for readability and retain the
integer dtypes and `errorIndex - 1` convention. A tiny local extraction helper
may be reasonable, but a registry of field descriptors is unnecessary for
thirteen arrays.

### 4. Low: Python annotations leave important contracts implicit

Locations: `analyseModel.py:44-51,237-260,354-365`,
`raDecPlots.py:38-45`, `altAzPlots.py:38`,
`analyseTypes.py:15-16,43-47`.

Functions are annotated, but `dict[str, Any]`, bare `np.ndarray`, arbitrary
`termCount: int` and free-form status/scope strings weaken the useful contracts.
For example, `compareSetups()` accepts any tuple length but indexes exactly two
distances. `designMatrix()` assumes an 11- or 22-column layout.

Recommendation:

- Give `analysisStatus` a `Literal["idle", "running", "ready", "failed"]` type.
- Express the two-candidate contract as a fixed pair, or accept named shared and
  split arguments. Keep unsupported recorded mount terms as an unavailable
  result; the internal fit repertoire is a different contract.
- Use `numpy.typing.NDArray` and `ArrayLike` where they improve clarity, especially
  the RA/DEC plotting helper's `x` and `y` arguments.
- Introduce a small `TypedDict` for loaded records only if it reduces meaningful
  `Any` usage. Do not introduce a runtime schema framework.

`TYPE_CHECKING` imports of `AnalyseWindow` are acceptable here. They are not
runtime circular dependencies and do not by themselves justify a protocol for
every component.

### 5. Low: analysis start has a caller-ordering requirement

Locations: `analyseW.py:114-123`, `analyseModel.py:53-62,100-104`.

The normal window path correctly calls `invalidateAnalysis()` before loading and
starting a new analysis. However, the public `startModelAnalysis()` method does
not advance the revision or clear old results/errors itself. Directly starting
another job without invalidation therefore reuses the same generation and can
temporarily expose a previous result/error.

This is not a failure of the current window path. It is an API invariant that
should be explicit now that `AnalyseModel` owns the lifecycle.

Recommendation: either document and test the required invalidate-before-start
sequence, or make public start begin a new generation itself and retain explicit
invalidation for failed loads/close. If changing this, avoid double revision
increments and retain the queued-error protection described below.

### 6. Low: small readability and maintenance leftovers

- `analyseW.py:91-112`: `d` and `de` obscure first/last record meaning; use
  `firstRecord` and `lastRecord`. The solver label is assigned twice, with the
  second assignment unconditionally replacing the first. Decide which recorded
  value is intended before removing the dead first write.
- `analyseModel.py:321-329`: the nested conditional assigning RMS comparison is
  valid Python but less readable than an ordinary unavailable/match/mismatch
  branch.
- `deriveAlignmentFeedback()` can overwrite an unresolved split-rule or
  unavailable-fit explanation with the excluded-sample explanation, and can
  overwrite it again for a negative recorded polar magnitude
  (`analyseModel.py:414-430`). Prefer accumulating independent reasons, as
  `compareAlignmentError()` already does, without building a diagnostics framework.
- `../tests/unit_tests/gui/extWindows/analyse/test_analyseModel.py` still contains
  `writeGui` and file-loading orchestration tests. Move those to
  `test_analyseW.py`; keep lifecycle and numerical tests with `analyseModel`.
- `PLAN_analyse_composition.md` contains successive, contradictory historical
  ownership proposals. Retain the final ownership diagram and clearly label or
  remove superseded proposals.

## Guard audit: keep, simplify or remove?

| Guard or fallback | Decision | Reason |
|---|---|---|
| Missing file checks before opening/loading | Keep | Cancellation and disappearing files are possible even with an app-written format |
| `OSError`/`JSONDecodeError` handling | Keep | Storage failures and interrupted writes are not schema questions |
| `modelJSON is None` after load | Keep | Explicitly stops UI updates and reconstruction after a logged load failure |
| Runtime schema-validation pass | Already removed; do not restore | Matches the requested trusted-producer contract |
| Broad zero substitution in `list2array()` | Simplify after producer-contract check | It mixes missing-data handling with silent conversion failure |
| `zip(..., strict=False)` for parallel plot arrays | Prefer strict alignment | All arrays originate from the same record list |
| No pending analysis / worker active | Keep | Completion can arrive with no queued load; requests can arrive while a job runs |
| `workerRebuildModel is None` | Keep | First-use worker setup connects the error callback before execution |
| Revision check on results/errors | Keep | Reload and close can invalidate a running job |
| Separate `analysisWorkerActive` flag | Keep | Worker lock release is not the same as delivery of queued GUI signals |
| Input snapshot via `deepcopy()` | Keep for now | The worker must not observe later mutation; optimize only with an immutable input contract |
| Finite values / coordinate limits | Keep relevant numerical checks | An app-written record does not guarantee a meaningful numerical observation |
| Missing/inconsistent recorded metadata | Keep | Missing reference values must not produce fabricated comparison matches |
| Duplicate-observation exclusion | Keep unless its scientific policy changes | Removing it changes the fit's weighting, not just defensive programming |
| Minimum observation count / full rank / SVD failure | Keep | Valid records can still produce an underconstrained or ill-conditioned fit |
| Excluded-sample comparison suppression | Keep | Comparing a subset against the mount's full sample can be misleading |
| Recorded zero alignment ambiguity | Keep while legacy encoding applies | Zero can mean unavailable, not necessarily perfect alignment |
| Unresolved 22-term alignment aggregation | Keep | No verified firmware combination rule exists |
| `sourceView == targetView` | Only needed by the current nested linker | A reference-view implementation can avoid the self-link case structurally |
| Horizon visibility check | Keep | It implements a UI choice, not input validation |

The worker distinction is particularly important:
`base/tpool.py:117-126` releases the worker lock before emitting `finished`.
Already emitted result/error signals may still be queued for the GUI thread.
Replacing `analysisWorkerActive` with only the lock state would reopen the race
where an old error is attributed to a newly started job. Existing
`test_undeliveredFailureDoesNotFailNewLoad` covers this behavior.

## Scientific behavior that must not be simplified away

The 11/22 repertoire, protocol rounding, residual direction, RMS normalization
and output-precision tolerances are domain behavior, not architectural clutter.
Preserve the file's authoritative `modelTerms`, especially 22 terms, regardless
of which candidate has the closer RMS.

The local polar/ortho mapping remains explicitly unverified against firmware
feedback. Per-side results must not be averaged merely to make the combined
22-term result easier to present. These limitations are already exposed in
typed results and diagnostics and should remain visible.

## Suggested cleanup order

The original architectural cleanup is implemented. Remaining work should proceed
in this order:

1. Preserve per-field missing-value masks in `AnalyseData` before legacy filling.
2. Apply filtering and missing-value presentation consistently across tabs,
   including missing counts, tooltips, color scales, contours, sorted errors and
   distributions.
3. Add mixed/all-missing and genuine-zero regression cases alongside those
   changes, verifying index and pier-side alignment after filtering.
4. Tighten remaining record and numerical-array types where useful.
5. Independently verify firmware alignment mapping and 22-term aggregation when
   suitable reference evidence is available. This work does not block the
   plotting improvements.

Avoid moving the numerical functions into static methods merely to place them
inside `AnalyseModel`: their current pure-function form is simpler to test and
keeps the worker controller distinct from the mathematics without another file.

## Review limitations

This review examines the current source, producer, worker contract and relevant
tests. It does not establish exact firmware equivalence or validate a new
view-link implementation. The previously completed package run had 100%
statement/branch coverage, but coverage alone does not establish correct GUI
event ordering, unloaded-state behavior or scientific equivalence. No source
changes or new test executions were required to write this review.
