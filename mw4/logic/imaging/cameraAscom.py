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
import numpy as np
from astropy.io import fits
from PyQt5.QtTest import QTest

# local imports
from base.ascomClass import AscomClass
from base.tpool import Worker
from base import transform


class CameraAscom(AscomClass):
    """
    the class CameraAscom inherits all information and handling of the Ascom device.
    """

    __all__ = ['CameraAscom',
               ]

    CYCLE_DEVICE = 3000
    CYCLE_DATA = 1000

    def __init__(self, app=None, signals=None, data=None):
        super().__init__(app=app, data=data, threadPool=app.threadPool)

        self.signals = signals
        self.data = data
        self.abortExpose = False

    def getInitialConfig(self):
        """
        :return: true for test purpose
        """
        super().getInitialConfig()

        if not self.deviceConnected:
            return False

        self.dataEntry(self.client.CameraXSize, 'CCD_INFO.CCD_MAX_X')
        self.dataEntry(self.client.CameraYSize, 'CCD_INFO.CCD_MAX_Y')
        self.dataEntry(self.client.CanFastReadout, 'CAN_FAST')
        self.dataEntry(self.client.CanAbortExposure, 'CAN_ABORT')
        self.dataEntry(self.client.PixelSizeX, 'CCD_INFO.CCD_PIXEL_SIZE_X')
        self.dataEntry(self.client.PixelSizeY, 'CCD_INFO.CCD_PIXEL_SIZE_Y')
        self.dataEntry(self.client.MaxBinX, 'CCD_BINNING.HOR_BIN_MAX')
        self.dataEntry(self.client.MaxBinY, 'CCD_BINNING.VERT_BIN_MAX')
        self.dataEntry(self.client.BinX, 'CCD_BINNING.HOR_BIN')
        self.dataEntry(self.client.BinY, 'CCD_BINNING.VERT_BIN')
        self.dataEntry(self.client.StartX, 'CCD_FRAME.X')
        self.dataEntry(self.client.StartY, 'CCD_FRAME.Y')
        self.log.debug(f'Initial data: {self.data}')

        return True

    def workerPollData(self):
        """
        :return: true for test purpose
        """
        if not self.deviceConnected:
            return False

        self.dataEntry(self.client.CameraState,
                       'CAMERA.STATE')
        self.dataEntry(self.client.CCDTemperature,
                       'CCD_TEMPERATURE.CCD_TEMPERATURE_VALUE')
        self.dataEntry(self.client.CoolerOn,
                       'CCD_COOLER.COOLER_ON')
        self.dataEntry(self.client.CoolerPower,
                       'CCD_COOLER_POWER.CCD_COOLER_VALUE')

        canFast = self.data.get('CAN_FAST', False)
        if not canFast:
            return False

        self.dataEntry(self.client.FastReadout,
                       'READOUT_QUALITY.QUALITY_LOW',
                       'READOUT_QUALITY.QUALITY_HIGH')

        return True

    def sendDownloadMode(self, fastReadout=False):
        """
        setDownloadMode sets the readout speed of the camera
        :return: success
        """
        canFast = self.data.get('CAN_FAST', False)

        if not canFast:
            return False

        if not self.deviceConnected:
            return False

        if fastReadout:
            self.client.FastReadout = True

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
        :return: success
        """
        if not self.deviceConnected:
            return False

        self.sendDownloadMode(fastReadout=fastReadout)
        self.client.BinX = int(binning)
        self.client.BinY = int(binning)
        self.client.StartX = int(posX / binning)
        self.client.StartY = int(posY / binning)
        self.client.NumX = int(width / binning)
        self.client.NumY = int(height / binning)

        isMount = self.app.deviceStat['mount']
        if isMount:
            ra = self.app.mount.obsSite.raJNow
            dec = self.app.mount.obsSite.decJNow
            obsTime = self.app.mount.obsSite.timeJD
            if ra is not None and dec is not None and obsTime is not None:
                ra, dec = transform.JNowToJ2000(ra, dec, obsTime)

        self.client.StartExposure(expTime, True)

        timeLeft = expTime
        while not self.client.ImageReady:
            text = f'expose {timeLeft:3.0f} s'
            QTest.qWait(100)
            if timeLeft >= 0.1:
                timeLeft -= 0.1

            else:
                timeLeft = 0

            self.signals.message.emit(text)
            if self.abortExpose:
                break

        self.signals.integrated.emit()

        if not self.abortExpose:
            self.signals.message.emit('download')
            data = np.array(self.client.ImageArray, dtype=np.uint16)
            data = np.transpose(data)

        if not self.abortExpose:
            self.signals.message.emit('saving')
            hdu = fits.PrimaryHDU(data=data)
            header = hdu.header
            header['OBJECT'] = 'skymodel'
            header['FRAME'] = 'Light'
            header['EQUINOX'] = 2000
            header['PIXSIZE1'] = self.data['CCD_INFO.CCD_PIXEL_SIZE_X'] * binning
            header['PIXSIZE2'] = self.data['CCD_INFO.CCD_PIXEL_SIZE_Y'] * binning
            header['XPIXSZ'] = self.data['CCD_INFO.CCD_PIXEL_SIZE_X'] * binning
            header['YPIXSZ'] = self.data['CCD_INFO.CCD_PIXEL_SIZE_Y'] * binning

            factor = binning / focalLength * 206.265
            header['SCALE'] = self.data['CCD_INFO.CCD_PIXEL_SIZE_X'] * factor
            header['XBINNING'] = binning
            header['YBINNING'] = binning
            header['EXPTIME'] = expTime
            header['OBSERVER'] = 'MW4'
            header['DATE-OBS'] = self.app.mount.obsSite.timeJD.utc_iso()
            header['CCD-TEMP'] = self.data.get('CCD_TEMPERATURE.CCD_TEMPERATURE_VALUE', 0)
            header['SQM'] = self.app.skymeter.data.get('SKY_QUALITY.SKY_BRIGHTNESS', 0)

            if isMount:
                header['RA'] = ra._degrees
                header['DEC'] = dec.degrees
                header['TELESCOP'] = self.app.mount.firmware.product

            hdu.writeto(imagePath, overwrite=True)
            self.log.info(f'Saved Image: [{imagePath}]')

        if self.abortExpose:
            imagePath = ''

        self.signals.saved.emit(imagePath)
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

        self.client.StopExposure()

        return True

    def sendCoolerSwitch(self, coolerOn=False):
        """
        :param coolerOn:
        :return: success
        """
        if not self.deviceConnected:
            return False

        self.client.CoolerOn = coolerOn

        return True

    def sendCoolerTemp(self, temperature=0):
        """
        :param temperature:
        :return: success
        """
        if not self.deviceConnected:
            return False

        self.client.SetCCDTemperature = temperature

        return True
