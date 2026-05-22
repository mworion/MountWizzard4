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
from mw4.logic.camera.cameraSgproNinaBase import CameraSgproNinaBase


class CameraNINA(CameraSgproNinaBase):

    def setExposureState(self) -> None:
        response = self.requestProperty(f"devicestatus/{self.DEVICE_TYPE}")
        state =  response.get("State", -1)
        if state == 3 and not self.exposing:
            self.exposing = True
        if state == 3 and self.exposing:
            timeLeft = max(
                self.parent.exposureTime - time.time() + self.startTimeExposure,
                0,
            )
            text = f"expose {timeLeft:3.0f} s"
            self.signals.message.emit(text)
        if state == 0 and self.exposing:
            self.signals.exposed.emit(self.parent.imagePath)
            self.signals.message.emit("download")

        receipt = self.data.get("IMAGE.RECEIPT", "")
        response = self.requestProperty(f"imagepath/{receipt}")
        if not response.get("Success", False):
            return

        self.parent.imagePath.with_suffix(".fit")
        self.parent.updateImageFitsHeaderPointing()
        self.signals.downloaded.emit(self.parent.imagePath)
        self.signals.message.emit("saving")
        self.parent.exposeFinished()
        self.exposing = False
