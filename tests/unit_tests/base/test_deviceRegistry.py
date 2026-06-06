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
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture()
def registry() -> DeviceRegistry:
    return DeviceRegistry(App())


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


def test_deviceEntryFrameworkProperty() -> None:
    class MockInstance:
        def __init__(self):
            self.framework = "indi"

    entry = DeviceEntry(
        name="camera", instance=MockInstance(), deviceType="camera", isConfigurable=True
    )
    assert entry.framework == "indi"


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


def test_deviceEntrySignalsPropertyRaisesWhenInstanceNone() -> None:
    entry = DeviceEntry(
        name="refraction", instance=None, deviceType=None, isConfigurable=False
    )
    with pytest.raises(AttributeError):
        _ = entry.signals


def test_deviceEntryDataPropertyRaisesWhenInstanceNone() -> None:
    entry = DeviceEntry(
        name="refraction", instance=None, deviceType=None, isConfigurable=False
    )
    with pytest.raises(AttributeError):
        _ = entry.data


def test_deviceEntryObsSitePropertyRaisesWhenInstanceNone() -> None:
    entry = DeviceEntry(
        name="refraction", instance=None, deviceType=None, isConfigurable=False
    )
    with pytest.raises(AttributeError):
        _ = entry.obsSite


def test_deviceEntrySettingPropertyRaisesWhenInstanceNone() -> None:
    entry = DeviceEntry(
        name="refraction", instance=None, deviceType=None, isConfigurable=False
    )
    with pytest.raises(AttributeError):
        _ = entry.setting


def test_deviceEntryLocationPropertyRaisesWhenInstanceNone() -> None:
    entry = DeviceEntry(
        name="refraction", instance=None, deviceType=None, isConfigurable=False
    )
    with pytest.raises(AttributeError):
        _ = entry.location


def test_deviceEntryTimeJDPropertyRaisesWhenInstanceNone() -> None:
    entry = DeviceEntry(
        name="refraction", instance=None, deviceType=None, isConfigurable=False
    )
    with pytest.raises(AttributeError):
        _ = entry.timeJD


# ------------------------------------------------------------------
# DeviceRegistry — population
# ------------------------------------------------------------------
def test_initiallyNotEmpty(registry: DeviceRegistry) -> None:
    assert "camera" in registry.drivers
    assert "dome" in registry.drivers
    assert "mount" in registry.drivers


def test_driversHaveRequiredFields(registry: DeviceRegistry) -> None:
    for name, entry in registry.drivers.items():
        assert isinstance(entry, DeviceEntry)
        assert entry.name == name
        assert hasattr(entry, "instance")
        assert hasattr(entry, "deviceType")
        assert hasattr(entry, "stat")
        assert hasattr(entry, "isConfigurable")


def test_cameraDriverExists(registry: DeviceRegistry) -> None:
    assert "camera" in registry.drivers
    entry = registry.drivers["camera"]
    assert entry.instance is not None
    assert entry.deviceType == "camera"
    assert entry.isConfigurable is True


def test_domeDriverExists(registry: DeviceRegistry) -> None:
    assert "dome" in registry.drivers
    entry = registry.drivers["dome"]
    assert entry.instance is not None
    assert entry.deviceType == "dome"
    assert entry.isConfigurable is True


def test_mountDriverExists(registry: DeviceRegistry) -> None:
    assert "mount" in registry.drivers
    entry = registry.drivers["mount"]
    assert entry.instance is not None
    assert entry.isConfigurable is False


def test_refractionIsNotConfigurable(registry: DeviceRegistry) -> None:
    entry = registry.drivers["refraction"]
    assert entry.instance is None
    assert entry.isConfigurable is False


# ------------------------------------------------------------------
# DeviceRegistry — mapping protocol
# ------------------------------------------------------------------
def test_registryGetItem(registry: DeviceRegistry) -> None:
    entry = registry["camera"]
    assert isinstance(entry, DeviceEntry)
    assert entry.name == "camera"


def test_registryContains(registry: DeviceRegistry) -> None:
    assert "camera" in registry
    assert "nonexistent" not in registry


def test_registryIter(registry: DeviceRegistry) -> None:
    names = list(registry)
    assert "camera" in names
    assert "mount" in names
    assert "refraction" in names


# ------------------------------------------------------------------
# DeviceRegistry — configurable() iterator
# ------------------------------------------------------------------
def test_configurableExcludesMount(registry: DeviceRegistry) -> None:
    names = [e.name for e in registry.configurable()]
    assert "mount" not in names


def test_configurableExcludesRefraction(registry: DeviceRegistry) -> None:
    names = [e.name for e in registry.configurable()]
    assert "refraction" not in names


def test_configurableIncludesCamera(registry: DeviceRegistry) -> None:
    names = [e.name for e in registry.configurable()]
    assert "camera" in names


def test_configurableAllHaveInstance(registry: DeviceRegistry) -> None:
    for entry in registry.configurable():
        assert entry.instance is not None


# ------------------------------------------------------------------
# DeviceRegistry — setStat()
# ------------------------------------------------------------------
def test_setStatTrue(registry: DeviceRegistry) -> None:
    registry.setStat("camera", True)
    assert registry.drivers["camera"].stat is True


def test_setStatFalse(registry: DeviceRegistry) -> None:
    registry.setStat("mount", False)
    assert registry.drivers["mount"].stat is False


def test_setStatNone(registry: DeviceRegistry) -> None:
    registry.setStat("refraction", None)
    assert registry.drivers["refraction"].stat is None
