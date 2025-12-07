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
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
from PySide6.QtCore import QObject, Signal


class MountSignals(QObject):
    """ """

    pointDone = Signal(object)
    domeDone = Signal(object)
    settingDone = Signal(object)
    getModelDone = Signal(object)
    namesDone = Signal(object)
    firmwareDone = Signal(object)
    locationDone = Signal(object)
    calcTLEdone = Signal(object)
    statTLEdone = Signal(object)
    getTLEdone = Signal(object)
    calcTrajectoryDone = Signal(object)
    mountUp = Signal(object)
    slewed = Signal()
    alert = Signal()
