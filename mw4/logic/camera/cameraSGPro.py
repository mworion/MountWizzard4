############################################################
# -*- coding: utf-8 -*-
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PySide for python
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import os

# external packages

# local imports
from base.sgproClass import SGProClass
from base.tpool import Worker
from gui.utilities.toolsQtWidget import sleepAndEvents


class CameraSGPro(SGProClass):
    """ """

    def __init__(self, parent):
        self.parent = parent
        self.app = parent.app
        self.data = parent.data
        super().__init__(parent=parent)
        self.threadPool = parent.threadPool
        self.signals = parent.signals
        self.worker: Worker = None

    def sgGetCameraTemp(self) -> [bool, dict]:
        """ """
        response = self.requestProperty("cameratemp")
        return response.get("Success", False), response

    def sgSetCameraTemp(self, temperature: float) -> bool:
        """ """
        response = self.requestProperty(f"setcameratemp/{temperature}")
        return response.get("Success", False)

    def sgCaptureImage(self, params: dict) -> [bool, dict]:
        """ """
        response = self.requestProperty("image", params=params)
        return response.get("Success", False), response

    def sgAbortImage(self) -> bool:
        """ """
        response = self.requestProperty("abortimage")
        return response.get("Success", False)

    def sgGetImagePath(self, receipt: str) -> bool:
        """ """
        response = self.requestProperty(f"imagepath/{receipt}")
        return response.get("Success", False)

    def sgGetCameraProps(self) -> [bool, dict]:
        """ """
        response = self.requestProperty("cameraprops")
        return response.get("Success", False), response

    def workerGetInitialConfig(self) -> None:
        """ """
        self.storePropertyToData(1, "CCD_BINNING.HOR_BIN")

    def workerPollData(self) -> None:
        """ """
        pass

    def sendDownloadMode(self) -> None:
        """ """
        pass

    def waitFunc(self) -> bool:
        """ """
        return "integrating" in self.data.get("Device.Message")

    def workerExpose(self) -> None:
        """ """
        params = {
            "BinningMode": self.parent.binning,
            "ExposureLength": max(self.parent.exposureTime, 1),
            "Path": self.parent.imagePath,
        }

        suc, response = self.sgCaptureImage(params=params)
        if not suc:
            self.log.debug(f"No capture image. {response}")
            return

        receipt = response.get("Receipt", "")
        if not receipt:
            self.log.debug(f"No receipt received. {response}")
            return

        self.parent.waitStart()
        self.parent.waitExposed(self.parent.exposureTime, self.waitFunc)
        self.signals.exposed.emit()
        self.parent.waitDownload()
        self.signals.downloaded.emit()
        self.parent.waitSave()
        self.parent.waitFinish(self.sgGetImagePath, receipt)

        if not self.parent.exposing:
            self.parent.imagePath = ""
        else:
            pre, _ = os.path.splitext(self.parent.imagePath)
            os.rename(pre + ".fit", self.parent.imagePath)
            sleepAndEvents(500)
            self.parent.updateImageFitsHeaderPointing()

    def expose(self) -> None:
        """ """
        self.worker = Worker(self.workerExpose)
        self.worker.signals.finished.connect(self.parent.exposeFinished)
        self.threadPool.start(self.worker)

    def abort(self) -> None:
        """ """
        return self.sgAbortImage()

    def sendCoolerSwitch(self, coolerOn: bool = False) -> None:
        """ """
        pass

    def sendCoolerTemp(self, temperature: float = 0) -> None:
        """ """
        pass

    def sendOffset(self, offset: int = 0) -> None:
        """ """
        pass

    def sendGain(self, gain: int = 0) -> None:
        """ """
        pass
