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
import hid
import logging
import threading
from dataclasses import dataclass, field
from mw4.base.signalsDevices import Signals
from mw4.base.tpool import Worker
from PySide6.QtCore import Signal
from typing import Any


@dataclass
class DeviceConfigHidController:
    deviceName: str = field(default="")
    moveRaDec: bool = field(default=True)
    moveAltAz: bool = field(default=True)
    tracking: bool = field(default=True)
    parkStop: bool = field(default=True)
    dome: bool = field(default=True)


class HidControllerSignals(Signals):
    hidABXY = Signal(object)
    hidPMH = Signal(object)
    hidDirection = Signal(object)
    hidSL = Signal(object, object)
    hidSR = Signal(object, object)


class HidController:
    DEVICE_TYPE = "hid"
    log = logging.getLogger("MW4")
    UPDATE_RATE: float = 0.05

    def __init__(self, app: Any) -> None:
        self.app = app
        self.threadPool = app.threadPool
        self.signals = HidControllerSignals()
        self.deviceConnected: bool = False
        self.hidControllerDevice = None
        self.data: dict[str, Any] = {}
        self.framework: str = "hid"
        self.run: dict[str, Any] = {"hid": self}
        self.config = DeviceConfigHidController()
        self.workerCommunicationLoop: Worker | None = None
        self.stopEvent: threading.Event = threading.Event()
        self.loggingTrace: bool = False

    @staticmethod
    def isNewerData(act: list, old: list) -> bool:
        if len(act) == 0:
            return False
        for i, dataVal in enumerate(act):
            if dataVal != old[i]:
                break
        else:
            return False
        return True

    def convertData(self, name: str, iR: list) -> list:
        oR = [0, 0, 0, 0, 0, 0, 0]
        if len(iR) == 0:
            return oR
        if name == "Pro Controller":
            oR = [iR[1], iR[2], iR[3], iR[5], iR[7], iR[9], iR[11]]
        elif name == "Controller (XBOX 360 For Windows)":
            if iR[11] == 0b00011100:
                val = 0b00000110
            elif iR[11] == 0b00010100:
                val = 0b00000100
            elif iR[11] == 0b00001100:
                val = 0b00000010
            elif iR[11] == 0b00000100:
                val = 0b00000000
            else:
                val = 0b00001111
            oR = [iR[10], 0, val, iR[1], iR[3], iR[5], iR[7]]
        return oR

    def sendHidControllerSignals(self, act: list, old: list) -> None:
        if (act[0] != old[0]) and self.config.tracking:
            self.signals.hidABXY.emit(act[0])
        if act[1] != old[1]:
            self.signals.hidPMH.emit(act[1])
        if (act[2] != old[2]) and self.config.moveAltAz:
            self.signals.hidDirection.emit(act[2])
        if (act[3] != old[3] or act[4] != old[4]) and self.config.dome:
            self.signals.hidSL.emit(act[3], act[4])
        if (act[5] != old[5] or act[6] != old[6]) and self.config.moveRaDec:
            self.signals.hidSR.emit(act[5], act[6])

    def readHidController(self) -> tuple[bool, list]:
        try:
            data = self.hidControllerDevice.read(64)
        except Exception as e:
            self.log.warning(f"HidController error {e}")
            return False, []
        return True, data

    def connectDevice(self) -> bool:
        vendorId = productId = 0
        for device in hid.enumerate():
            if device["product_string"] == self.config.deviceName:
                vendorId = device["vendor_id"]
                productId = device["product_id"]
                break
        if not vendorId:
            self.hidControllerDevice = None
            return False
        try:
            self.hidControllerDevice = hid.device()
            self.hidControllerDevice.open(vendorId, productId)
            self.hidControllerDevice.set_nonblocking(True)
        except Exception as e:
            self.hidControllerDevice = None
            self.log.warning(f"Failed to open HID device: {e}")
            return False
        self.log.debug(f"HidController: [{self.config.deviceName} {vendorId}:{productId}]")
        return True

    def runnerHidController(self, reportOld) -> tuple[bool, list]:
        connect, report = self.readHidController()
        if not connect:
            return False, reportOld
        if len(report) == 0:
            return True, reportOld
        if not self.isNewerData(report, reportOld):
            return True, report
        report = self.convertData(self.config.deviceName, report)
        self.sendHidControllerSignals(report, reportOld)
        return True, report

    def handleDeviceConnect(self) -> None:
        if not self.connectDevice():
            return
        if not self.deviceConnected:
            self.signals.deviceConnected.emit(self.config.deviceName)
            self.deviceConnected = True

    def handleDeviceDisconnect(self) -> None:
        self.deviceConnected = False
        if self.hidControllerDevice:
            self.hidControllerDevice.close()
            self.hidControllerDevice = None
        self.signals.deviceDisconnected.emit(self.config.deviceName)

    def runnerCommunicationLoop(self) -> None:
        reportOld = [0] * 16
        while not self.stopEvent.is_set():
            if not self.deviceConnected:
                self.handleDeviceConnect()
            else:
                connect, reportOld = self.runnerHidController(reportOld)
                if not connect:
                    self.handleDeviceDisconnect()
            self.stopEvent.wait(timeout=self.UPDATE_RATE)

    def startCommunication(self) -> None:
        self.deviceConnected = False
        self.stopEvent.clear()
        self.workerCommunicationLoop = Worker(self.runnerCommunicationLoop)
        self.threadPool.start(self.workerCommunicationLoop)

    def stopCommunication(self) -> None:
        self.stopEvent.set()
        self.deviceConnected = False
        self.signals.deviceDisconnected.emit(self.config.deviceName)

    @staticmethod
    def isValidHidControllers(name: str) -> bool:
        validStrings = ["Controller", "Game"]
        for check in validStrings:
            if check in name:
                break
        else:
            return False
        return True

    def discoverDevices(self, deviceType: str) -> list[str]:
        result = []
        for device in hid.enumerate():
            name = device["product_string"]
            if self.isValidHidControllers(name) and name not in result:
                result.append(name)
        return result
