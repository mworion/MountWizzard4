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
import numpy as np
from mw4.base.signalsDevices import Signals
from mw4.logic.measure.measureCSV import MeasureDataCSV
from mw4.logic.measure.measureRaw import MeasureDataRaw
from PySide6.QtCore import QMutex
from mw4.logic.measure.measureAddOns import measure


class MeasureData:
    """ """

    log = logging.getLogger("MW4")
    MAXSIZE = 48 * 60 * 60

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.signals = Signals()
        self.mutexMeasure = QMutex()
        self.shorteningStart: bool = True
        self.data: dict = {}
        self.devices: dict = {}
        self.deviceName: str = ""
        self.defaultConfig = {"framework": "", "frameworks": {}}
        self.framework: str = ""
        self.run = {
            "raw": MeasureDataRaw(self.app, self, self.data),
            "csv": MeasureDataCSV(self.app, self, self.data),
        }
        for fw in self.run:
            self.defaultConfig["frameworks"].update(self.run[fw].defaultConfig)

    def collectDataDevices(self) -> None:
        """"""
        self.devices.clear()
        deviceStat = self.app.deviceStat
        deviceDrivers = self.app.mainW.mainWindowAddons.addons['SettDevice'].drivers
        devices = [device for device in deviceStat if deviceStat[device] is not None]
        for device in devices:
            if device not in measure:
                continue
            if device not in deviceDrivers:
                continue
            self.devices[device] = deviceDrivers[device]["class"]
        self.devices["mount"] = self.app.mount

    def clearData(self) -> None:
        """ """
        self.data.clear()
        self.data["time"] = np.empty(shape=[0, 1], dtype="datetime64")
        for device in self.devices:
            if device not in measure:
                continue
            for source in measure[device]:
                item = f"{device}-{source}"
                self.data[item] = np.empty(shape=[0, 1])

    def startCommunication(self) -> None:
        """ """
        self.collectDataDevices()
        self.clearData()
        name = self.run[self.framework].deviceName
        self.run[self.framework].startCommunication()
        self.signals.deviceConnected.emit(name)

    def stopCommunication(self) -> None:
        """ """
        self.run[self.framework].stopCommunication()
        name = self.run[self.framework].deviceName
        self.signals.serverDisconnected.emit({name: 0})
        self.signals.deviceDisconnected.emit(name)

    def checkStart(self) -> None:
        """ """
        if self.shorteningStart and len(self.data['time']) > 2:
            self.shorteningStart = False
            for measure in self.data:
                self.data[measure] = np.delete(self.data[measure], range(0, 2))

    def checkSize(self) -> None:
        """ """
        if len(self.data["time"]) < self.MAXSIZE:
            return
        for measure in self.data:
            self.data[measure] = np.split(self.data[measure], 2)[1]

    def measureTask(self) -> None:
        """ """
        if not self.mutexMeasure.tryLock():
            return
        self.checkStart()
        self.checkSize()
        timeStamp = self.app.mount.obsSite.timeJD.utc_datetime().replace(tzinfo=None)
        self.data["time"] = np.append(self.data["time"], np.datetime64(timeStamp))
        for device in self.devices:
            for source in measure[device]:
                value = self.devices[device].data.get(source, 0)
                item = f"{device}-{source}"
                self.data[item] = np.append(self.data[item], value)
        self.mutexMeasure.unlock()
