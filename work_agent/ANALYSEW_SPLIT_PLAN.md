# Plan: split analyseW.py

Move `extWindows/analyseW.py` to the package `extWindows/analyse/`:

- `analyseW.py`: `AnalyseWindow(AnalyseDataMixin, AnalysePlotsMixin, MWidget)`
  with init, config, window handling, `loadModel`, `showAnalyse`, `drawAll`.
- `analyseData.py`: `AnalyseDataMixin` with `MODEL_DATA_KEYS`, `writeGui`,
  `list2array`, `validateModelData`, `generateDataSets`, `processModel`.
- `analysePlots.py`: `AnalysePlotsMixin` with all `draw*` and `linkViews*`
  methods. Duplicated RA/DEC reference charts and link methods are merged
  into shared helpers (`drawRaRef`, `drawDecRef`, `linkViews`).

Public method names stay unchanged. Tests move to
`../tests/unit_tests/gui/extWindows/analyse` (one module per file), imports
are updated in `externalWindows.py`. Finish with ruff, lint-imports and
100 % coverage of the new package.
