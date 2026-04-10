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
"""Structural protocol that every driver adapter must satisfy.

AlpacaClass, AscomClass, NINAClass, and SGProClass all implement this
contract.  Declaring it as a ``typing.Protocol`` (PEP 544) lets type
checkers verify that the strategy dicts used in device logic classes
(``Camera.run``, ``Dome.run``, etc.) are properly typed without
introducing a concrete inheritance hierarchy.
"""
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class DriverProtocol(Protocol):
    """Structural type for all driver adapter classes."""

    deviceConnected: bool
    serverConnected: bool
    defaultConfig: dict[str, Any]
    data: dict[str, Any]

    def startCommunication(self) -> None:
        """Establish connection to the device server."""
        ...

    def stopCommunication(self) -> None:
        """Disconnect from the device server and clean up."""
        ...

    def discoverDevices(self, deviceType: str) -> list:
        """Return a list of discovered device name strings."""
        ...

    def pollData(self) -> None:
        """Trigger an asynchronous device-data poll cycle."""
        ...

    def pollStatus(self) -> None:
        """Trigger an asynchronous connection-status poll cycle."""
        ...

    def processPolledData(self) -> None:
        """Process data returned by the most recent poll worker."""
        ...

    def getInitialConfig(self) -> None:
        """Read and store driver metadata after first connection."""
        ...

