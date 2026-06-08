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
import json
import platform
import subprocess
import sys
from dataclasses import dataclass, field
from mw4.base.alpacaAscomCommon import AlpacaAscomCommon
from mw4.base.tpool import Worker
from typing import Any

if platform.system() == "Windows":
    from pythoncom import CoInitialize, CoUninitialize
    from win32com import client


@dataclass
class DeviceConfigAscom:
    deviceName: str = field(default=None)


class AscomClass(AlpacaAscomCommon):
    PROTOCOL_NAME: str = "ASCOM"

    def __init__(self, parent: Any) -> None:
        super().__init__(parent)
        self.deviceName: str = ""
        self.config = DeviceConfigAscom()
        self.workerRunnerCoreLoop: Worker | None = None
        self.defaultConfig: dict[str, Any] = {
            "deviceName": "",
        }

    def runnerCoreLoop(self) -> None:
        CoInitialize()
        try:
            self.device = client.dynamic.Dispatch(self.deviceName)
            self.log.debug(f"[{self.deviceName}] Dispatching")
        except Exception as e:
            self.log.error(f"[{self.deviceName}] Dispatch error: [{e}]")
            return
        else:
            self.runnerCommunicationLoop()
        finally:
            if self.device:
                self.setDeviceProp("Connected", False)
                self.device = None
            CoUninitialize()

    def startCommunication(self) -> None:
        self.deviceConnected = False
        self.serverConnected = False
        self.data.clear()
        self.propertyExceptions.clear()
        if not self.deviceName:
            return
        self.stopEvent.clear()
        self.workerRunnerCoreLoop = Worker(self.runnerCoreLoop)
        self.threadPool.start(self.workerRunnerCoreLoop)

    def selectAscomDriver(self, deviceName: str, deviceType: str) -> str:
        # Arguments are passed as a JSON payload to avoid code injection via
        # f-string interpolation into the subprocess script. (SEC-1)
        script = (
            "import sys, json, win32com.client; "
            "args = json.loads(sys.argv[1]); "
            "chooser = win32com.client.Dispatch('ASCOM.Utilities.Chooser'); "
            "chooser.DeviceType = args['deviceType']; "
            "result = chooser.Choose(args['deviceName']); "
            "print(result if result else '', end='')"
        )
        payload = json.dumps({"deviceName": deviceName, "deviceType": deviceType})
        try:
            result = subprocess.check_output(  # nosec B603
                [sys.executable, "-c", script, payload],
                text=True,
                creationflags=0x08000000,  # CREATE_NO_WINDOW
            ).strip()
        except subprocess.CalledProcessError as e:
            self.log.critical(f"ASCOM Chooser subprocess error: {e}")
            return deviceName
        self.log.debug(f"ASCOM Chooser result: [{result}]")
        return result if result else deviceName
