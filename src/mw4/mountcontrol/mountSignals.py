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
from mw4.base.signalsDevices import Signals
from PySide6.QtCore import Signal


class MountSignals(Signals):
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
    mountIsUp = Signal(object)
    slewed = Signal()
    alert = Signal()
