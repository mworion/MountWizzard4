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
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import logging

# external packages
from PySide6.QtCore import Signal, QObject

# local imports


class RemoteDeviceShutdown(QObject):
    """ """

    signalRemoteShutdown = Signal()


class DriverData:
    log = logging.getLogger("MW4")

    def storePropertyToData(self, value, element, elementInv=None):
        """
        :param value:
        :param element:
        :param elementInv:
        :return: reset entry
        """
        removeElement = value is None

        if removeElement and element in self.data:
            del self.data[element]

        if removeElement and elementInv is not None:
            if elementInv in self.data:
                del self.data[elementInv]

        if removeElement:
            return False

        self.data[element] = value

        if elementInv is not None:
            self.data[elementInv] = value

        return True
