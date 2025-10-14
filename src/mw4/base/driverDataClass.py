############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import logging

# external packages
from PySide6.QtCore import QObject, Signal

# local imports


class RemoteDeviceShutdown(QObject):
    """ """

    signalRemoteShutdown = Signal()


class DriverData:
    log = logging.getLogger("MW4")

    def storePropertyToData(self, value: str | float, element: str) -> None:
        """ """
        if value is None and element in self.data:
            del self.data[element]
        else:
            self.data[element] = value
