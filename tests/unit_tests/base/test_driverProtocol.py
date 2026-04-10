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
# Licence APL2.0
#
###########################################################
"""Unit tests for mw4.base.driverProtocol.DriverProtocol."""
import pytest
from typing import Protocol, get_protocol_members, runtime_checkable
from mw4.base.driverProtocol import DriverProtocol


# ---------------------------------------------------------------------------
# Concrete stubs used across tests
# ---------------------------------------------------------------------------

class FullyConformingDriver:
    """Implements every attribute and method required by DriverProtocol."""

    deviceConnected: bool = False
    serverConnected: bool = False
    defaultConfig: dict = {}
    data: dict = {}

    def startCommunication(self) -> None:
        pass

    def stopCommunication(self) -> None:
        pass

    def discoverDevices(self, deviceType: str) -> list:
        return []

    def pollData(self) -> None:
        pass

    def pollStatus(self) -> None:
        pass

    def processPolledData(self) -> None:
        pass

    def getInitialConfig(self) -> None:
        pass


class MethodsOnlyDriver:
    """Has all required methods but no data attributes."""

    def startCommunication(self) -> None:
        pass

    def stopCommunication(self) -> None:
        pass

    def discoverDevices(self, deviceType: str) -> list:
        return []

    def pollData(self) -> None:
        pass

    def pollStatus(self) -> None:
        pass

    def processPolledData(self) -> None:
        pass

    def getInitialConfig(self) -> None:
        pass


class MissingMethodDriver:
    """Missing stopCommunication — should fail isinstance check."""

    deviceConnected: bool = False
    serverConnected: bool = False
    defaultConfig: dict = {}
    data: dict = {}

    def startCommunication(self) -> None:
        pass

    # stopCommunication intentionally omitted

    def discoverDevices(self, deviceType: str) -> list:
        return []

    def pollData(self) -> None:
        pass

    def pollStatus(self) -> None:
        pass

    def processPolledData(self) -> None:
        pass

    def getInitialConfig(self) -> None:
        pass


class EmptyDriver:
    """No methods, no attributes."""
    pass


# ---------------------------------------------------------------------------
# Tests: protocol structure
# ---------------------------------------------------------------------------

def test_driver_protocol_is_a_protocol():
    """DriverProtocol must be a subclass of Protocol."""
    assert issubclass(DriverProtocol, Protocol)


def test_driver_protocol_is_runtime_checkable():
    """DriverProtocol must be decorated with @runtime_checkable."""
    # If not runtime_checkable, isinstance raises TypeError
    try:
        isinstance(object(), DriverProtocol)
    except TypeError:
        pytest.fail("DriverProtocol is not @runtime_checkable")


# ---------------------------------------------------------------------------
# Tests: required data-attribute annotations
# ---------------------------------------------------------------------------

EXPECTED_ANNOTATIONS = {"deviceConnected", "serverConnected", "defaultConfig", "data"}


def test_protocol_declares_device_connected():
    assert "deviceConnected" in DriverProtocol.__annotations__


def test_protocol_declares_server_connected():
    assert "serverConnected" in DriverProtocol.__annotations__


def test_protocol_declares_default_config():
    assert "defaultConfig" in DriverProtocol.__annotations__


def test_protocol_declares_data():
    assert "data" in DriverProtocol.__annotations__


def test_protocol_has_all_expected_annotations():
    assert EXPECTED_ANNOTATIONS <= set(DriverProtocol.__annotations__)


# ---------------------------------------------------------------------------
# Tests: required method members
# ---------------------------------------------------------------------------

EXPECTED_METHODS = {
    "startCommunication",
    "stopCommunication",
    "discoverDevices",
    "pollData",
    "pollStatus",
    "processPolledData",
    "getInitialConfig",
}


def test_protocol_members_contain_all_methods():
    members = set(get_protocol_members(DriverProtocol))
    assert EXPECTED_METHODS <= members, (
        f"Missing protocol members: {EXPECTED_METHODS - members}"
    )


@pytest.mark.parametrize("method_name", sorted(EXPECTED_METHODS))
def test_protocol_has_method(method_name):
    assert hasattr(DriverProtocol, method_name), (
        f"DriverProtocol is missing method: {method_name}"
    )


# ---------------------------------------------------------------------------
# Tests: isinstance checks (runtime_checkable behaviour)
# ---------------------------------------------------------------------------

def test_isinstance_fully_conforming_driver():
    """A class with all methods passes the isinstance check."""
    obj = FullyConformingDriver()
    assert isinstance(obj, DriverProtocol)


def test_isinstance_methods_only_driver():
    """Since Python 3.12 runtime_checkable also checks data attributes,
    so a class missing the required data attributes must fail isinstance."""
    obj = MethodsOnlyDriver()
    assert not isinstance(obj, DriverProtocol)


def test_isinstance_missing_method_driver():
    """A class missing any required method must fail the isinstance check."""
    obj = MissingMethodDriver()
    assert not isinstance(obj, DriverProtocol)


def test_isinstance_empty_driver():
    """A class with no members must fail the isinstance check."""
    obj = EmptyDriver()
    assert not isinstance(obj, DriverProtocol)


def test_isinstance_plain_object():
    """A raw object instance must fail the isinstance check."""
    assert not isinstance(object(), DriverProtocol)


# ---------------------------------------------------------------------------
# Tests: conforming class used as return value / type annotation
# ---------------------------------------------------------------------------

def test_discover_devices_returns_list():
    drv = FullyConformingDriver()
    result = drv.discoverDevices("camera")
    assert isinstance(result, list)


def test_fully_conforming_attributes_types():
    drv = FullyConformingDriver()
    assert isinstance(drv.deviceConnected, bool)
    assert isinstance(drv.serverConnected, bool)
    assert isinstance(drv.defaultConfig, dict)
    assert isinstance(drv.data, dict)

