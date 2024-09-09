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

# external packages

# local imports
from base.ninaClass import NINAClass
from base.tpool import Worker
from gui.utilities.toolsQtWidget import sleepAndEvents


class CameraNINA(NINAClass):
    """
    """
    __all__ = ['CameraNINA']

    DEVICE_TYPE = 'Camera'

    def __init__(self, parent):
        self.parent = parent
        self.app = parent.app
        self.data = parent.data
        self.threadPool = parent.threadPool
        self.signals = parent.signals
        super().__init__(app=parent.app, data=parent.data) 

    def getCameraTemp(self) -> [bool, dict]:
        """
        """
        response = self.requestProperty('cameratemp')
        if response is None:
            return False, {}

        return response.get('Success', ''), response

    def setCameraTemp(self, temperature: float) -> bool:
        """
        """
        response = self.requestProperty(f'setcameratemp/{temperature}')
        if response is None:
            return False
        return response.get('Success', '')

    def captureImage(self, params: dict) -> [bool, dict]:
        """
        """
        response = self.requestProperty('image', params=params)
        if response is None:
            return False, {}
        return response.get('Success', ''), response

    def abortImage(self) -> bool:
        """
        """
        response = self.requestProperty('abortimage')
        if response is None:
            return False
        return response.get('Success', '')

    def getImagePath(self, receipt: str) -> bool:
        """
        """
        response = self.requestProperty(f'imagepath/{receipt}')
        if response is None:
            return False
        return response.get('Success', '')

    def getCameraProps(self) -> [bool, dict]:
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
        if 'controlled' in self.deviceName:
            return
        suc, response = self.getCameraProps()
        if not suc:
            self.log.debug('No camera props received')
            return

        self.storePropertyToData(response['Message'], 'CCD_INFO.Message')
        gainList = response.get('IsoValues')
        if gainList:
            self.storePropertyToData(gainList, 'CCD_GAIN.GAIN_LIST')

        gainList = response.get('GainValues')
        if gainList:
            self.storePropertyToData(gainList, 'CCD_GAIN.GAIN_LIST')
            self.storePropertyToData(1, 'CCD_GAIN.GAIN')

        self.storePropertyToData(response['NumPixelsX'], 'CCD_INFO.CCD_MAX_X')
        self.storePropertyToData(response['NumPixelsY'], 'CCD_INFO.CCD_MAX_Y')
        canSubframe = response.get('SupportsSubframe')
        if canSubframe:
            self.storePropertyToData(response['NumPixelsX'], 'CCD_FRAME.X')
            self.storePropertyToData(response['NumPixelsY'], 'CCD_FRAME.Y')

        self.storePropertyToData(True, 'CAN_SET_CCD_TEMPERATURE')
        self.log.debug(f'Initial data: {self.data}')

    def workerPollData(self) -> None:
        """
        """
        if 'controlled' in self.deviceName:
            return
        suc, response = self.getCameraTemp()
        if not suc:
            return

        self.storePropertyToData(response.get('Temperature'),
                                 'CCD_TEMPERATURE.CCD_TEMPERATURE_VALUE')

    def sendDownloadMode(self) -> None:
        """
        """
        return

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

        addParams = {
            'UseSubframe': True,
            'X': self.parent.posX,
            'Y': self.parent.posY,
            'Width': self.parent.width,
            'Height': self.parent.height,
            'FrameType': 'Light'}

        if 'READOUT_QUALITY.QUALITY_LOW' in self.data:
            speed = 'High' if self.parent.fastReadout else 'Normal'
            speedParams = {'Speed': speed}
        else:
            speedParams = {}

        if 'controlled' not in self.deviceName:
            params = {**params, **addParams, **speedParams}

        suc, response = self.captureImage(params=params)
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

        if not self.parent.exposing:
            self.parent.imagePath = ''
        else:
            sleepAndEvents(500)
            self.parent.updateImageFitsHeaderPointing()

    def expose(self) -> None:
        """
        """
        worker = Worker(self.workerExpose)
        worker.signals.finished.connect(self.parent.exposeFinished)
        self.threadPool.start(worker)

    def abort(self) -> bool:
        """
        """
        return self.abortImage()

    def sendCoolerSwitch(self, coolerOn: bool = False) -> None:
        """
        """
        pass

    def sendCoolerTemp(self, temperature: float = 0) -> None:
        """
        """
        self.setCameraTemp(temperature=temperature)

    def sendOffset(self, offset: int = 0) -> None:
        """
        """
        self.data['CCD_OFFSET.OFFSET'] = offset
 
    def sendGain(self, gain: int = 0) -> None:
        """
        """
        self.data['CCD_GAIN.GAIN'] = gain
 