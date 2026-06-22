############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10_micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2026 by mworion
# License APL2.0
#
###########################################################
import pytest
from mw4.base.deviceRegistry import DeviceEntry, DeviceRegistry
from pathlib import Path
from PySide6.QtCore import QThreadPool
from unittest import mock


@pytest.fixture()
def registry() -> DeviceRegistry:
    """Minimal registry for testing without full App initialization."""
    app = mock.MagicMock()
    app.mwGlob = {"tempDir": Path("/tmp")}
    app.msg = mock.MagicMock()
    app.threadPool = QThreadPool()
    app.threadPool.activeThreadCount = mock.MagicMock(return_value=0)
    dReg = DeviceRegistry(app)
    # Skip addDevices to avoid cascading initialization errors
    return dReg


# ------------------------------------------------------------------
# DeviceEntry — attribute access
# ------------------------------------------------------------------
def test_deviceEntryAttributes() -> None:
    entry = DeviceEntry(
        name="test", instance=object(), deviceType="camera", isConfigurable=True
    )
    assert entry.name == "test"
    assert entry.deviceType == "camera"
    assert entry.isConfigurable is True
    assert entry.stat is None


# ------------------------------------------------------------------
# DeviceEntry — convenience properties for instance attributes
# ------------------------------------------------------------------
def test_deviceEntrySignalsProperty() -> None:
    class MockInstance:
        def __init__(self):
            self.signals = "test_signals"

    entry = DeviceEntry(
        name="camera", instance=MockInstance(), deviceType="camera", isConfigurable=True
    )
    assert entry.signals == "test_signals"


def test_deviceEntryDataProperty() -> None:
    class MockInstance:
        def __init__(self):
            self.data = {"test_key": "test_value"}

    entry = DeviceEntry(
        name="camera", instance=MockInstance(), deviceType="camera", isConfigurable=True
    )
    assert entry.data == {"test_key": "test_value"}


def test_deviceEntryRunProperty() -> None:
    class MockInstance:
        def __init__(self):
            self.run = {"indi": "device_driver"}

    entry = DeviceEntry(
        name="camera", instance=MockInstance(), deviceType="camera", isConfigurable=True
    )
    assert entry.run == {"indi": "device_driver"}


def test_deviceEntryObsSiteProperty() -> None:
    class MockObsSite:
        pass

    class MockInstance:
        def __init__(self):
            self.obsSite = MockObsSite()

    entry = DeviceEntry(
        name="mount", instance=MockInstance(), deviceType=None, isConfigurable=False
    )
    assert isinstance(entry.obsSite, MockObsSite)


def test_deviceEntrySettingProperty() -> None:
    class MockSetting:
        pass

    class MockInstance:
        def __init__(self):
            self.setting = MockSetting()

    entry = DeviceEntry(
        name="mount", instance=MockInstance(), deviceType=None, isConfigurable=False
    )
    assert isinstance(entry.setting, MockSetting)


def test_deviceEntryLocationProperty() -> None:
    class MockLocation:
        pass

    class MockObsSite:
        def __init__(self):
            self.location = MockLocation()

    class MockInstance:
        def __init__(self):
            self.obsSite = MockObsSite()

    entry = DeviceEntry(
        name="mount", instance=MockInstance(), deviceType=None, isConfigurable=False
    )
    assert isinstance(entry.location, MockLocation)


def test_deviceEntryTimeJDProperty() -> None:
    class MockTimeJD:
        pass

    class MockObsSite:
        def __init__(self):
            self.timeJD = MockTimeJD()

    class MockInstance:
        def __init__(self):
            self.obsSite = MockObsSite()

    entry = DeviceEntry(
        name="mount", instance=MockInstance(), deviceType=None, isConfigurable=False
    )
    assert isinstance(entry.timeJD, MockTimeJD)


