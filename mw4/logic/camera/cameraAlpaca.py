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
from base.alpacaClass import AlpacaClass
from base.tpool import Worker
from logic.camera.cameraSupport import CameraSupport


class CameraAlpaca(AlpacaClass, CameraSupport):
    """
    """

    __all__ = ['CameraAlpaca']

    def __init__(self, app=None, signals=None, data=None, parent=None):
        super().__init__(app=app, data=data)
        self.signals = signals
        self.data = data
        self.abortExpose = False
        self.parent = parent

    def workerGetInitialConfig(self):
        """
        :return: true for test purpose
        """
        super().workerGetInitialConfig()
        self.getAndStoreAlpacaProperty('cameraxsize', 'CCD_INFO.CCD_MAX_X')
        self.getAndStoreAlpacaProperty('cameraysize', 'CCD_INFO.CCD_MAX_Y')
        self.getAndStoreAlpacaProperty('canfastreadout', 'CAN_FAST')
        self.getAndStoreAlpacaProperty('canabortexposure', 'CAN_ABORT')
        self.getAndStoreAlpacaProperty('cansetccdtemperature', 'CAN_SET_CCD_TEMPERATURE')
        self.getAndStoreAlpacaProperty('cangetcoolerpower', 'CAN_GET_COOLER_POWER')
        self.getAndStoreAlpacaProperty('pixelsizex', 'CCD_INFO.CCD_PIXEL_SIZE_X')
        self.getAndStoreAlpacaProperty('pixelsizey', 'CCD_INFO.CCD_PIXEL_SIZE_Y')
        self.getAndStoreAlpacaProperty('maxbinx', 'CCD_BINNING.HOR_BIN_MAX')
        self.getAndStoreAlpacaProperty('maxbiny', 'CCD_BINNING.VERT_BIN_MAX')
        self.getAndStoreAlpacaProperty('gainmax', 'CCD_GAIN.GAIN_MAX')
        self.getAndStoreAlpacaProperty('gainmin', 'CCD_GAIN.GAIN_MIN')
        self.getAndStoreAlpacaProperty('gains', 'CCD_GAIN.GAIN_LIST')
        self.getAndStoreAlpacaProperty('offsetmax', 'CCD_OFFSET.OFFSET_MAX')
        self.getAndStoreAlpacaProperty('offsetmin', 'CCD_OFFSET.OFFSET_MIN')
        self.getAndStoreAlpacaProperty('offsets', 'CCD_OFFSET.OFFSET_LIST')
        self.getAndStoreAlpacaProperty('startx', 'CCD_FRAME.X')
        self.getAndStoreAlpacaProperty('starty', 'CCD_FRAME.Y')
        self.log.debug(f'Initial data: {self.data}')
        return True

    def workerPollData(self):
        """
        :return: true for test purpose
        """
        self.getAndStoreAlpacaProperty('binx', 'CCD_BINNING.HOR_BIN')
        self.getAndStoreAlpacaProperty('biny', 'CCD_BINNING.VERT_BIN')
        self.getAndStoreAlpacaProperty('camerastate', 'CAMERA.STATE')
        self.getAndStoreAlpacaProperty('gain', 'CCD_GAIN.GAIN')
        self.getAndStoreAlpacaProperty('offset', 'CCD_OFFSET.OFFSET')
        self.getAndStoreAlpacaProperty('fastreadout',
                                       'READOUT_QUALITY.QUALITY_LOW',
                                       'READOUT_QUALITY.QUALITY_HIGH')
        self.getAndStoreAlpacaProperty('ccdtemperature',
                                       'CCD_TEMPERATURE.CCD_TEMPERATURE_VALUE')
        self.getAndStoreAlpacaProperty('cooleron', 'CCD_COOLER.COOLER_ON')
        self.getAndStoreAlpacaProperty('coolerpower',
                                       'CCD_COOLER_POWER.CCD_COOLER_VALUE')
        return True

    def sendDownloadMode(self, fastReadout=False):
        """
        :return: success
        """
        canFast = self.data.get('CAN_FAST', False)
        if not canFast:
            return False
        if fastReadout:
            self.setAlpacaProperty('fastreadout', FastReadout=True)

        quality = 'High' if self.data.get('READOUT_QUALITY.QUALITY_HIGH', True) else 'Low'
        self.log.info(f'Camera has readout quality entry: {quality}')
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
        self.setAlpacaProperty('binx', BinX=int(binning))
        self.setAlpacaProperty('biny', BinY=int(binning))
        self.setAlpacaProperty('startx', StartX=int(posX / binning))
        self.setAlpacaProperty('starty', StartY=int(posY / binning))
        self.setAlpacaProperty('numx', NumX=int(width / binning))
        self.setAlpacaProperty('numy', NumY=int(height / binning))

        self.setAlpacaProperty('startexposure', Duration=expTime, Light=True)
        self.waitExposed(self.getAlpacaProperty, 'imageready', expTime)
        self.signals.exposed.emit()
        data = self.retrieveFits(self.getAlpacaProperty, 'imagearray')
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
        self.raJ2000 = None
        self.decJ2000 = None
        self.abortExpose = True
        if not self.deviceConnected:
            return False

        canAbort = self.data.get('CAN_ABORT', False)
        if not canAbort:
            return False

        self.getAlpacaProperty('stopexposure')
        return True

    def sendCoolerSwitch(self, coolerOn=False):
        """
        :param coolerOn:
        :return: success
        """
        if not self.deviceConnected:
            return False

        self.setAlpacaProperty('cooleron', CoolerOn=coolerOn)
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

        self.setAlpacaProperty('setccdtemperature', SetCCDTemperature=temperature)
        return True

    def sendOffset(self, offset=0):
        """
        :param offset:
        :return: success
        """
        if not self.deviceConnected:
            return False

        self.setAlpacaProperty('offset', Offset=offset)
        return True

    def sendGain(self, gain=0):
        """
        :param gain:
        :return: success
        """
        if not self.deviceConnected:
            return False

        self.setAlpacaProperty('gain', Gain=gain)
        return True
