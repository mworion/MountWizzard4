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
import os
import logging

# external packages
from PyQt5.QtCore import pyqtSignal, QObject
import numpy as np
import cv2
from astropy.io import fits
from xisf import XISF
from astropy import wcs

# local import
from base.tpool import Worker
from mountcontrol.convert import valueToFloat


class FileHandlerSignals(QObject):
    """
    """
    __all__ = ['FileHandlerSignals']
    imageLoaded = pyqtSignal()


class FileHandler:
    """
    """
    __all__ = ['FileHandler']
    log = logging.getLogger(__name__)

    def __init__(self, app, imagePath='', flipH=False, flipV=False):
        self.threadPool = app.threadPool
        self.signals = FileHandlerSignals()

        self.imagePath = imagePath
        self.flipH = flipH
        self.flipV = flipV
        self.image = None
        self.header = None
        self.wcs = None
        self.hasCelestial = False
        self.sizeX = 0
        self.sizeY = 0

    def debayerImage(self, pattern):
        """
        :param: pattern:
        :return:
        """
        if pattern == 'GBRG':
            R = self.image[1::2, 0::2]
            B = self.image[0::2, 1::2]
            G0 = self.image[0::2, 0::2]
            G1 = self.image[1::2, 1::2]

        elif pattern == 'RGGB':
            R = self.image[0::2, 0::2]
            B = self.image[1::2, 1::2]
            G0 = self.image[0::2, 1::2]
            G1 = self.image[1::2, 0::2]

        elif pattern == 'GRBG':
            R = self.image[0::2, 1::2]
            B = self.image[1::2, 0::2]
            G0 = self.image[0::2, 0::2]
            G1 = self.image[1::2, 1::2]

        elif pattern == 'BGGR':
            R = self.image[1::2, 1::2]
            B = self.image[0::2, 0::2]
            G0 = self.image[0::2, 1::2]
            G1 = self.image[1::2, 0::2]

        else:
            self.log.info('Unknown debayer pattern, keep it')
            return False

        self.image = 0.2989 * R + 0.5870 * (G0 + G1) / 2 + 0.1140 * B
        self.image = cv2.resize(self.image, (self.w, self.h))
        return True

    def cleanImageFormat(self):
        """
        :return:
        """
        if not self.flipV:
            self.image = np.flipud(self.image)
        if self.flipH:
            self.image = np.fliplr(self.image)
        self.image = (self.image / np.max(self.image) * 65536.0).astype('float32')
        return True

    def checkValidImageFormat(self):
        """
        :return:
        """
        if self.image is None or len(self.image) == 0:
            self.log.debug('No image data in FITS')
            self.image = None
            self.header = None
            return False
        if self.header is None:
            self.log.debug('No header data in FITS')
            self.image = None
            return False
        if self.header.get('NAXIS') != 2:
            self.log.debug('Incompatible format in FITS')
            self.image = None
            self.header = None
            return False
        return True

    def loadFITS(self):
        """
        :return:
        """
        with fits.open(self.imagePath) as fitsHandle:
            self.image = fitsHandle[0].data
            self.header = fitsHandle[0].header
        return True

    @staticmethod
    def convHeaderXISF2FITS(header):
        """
        :param header:
        :return:
        """
        hdu = fits.PrimaryHDU()
        fitsHeaderNew = hdu.header
        fitsHeaderNew['NAXIS'] = 2
        fitsHeaderNew['NAXIS1'] = header['geometry'][0]
        fitsHeaderNew['NAXIS2'] = header['geometry'][1]

        fitHeaderXisf = header['FITSKeywords']
        for key in fitHeaderXisf:
            if key in ['SIMPLE', 'EXTEND', 'NAXIS', 'NAXIS1', 'NAXIS2']:
                continue
            value = fitHeaderXisf[key][0].get('value', '')
            valueFloat = valueToFloat(value)
            value = value if valueFloat is None else valueFloat
            comment = fitHeaderXisf[key][0].get('comment', '')
            fitsHeaderNew.append((key, value, comment))
        return fitsHeaderNew

    def loadXISF(self):
        """
        :return:
        """
        header = {}
        self.image = XISF.read(self.imagePath, image_metadata=header)[:, :, -1]
        self.header = self.convHeaderXISF2FITS(header)
        return True

    def workerLoadImage(self, imagePath):
        """
        :param imagePath:
        :return:
        """
        self.imagePath = imagePath
        _, ext = os.path.splitext(self.imagePath)

        if ext in ['.fits', '.fit']:
            self.loadFITS()
        elif ext in ['.xisf']:
            self.loadXISF()

        isValid = self.checkValidImageFormat()
        if not isValid:
            self.signals.imageLoaded.emit()
            return False

        self.cleanImageFormat()
        bayerPattern = self.header.get('BAYERPAT', '')
        if bayerPattern:
            self.debayerImage(bayerPattern)
            self.log.debug(f'Image has bayer pattern: {bayerPattern}')

        self.wcs = wcs.WCS(self.header)
        self.hasCelestial = self.wcs.has_celestial
        self.sizeY, self.sizeX = self.wcs.array_shape
        self.signals.imageLoaded.emit()
        return True

    def loadImage(self, imagePath='', flipH=False, flipV=False):
        """
        :param: imagePath:
        :param: flipH:
        :param: flipV:
        :return:
        """
        if not os.path.isfile(imagePath):
            return False

        self.image = None
        self.imagePath = imagePath
        self.flipH = flipH
        self.flipV = flipV

        worker = Worker(self.workerLoadImage, imagePath)
        self.threadPool.start(worker)
        return True
