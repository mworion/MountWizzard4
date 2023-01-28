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

    @staticmethod
    def writeHeaderBasic(header):
        """
        :param header:
        :return:
        """
        header.append(('OBJECT', 'SKY_OBJECT', 'default name from MW4'))
        header.append(('AUTHOR', 'MountWizzard4', 'default name from MW4'))
        header.append(('FRAME', 'Light', 'Modeling works with light frames'))
        header.append(('EQUINOX', 2000, 'All data is stored in J2000'))
        header.append(('OBSERVER', 'MW4'))
        return True

    def writeHeaderCamera(self, header, expTime, binning):
        """
        :param header:
        :param expTime:
        :param binning:
        :return:
        """
        header.append(('PIXSIZE1', self.data['CCD_INFO.CCD_PIXEL_SIZE_X'] * binning))
        header.append(('PIXSIZE2', self.data['CCD_INFO.CCD_PIXEL_SIZE_Y'] * binning))
        header.append(('XPIXSZ', self.data['CCD_INFO.CCD_PIXEL_SIZE_X'] * binning))
        header.append(('YPIXSZ', self.data['CCD_INFO.CCD_PIXEL_SIZE_Y'] * binning))
        header.append(('XBINNING', binning, 'MW4 same binning x/y'))
        header.append(('YBINNING', binning, 'MW4 same binning x/y'))
        header.append(('EXPTIME', expTime))
        header.append(('OBSERVER', 'MW4'))
        header.append(('CCD-TEMP',
                       self.data.get('CCD_TEMPERATURE.CCD_TEMPERATURE_VALUE', 0)))
        header.append(('SQM',
                       self.app.skymeter.data.get('SKY_QUALITY.SKY_BRIGHTNESS', 0)))
        header.append(('FOCPOS',
                       self.app.focuser.data.get(
                           'ABS_FOCUS_POSITION.FOCUS_ABSOLUTE_POSITION', 0)))
        header.append(('FOCTEMP',
                       self.app.directWeather.data.get(
                           'WEATHER_PARAMETERS.WEATHER_TEMPERATURE', 0)))

        filterNumber = self.app.filter.data.get('FILTER_SLOT.FILTER_SLOT_VALUE', 1)
        key = f'FILTER_NAME.FILTER_SLOT_NAME_{filterNumber:1.0f}'
        filterName = self.app.filter.data.get(key, 'not found')
        header.append(('FILTER', filterName))
        return True

    @staticmethod
    def writeHeaderTime(header, obs):
        """
        :param header:
        :param obs:
        :return:
        """
        timeJD = obs.timeJD
        header.append(('DATE-OBS', timeJD.tt_strftime('%Y-%m-%dT%H:%M:%S'),
                       'Time is UTC of mount at end of exposure'))
        header.append(('MJD-OBS', timeJD.tt - 2400000.5,
                       'Time is UTC of mount at end of exposure'))
        return True

    def writeHeaderOptical(self, header, binning, focalLength):
        """
        :param header:
        :param binning:
        :param focalLength:
        :return:
        """
        if not focalLength:
            return False

        factor = binning / focalLength * 206.265
        header.append(('FOCALLEN',
                       focalLength, 'Data taken from driver or manual input'))
        header.append(('SCALE',
                       self.data['CCD_INFO.CCD_PIXEL_SIZE_X'] * factor))
        return True

    def writeHeaderSite(self, header, obs):
        """
        :param header:
        :param obs:
        :return:
        """
        hasCoordinate = self.raJ2000 is not None and self.decJ2000 is not None
        if hasCoordinate:
            header.append(('RA', self.raJ2000._degrees, 'Float value in degree'))
            header.append(('DEC', self.decJ2000.degrees, 'Float value in degree'))

        isMount = obs.location is not None
        if isMount:
            header.append(('TELESCOP', self.app.mount.firmware.product,
                           'Mount version from firmware'))
            lat = obs.location.latitude
            header.append(('SITELAT', formatDstrToText(lat)))
            lon = obs.location.longitude
            header.append(('SITELON', formatDstrToText(lon)))
            elev = obs.location.elevation.m
            header.append(('SITEELEV', elev))
        return True

    @staticmethod
    def writeHeaderFocus(header, focuser):
        """
        :param header:
        :param focuser:
        :return:
        """
        pos = focuser.data.get('ABS_FOCUS_POSITION.FOCUS_ABSOLUTE_POSITION', 0)
        header.append(('FOCUSPOS', pos, 'Actual focuser position'))
        return True

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

        self.signals.message.emit('saving')
        hdu = fits.PrimaryHDU(data=data)
        obs = self.app.mount.obsSite
        self.writeHeaderBasic(hdu.header)
        self.writeHeaderCamera(hdu.header, expTime, binning)
        self.writeHeaderTime(hdu.header, obs)
        self.writeHeaderOptical(hdu.header, binning, focalLength)
        self.writeHeaderSite(hdu.header, obs)
        self.writeHeaderFocus(hdu.header, self.app.focuser)
        hdu.writeto(imagePath, overwrite=True, output_verify='silentfix+warn')
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

    def waitExposedApp(self, timeLeft):
        """
        :param timeLeft:
        :return:
        """
        while 'integrating' in self.data.get('Device.Message'):
            if self.abortExpose:
                break
            sleepAndEvents(100)
            text = f'expose {timeLeft:3.0f} s'
            self.signals.message.emit(text)
            if timeLeft >= 0.1:
                timeLeft -= 0.1
            else:
                timeLeft = 0
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
