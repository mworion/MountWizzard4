# Plan: Fix Unittests for SettMisc, SettParkPos, SettRelay, and SettingWindow

## Issues Identified Across All Files

### Common Issues (All Files):
1. ✗ Generic fixture names ("function" instead of descriptive names)
2. ✗ Poor test naming (numeric suffixes)
3. ✗ Wrong config keys ("WindowMain" instead of correct keys)
4. ✗ Missing assertions in many tests
5. ✗ Tests just calling methods without verification

### Test Files to Fix:

#### 1. test_tabSettMisc.py (409 lines)
- Fixture: "function" → "settMisc"
- Config key: "WindowMain" → "SettingMisc" (line 40)
- Missing mock UI elements for sound widgets
- Tests need better assertions
- test_initConfig_1 needs to verify defaults
- Multiple tests (test_playSound_*) need proper setup

#### 2. test_tabSettParkPos.py (131 lines)  
- Fixture: "function" → "settParkPos"
- Config key: "WindowMain" → "SettingParkPos" (lines 38, 47)
- Bad test naming (test_slewParkPos_2 should be _fail_when_settarget_fails)
- Missing assertions on config storage
- test_initConfig tests need better descriptions

#### 3. test_tabSettRelay.py (121 lines)
- Fixture: "function" → "settRelay"
- No config key issue (good!)
- Bad test naming (test_toggleRelay_1 is too vague)
- test_updateRelayGui creates empty lists instead of proper setup
- Missing assertions for button state verification

#### 4. test_settingW.py (95 lines)
- Fixture: "function" → "settingWindow"
- Tests need more descriptive names
- test_initConfig_1 doesn't verify anything
- test_storeConfig needs to verify values are saved

## Implementation Plan

1. Fix all fixtures with descriptive names
2. Correct all config keys
3. Add helper functions for mock UI creation where needed
4. Improve test names with descriptive suffixes
5. Add comprehensive assertions
6. Add missing edge case tests
7. Verify 100% coverage on each

