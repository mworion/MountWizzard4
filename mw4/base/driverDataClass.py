############################################################
# -*- coding: utf-8 -*-
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PySide for python
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
from typing import Union

# external packages
from PySide6.QtCore import Signal, QObject

# local imports


class RemoteDeviceShutdown(QObject):
    """ """

    signalRemoteShutdown = Signal()


class DriverData:
    log = logging.getLogger("MW4")

    def storePropertyToData(self, value: Union[str, float], element: str) -> None:
        """ """
        if value is None and element in self.data:
            del self.data[element]
        else:
            self.data[element] = value
