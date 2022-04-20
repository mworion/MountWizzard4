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
import logging

# external packages
from astropy.io import fits
import numpy as np

# local imports
from gui.utilities.toolsQtWidget import sleepAndEvents
from mountcontrol.convert import formatDstrToText


class CameraSupport:
    """
    """
    __all__ = ['CameraSupport']
    log = logging.getLogger(__name__)
    raJ2000 = None
    decJ2000 = None

    def writeHeaderInfo(self, header, obs, expTime, binning, focalLength):
        """
        :param header:
        :param obs:
        :param expTime:
        :param binning:
        :param focalLength:
        :return:
        """
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
        header.append(('XBINNING', binning, 'MW4 same binning x/y'))
        header.append(('YBINNING', binning, 'MW4 same binning x/y'))
        header.append(('EXPTIME', expTime))
        header.append(('OBSERVER', 'MW4'))
        timeJD = obs.timeJD
        header.append(('DATE-OBS', timeJD.tt_strftime('%Y-%m-%dT%H:%M:%S'),
                       'Time is UTC of mount'))
        header.append(('MJD-OBS', timeJD.tt - 2400000.5, 'Time is UTC of mount'))
        header.append(('CCD-TEMP',
                       self.data.get('CCD_TEMPERATURE.CCD_TEMPERATURE_VALUE', 0)))
        header.append(('SQM',
                       self.app.skymeter.data.get('SKY_QUALITY.SKY_BRIGHTNESS', 0)))

        hasCoordinate = self.raJ2000 is not None and self.decJ2000 is not None
        isMount = obs.location is not None
        if hasCoordinate:
            header.append(('RA', self.raJ2000._degrees, 'Float value in degree'))
            header.append(('DEC', self.decJ2000.degrees, 'Float value in degree'))
        if isMount:
            header.append(('TELESCOP', self.app.mount.firmware.product,
                           'Mount version from firmware'))
            lat = obs.location.latitude
            header.append(('SITELAT', formatDstrToText(lat)))
            lon = obs.location.longitude
            header.append(('SITELON', formatDstrToText(lon)))
            elev = obs.location.elevation.m
            header.append(('SITEELEV', elev))

        return header

    def saveFits(self, imagePath, data, expTime, binning, focalLength):
        """
        :param imagePath:
        :param data:
        :param expTime:
        :param binning:
        :param focalLength:
        :return:
        """
        if self.abortExpose:
            return ''

        self.signals.downloaded.emit()
        self.signals.message.emit('saving')
        hdu = fits.PrimaryHDU(data=data)
        obs = self.app.mount.obsSite
        hdu.header = self.writeHeaderInfo(hdu.header, obs, expTime,
                                          binning, focalLength)
        hdu.writeto(imagePath, overwrite=True, output_verify='silentfix+warn')
        sleepAndEvents(100)
        self.log.info(f'Saved Image: [{imagePath}]')
        return imagePath

    def retrieveFits(self, function, param):
        """
        :param function:
        :param param:
        :return:
        """
        if self.abortExpose:
            return np.array([], dtype=np.uint16)

        self.signals.integrated.emit()
        self.signals.message.emit('download')
        tmp = function(param)
        if tmp is None:
            self.abortExpose = True
            data = np.array([], dtype=np.uint16)
        else:
            data = np.array(tmp, dtype=np.uint16).transpose()
        return data

    def waitExposed(self, function, param, expTime):
        """
        :param function:
        :param param:
        :param expTime:
        :return:
        """
        timeLeft = expTime
        while not function(param):
            if self.abortExpose:
                break
            text = f'expose {timeLeft:3.0f} s'
            sleepAndEvents(100)
            self.signals.message.emit(text)
            if timeLeft >= 0.1:
                timeLeft -= 0.1
            else:
                timeLeft = 0
        return True

    def waitStart(self):
        """
        :return:
        """
        while 'integrating' not in self.data.get('Device.Message'):
            if self.abortExpose:
                break
            sleepAndEvents(100)
        return True

    def waitIntegrate(self, timeLeft):
        """
        :param timeLeft:
        :return:
        """
        while 'integrating' in self.data.get('Device.Message'):
            if self.abortExpose:
                break
            text = f'expose {timeLeft:3.0f} s'
            sleepAndEvents(100)
            self.signals.message.emit(text)
            if timeLeft >= 0.1:
                timeLeft -= 0.1
            else:
                timeLeft = 0

        self.signals.integrated.emit()
        return True

    def waitDownload(self):
        """
        :return:
        """
        self.signals.message.emit('download')
        while 'downloading' in self.data.get('Device.Message'):
            if self.abortExpose:
                break
            sleepAndEvents(100)

        self.signals.downloaded.emit()
        return True

    def waitSave(self):
        """
        :return:
        """
        self.signals.message.emit('saving')
        while 'image is ready' in self.data.get('Device.Message'):
            if self.abortExpose:
                break
            sleepAndEvents(100)
        return True

    def waitFinish(self, function, param):
        """
        :param function:
        :param param:
        :return:
        """
        while not function(param):
            if self.abortExpose:
                break
            sleepAndEvents(100)
        return True

    def waitCombinedSGPro(self, function, param, expTime):
        """
        :param function:
        :param param:
        :param expTime:
        :return:
        """
        timeLeft = expTime
        self.waitStart()
        self.waitIntegrate(timeLeft)
        self.waitDownload()
        self.waitSave()
        self.waitFinish(function, param)
        return True

    def waitCombinedNINA(self, expTime):
        """
        :param expTime:
        :return:
        """
        timeLeft = expTime
        self.waitStart()
        self.waitIntegrate(timeLeft)
        self.waitDownload()
        self.waitSave()
        return True
