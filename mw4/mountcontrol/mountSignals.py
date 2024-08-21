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
import PySide6.QtCore

# local imports


class MountSignals(PySide6.QtCore.QObject):
    """
    """
    pointDone = PySide6.QtCore.Signal(object)
    domeDone = PySide6.QtCore.Signal(object)
    settingDone = PySide6.QtCore.Signal(object)
    alignDone = PySide6.QtCore.Signal(object)
    namesDone = PySide6.QtCore.Signal(object)
    firmwareDone = PySide6.QtCore.Signal(object)
    locationDone = PySide6.QtCore.Signal(object)
    calcTLEdone = PySide6.QtCore.Signal(object)
    statTLEdone = PySide6.QtCore.Signal(object)
    getTLEdone = PySide6.QtCore.Signal(object)
    calcProgress = PySide6.QtCore.Signal(object)
    calcTrajectoryDone = PySide6.QtCore.Signal(object)
    mountUp = PySide6.QtCore.Signal(object)
    slewFinished = PySide6.QtCore.Signal()
    alert = PySide6.QtCore.Signal()
