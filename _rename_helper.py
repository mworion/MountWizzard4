import pathlib

RENAMES = [
    ("getAndStoreAscomProperty", "getAndStoreDeviceProp"),
    ("getAscomProperty",         "getDeviceProp"),
    ("setAscomPropertyQueued",   "setDevicePropQueued"),
    ("setAscomProperty",         "setDeviceProp"),
    ("callAscomMethodQueued",    "callDeviceMethodQueued"),
    ("callAscomMethod",          "callDeviceMethod"),
]

ascom_files = [
    "src/mw4/logic/camera/cameraAscom.py",
    "src/mw4/logic/dome/domeAscom.py",
    "src/mw4/logic/focuser/focuserAscom.py",
    "src/mw4/logic/filter/filterAscom.py",
    "src/mw4/logic/cover/coverAscom.py",
    "src/mw4/logic/lightPanel/lightPanelAscom.py",
    "src/mw4/logic/environment/sensorWeatherAscom.py",
    "src/mw4/logic/telescope/telescopeAscom.py",
    "src/mw4/logic/powerswitch/pegasusUPBAscom.py",
]

for fpath in ascom_files:
    p = pathlib.Path(fpath)
    text = p.read_text()
    for old, new in RENAMES:
        text = text.replace(old, new)
    p.write_text(text)
    print(f"Updated: {fpath}")

alpaca_fix = [
    "src/mw4/logic/cover/coverAlpaca.py",
    "src/mw4/logic/lightPanel/lightPanelAlpaca.py",
]
for fpath in alpaca_fix:
    p = pathlib.Path(fpath)
    text = p.read_text()
    text = text.replace("self.alpacaSignals", "self.signals")
    p.write_text(text)
    print(f"Harmonised: {fpath}")

print("Done.")

