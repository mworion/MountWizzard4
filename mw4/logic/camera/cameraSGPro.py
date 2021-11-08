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

# external packages

# local imports
from base.sgproClass import SGProClass
from base.tpool import Worker
from logic.camera.cameraSupport import CameraSupport


class CameraSGPro(SGProClass, CameraSupport):
    """
    """

    __all__ = ['CameraSGPro']

    def __init__(self, app=None, signals=None, data=None, parent=None):
        super().__init__(app=app, data=data, threadPool=app.threadPool)
        self.signals = signals
        self.data = data
        self.abortExpose = False
        self.parent = parent

    def getInitialConfig(self):
        """
        :return: true for test purpose
        """
        if not self.deviceConnected:
            return False
        super().getInitialConfig()
        self.log.debug(f'Initial data: {self.data}')
        return True

    def workerPollData(self):
        """
        :return: true for test purpose
        """
        if not self.deviceConnected:
            return False

        return True

    def sendDownloadMode(self, fastReadout=False):
        """
        :return: success
        """
        canFast = self.data.get('CAN_FAST', False)
        if not canFast:
            return False
        if fastReadout:
            self.client.fastreadout(FastReadout=True)

        quality = 'High' if self.data.get('READOUT_QUALITY.QUALITY_HIGH', True) else 'Low'
        self.log.debug(f'camera has readout quality entry: {quality}')
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
        self.sendDownloadMode(fastReadout=fastReadout)
        self.setSGProProperty('binx', BinX=int(binning))
        self.setSGProProperty('biny', BinY=int(binning))
        self.setSGProProperty('startx', StartX=int(posX / binning))
        self.setSGProProperty('starty', StartY=int(posY / binning))
        self.setSGProProperty('numx', NumX=int(width / binning))
        self.setSGProProperty('numy', NumX=int(width / binning))

        self.setSGProProperty('startexposure', Duration=expTime, Light=True)
        self.waitExposed(self.getSGProProperty, 'imageready', expTime)
        data = self.retrieveFits(self.getSGProProperty, 'imagearray')
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

        self.abortExpose = True
        canAbort = self.data.get('CAN_ABORT', False)

        if not canAbort:
            return False

        self.client.stopexposure()
        return True

    def sendCoolerSwitch(self, coolerOn=False):
        """
        :param coolerOn:
        :return: success
        """
        if not self.deviceConnected:
            return False

        self.client.cooleron(CoolerOn=coolerOn)
        return True

    def sendCoolerTemp(self, temperature=0):
        """
        :param temperature:
        :return: success
        """
        if not self.deviceConnected:
            return False

        self.client.setccdtemperature(SetCCDTemperature=temperature)
        return True
