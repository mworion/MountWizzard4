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
import time
from collections.abc import Callable
from mw4.base.sgproClass import SGProClass
from mw4.base.tpool import Worker, startWorker
from pathlib import Path
from typing import Any


class CameraSGPro(SGProClass):
    POLL_INTERVAL: float = 0.1
    START_TIMEOUT: float = 30
    EXPOSE_MARGIN: float = 60
    DOWNLOAD_TIMEOUT: float = 120
    SAVE_TIMEOUT: float = 60

    def __init__(self, parent: Any) -> None:
        self.deviceType: str = "camera"
        super().__init__(parent=parent)
        self.startTimeExposure: float = 0
        self.workerExpose: Worker | None = None

    def waitForMessage(
        self,
        text: str,
        present: bool,
        timeout: float,
        tick: Callable[[], None] | None = None,
    ) -> bool:
        # waits until the presence of text in Device.Message equals present. an
        # abort (exposing cleared) ends the wait with True as before; a timeout
        # or a stopped communication returns False.
        deadline = time.monotonic() + timeout
        while self.parent.exposing:
            if (text in self.data.get("Device.Message", "")) == present:
                break
            if time.monotonic() > deadline:
                self.log.warning(f"[{self.config.deviceName}] timeout waiting for [{text}]")
                self.msg.emit(2, self.PROTOCOL_NAME, "Timeout", f"Waiting for [{text}]")
                return False
            if tick is not None:
                tick()
            if self.stopEvent.wait(self.POLL_INTERVAL):
                return False
        return True

    def showTimeLeft(self) -> None:
        timeLeft = max(self.parent.exposureTime - time.time() + self.startTimeExposure, 0)
        self.signals.message.emit(f"expose {timeLeft:3.0f} s")

    def showDownload(self) -> None:
        self.signals.message.emit("download")

    def captureImage(self, params: dict) -> tuple[bool, dict]:
        response = self.requestProperty("image", params=params)
        return response.get("Success", False), response

    def abortImage(self) -> bool:
        response = self.requestProperty("abortimage")
        return response.get("Success", False)

    def getImagePath(self, receipt: str) -> tuple[bool, str]:
        response = self.requestProperty(f"imagepath/{receipt}")
        return response.get("Success", False), response.get("Message", "")

    def getCameraProps(self) -> tuple[bool, dict]:
        response = self.requestProperty("cameraprops")
        return response.get("Success", False), response

    def getInitialConfig(self) -> None:
        super().getInitialConfig()
        self.storePropertyToData(1, "CCD_BINNING.HOR_BIN")

    def sendDownloadMode(self) -> None:
        pass

    def startExpose(self) -> str:
        params = {
            "BinningMode": self.parent.binning,
            "ExposureLength": max(self.parent.exposureTime, 1),
            "Path": str(self.parent.imagePath),
        }
        suc, response = self.captureImage(params=params)
        self.log.debug(f"Capture: [{self.parent.imagePath}]")
        if not suc:
            self.log.debug(f"No capture image. {response}")
            return ""
        receipt = response.get("Receipt", "")
        if not receipt:
            self.log.debug(f"No receipt received. {response}")
            return ""
        if not self.waitForMessage("integrating", True, self.START_TIMEOUT):
            return ""
        return receipt

    def runExpose(self) -> bool:
        timeout = self.parent.exposureTime + self.EXPOSE_MARGIN
        if not self.waitForMessage("integrating", False, timeout, self.showTimeLeft):
            return False
        self.signals.exposed.emit(self.parent.imagePath)
        return True

    def runDownload(self) -> bool:
        if not self.waitForMessage("ready", True, self.DOWNLOAD_TIMEOUT, self.showDownload):
            return False
        self.signals.downloaded.emit(self.parent.imagePath)
        return True

    def runSave(self, receipt: str) -> bool:
        self.signals.message.emit("save")
        if not self.waitForMessage("idle", True, self.SAVE_TIMEOUT):
            return False

        suc, imagePath = self.getImagePath(receipt)
        if suc:
            imagePath = Path(imagePath)
            imagePath.rename(self.parent.imagePath)
        return suc

    def runnerExpose(self) -> None:
        receipt = self.startExpose()
        if receipt and self.runExpose() and self.runDownload() and self.runSave(receipt):
            self.parent.writeImageFitsHeader()
            self.stopEvent.wait(1)
        self.parent.exposeFinished()

    def expose(self) -> None:
        self.startTimeExposure = time.time()
        self.workerExpose = startWorker(self.workerExpose, self.threadPool, self.runnerExpose)

    def abort(self) -> bool:
        return self.abortImage()

    def sendCoolerSwitch(self, coolerOn: bool = False) -> None:
        pass

    def sendCoolerTemp(self, temperature: float = 0) -> None:
        pass

    def sendOffset(self, offset: int = 0) -> None:
        pass

    def sendGain(self, gain: int = 0) -> None:
        pass
