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

# external packages
from PySide6.QtCore import QObject, Signal

# local imports


class MountSignals(QObject):
    """
    """
    pointDone = Signal(object)
    domeDone = Signal(object)
    settingDone = Signal(object)
    alignDone = Signal(object)
    namesDone = Signal(object)
    firmwareDone = Signal(object)
    locationDone = Signal(object)
    calcTLEdone = Signal(object)
    statTLEdone = Signal(object)
    getTLEdone = Signal(object)
    calcProgress = Signal(object)
    calcTrajectoryDone = Signal(object)
    mountUp = Signal(object)
    slewFinished = Signal()
    alert = Signal()
