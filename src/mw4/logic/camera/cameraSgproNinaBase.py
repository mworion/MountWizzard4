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
from mw4.base.sgproNinaClass import SgproNinaCommon
from typing import Any


class CameraSgproNinaBase(SgproNinaCommon):
    DEVICE_TYPE: str = "Camera"

    def __init__(self, parent: Any) -> None:
        super().__init__(parent=parent)
        self.exposing: bool = False

    def getInitialConfig(self) -> None:
        self.storePropertyToData(0, "CCD_BINNING.HOR_BIN")

    def setExposureState(self) -> None:
        pass

    def pollData(self) -> None:
        if self.parent.exposing:
            self.setExposureState()
        else:
            if self.exposing:
                self.exposing = False
                self.parent.exposeFinished()

    def sendDownloadMode(self) -> None:
        pass

    def expose(self) -> None:
        params = {
            "BinningMode": self.parent.binning,
            "ExposureLength": max(self.parent.exposureTime, 1),
            "Path": str(self.parent.imagePath),
        }
        self.requestPropertyQueued("image", params=params)

    def abort(self) -> bool:
        self.requestPropertyQueued("abortimage")
        return True

    def sendCoolerSwitch(self, coolerOn: bool = False) -> None:
        pass

    def sendCoolerTemp(self, temperature: float = 0) -> None:
        pass

    def sendOffset(self, offset: int = 0) -> None:
        pass

    def sendGain(self, gain: int = 0) -> None:
        pass

