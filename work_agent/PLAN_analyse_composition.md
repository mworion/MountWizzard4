# Analyse composition and review improvements

## Final ownership

- `AnalyseWindow(MWidget)` owns UI/configuration and coordinates loading/display.
- `AnalyseData` owns file reading, dataset generation and plot arrays.
- `AnalyseModel(QObject)` owns reconstruction snapshots, revisions, workers,
  results and diagnostics; numerical functions remain pure module functions.
- `GeneralPlots`, `AltAzPlots`, `RaDecPlots` own independent tab drawing.
- `plotHelpers.py` provides shared palette coloring and view linking.
- `analyseTypes.py` defines immutable results.

## Review implementation plan

1. Gate window redraws before plot data exists; keep palette updates available.
2. Link views to one reference, verifying synchronization from every member.
3. Extract only plotted fields; retain logged legacy null/NaN replacement but
   reject invalid conversions/infinities instead of silently fabricating zeros.
   Enforce equal-length plot arrays with strict zip.
4. Make public analysis start invalidate previous generations itself; keep
   invalidation for close and failed loads without double increments on success.
5. Tighten lifecycle, supported-term and plotting types; clarify RMS comparison,
   record names and solver display. Accumulate independent diagnostic reasons.
6. Put tests with their owners and document the new behavior. Preserve all
   numerical formulas, mount-truth rules and asynchronous signal guards.

## Validation

Cover unloaded GUI events, linked panning, dataset contracts and repeated starts.
Run focused tests to 100% branch coverage, Ruff, typing and import contracts.
Finish with the full package test suite at 100% coverage.