def test_deviceEntryModelProperty() -> None:
    class MockModel:
        pass

    class MockInstance:
        def __init__(self):
            self.model = MockModel()

    entry = DeviceEntry(
        name="mount", instance=MockInstance(), deviceType=None, isConfigurable=False
    )
    assert isinstance(entry.model, MockModel)


def test_deviceEntryGeometryProperty() -> None:
    class MockGeometry:
        pass

    class MockInstance:
        def __init__(self):
            self.geometry = MockGeometry()

    entry = DeviceEntry(
        name="mount", instance=MockInstance(), deviceType=None, isConfigurable=False
    )
    assert isinstance(entry.geometry, MockGeometry)


def test_deviceEntryFirmwareProperty() -> None:
    class MockFirmware:
        pass

    class MockInstance:
        def __init__(self):
            self.firmware = MockFirmware()

    entry = DeviceEntry(
        name="mount", instance=MockInstance(), deviceType=None, isConfigurable=False
    )
    assert isinstance(entry.firmware, MockFirmware)


def test_deviceEntryFrameworkProperty() -> None:
    class MockFramework:
        pass

    class MockInstance:
        def __init__(self):
            self.framework = "indi"

    entry = DeviceEntry(
        name="camera", instance=MockInstance(), deviceType="camera", isConfigurable=True
    )
    assert entry.framework == "indi"


def test_deviceEntrySatelliteProperty() -> None:
    class MockSatellite:
        pass

    class MockInstance:
        def __init__(self):
            self.satellite = MockSatellite()

    entry = DeviceEntry(
        name="mount", instance=MockInstance(), deviceType=None, isConfigurable=False
    )
    assert isinstance(entry.satellite, MockSatellite)


def test_deviceEntryNoneInstanceRunProperty() -> None:
    entry = DeviceEntry(name="test", instance=None, deviceType="camera", isConfigurable=True)
    with pytest.raises(AttributeError, match="Device 'test' instance is None"):
        _ = entry.run


def test_deviceEntryNoneInstanceFrameworkProperty() -> None:
    entry = DeviceEntry(name="test", instance=None, deviceType="camera", isConfigurable=True)
    with pytest.raises(AttributeError, match="Device 'test' instance is None"):
        _ = entry.framework


def test_deviceEntryConfigProperty() -> None:
    """Test config property returns config from run[framework]."""

    class MockConfig:
        value = "test_config"

    class MockFramework:
        def __init__(self):
            self.config = MockConfig()

    class MockInstance:
        def __init__(self):
            self.framework = "indi"
            self.run = {"indi": MockFramework()}

    entry = DeviceEntry(
        name="camera", instance=MockInstance(), deviceType="camera", isConfigurable=True
    )
    assert entry.config.value == "test_config"


# ------------------------------------------------------------------
# DeviceEntry — error handling for None instance
# ------------------------------------------------------------------
def test_deviceEntryNoneInstanceSignalsProperty() -> None:
    entry = DeviceEntry(name="test", instance=None, deviceType="camera", isConfigurable=True)
    with pytest.raises(AttributeError, match="Device 'test' instance is None"):
        _ = entry.signals


def test_deviceEntryNoneInstanceDataProperty() -> None:
    entry = DeviceEntry(name="test", instance=None, deviceType="camera", isConfigurable=True)
    with pytest.raises(AttributeError, match="Device 'test' instance is None"):
        _ = entry.data


def test_deviceEntryNoneInstanceObsSiteProperty() -> None:
    entry = DeviceEntry(name="test", instance=None, deviceType=None, isConfigurable=False)
    with pytest.raises(AttributeError, match="Device 'test' instance is None"):
        _ = entry.obsSite


def test_deviceEntryNoneInstanceSettingProperty() -> None:
    entry = DeviceEntry(name="test", instance=None, deviceType=None, isConfigurable=False)
    with pytest.raises(AttributeError, match="Device 'test' instance is None"):
        _ = entry.setting


def test_deviceEntryNoneInstanceLocationProperty() -> None:
    entry = DeviceEntry(name="test", instance=None, deviceType=None, isConfigurable=False)
    with pytest.raises(AttributeError, match="Device 'test' instance is None"):
        _ = entry.location


