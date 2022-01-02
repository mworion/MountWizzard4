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
# written in python3, (c) 2019-2021 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
import os

# external packages

# local imports
from base.sgproClass import SGProClass
from base.tpool import Worker
from logic.camera.cameraSupport import CameraSupport


class CameraSGPro(SGProClass, CameraSupport):
    """
    """
    DEVICE_TYPE = 'Camera'

    __all__ = ['CameraSGPro']

    def __init__(self, app=None, signals=None, data=None, parent=None):
        super().__init__(app=app, data=data, threadPool=app.threadPool)
        self.signals = signals
        self.data = data
        self.abortExpose = False
        self.parent = parent

    def sgGetCameraTemp(self):
        """
        :return:
        """
        prop = f'cameratemp'
        response = self.requestProperty(prop)
        if response is None:
            return False, {}

        return response['Success'], response

    def sgSetCameraTemp(self, temperature):
        """
        :param: temperature:
        :return:
        """
        prop = f'setcameratemp/{temperature}'
        response = self.requestProperty(prop)
        if response is None:
            return False

        return response['Success']

    def sgCaptureImage(self, params):
        """
        :param: params:
        :return:
        """
        response = self.requestProperty('image', params=params)
        if response is None:
            return False, {}

        return response['Success'], response

    def sgAbortImage(self):
        """
        :return:
        """
        response = self.requestProperty('abortimage')
        if response is None:
            return False

        return response['Success']

    def sgGetImagePath(self, receipt):
        """
        :param: receipt:
        :return:
        """
        prop = f'imagepath/{receipt}'
        response = self.requestProperty(prop)
        if response is None:
            return False

        return response['Success']

    def sgGetCameraProps(self):
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
        suc, response = self.sgGetCameraProps()
        if not suc:
            return False

        self.storePropertyToData(response['Message'],
                                 'CCD_INFO.Message')
        self.storePropertyToData(response.get('IsoValues', []),
                                 'CCD_INFO.IsoValues')
        self.storePropertyToData(response.get('GainValues', []),
                                 'CCD_INFO.GainValues')
        self.storePropertyToData(response['NumPixelsX'],
                                 'CCD_INFO.CCD_MAX_X')
        self.storePropertyToData(response['NumPixelsY'],
                                 'CCD_INFO.CCD_MAX_Y')
        canSubframe = response.get('CanSubframe', False)
        if canSubframe:
            self.storePropertyToData(response['NumPixelsX'],
                                     'CCD_FRAME.X')
            self.storePropertyToData(response['NumPixelsY'],
                                     'CCD_FRAME.Y')
        self.storePropertyToData(True, 'CAN_SET_CCD_TEMPERATURE')
        self.storePropertyToData(1, 'CCD_BINNING.HOR_BIN')
        self.log.debug(f'Initial data: {self.data}')
        return True

    def workerPollData(self):
        """
        :return: true for test purpose
        """
        suc, response = self.sgGetCameraTemp()
        if not suc:
            return False

        self.storePropertyToData(response.get('Temperature', 10),
                                 'CCD_TEMPERATURE.CCD_TEMPERATURE_VALUE')
        return True

    def sendDownloadMode(self, fastReadout=False):
        """
        :return: success
        """
        self.storePropertyToData(fastReadout,
                                 'READOUT_QUALITY.QUALITY_LOW',
                                 'READOUT_QUALITY.QUALITY_HIGH')
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
                     focalLength=1,
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
        :param focalLength:
        :return:
        """
        speed = 'High' if fastReadout else 'Normal'
        params = {'BinningMode': binning,
                  'ExposureLength': expTime,
                  'UseSubframe': True,
                  'X': int(posX / binning),
                  'Y': int(posY / binning),
                  'Width': int(width / binning),
                  'Height': int(height / binning),
                  'FrameType': 'Light',
                  'Speed': speed,
                  'Path': imagePath,
                  }

        suc, response = self.sgCaptureImage(params=params)
        if not suc:
            return False
        receipt = response.get('Receipt', '')
        if not receipt:
            return False
        self.waitCombined(self.sgGetImagePath, receipt, expTime)
        if not self.abortExpose:
            pre, ext = os.path.splitext(imagePath)
            os.rename(pre + '.fit', imagePath)
        else:
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
               ):
        """
        :return: success
        """
        if not self.deviceConnected:
            return False

        self.abortExpose = False
        worker = Worker(self.workerExpose,
                        imagePath=imagePath,
                        expTime=expTime,
                        binning=binning,
                        fastReadout=fastReadout,
                        posX=posX,
                        posY=posY,
                        width=width,
                        height=height,
                        focalLength=focalLength)
        self.threadPool.start(worker)
        return True

    def abort(self):
        """
        :return: success
        """
        if not self.deviceConnected:
            return False

        self.sgAbortImage()
        self.abortExpose = True
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

        self.sgSetCameraTemp(temperature=temperature)
        return True

    def sendOffset(self, offset=0):
        """
        :param offset:
        :return: success
        """
        if not self.deviceConnected:
            return False
        return True

    def sendGain(self, gain=0):
        """
        :param gain:
        :return: success
        """
        if not self.deviceConnected:
            return False
        return True
