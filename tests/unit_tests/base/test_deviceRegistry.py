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
    app = App()
    dReg = DeviceRegistry(app)
    dReg.addDevices(app)
    return dReg


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


def test_deviceEntryModelPropertyRaisesWhenInstanceNone() -> None:
    entry = DeviceEntry(
        name="refraction", instance=None, deviceType=None, isConfigurable=False
    )
    with pytest.raises(AttributeError):
        _ = entry.model


def test_deviceEntryGeometryPropertyRaisesWhenInstanceNone() -> None:
    entry = DeviceEntry(
        name="refraction", instance=None, deviceType=None, isConfigurable=False
    )
    with pytest.raises(AttributeError):
        _ = entry.geometry


def test_deviceEntryFirmwarePropertyRaisesWhenInstanceNone() -> None:
    entry = DeviceEntry(
        name="refraction", instance=None, deviceType=None, isConfigurable=False
    )
    with pytest.raises(AttributeError):
        _ = entry.firmware


def test_deviceEntrySatellitePropertyRaisesWhenInstanceNone() -> None:
    entry = DeviceEntry(
        name="refraction", instance=None, deviceType=None, isConfigurable=False
    )
    with pytest.raises(AttributeError):
        _ = entry.satellite


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


# ------------------------------------------------------------------
# DeviceRegistry — two-phase initialization pattern
# ------------------------------------------------------------------
def test_initPhase1OnlyMountExists() -> None:
    """After __init__, only mount device exists."""
    app = App()
    dReg = DeviceRegistry(app)
    assert "mount" in dReg.drivers
    assert "camera" not in dReg.drivers
    assert "dome" not in dReg.drivers
    assert len(dReg.drivers) == 1


def test_initPhase2AllDevicesExist() -> None:
    """After addDevices(), all devices exist."""
    app = App()
    dReg = DeviceRegistry(app)
    dReg.addDevices(app)
    assert "mount" in dReg.drivers
    assert "camera" in dReg.drivers
    assert "dome" in dReg.drivers
    assert "refraction" in dReg.drivers
    assert len(dReg.drivers) > 1


def test_initPhase2MountAccessibleDuringAddDevices() -> None:
    """Mount is accessible during addDevices() for device initialization."""
    app = App()
    dReg = DeviceRegistry(app)
    assert app.mount is not None
    dReg.addDevices(app)
    assert dReg["mount"].instance is app.mount


def test_initProductionCreatesNewMount() -> None:
    """In production (no pre-existing mount), __init__ creates new MountDevice."""
    from mw4.mountcontrol.mount import MountDevice

    app = App()
    # Ensure app.mount doesn't exist before initialization
    if hasattr(app, "mount"):
        delattr(app, "mount")

    dReg = DeviceRegistry(app)

    # Assert mount was created
    assert hasattr(app, "mount")
    assert app.mount is not None
    assert isinstance(app.mount, MountDevice)
    # Assert mount entry is in registry
    assert "mount" in dReg.drivers
    assert dReg["mount"].instance is app.mount


def test_initTestModeMountsInjected() -> None:
    """In test mode (pre-existing mount), __init__ uses injected mount."""
    from mw4.mountcontrol.mount import MountDevice

    app = App()
    # Create a mock mount and inject it
    mock_mount = MountDevice(app, verbose=True)
    app.mount = mock_mount

    dReg = DeviceRegistry(app)

    # Assert the injected mount is used
    assert dReg["mount"].instance is mock_mount
    assert app.mount is mock_mount


