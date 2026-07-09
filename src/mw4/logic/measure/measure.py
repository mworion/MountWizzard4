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
import logging
import numpy as np
from mw4.base.signalsDevices import Signals
from mw4.logic.measure.measureAddOns import measure
from mw4.logic.measure.measureCSV import MeasureDataCSV
from mw4.logic.measure.measureRaw import MeasureDataRaw
from PySide6.QtCore import QMutex
from typing import Any


class MeasureData:
    DEVICE_TYPE = "misc"
    log = logging.getLogger("MW4")
    MAXSIZE = 48 * 60 * 60
    CYCLE_UPDATE_TASK = 1000

    def __init__(self, app: Any) -> None:
        super().__init__()
        self.app = app
        self.signals = Signals()
        self.mutexMeasure = QMutex()
        self.shorteningStart: bool = True
        self.data: dict[str, Any] = {}
        self.measuredDevices: dict[str, Any] = {}
        self.framework: str = ""
        self.run: dict[str, Any] = {
            "raw": MeasureDataRaw(self.app, self, self.data),
            "csv": MeasureDataCSV(self.app, self, self.data),
        }

    def collectDataDevices(self) -> None:
        self.measuredDevices.clear()
        for name, entry in self.app.dReg.d.items():
            if name not in measure or entry.instance is None:
                continue
            self.measuredDevices[name] = entry.instance

    def clearData(self) -> None:
        self.data.clear()
        self.data["time"] = np.empty(shape=[0, 1], dtype="datetime64")
        for device in self.measuredDevices:
            if device not in measure:
                continue
            for source in measure[device]:
                item = f"{device}-{source}"
                self.data[item] = np.empty(shape=[0, 1])

    def startCommunication(self) -> None:
        self.collectDataDevices()
        self.clearData()
        self.run[self.framework].startCommunication()
        self.signals.deviceConnected.emit(self.run[self.framework].config.deviceName)

    def stopCommunication(self) -> None:
        self.run[self.framework].stopCommunication()
        self.signals.deviceDisconnected.emit(self.run[self.framework].config.deviceName)

    def checkStart(self) -> None:
        if self.shorteningStart and len(self.data["time"]) > 2:
            self.shorteningStart = False
            for measure in self.data:
                self.data[measure] = np.delete(self.data[measure], range(0, 2))

    def checkSize(self) -> None:
        if len(self.data["time"]) < self.MAXSIZE:
            return
        for item in self.data:
            self.data[item] = np.split(self.data[item], 2)[1]

    def measureTask(self) -> None:
        if not self.mutexMeasure.tryLock():
            return
        self.checkStart()
        self.checkSize()
        timeStamp = self.app.dReg["mount"].obsSite.timeJD.utc_datetime().replace(tzinfo=None)
        self.data["time"] = np.append(self.data["time"], np.datetime64(timeStamp))
        for device in self.measuredDevices:
            for source in measure[device]:
                value = self.measuredDevices[device].data.get(source, 0)
                item = f"{device}-{source}"
                self.data[item] = np.append(self.data[item], value)
        self.mutexMeasure.unlock()
