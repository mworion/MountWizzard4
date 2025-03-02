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
import PySide6

# local imports


class MeasureDataRaw(PySide6.QtCore.QObject):
    """ """

    log = logging.getLogger("MW4")

    # update rate to 1 seconds for setting indi server
    CYCLE_UPDATE_TASK = 1000
    # maximum size of measurement task
    MAXSIZE = 24 * 60 * 60

    def __init__(self, app=None, parent=None, data=None):
        super().__init__()

        self.app = app
        self.parent = parent
        self.data = data
        self.deviceName = "RAW"
        self.defaultConfig = {
            "raw": {
                "deviceName": "display only",
            }
        }

        # time for measurement
        self.timerTask = PySide6.QtCore.QTimer()
        self.timerTask.setSingleShot(False)
        self.timerTask.timeout.connect(self.measureTask)

    def startCommunication(self) -> None:
        """ """
        self.parent.setEmptyData()
        self.timerTask.start(self.CYCLE_UPDATE_TASK)

    def stopCommunication(self) -> None:
        """ """
        self.timerTask.stop()

    def measureTask(self) -> None:
        """
        measureTask runs all necessary pre-processing and collecting task to
        assemble a large dict of lists, where all measurement data is stored.
        the intention later on would be to store and export this data.
        the time object is related to the time held in mount computer and is
        in utc timezone.

        data sources are:
            environment
            mount pointing position

        """
        self.parent.measureTask()
