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
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture()
def registry() -> DeviceRegistry:
    return DeviceRegistry(App())


def test_initiallyNotEmpty(registry: DeviceRegistry) -> None:
    # DeviceRegistry now initializes with all drivers on construction
    assert "camera" in registry.drivers
    assert "dome" in registry.drivers
    assert "mount" in registry.drivers


def test_driversHaveRequiredFields(registry: DeviceRegistry) -> None:
    # arrange / act / assert
    for driver_name, driver_info in registry.drivers.items():
        assert isinstance(driver_info, dict)
        assert "class" in driver_info
        assert "deviceType" in driver_info
        assert "stat" in driver_info


def test_cameraDriverExists(registry: DeviceRegistry) -> None:
    # arrange / act / assert
    assert "camera" in registry.drivers
    camera_driver = registry.drivers["camera"]
    assert camera_driver["class"] is not None
    assert camera_driver["deviceType"] == "camera"


def test_domeDriverExists(registry: DeviceRegistry) -> None:
    # arrange / act / assert
    assert "dome" in registry.drivers
    dome_driver = registry.drivers["dome"]
    assert dome_driver["class"] is not None
    assert dome_driver["deviceType"] == "dome"


def test_mountDriverExists(registry: DeviceRegistry) -> None:
    # arrange / act / assert
    assert "mount" in registry.drivers
    mount_driver = registry.drivers["mount"]
    assert mount_driver["class"] is not None
