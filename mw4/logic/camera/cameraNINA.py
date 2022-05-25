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
# GUI with PyQT5 for python
#
# written in python3, (c) 2019-2022 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages

# local imports
from base.ninaClass import NINAClass
from base.tpool import Worker
from logic.camera.cameraSupport import CameraSupport


class CameraNINA(NINAClass, CameraSupport):
    """
    """
    DEVICE_TYPE = 'Camera'

    __all__ = ['CameraNINA']

    def __init__(self, app=None, signals=None, data=None, parent=None):
        super().__init__(app=app, data=data)
        self.signals = signals
        self.data = data
        self.threadPool = app.threadPool
        self.abortExpose = False
        self.parent = parent

    def getCameraTemp(self):
        """
        :return:
        """
        prop = 'cameratemp'
        response = self.requestProperty(prop)
        if response is None:
            return False, {}

        return response['Success'], response

    def setCameraTemp(self, temperature):
        """
        :param: temperature:
        :return:
        """
        prop = f'setcameratemp/{temperature}'
        response = self.requestProperty(prop)
        if response is None:
            return False

        return response['Success']

    def captureImage(self, params):
        """
        :param: params:
        :return:
        """
        response = self.requestProperty('image', params=params)
        if response is None:
            return False, {}

        return response['Success'], response

    def abortImage(self):
        """
        :return:
        """
        response = self.requestProperty('abortimage')
        if response is None:
            return False

        return response['Success']

    def getImagePath(self, receipt):
        """
        :param: receipt:
        :return:
        """
        prop = f'imagepath/{receipt}'
        response = self.requestProperty(prop)
        if response is None:
            return False

        return response['Success']

    def getCameraProps(self):
        """
        :return:
        """
        response = self.requestProperty('cameraprops')
        if response is None:
            return False, {}

        return response['Success'], response

    def workerGetInitialConfig(self):
        """
        :return:
        """
        self.storePropertyToData(1, 'CCD_BINNING.HOR_BIN')
        if 'controlled' in self.deviceName:
            return False
        suc, response = self.getCameraProps()
        if not suc:
            return False

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
        return True

    def workerPollData(self):
        """
        :return: true for test purpose
        """
        if 'controlled' in self.deviceName:
            return False
        suc, response = self.getCameraTemp()
        if not suc:
            return False

        self.storePropertyToData(response.get('Temperature'),
                                 'CCD_TEMPERATURE.CCD_TEMPERATURE_VALUE')
        return True

    @staticmethod
    def sendDownloadMode(fastReadout=False):
        """
        :return: success
        """
        return True

    def workerExpose(self,
                     imagePath='',
                     expTime=3,
                     binning=1,
                     fastReadout=True,
                     posX=0,
                     posY=0,
                     width=1,
                     height=1,
                     ):
        """
        :param imagePath:
        :param expTime:
        :param binning:
        :param fastReadout:
        :param posX:
        :param posY:
        :param width:
        :param height:
        :return:
        """
        params = {'BinningMode': binning,
                  'ExposureLength': max(expTime, 1),
                  'Path': imagePath,
                  }

        addParams = {
            'UseSubframe': True,
            'X': int(posX),
            'Y': int(posY),
            'Width': int(width),
            'Height': int(height),
            'FrameType': 'Light'}

        if 'READOUT_QUALITY.QUALITY_LOW' in self.data:
            speed = 'High' if fastReadout else 'Normal'
            speedParams = {'Speed': speed}
        else:
            speedParams = {}

        if 'controlled' not in self.deviceName:
            params = {**params, **addParams, **speedParams}

        suc, response = self.captureImage(params=params)
        if not suc:
            return False

        receipt = response.get('Receipt', '')
        if not receipt:
            return False

        self.waitStart()
        self.waitExposedApp(expTime)
        self.signals.exposed.emit()
        self.waitDownload()
        self.signals.downloaded.emit()
        self.waitSave()

        if self.abortExpose:
            imagePath = ''

        self.signals.saved.emit(imagePath)
        self.signals.exposeReady.emit()
        self.signals.message.emit('')
        return True

    def expose(self,
               imagePath='',
               expTime=3,
               binning=1,
               fastReadout=True,
               posX=0,
               posY=0,
               width=1,
               height=1,
               focalLength=1,
               ra=None,
               dec=None,
               ):
        """
        :return: success
        """
        if not self.deviceConnected:
            return False
        self.raJ2000 = ra
        self.decJ2000 = dec
        self.abortExpose = False
        worker = Worker(self.workerExpose,
                        imagePath=imagePath,
                        expTime=expTime,
                        binning=binning,
                        fastReadout=fastReadout,
                        posX=posX,
                        posY=posY,
                        width=width,
                        height=height,)
        self.threadPool.start(worker)
        return True

    def abort(self):
        """
        :return: success
        """
        self.raJ2000 = None
        self.decJ2000 = None
        self.abortExpose = True
        if not self.deviceConnected:
            return False

        self.abortImage()
        return True

    def sendCoolerSwitch(self, coolerOn=False):
        """
        :param coolerOn:
        :return: success
        """
        if not self.deviceConnected:
            return False
        return True

    def sendCoolerTemp(self, temperature=0):
        """
        :param temperature:
        :return: success
        """
        if not self.deviceConnected:
            return False

        self.setCameraTemp(temperature=temperature)
        return True

    def sendOffset(self, offset=0):
        """
        :param offset:
        :return: success
        """
        if not self.deviceConnected:
            return False
        self.data['CCD_OFFSET.OFFSET'] = offset
        return True

    def sendGain(self, gain=0):
        """
        :param gain:
        :return: success
        """
        if not self.deviceConnected:
            return False
        self.data['CCD_GAIN.GAIN'] = gain
        return True
