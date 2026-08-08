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
from mw4.base.sgproClass import SGProClass
from mw4.base.tpool import Worker
from pathlib import Path
from typing import Any


class CameraSGPro(SGProClass):
    def __init__(self, parent: Any) -> None:
        self.deviceType: str = "camera"
        super().__init__(parent=parent)
        self.startTimeExposure: float = 0
        self.workerExpose: Worker | None = None

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
        while self.parent.exposing and "integrating" not in self.data.get(
            "Device.Message", ""
        ):
            time.sleep(0.1)
        return receipt

    def runExpose(self) -> None:
        while self.parent.exposing and "integrating" in self.data.get("Device.Message", ""):
            timeLeft = max(self.parent.exposureTime - time.time() + self.startTimeExposure, 0)
            text = f"expose {timeLeft:3.0f} s"
            self.signals.message.emit(text)
            time.sleep(0.1)
        self.signals.exposed.emit(self.parent.imagePath)

    def runDownload(self) -> None:
        while self.parent.exposing and "ready" not in self.data.get("Device.Message", ""):
            self.signals.message.emit("download")
            time.sleep(0.1)
        self.signals.downloaded.emit(self.parent.imagePath)

    def runSave(self, receipt: str) -> bool:
        self.signals.message.emit("save")
        while self.parent.exposing and "idle" not in self.data.get("Device.Message", ""):
            time.sleep(0.1)

        suc, imagePath = self.getImagePath(receipt)
        if suc:
            imagePath = Path(imagePath)
            imagePath.rename(self.parent.imagePath)
        return suc

    def runnerExpose(self) -> None:
        receipt = self.startExpose()
        if not receipt:
            self.parent.exposeFinished()
            return
        self.runExpose()
        self.runDownload()
        if self.runSave(receipt):
            self.parent.writeImageFitsHeader()
            time.sleep(1)
        self.parent.exposeFinished()

    def expose(self) -> None:
        self.startTimeExposure = time.time()
        self.workerExpose = Worker(self.runnerExpose)
        self.threadPool.start(self.workerExpose)

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
