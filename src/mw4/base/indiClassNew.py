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
from queue import Queue
import time

from mw4.base.indiClassAddOns import INDI_TYPES, INDIGO
from mw4.base.threadUtils import mainThreadSleep
from indipyclient.queclient import runqueclient
from mw4.base.tpool import Worker
from PySide6.QtCore import Qt, QThreadPool, QTimer, QMutex
from typing import Any


class IndiClassNew:
    log = logging.getLogger("MW4")
    RETRY_DELAY: int = 1500
    NUMBER_RETRY: int = 5

    def __init__(self, parent: Any) -> None:
        self.parent: Any = parent
        self.app: Any = parent.app
        self.msg: Any = parent.app.msg
        self.data: dict = parent.data
        self.signals: Any = parent.signals
        self.loadConfig: bool = parent.loadConfig
        self.updateRate: int = parent.updateRate
        self.threadPool: QThreadPool = parent.app.threadPool
        self.clientMutex: QMutex = QMutex()

        self.deviceName: str = ""
        self.device: Any = None
        self.deviceConnected: bool = False
        self._hostaddress: str | None = None
        self._host: tuple[str, int] | None = None
        self._port: int | None = None
        self.discoverType: int | None = None
        self.discoverList: list[str] = []
        self.isINDIGO: bool = False
        self.messages: bool = False
        self.commandRunning: bool = False
        self.rxQueue: Queue = Queue()
        self.txQueue: Queue = Queue()
        self.workerIndiQueue: Worker | None = None
        self.workerIndiCommand: Worker | None = None

        self.defaultConfig: dict[str, Any] = {
            "deviceName": "",
            "deviceList": [],
            "hostaddress": "localhost",
            "port": 7624,
            "loadConfig": False,
            "messages": False,
            "updateRate": 1000,
        }

    @property
    def host(self) -> tuple[str, int] | None:
        return ("127.0.0.1", 7624)
        return self._host

    @host.setter
    def host(self, value: tuple[str, int] | None) -> None:
        self._host = value
        self.client.host = value

    @property
    def hostaddress(self) -> str | None:
        return "127.0.0.1"
        return self._hostaddress

    @hostaddress.setter
    def hostaddress(self, value: str | None) -> None:
        self._hostaddress = value

    @property
    def port(self) -> int | None:
        return 7624
        return self._port

    @port.setter
    def port(self, value: int | str) -> None:
        self._port = int(value)

    def manageResults(self) -> None:
        while self.commandRunning:
            if self.rxQueue.empty():
                time.sleep(0.1)
                continue
            rxItem = self.rxQueue.get()
            if rxItem.snapshot.get("CCD Simulator") is None:
                continue
            print(rxItem.snapshot.get("CCD Simulator"))
            if rxItem.snapshot["CCD Simulator"].get("DRIVER_INFO") is None:
                continue
            dev = int(rxItem.snapshot["CCD Simulator"]["DRIVER_INFO"]["DRIVER_INTERFACE"])
            print(dev)
            if (dev & (1 << 1)) != 1 << 1:
                continue
            print(rxItem.snapshot["CCD Simulator"])
            if rxItem.timestamp:
                timestr = rxItem.timestamp.astimezone(tz=None).strftime('%H:%M:%S')
            else:
                timestr = "No timestamp"
            print(f"{timestr}")

    def cleanupStop(self):
        self.clientMutex.unlock()
        self.commandRunning = False
        print("stopped")

    def startCommunication(self) -> None:
        if not self.clientMutex.tryLock():
            return
        self.commandRunning = True
        self.data.clear()
        self.workerIndiQueue = Worker(runqueclient, self.txQueue, self.rxQueue, indihost=self.hostaddress, indiport=self.port)
        self.workerIndiQueue.signals.finished.connect(self.cleanupStop)
        self.threadPool.start(self.workerIndiQueue)
        self.workerIndiCommand = Worker(self.manageResults)
        self.threadPool.start(self.workerIndiCommand)
        self.txQueue.put((None, None, "snapshot"))


    def stopCommunication(self) -> None:
        self.txQueue.put(None)
        self.deviceName = ""
        self.deviceConnected = False

    def connectDevice(self, deviceName: str, propertyName: str) -> None:
        if propertyName != "CONNECTION":
            return

        if deviceName == self.deviceName:
            self.client.connectDevice(deviceName=deviceName)

    def loadIndiConfig(self, deviceName: str) -> None:
        loadObject = self.device.getSwitch("CONFIG_PROCESS")
        loadObject["CONFIG_LOAD"] = True
        suc = self.client.sendNewSwitch(
            deviceName=deviceName, propertyName="CONFIG_PROCESS", elements=loadObject
        )
        t = f"Config load [{deviceName}] success: [{suc}], value: [True]"
        self.log.info(t)

    def discoverDevices(self, deviceType: str) -> list[str]:
        self.discoverList = []
        return self.discoverList