def test_deviceEntryNoneInstanceTimeJDProperty() -> None:
    entry = DeviceEntry(name="test", instance=None, deviceType=None, isConfigurable=False)
    with pytest.raises(AttributeError, match="Device 'test' instance is None"):
        _ = entry.timeJD


def test_deviceEntryNoneInstanceModelProperty() -> None:
    entry = DeviceEntry(name="test", instance=None, deviceType=None, isConfigurable=False)
    with pytest.raises(AttributeError, match="Device 'test' instance is None"):
        _ = entry.model


def test_deviceEntryNoneInstanceGeometryProperty() -> None:
    entry = DeviceEntry(name="test", instance=None, deviceType=None, isConfigurable=False)
    with pytest.raises(AttributeError, match="Device 'test' instance is None"):
        _ = entry.geometry


def test_deviceEntryNoneInstanceFirmwareProperty() -> None:
    entry = DeviceEntry(name="test", instance=None, deviceType=None, isConfigurable=False)
    with pytest.raises(AttributeError, match="Device 'test' instance is None"):
        _ = entry.firmware


def test_deviceEntryNoneInstanceSatelliteProperty() -> None:
    entry = DeviceEntry(name="test", instance=None, deviceType=None, isConfigurable=False)
    with pytest.raises(AttributeError, match="Device 'test' instance is None"):
        _ = entry.satellite


def test_deviceEntryNoneInstanceConfigProperty() -> None:
    entry = DeviceEntry(name="test", instance=None, deviceType="camera", isConfigurable=True)
    with pytest.raises(AttributeError, match="Device 'test' instance is None"):
        _ = entry.config


# ------------------------------------------------------------------
# DeviceEntry — multiple properties on same entry
# ------------------------------------------------------------------
def test_deviceEntryMultipleProperties() -> None:
    """Test accessing multiple properties on the same entry."""

    class MockConfig:
        hostAddress = "192.168.1.1"

    class MockFramework:
        def __init__(self):
            self.config = MockConfig()

    class MockObsSite:
        def __init__(self):
            self.location = "Observatory"
            self.timeJD = 2459000

    class MockInstance:
        def __init__(self):
            self.signals = "camera_signals"
            self.data = {"exposure": 1.0}
            self.run = {"indi": MockFramework()}
            self.framework = "indi"
            self.obsSite = MockObsSite()
            self.model = "ModelX"
            self.geometry = "GeometryY"
            self.firmware = "FirmwareZ"
            self.satellite = "SatelliteW"

    entry = DeviceEntry(
        name="camera", instance=MockInstance(), deviceType="camera", isConfigurable=True
    )

    assert entry.signals == "camera_signals"
    assert entry.data == {"exposure": 1.0}
    assert "indi" in entry.run
    assert entry.run["indi"].config.hostAddress == "192.168.1.1"
    assert entry.framework == "indi"
    assert entry.obsSite.location == "Observatory"
    assert entry.config.hostAddress == "192.168.1.1"
    assert entry.model == "ModelX"
    assert entry.geometry == "GeometryY"
    assert entry.firmware == "FirmwareZ"
    assert entry.satellite == "SatelliteW"


# ------------------------------------------------------------------
# DeviceEntry — stat field variations
# ------------------------------------------------------------------
def test_deviceEntryStatFieldNone() -> None:
    entry = DeviceEntry(
        name="test", instance=object(), deviceType="camera", isConfigurable=True, stat=None
    )
    assert entry.stat is None


def test_deviceEntryStatFieldTrue() -> None:
    entry = DeviceEntry(
        name="test", instance=object(), deviceType="camera", isConfigurable=True, stat=True
    )
    assert entry.stat is True


def test_deviceEntryStatFieldFalse() -> None:
    entry = DeviceEntry(
        name="test", instance=object(), deviceType="camera", isConfigurable=True, stat=False
    )
    assert entry.stat is False
