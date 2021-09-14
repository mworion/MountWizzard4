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
from mountcontrol.convert import sexagesimalizeToInt
from base.alpacaClass import AlpacaClass
from base.alpacaBase import Camera
from base.tpool import Worker
from base.transform import JNowToJ2000


def formatDstrToText(angle):
    """
    :param angle:
    :return:
    """
    sgn, d, m, s, frac = sexagesimalizeToInt(angle.degrees, 0)
    sign = '+' if sgn >= 0 else '-'
    text = f'{sign}{d:02d} {m:02d} {s:02d}'
    return text


class CameraAlpaca(AlpacaClass):
    """
    the class CameraAlpaca inherits all information and handling of the CameraAlpaca device.
    """

    __all__ = ['CameraAlpaca',
               ]

    CYCLE_POLL_DATA = 1000

    def __init__(self, app=None, signals=None, data=None):
        super().__init__(app=app, data=data, threadPool=app.threadPool)
        self.client = Camera()
        self.signals = signals
        self.data = data
        self.abortExpose = False

    def getInitialConfig(self):
        """

        :return: true for test purpose
        """

        super().getInitialConfig()

        self.storePropertyToData(self.client.cameraxsize(), 'CCD_INFO.CCD_MAX_X')
        self.storePropertyToData(self.client.cameraysize(), 'CCD_INFO.CCD_MAX_Y')
        self.storePropertyToData(self.client.canfastreadout(), 'CAN_FAST')
        self.storePropertyToData(self.client.canstopexposure(), 'CAN_ABORT')
        self.storePropertyToData(self.client.cansetccdtemperature(), 'CAN_SET_CCD_TEMPERATURE')
        self.storePropertyToData(self.client.cangetcoolerpower(), 'CAN_GET_COOLER_POWER')
        self.storePropertyToData(self.client.pixelsizex(), 'CCD_INFO.CCD_PIXEL_SIZE_X')
        self.storePropertyToData(self.client.pixelsizey(), 'CCD_INFO.CCD_PIXEL_SIZE_Y')
        self.storePropertyToData(self.client.maxbinx(), 'CCD_BINNING.HOR_BIN_MAX')
        self.storePropertyToData(self.client.maxbiny(), 'CCD_BINNING.VERT_BIN_MAX')
        self.storePropertyToData(self.client.gainmax(), 'CCD_INFO.GAIN_MAX')
        self.storePropertyToData(self.client.gainmin(), 'CCD_INFO.GAIN_MIN')
        self.storePropertyToData(self.client.startx(), 'CCD_FRAME.X')
        self.storePropertyToData(self.client.starty(), 'CCD_FRAME.Y')
        self.log.debug(f'Initial data: {self.data}')

        return True

    def workerPollData(self):
        """

        :return: true for test purpose
        """
        if not self.deviceConnected:
            return False

        self.storePropertyToData(self.client.binx(), 'CCD_BINNING.HOR_BIN')
        self.storePropertyToData(self.client.biny(), 'CCD_BINNING.VERT_BIN')
        self.storePropertyToData(self.client.camerastate(), 'CAMERA.STATE')
        self.storePropertyToData(self.client.gain(), 'CCD_GAIN.GAIN')
        self.storePropertyToData(self.client.offset(), 'CCD_OFFSET.OFFSET')
        self.storePropertyToData(self.client.fastreadout(),
                                 'READOUT_QUALITY.QUALITY_LOW',
                                 'READOUT_QUALITY.QUALITY_HIGH')
        self.storePropertyToData(self.client.ccdtemperature(),
                                 'CCD_TEMPERATURE.CCD_TEMPERATURE_VALUE')
        self.storePropertyToData(self.client.cooleron(), 'CCD_COOLER.COOLER_ON')
        self.storePropertyToData(self.client.coolerpower(),
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
        :return: success
        """
        self.sendDownloadMode(fastReadout=fastReadout)
        self.client.binx(BinX=int(binning))
        self.client.biny(BinY=int(binning))
        self.client.startx(StartX=int(posX / binning))
        self.client.starty(StartY=int(posY / binning))
        self.client.numx(NumX=int(width / binning))
        self.client.numy(NumY=int(height / binning))

        isMount = self.app.deviceStat['mount']
        if isMount:
            ra = self.app.mount.obsSite.raJNow
            dec = self.app.mount.obsSite.decJNow
            obsTime = self.app.mount.obsSite.timeJD
            if ra is not None and dec is not None and obsTime is not None:
                ra, dec = JNowToJ2000(ra, dec, obsTime)

        self.client.startexposure(Duration=expTime, Light=True)

        timeLeft = expTime
        while not self.client.imageready():
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
        self.signals.message.emit('download')
        tmp = self.client.imagearray()
        if tmp is None:
            self.abortExpose = True
        else:
            data = np.array(tmp, dtype=np.uint16).transpose()
        
        if not self.abortExpose:
            self.signals.message.emit('saving')
            hdu = fits.PrimaryHDU(data=data)
            header = hdu.header
            header.append(('OBJECT', 'SKY_OBJECT', 'default name from MW4'))
            header.append(('FRAME', 'Light', 'Modeling works with light frames'))
            header.append(('EQUINOX', 2000, 'All data is stored in J2000'))
            header.append(('PIXSIZE1', self.data['CCD_INFO.CCD_PIXEL_SIZE_X'] * binning))
            header.append(('PIXSIZE2', self.data['CCD_INFO.CCD_PIXEL_SIZE_Y'] * binning))
            header.append(('XPIXSZ', self.data['CCD_INFO.CCD_PIXEL_SIZE_X'] * binning))
            header.append(('YPIXSZ', self.data['CCD_INFO.CCD_PIXEL_SIZE_Y'] * binning))

            if focalLength:
                factor = binning / focalLength * 206.265
                header.append(('FOCALLEN', focalLength,
                               'Data taken from driver or manual input'))
            else:
                factor = 1

            header.append(('SCALE', self.data['CCD_INFO.CCD_PIXEL_SIZE_X'] * factor))
            header.append(('XBINNING', binning, 'MW4 is using the same binning for x and y'))
            header.append(('YBINNING', binning, 'MW4 is using the same binning for x and y'))
            header.append(('EXPTIME', expTime))
            header.append(('OBSERVER', 'MW4'))
            timeJD = self.app.mount.obsSite.timeJD
            header.append(('DATE-OBS', timeJD.tt_strftime('%Y-%m-%dT%H:%M:%S'),
                           'Time is UTC of mount'))
            header.append(('CCD-TEMP', self.data.get('CCD_TEMPERATURE.CCD_TEMPERATURE_VALUE', 0)))
            header.append(('SQM', self.app.skymeter.data.get('SKY_QUALITY.SKY_BRIGHTNESS', 0)))

            if isMount:
                header.append(('RA', ra._degrees))
                header.append(('DEC', dec.degrees))
                header.append(('TELESCOP',
                               self.app.mount.firmware.product,
                               'Mount version from firmware'))
                lat = self.app.mount.obsSite.location.latitude
                header.append(('SITELAT', formatDstrToText(lat)))
                lon = self.app.mount.obsSite.location.longitude
                header.append(('SITELON', formatDstrToText(lon)))
                elev = self.app.mount.obsSite.location.elevation.m
                header.append(('SITEELEV', elev))

            hdu.writeto(imagePath, overwrite=True, output_verify='silentfix+warn')
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

        self.abortExpose = True
        canAbort = self.data.get('CAN_ABORT', False)

        if not canAbort:
            return False

        self.client.stopexposure()

        return True

    def sendCoolerSwitch(self, coolerOn=False):
        """
        sendCoolerTemp send the desired cooler temp, but does not switch on / off the cooler

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

        canSetCCDTemp = self.data.get('CAN_SET_CCD_TEMPERATURE', False)
        if not canSetCCDTemp:
            return False

        self.client.setccdtemperature(SetCCDTemperature=temperature)
        return True

    def sendOffset(self, offset=0):
        """
        :param offset:
        :return: success
        """
        if not self.deviceConnected:
            return False

        self.client.offset(Offset=offset)
        return True

    def sendGain(self, gain=0):
        """
        :param gain:
        :return: success
        """
        if not self.deviceConnected:
            return False

        self.client.gain(Gain=gain)
        return True
