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

# local import
from base.tpool import Worker


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
            return False
        if self.header is None:
            self.log.debug('No header data in FITS')
            return False
        if self.header.get('NAXIS') != 2:
            self.log.debug('Incompatible format in FITS')
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

    def loadXSIF(self):
        """
        :return:
        """
        return True

    def workerLoadImage(self, imagePath):
        """
        :param imagePath:
        :return:
        """
        self.imagePath = imagePath
        _, ext = os.path.splitext(self.imagePath)

        self.image = None
        self.header = None
        if ext in ['.fits', '.fit']:
            self.loadFITS()
        elif ext in ['.xsif']:
            self.loadXSIF()

        isValid = self.checkValidImageFormat()
        if not isValid:
            self.signals.imageLoaded.emit()
            return False

        self.cleanImageFormat()
        bayerPattern = self.header.get('BAYERPAT', '')
        if bayerPattern:
            self.debayerImage(bayerPattern)
            self.log.debug(f'Image has bayer pattern: {bayerPattern}')

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
