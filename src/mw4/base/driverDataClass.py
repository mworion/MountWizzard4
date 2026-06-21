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
############################################################
import logging
from PySide6.QtCore import QObject, Signal
from collections.abc import Any


class RemoteDeviceShutdown(QObject):
    signalRemoteShutdown = Signal()


class DriverData:
    log = logging.getLogger("MW4")

    def __init__(self, data: dict) -> None:
        self.data: dict = data

    def storePropertyToData(self, value: Any, element: str) -> None:
        if value is None and element in self.data:
            del self.data[element]
        else:
            self.data[element] = value
