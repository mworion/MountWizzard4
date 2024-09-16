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
# written in python3, (c) 2019-2024 by mworion
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
    """
    """
    __all__ = ['CameraSGPro']

    DEVICE_TYPE = 'Camera'

    def __init__(self, parent):
        self.parent = parent
        self.app = parent.app
        self.data = parent.data
        super().__init__(app=parent.app, data=parent.data) 
        self.threadPool = parent.threadPool
        self.signals = parent.signals

    def sgGetCameraTemp(self) -> [bool, dict]:
        """
        """
        response = self.requestProperty('cameratemp')
        if response is None:
            return False, {}

        return response.get('Success', ''), response

    def sgSetCameraTemp(self, temperature: float) -> bool:
        """
        """
        response = self.requestProperty(f'setcameratemp/{temperature}')
        if response is None:
            return False
        return response.get('Success', '')

    def sgCaptureImage(self, params: dict) -> [bool, dict]:
        """
        """
        response = self.requestProperty('image', params=params)
        if response is None:
            return False, {}
        return response.get('Success', ''), response

    def sgAbortImage(self) -> bool:
        """
        """
        response = self.requestProperty('abortimage')
        if response is None:
            return False
        return response.get('Success', '')

    def sgGetImagePath(self, receipt: str) -> bool:
        """
        """
        response = self.requestProperty(f'imagepath/{receipt}')
        if response is None:
            return False
        return response.get('Success', '')

    def sgGetCameraProps(self) -> [bool, dict]:
        """
        """
        response = self.requestProperty('cameraprops')
        if response is None:
            return False, {}
        return response.get('Success', ''), response

    def workerGetInitialConfig(self) -> None:
        """
        """
        self.storePropertyToData(1, 'CCD_BINNING.HOR_BIN')

    def workerPollData(self) -> None:
        """
        """
        pass

    def sendDownloadMode(self) -> None:
        """
        """
        pass

    def waitFunc(self) -> bool:
        """
        """
        return 'integrating' in self.data.get('Device.Message')
        
    def workerExpose(self) -> None:
        """
        """
        params = {'BinningMode': self.parent.binning,
                  'ExposureLength': max(self.parent.expTime, 1),
                  'Path': self.parent.imagePath}

        suc, response = self.sgCaptureImage(params=params)
        if not suc:
            self.log.debug(f'No capture image. {response}')
            return

        receipt = response.get('Receipt', '')
        if not receipt:
            self.log.debug(f'No receipt received. {response}')
            return

        self.parent.waitStart()
        self.parent.waitExposed(self.parent.expTime, self.waitFunc)
        self.signals.exposed.emit()
        self.parent.waitDownload()
        self.signals.downloaded.emit()
        self.parent.waitSave()
        self.parent.waitFinish(self.sgGetImagePath, receipt)

        if not self.parent.exposing:
            self.parent.imagePath = ''
        else:
            pre, _ = os.path.splitext(self.parent.imagePath)
            os.rename(pre + '.fit', self.parent.imagePath)
            sleepAndEvents(500)
            self.parent.updateImageFitsHeaderPointing()

    def expose(self) -> None:
        """
        """
        worker = Worker(self.workerExpose)
        worker.signals.finished.connect(self.parent.exposeFinished)
        self.threadPool.start(worker)

    def abort(self) -> None:
        """
        """
        return self.sgAbortImage()

    def sendCoolerSwitch(self, coolerOn: bool = False) -> None:
        """
        """
        pass

    def sendCoolerTemp(self, temperature: float = 0) -> None:
        """
        """
        pass

    def sendOffset(self, offset: int = 0) -> None:
        """
        """
        pass

    def sendGain(self, gain: int = 0) -> None:
        """
        """
        pass
