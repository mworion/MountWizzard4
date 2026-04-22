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
# Licence APL2.0
#
###########################################################
import logging
import PySide6
from typing import Any


class MeasureDataRaw(PySide6.QtCore.QObject):
    log = logging.getLogger("MW4")

    def __init__(self, app: Any = None, parent: Any = None, data: Any = None) -> None:
        super().__init__()

        self.app = app
        self.parent = parent
        self.data = data
        self.deviceName: str = "RAW"
        self.defaultConfig: dict[str, Any] = {
            "raw": {
                "deviceName": "display only",
            }
        }
        self.timerTask = PySide6.QtCore.QTimer()
        self.timerTask.setSingleShot(False)
        self.timerTask.timeout.connect(self.measureTask)

    def startCommunication(self) -> None:
        self.timerTask.start(self.parent.CYCLE_UPDATE_TASK)

    def stopCommunication(self) -> None:
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
