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

# external packages
from PySide6.QtCore import QObject, Signal


class QMultiWait(QObject):
    """
    QMultiWaitable implements a signal collection class for waiting of entering
    multiple signals before firing the "AND" relation of all signals.
    derived from:

    https://stackoverflow.com/questions/21108407/qt-how-to-wait-for-multiple-signals

    in addition, all received signals could be reset
    """

    ready = Signal()
    log = logging.getLogger("MW4")

    def __init__(self):
        super().__init__()
        self.waitable = set()
        self.waitready = set()

    def addWaitableSignal(self, signal):
        if signal not in self.waitable:
            self.waitable.add(signal)
            signal.connect(self.checkSignal)

    def checkSignal(self):
        sender = self.sender()
        self.waitready.add(sender)
        self.log.debug(f"QMultiWait [{self}]: [{self.waitready}]")

        if len(self.waitready) == len(self.waitable):
            self.log.debug(f"Firing QMultiWait for [{self}]")
            self.ready.emit()

    def resetSignals(self):
        self.waitready = set()

    def clear(self):
        for signal in self.waitable:
            signal.disconnect(self.checkSignal)

        self.waitable = set()
        self.waitready = set()
