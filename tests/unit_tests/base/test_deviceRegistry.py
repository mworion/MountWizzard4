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
# DeviceEntry — legacy dict-style access (backward compatibility)
# ------------------------------------------------------------------
def test_deviceEntryLegacyGetItem() -> None:
    obj = object()
    entry = DeviceEntry(
        name="test", instance=obj, deviceType="camera", isConfigurable=True, stat=True
    )
    assert entry["class"] is obj
    assert entry["deviceType"] == "camera"
    assert entry["stat"] is True


def test_deviceEntryLegacySetItem() -> None:
    entry = DeviceEntry(name="test", instance=None, deviceType=None, isConfigurable=True)
    entry["stat"] = True
    assert entry.stat is True
    entry["class"] = "new"
    assert entry.instance == "new"
    entry["deviceType"] = "dome"
    assert entry.deviceType == "dome"


def test_deviceEntryLegacySetItemUnknownKeyRaises() -> None:
    entry = DeviceEntry(name="x", instance=None, deviceType=None, isConfigurable=True)
    with pytest.raises(KeyError):
        entry["unknown"] = 1


def test_deviceEntryLegacyGetItemUnknownKeyRaises() -> None:
    entry = DeviceEntry(name="x", instance=None, deviceType=None, isConfigurable=True)
    with pytest.raises(KeyError):
        _ = entry["unknown"]


def test_deviceEntryContains() -> None:
    entry = DeviceEntry(name="x", instance=None, deviceType=None, isConfigurable=True)
    assert "class" in entry
    assert "deviceType" in entry
    assert "stat" in entry
    assert "unknown" not in entry


def test_deviceEntryGet() -> None:
    entry = DeviceEntry(name="x", instance="inst", deviceType="t", isConfigurable=True)
    assert entry.get("class") == "inst"
    assert entry.get("missing") is None
    assert entry.get("missing", 42) == 42



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


def test_setStatReflectedInLegacyAccess(registry: DeviceRegistry) -> None:
    registry.setStat("dome", True)
    assert registry.drivers["dome"]["stat"] is True



