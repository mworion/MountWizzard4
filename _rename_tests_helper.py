import pathlib

# Rename old ASCOM method names in test mocks / assertions
RENAMES = [
    ("getAndStoreAscomProperty", "getAndStoreDeviceProp"),
    ("getAscomProperty",         "getDeviceProp"),
    ("setAscomPropertyQueued",   "setDevicePropQueued"),
    ("setAscomProperty",         "setDeviceProp"),
    ("callAscomMethodQueued",    "callDeviceMethodQueued"),
    ("callAscomMethod",          "callDeviceMethod"),
    # import fix
    ("from mw4.base.ascomClass import AscomClass, CommandItem",
     "from mw4.base.ascomClass import AscomClass\nfrom mw4.base.alpacaAscomCommon import CommandItem"),
]

test_files = [
    "tests/unit_tests/logic/camera/test_cameraAscom.py",
    "tests/unit_tests/logic/dome/test_domeAscom.py",
    "tests/unit_tests/logic/focuser/test_focuserAscom.py",
    "tests/unit_tests/logic/filter/test_filterAscom.py",
    "tests/unit_tests/logic/cover/test_coverAscom.py",
    "tests/unit_tests/logic/lightPanel/test_lightPanelAscom.py",
    "tests/unit_tests/logic/environment/test_sensorWeatherAscom.py",
    "tests/unit_tests/logic/telescope/test_telescopeAscom.py",
    "tests/unit_tests/logic/powerswitch/test_pegasusUPBAscom.py",
]

for fpath in test_files:
    p = pathlib.Path(fpath)
    if not p.exists():
        print(f"MISSING: {fpath}")
        continue
    text = p.read_text()
    for old, new in RENAMES:
        text = text.replace(old, new)
    p.write_text(text)
    print(f"Updated: {fpath}")

# Fix alpacaSignals in coverAlpaca and lightPanelAlpaca test files
alpaca_test_fix = [
    "tests/unit_tests/logic/cover/test_coverAlpaca.py",
    "tests/unit_tests/logic/lightPanel/test_lightPanelAlpaca.py",
]
for fpath in alpaca_test_fix:
    p = pathlib.Path(fpath)
    if not p.exists():
        print(f"MISSING: {fpath}")
        continue
    text = p.read_text()
    text = text.replace("alpacaSignals", "signals")
    p.write_text(text)
    print(f"Harmonised: {fpath}")

print("Done.")

