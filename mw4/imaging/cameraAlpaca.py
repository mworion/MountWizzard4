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
# Python  v3.7.5
#
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
from datetime import datetime
# external packages
import PyQt5
import numpy as np
# local imports
from mw4.base.loggerMW import CustomLogger
from mw4.base.alpacaClass import AlpacaClass
from mw4.base.alpacaBase import Camera
from mw4.base.tpool import Worker


class CameraAlpaca(AlpacaClass):
    """
    the class Dome inherits all information and handling of the Dome device. there will be
    some parameters who will define the slewing position of the dome relating to the
    mount.dome = DomeAlpaca(app=None)
    """

    __all__ = ['CameraAlpaca',
               ]

    logger = logging.getLogger(__name__)
    log = CustomLogger(logger, {})

    def __init__(self, app=None, signals=None, data=None):
        super().__init__(app=app)

        # as we have in the base class only the base client there, we will get more
        # specialized with Dome (which is derived from the base class)
        self.client = Camera()
        self.signals = signals
        self.data = data
        self.imagePath = ''

        self.app.update1s.connect(self.pollStatus)

    def getInitialConfig(self):
        """

        :return: true for test purpose
        """
        super().getInitialConfig()

        self.data['CCD_INFO.CCD_MAX_X'] = self.client.cameraxsize()
        self.data['CCD_INFO.CCD_MAX_Y'] = self.client.cameraysize()
        self.data['CAN_FAST'] = self.client.canfastreadout()
        self.data['CCD_INFO.CCD_PIXEL_SIZE_X'] = self.client.pixelsizex()
        self.data['CCD_INFO.CCD_PIXEL_SIZE_Y'] = self.client.pixelsizey()
        self.data['CCD_BINNING.HOR_BIN_MAX'] = self.client.maxbinx()
        self.data['CCD_BINNING.VERT_BIN_MAX'] = self.client.maxbiny()
        self.data['CCD_BINNING.HOR_BIN'] = self.client.binx()
        self.data['CCD_BINNING.VERT_BIN'] = self.client.biny()
        self.data['CCD_FRAME.X'] = self.client.startx()
        self.data['CCD_FRAME.Y'] = self.client.starty()

        return True

    def emitStatus(self):
        """

        :return: true for test purpose
        """
        states = ['Idle', 'Wait', 'Expose', 'Read', 'Download', 'Error']

        state = self.data['CAMERA.STATE']
        self.signals.message.emit(states[state])

        return True

    def workerStatus(self):
        """

        :return: true for test purpose
        """
        # bin
        # frame
        # expose
        # download
        # state

        self.data['CAMERA.STATE'] = self.client.camerastate()
        self.data['CCD_TEMPERATURE.CCD_TEMPERATURE_VALUE'] = self.client.ccdtemperature()
        self.data['IMAGEREADY'] = self.client.imageready()
        self.data['CCD_EXPOSURE.CCD_EXPOSURE_VALUE'] = self.client.lastexposureduration()
        value = self.client.fastreadout()
        self.data['READOUT_QUALITY.QUALITY_LOW'] = value
        self.data['READOUT_QUALITY.QUALITY_HIGH'] = not value

        return True

    def status(self):
        """

        :return: success
        """

        if not self.deviceConnected:
            return False

        worker = Worker(self.workerStatus)
        worker.signals.result.connect(self.emitStatus)
        self.threadPool.start(worker)
        return True

    def sendDownloadMode(self, fastReadout=False):
        """
        setDownloadMode sets the readout speed of the camera

        :return: success
        """

        # setting fast mode:
        suc = self.data['CAN_FAST']
        if suc:
            self.client.fastreadout(FastReadout=True)
        quality = 'High' if self.data.get('READOUT_QUALITY.QUALITY_HIGH', True) else 'Low'
        self.log.info(f'camera has readout quality entry: {quality}')

        return suc

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
        :return: success
        """

        self.imagePath = imagePath

        suc = self.sendDownloadMode(fastReadout=fastReadout)
        if not suc:
            self.log.info('Camera has no download quality settings')

        # bin
        # frame
        # expose
        print('exposing')
        self.signals.saved.emit(self.imagePath)

        return suc

    def expose(self,
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

        :return: success
        """

        if not self.deviceConnected:
            return False

        worker = Worker(self.workerExpose,
                        imagePath=imagePath,
                        expTime=expTime,
                        binning=binning,
                        fastReadout=fastReadout,
                        posX=posX,
                        posY=posY,
                        width=width,
                        height=height)
        # worker.signals.result.connect(self.emitStatus)
        self.threadPool.start(worker)
        return True

    def abort(self):
        """
        abort cancels the exposing

        :return: success
        """

        if not self.deviceConnected:
            return False

        # abort

        return True
