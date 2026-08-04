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
from typing import Any


class CameraSGPro(SGProClass):
    def __init__(self, parent: Any) -> None:
        self.parent = parent
        self.app = parent.app
        self.data = parent.data
        super().__init__(parent=parent)
        self.threadPool = parent.threadPool
        self.signals = parent.signals
        self.worker: Worker | None = None

    def captureImage(self, params: dict) -> tuple[bool, dict]:
        response = self.requestProperty("image", params=params)
        return response.get("Success", False), response

    def abortImage(self) -> bool:
        response = self.requestProperty("abortimage")
        return response.get("Success", False)

    def getImagePath(self, receipt: str) -> bool:
        response = self.requestProperty(f"imagepath/{receipt}")
        return response.get("Success", False)

    def getCameraProps(self) -> tuple[bool, dict]:
        response = self.requestProperty("cameraprops")
        return response.get("Success", False), response

    def getInitialConfig(self) -> None:
        super().getInitialConfig()
        self.storePropertyToData(1, "CCD_BINNING.HOR_BIN")

    def sendDownloadMode(self) -> None:
        pass

    def waitFunc(self) -> bool:
        return "integrating" in self.data.get("Device.Message", "")

    def workerExpose(self) -> None:
        params = {
            "BinningMode": self.parent.binning,
            "ExposureLength": max(self.parent.exposureTime, 1),
            "Path": str(self.parent.imagePath),
        }

        suc, response = self.captureImage(params=params)
        if not suc:
            self.log.debug(f"No capture image. {response}")
            self.parent.exposing = False
            return

        receipt = response.get("Receipt", "")
        if not receipt:
            self.log.debug(f"No receipt received. {response}")
            self.parent.exposing = False
            return

        self.signals.message.emit(f"expose {self.parent.exposureTime:3.0f} s")
        while self.parent.exposing and self.waitFunc():
            time.sleep(0.1)

        if not self.parent.exposing:
            return

        self.signals.exposed.emit(self.parent.imagePath)
        self.signals.message.emit("download")
        self.signals.downloaded.emit(self.parent.imagePath)
        self.signals.message.emit("saving")

        for _ in range(50):
            if self.getImagePath(receipt):
                break
            time.sleep(0.1)

        if not self.parent.exposing:
            return

        self.parent.updateImageFitsHeaderPointing()

    def expose(self) -> None:
        self.worker = Worker(self.workerExpose)
        self.worker.signals.finished.connect(self.parent.exposeFinished)
        self.threadPool.start(self.worker)

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
