# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import json
import subprocess
import sys
from dataclasses import dataclass, field
from mw4.base import platformInfo
from mw4.base.alpacaAscomCommon import AlpacaAscomCommon
from mw4.base.tpool import Worker, startWorker
from typing import Any

if platformInfo.IS_WINDOWS:
    from pythoncom import CoInitialize, CoUninitialize
    from win32com import client


@dataclass
class DeviceConfigAscom:
    deviceName: str = field(default="")


class AscomClass(AlpacaAscomCommon):
    PROTOCOL_NAME: str = "ASCOM"

    def __init__(self, parent: Any) -> None:
        super().__init__(parent)
        self.config = DeviceConfigAscom()
        self.workerRunnerCoreLoop: Worker | None = None

    def runnerCoreLoop(self) -> None:
        CoInitialize()
        try:
            self.device = client.dynamic.Dispatch(self.config.deviceName)
            self.log.debug("[%s] Dispatching", self.config.deviceName)
        except (AttributeError, OSError) as e:
            self.log.error("[%s] Dispatch error: [%s]", self.config.deviceName, e)
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
        self.data.clear()
        self.propertyExceptions.clear()
        if not self.config.deviceName:
            return
        self.stopEvent.clear()
        self.workerRunnerCoreLoop = startWorker(
            self.workerRunnerCoreLoop, self.threadPool, self.runnerCoreLoop
        )

    @classmethod
    def selectAscomDriver(cls, deviceName: str, deviceType: str) -> str:
        # Runs the ASCOM chooser via a logger only, so it can be called without
        # constructing an AscomClass instance (see DevicePopup.selectAscomDriver).
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
            cls.log.critical("ASCOM Chooser subprocess error: %s", e)
            return deviceName
        cls.log.debug("ASCOM Chooser result: [%s]", result)
        return result if result else deviceName
