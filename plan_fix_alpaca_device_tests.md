# Plan: Fix All *Alpaca Device Unit Tests

## Date: 2026-05-23

## Root Cause

Every `*Alpaca` class now reads `parent.DEVICE_TYPE` (uppercase class
constant) inside `__init__`. All test `Parent` fixtures only define
`deviceType` (lowercase instance attribute) — so construction fails with
`AttributeError: 'Parent' object has no attribute 'DEVICE_TYPE'`.

Additionally, each `*Alpaca` class gained a `startCommunication` override
whose two branches are not covered by any existing test.

---

## Changes Required per Test File

| Test file | Add to Parent | startCommunication tests to add |
|-----------|--------------|--------------------------------|
| `test_cameraAlpaca.py` | already OK (uses `Camera` which has `DEVICE_TYPE`) | add tests |
| `test_coverAlpaca.py` | `DEVICE_TYPE = "cover"` | add tests |
| `test_domeAlpaca.py` | `DEVICE_TYPE = "dome"` | add tests |
| `test_sensorWeatherAlpaca.py` | `DEVICE_TYPE = "observingconditions"` | add tests |
| `test_filterAlpaca.py` | `DEVICE_TYPE = "filterwheel"` | add tests |
| `test_focuserAlpaca.py` | `DEVICE_TYPE = "focuser"` | add tests |
| `test_lightPanelAlpaca.py` | `DEVICE_TYPE = "covercalibrator"` | add tests |
| `test_pegasusUPBAlpaca.py` | `DEVICE_TYPE = "switch"` | add tests |
| `test_telescopeAlpaca.py` | `DEVICE_TYPE = "telescope"` | add tests |

## startCommunication test pattern (per file)

```python
def test_startCommunication_1(function):
    # createAlpacaDevice returns False -> emit error and return
    with mock.patch.object(function, "createAlpacaDevice", return_value=False):
        with mock.patch.object(function.threadPool, "start") as m_start:
            function.startCommunication()
            m_start.assert_not_called()

def test_startCommunication_2(function):
    # createAlpacaDevice returns True -> delegate to super
    with mock.patch.object(function, "createAlpacaDevice", return_value=True):
        with mock.patch.object(function.threadPool, "start") as m_start:
            function.startCommunication()
            m_start.assert_called_once()
```

