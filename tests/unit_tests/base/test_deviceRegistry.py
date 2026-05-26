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
from mw4.base.deviceRegistry import DeviceRegistry


@pytest.fixture()
def registry() -> DeviceRegistry:
    return DeviceRegistry()


def test_initiallyEmpty(registry: DeviceRegistry) -> None:
    # arrange / act / assert
    assert registry.getDrivers() == {}


def test_updateAndGet(registry: DeviceRegistry) -> None:
    # arrange
    drivers = {"camera": {"class": object()}}
    # act
    registry.update(drivers)
    # assert – same object reference (no copy is made)
    assert registry.getDrivers() is drivers


def test_updateReplacesMapping(registry: DeviceRegistry) -> None:
    # arrange
    registry.update({"camera": {}})
    newDrivers = {"dome": {}}
    # act
    registry.update(newDrivers)
    # assert
    assert registry.getDrivers() is newDrivers
    assert "camera" not in registry.getDrivers()


def test_mutationOfOriginalDictIsVisible(registry: DeviceRegistry) -> None:
    # The registry holds a reference, not a copy.
    # In-place mutations made by SettDevice are immediately visible
    # to logic-layer consumers.
    # arrange
    drivers: dict = {}
    registry.update(drivers)
    # act – simulate SettDevice adding an entry after __init__
    drivers["focuser"] = {"class": object()}
    # assert
    assert "focuser" in registry.getDrivers()


def test_updateWithEmptyDict(registry: DeviceRegistry) -> None:
    # arrange
    registry.update({"camera": {}})
    # act
    registry.update({})
    # assert
    assert registry.getDrivers() == {}


def test_getDriversReturnsAllKeys(registry: DeviceRegistry) -> None:
    # arrange
    drivers = {
        "camera": {"class": object()},
        "dome": {"class": object()},
        "focuser": {"class": object()},
    }
    # act
    registry.update(drivers)
    result = registry.getDrivers()
    # assert
    assert set(result.keys()) == {"camera", "dome", "focuser"}
