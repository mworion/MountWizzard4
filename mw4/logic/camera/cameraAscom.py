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
# written in python3, (c) 2019-2023 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages

# local imports
from base.ascomClass import AscomClass
from logic.camera.cameraSupport import CameraSupport


class CameraAscom(AscomClass, CameraSupport):
    """
    """

    __all__ = ['CameraAscom']

    def __init__(self, app=None, signals=None, data=None):
        super().__init__(app=app, data=data)
        self.signals = signals
        self.abortExpose = False

    def workerGetInitialConfig(self):
        """
        :return: true for test purpose
        """
        super().workerGetInitialConfig()
        self.getAndStoreAscomProperty('CameraXSize', 'CCD_INFO.CCD_MAX_X')
        self.getAndStoreAscomProperty('CameraYSize', 'CCD_INFO.CCD_MAX_Y')
        self.getAndStoreAscomProperty('CanFastReadout', 'CAN_FAST')
        self.getAndStoreAscomProperty('CanAbortExposure', 'CAN_ABORT')
        self.getAndStoreAscomProperty('CanSetCCDTemperature', 'CAN_SET_CCD_TEMPERATURE')
        self.getAndStoreAscomProperty('CanGetCoolerPower', 'CAN_GET_COOLER_POWER')
        self.getAndStoreAscomProperty('PixelSizeX', 'CCD_INFO.CCD_PIXEL_SIZE_X')
        self.getAndStoreAscomProperty('PixelSizeY', 'CCD_INFO.CCD_PIXEL_SIZE_Y')
        self.getAndStoreAscomProperty('MaxBinX', 'CCD_BINNING.HOR_BIN_MAX')
        self.getAndStoreAscomProperty('MaxBinY', 'CCD_BINNING.VERT_BIN_MAX')
        self.getAndStoreAscomProperty('GainMax', 'CCD_GAIN.GAIN_MAX')
        self.getAndStoreAscomProperty('GainMin', 'CCD_GAIN.GAIN_MIN')
        self.getAndStoreAscomProperty('Gains', 'CCD_GAIN.GAIN_LIST')
        self.getAndStoreAscomProperty('OffsetMax', 'CCD_OFFSET.OFFSET_MAX')
        self.getAndStoreAscomProperty('OffsetMin', 'CCD_OFFSET.OFFSET_MIN')
        self.getAndStoreAscomProperty('Offsets', 'CCD_OFFSET.OFFSET_LIST')
        self.getAndStoreAscomProperty('StartX', 'CCD_FRAME.X')
        self.getAndStoreAscomProperty('StartY', 'CCD_FRAME.Y')
        self.log.debug(f'Initial data: {self.data}')
        return True

    def workerPollData(self):
        """
        :return: true for test purpose
        """
        self.getAndStoreAscomProperty('BinX', 'CCD_BINNING.HOR_BIN')
        self.getAndStoreAscomProperty('BinY', 'CCD_BINNING.VERT_BIN')
        self.getAndStoreAscomProperty('CameraState', 'CAMERA.STATE')
        self.getAndStoreAscomProperty('Gain', 'CCD_GAIN.GAIN')
        self.getAndStoreAscomProperty('Offset', 'CCD_OFFSET.OFFSET')
        self.getAndStoreAscomProperty('FastReadout',
                                      'READOUT_QUALITY.QUALITY_LOW',
                                      'READOUT_QUALITY.QUALITY_HIGH')
        self.getAndStoreAscomProperty('CCDTemperature',
                                      'CCD_TEMPERATURE.CCD_TEMPERATURE_VALUE')
        self.getAndStoreAscomProperty('CoolerOn', 'CCD_COOLER.COOLER_ON')
        self.getAndStoreAscomProperty('CoolerPower',
                                      'CCD_COOLER_POWER.CCD_COOLER_VALUE')
        return True

    def sendDownloadMode(self, fastReadout=False):
        """
        setDownloadMode sets the readout speed of the camera
        :return: success
        """
        canFast = self.data.get('CAN_FAST', False)
        if not canFast:
            return False
        if fastReadout:
            self.setAscomProperty('FastReadout', True)

        isQualityHigh = self.data.get('READOUT_QUALITY.QUALITY_HIGH', True)
        qualityText = 'High' if isQualityHigh else 'Low'
        self.log.debug(f'Camera has readout quality entry: {qualityText}')
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
        :return: success
        """
        self.sendDownloadMode(fastReadout=fastReadout)
        self.setAscomProperty('BinX', int(binning))
        self.setAscomProperty('BinY', int(binning))
        self.setAscomProperty('StartX', int(posX / binning))
        self.setAscomProperty('StartY', int(posY / binning))
        self.setAscomProperty('NumX', int(width / binning))
        self.setAscomProperty('NumY', int(height / binning))

        self.client.StartExposure(expTime, True)
        self.waitExposed(self.getAscomProperty, 'ImageReady', expTime)
        self.signals.exposed.emit()
        data = self.retrieveFits(self.getAscomProperty, 'ImageArray')
        self.signals.downloaded.emit()
        imagePath = self.saveFits(imagePath, data, expTime, binning, focalLength)
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
        self.raJ2000 = ra
        self.decJ2000 = dec
        self.abortExpose = False
        self.callMethodThreaded(self.workerExpose,
                                imagePath=imagePath,
                                expTime=expTime,
                                binning=binning,
                                fastReadout=fastReadout,
                                posX=posX,
                                posY=posY,
                                width=width,
                                height=height,
                                focalLength=focalLength)
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

        canAbort = self.data.get('CAN_ABORT', False)
        if not canAbort:
            return False

        self.callMethodThreaded(self.client.StopExposure)
        return True

    def sendCoolerSwitch(self, coolerOn=False):
        """
        :param coolerOn:
        :return: success
        """
        if not self.deviceConnected:
            return False

        self.setAscomProperty('CoolerOn', coolerOn)
        return True

    def sendCoolerTemp(self, temperature=0):
        """
        :param temperature:
        :return: success
        """
        if not self.deviceConnected:
            return False

        canSetCCDTemp = self.data.get('CAN_SET_CCD_TEMPERATURE', False)
        if not canSetCCDTemp:
            return False

        self.setAscomProperty('SetCCDTemperature', temperature)
        return True

    def sendOffset(self, offset=0):
        """
        :param offset:
        :return: success
        """
        if not self.deviceConnected:
            return False

        self.setAscomProperty('Offset', offset)
        return True

    def sendGain(self, gain=0):
        """
        :param gain:
        :return: success
        """
        if not self.deviceConnected:
            return False

        self.setAscomProperty('Gain', gain)
        return True
