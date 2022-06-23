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
import numpy as np
import cv2
import sep
from PyQt5.QtCore import pyqtSignal, QObject
from astropy.io import fits
from scipy.interpolate import griddata
from scipy.ndimage import uniform_filter

# local import
from base.tpool import Worker


class PhotometrySignals(QObject):
    """
    """
    __all__ = ['PhotometrySignals']
    image = pyqtSignal()
    hfr = pyqtSignal()
    hfrSquare = pyqtSignal()
    hfrTriangle = pyqtSignal()
    aberration = pyqtSignal()
    roundness = pyqtSignal()
    background = pyqtSignal()
    backgroundRMS = pyqtSignal()
    sepFinished = pyqtSignal()


class Photometry:
    """
    """
    __all__ = ['Photometry']
    log = logging.getLogger(__name__)

    ABERRATION_SIZE = 250
    FILTER_SCALE = 10

    def __init__(self, parent, imagePath=''):
        self.threadPool = parent.threadPool
        self.signals = PhotometrySignals()

        self.image = None
        self.header = None
        self.aberrationImage = None

        self.objs = None
        self.objsAll = None
        self.bkg = None

        self.xm = None
        self.ym = None
        self.h = None
        self.w = None
        self.filterConstW = None
        self.filterConstH = None

        self.roundnessGrid = None
        self.roundnessMin = None
        self.roundnessMax = None
        self.roundnessPercentile = None

        self.background = None
        self.backgroundMin = None
        self.backgroundMax = None
        self.backgroundRMS = None

        self.HFR = None
        self.hfrMin = None
        self.hfrMax = None
        self.hfrPercentile = None
        self.hfrMedian = None
        self.hfrGrid = None
        self.hfrInner = None
        self.hfrOuter = None
        self.hfrSegTriangle = None
        self.hfrSegSquare = None

        self.processImage(imagePath)

    def baseCalcs(self):
        """
        :return:
        """
        self.h, self.w = self.image.shape
        self.filterConstW = int(self.w / (self.FILTER_SCALE * 3))
        self.filterConstH = int(self.h / (self.FILTER_SCALE * 3))
        rangeX = np.linspace(0, self.w, int(self.w / self.FILTER_SCALE))
        rangeY = np.linspace(0, self.h, int(self.h / self.FILTER_SCALE))
        self.xm, self.ym = np.meshgrid(rangeX, rangeY)
        x = self.objs['x'] - self.w / 2
        y = self.objs['y'] - self.h / 2
        radius = np.sqrt(x * x + y * y)
        maskOuter = np.sqrt(self.h * self.h / 4 + self.w * self.w / 4) * 0.75 < radius
        maskInner = np.sqrt(self.h * self.h / 4 + self.w * self.w / 4) * 0.25 > radius
        self.hfrOuter = np.median(self.HFR[maskOuter])
        self.hfrInner = np.median(self.HFR[maskInner])
        self.hfrPercentile = np.percentile(self.HFR, 90)
        self.hfrMedian = np.median(self.HFR)
        return True

    def workerGetHFR(self):
        """
        :return:
        """
        img = griddata((self.objs['x'], self.objs['y']),
                       self.HFR, (self.xm, self.ym),
                       method='nearest', fill_value=np.min(self.HFR))
        self.hfrGrid = uniform_filter(img, size=[self.filterConstH,
                                      self.filterConstW])
        minB, maxB = np.percentile(self.hfrGrid, (50, 95))
        self.hfrMin = minB
        self.hfrMax = maxB
        self.signals.hfr.emit()
        return True

    def workerGetRoundness(self):
        """
        :return:
        """
        a = self.objs['a']
        b = self.objs['b']
        aspectRatio = np.maximum(a / b, b / a)
        minB, maxB = np.percentile(aspectRatio, (50, 95))
        img = griddata((self.objs['x'], self.objs['y']), aspectRatio, (self.xm,
                                                                       self.ym),
                       method='linear', fill_value=np.min(aspectRatio))
        self.roundnessGrid = uniform_filter(img, size=[self.filterConstH,
                                            self.filterConstW])
        self.roundnessPercentile = np.percentile(aspectRatio, 90)
        self.roundnessMin = minB
        self.roundnessMax = maxB
        self.signals.roundness.emit()
        return True

    def workerCalcTiltValuesSquare(self):
        """
        :return:
        """
        stepY = int(self.h / 3)
        stepX = int(self.w / 3)

        xRange = [0, stepX, 2 * stepX, 3 * stepX]
        yRange = [0, stepY, 2 * stepY, 3 * stepY]
        x = self.objs['x']
        y = self.objs['y']
        segHFR = np.zeros((3, 3))
        for ix in range(3):
            for iy in range(3):
                xMin = xRange[ix]
                xMax = xRange[ix + 1]
                yMin = yRange[iy]
                yMax = yRange[iy + 1]
                hfr = self.HFR[(x > xMin) & (x < xMax) & (y > yMin) & (y < yMax)]
                med_hfr = np.median(hfr)
                segHFR[ix][iy] = med_hfr
        self.hfrSegSquare = segHFR
        self.signals.hfrSquare.emit()
        return True

    def workerCalcTiltValuesTriangle(self):
        """
        :return:
        """
        x = self.objs['x'] - self.w / 2
        y = self.objs['y'] - self.h / 2
        radius = min(self.h / 2, self.w / 2)
        mask1 = np.sqrt(self.h * self.h + self.w * self.w) * 0.25 < radius
        mask2 = np.sqrt(self.h * self.h + self.w * self.w) > radius
        segHFR = np.zeros(36)
        angles = np.mod(np.arctan2(y, x), 2 * np.pi)
        rangeA = np.radians(range(0, 361, 10))
        for i in range(36):
            mask3 = rangeA[i] < angles
            mask4 = rangeA[i + 1] > angles
            segHFR[i] = np.median(self.HFR[mask1 & mask2 & mask3 & mask4])
        self.hfrSegTriangle = np.concatenate([segHFR, segHFR])
        self.signals.hfrTriangle.emit()
        return True

    def calcAberrationInspectView(self):
        """
        :return:
        """
        size = self.ABERRATION_SIZE
        if self.w < 3 * size or self.h < 3 * size:
            self.aberrationImage = self.image
            return False

        dw = int((self.w - 3 * size) / 2)
        dh = int((self.h - 3 * size) / 2)

        img = np.delete(self.image, np.s_[size:size + dh], axis=0)
        img = np.delete(img, np.s_[size * 2:size * 2 + dh], axis=0)
        img = np.delete(img, np.s_[size:size + dw], axis=1)
        img = np.delete(img, np.s_[size * 2:size * 2 + dw], axis=1)
        self.aberrationImage = img
        self.signals.aberration.emit()
        return True

    def calcBackground(self):
        """
        :return:
        """
        back = self.bkg.back()
        maxB = np.max(back) / self.bkg.globalback
        minB = np.min(back) / self.bkg.globalback
        img = back / self.bkg.globalback
        self.background = uniform_filter(img, size=[self.filterConstH,
                                         self.filterConstW])
        self.backgroundMin = minB
        self.backgroundMax = maxB
        self.signals.background.emit()
        return True

    def calcBackgroundRMS(self):
        """
        :return:
        """
        img = self.bkg.rms()
        self.backgroundRMS = uniform_filter(img, size=[self.filterConstH,
                                            self.filterConstW])
        self.signals.backgroundRMS.emit()
        return True

    def runCalcs(self):
        """
        :return:
        """
        self.baseCalcs()
        self.workerGetHFR()
        self.workerCalcTiltValuesSquare()
        self.workerCalcTiltValuesTriangle()
        self.workerGetRoundness()
        self.calcAberrationInspectView()
        self.calcBackground()
        self.calcBackgroundRMS()
        return True

    def workerCalcPhotometry(self):
        """
        :return:
        """
        self.bkg = sep.Background(self.image, bw=64, bh=64)
        image_sub = self.image - self.bkg

        try:
            objs = sep.extract(image_sub, 2.5, err=self.bkg.rms(),
                               filter_type='matched', minarea=11)
        except Exception as e:
            self.log.error(e)
            self.objs = None
            self.objsAll = None
            self.HFR = None
            return False

        self.objsAll = objs

        # limiting the resulting object by some constraints
        r = np.sqrt(objs['a'] * objs['a'] + objs['b'] * objs['b'])
        mask = (r < 10) & (r > 0.8)
        objs = objs[mask]

        # equivalent to FLUX_AUTO of sextractor
        PHOT_AUTOPARAMS = [2.5, 1.5]

        kronRad, krFlag = sep.kron_radius(
            image_sub, objs['x'], objs['y'], objs['a'], objs['b'], objs['theta'], 6.0)

        flux, fluxErr, flag = sep.sum_ellipse(
            image_sub, objs['x'], objs['y'], objs['a'], objs['b'], objs['theta'],
            PHOT_AUTOPARAMS[0] * kronRad, subpix=1)

        flag |= krFlag
        r_min = PHOT_AUTOPARAMS[1] / 2

        useCircle = kronRad * np.sqrt(objs['a'] * objs['b']) < r_min
        cFlux, cFluxErr, cFlag = sep.sum_circle(
            image_sub, objs['x'][useCircle], objs['y'][useCircle], r_min, subpix=1)

        flux[useCircle] = cFlux
        fluxErr[useCircle] = cFluxErr
        flag[useCircle] = cFlag

        # equivalent of FLUX_RADIUS
        PHOT_FLUXFRAC = 0.5

        radius, _ = sep.flux_radius(
            image_sub, objs['x'], objs['y'], 6.0 * objs['a'], PHOT_FLUXFRAC,
            normflux=flux, subpix=5)

        # limiting the resulting object by some more constraints
        # s/n = mean / standard deviation
        # https://www1.phys.vt.edu/~jhs/phys3154/snr20040108.pdf
        sn = flux / np.sqrt(flux + 99 * 99 * 3.1415926 * self.bkg.globalrms / 1.46)
        mask = (sn > 10) & (radius < 10)

        # to get HFR
        self.objs = objs[mask]
        self.HFR = radius[mask]
        self.runCalcs()
        return True

    def processPhotometry(self):
        """
        :return:
        """
        worker = Worker(self.workerCalcPhotometry)
        worker.signals.finished.connect(lambda:  self.signals.sepFinished.emit())
        self.threadPool.start(worker)
        return True

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
        self.image = np.flipud(self.image)
        self.image = (self.image / np.max(self.image) * 65536.0).astype('float32')
        return True

    def workerLoadImage(self, imagePath):
        """
        :param imagePath:
        :return:
        """
        with fits.open(imagePath) as fitsHandle:
            self.image = fitsHandle[0].data
            self.header = fitsHandle[0].header

        if self.image is None or len(self.image) == 0:
            self.log.debug('No image data in FITS')
            return False
        if self.header is None:
            self.log.debug('No header data in FITS')
            return False

        self.cleanImageFormat()
        bayerPattern = self.header.get('BAYERPAT', '')
        if bayerPattern:
            self.debayerImage(bayerPattern)
            self.log.debug(f'Image has bayer pattern: {bayerPattern}')

        self.signals.image.emit()
        return True

    def processImage(self, imagePath=''):
        """
        :param: imagePath:
        :return:
        """
        if not os.path.isfile(imagePath):
            return False

        worker = Worker(self.workerLoadImage, imagePath)
        self.threadPool.start(worker)
        return True
