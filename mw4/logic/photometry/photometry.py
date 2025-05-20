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
# GUI with PySide for python
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import logging

# external packages
import numpy as np
import sep
from PySide6.QtCore import Signal, QObject, QMutex
from scipy.interpolate import griddata
from scipy.ndimage import uniform_filter

# local import
from base.tpool import Worker


class PhotometrySignals(QObject):
    """ """

    hfr = Signal()
    hfrSquare = Signal()
    hfrTriangle = Signal()
    aberration = Signal()
    roundness = Signal()
    background = Signal()
    backgroundRMS = Signal()
    sepFinished = Signal()


class Photometry:
    """ """

    log = logging.getLogger("MW4")

    ABERRATION_SIZE = 250
    FILTER_SCALE = 10
    SN = [30, 20, 15, 10, 10]
    SEP = [3.0, 3.0, 2.5, 2.5, 2.0]

    def __init__(self, app, image=None, snSelector=0):
        self.threadPool = app.threadPool
        self.signals = PhotometrySignals()

        self.image = image
        self.aberrationImage = None
        self.snTarget = self.SN[snSelector]
        self.sepThreshold = self.SEP[snSelector]
        self.lock = QMutex()
        self.worker: Worker = None

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
        self.backSignal = None
        self.backRMS = None

        self.hfr = None
        self.hfrAll = None
        self.hfrMin = None
        self.hfrMax = None
        self.hfrPercentile = None
        self.hfrMedian = None
        self.hfrGrid = None
        self.hfrInner = None
        self.hfrOuter = None
        self.hfrSegTriangle = None
        self.hfrSegSquare = None

    def baseCalcs(self) -> None:
        """ """
        self.h, self.w = self.image.shape
        self.filterConstW = int(self.w / (self.FILTER_SCALE * 3))
        self.filterConstH = int(self.h / (self.FILTER_SCALE * 3))
        rangeX = np.linspace(0, self.w, int(self.w / self.FILTER_SCALE))
        rangeY = np.linspace(0, self.h, int(self.h / self.FILTER_SCALE))
        self.xm, self.ym = np.meshgrid(rangeX, rangeY)
        x = self.objs["x"] - self.w / 2
        y = self.objs["y"] - self.h / 2
        radius = np.sqrt(x * x + y * y)
        maskOuter = np.sqrt(self.h * self.h / 4 + self.w * self.w / 4) * 0.75 < radius
        maskInner = np.sqrt(self.h * self.h / 4 + self.w * self.w / 4) * 0.25 > radius
        self.hfrOuter = np.median(self.hfr[maskOuter])
        self.hfrInner = np.median(self.hfr[maskInner])
        self.hfrPercentile = np.percentile(self.hfr, 90)
        self.hfrMedian = np.median(self.hfr)

    def workerGetHFR(self) -> None:
        """ """
        img = griddata(
            (self.objs["x"], self.objs["y"]),
            self.hfr,
            (self.xm, self.ym),
            method="nearest",
            fill_value=np.min(self.hfr),
        )
        self.hfrGrid = uniform_filter(img, size=[self.filterConstH, self.filterConstW])
        minB, maxB = np.percentile(self.hfrGrid, (50, 95))
        self.hfrMin = minB
        self.hfrMax = maxB
        self.signals.hfr.emit()

    def workerGetRoundness(self) -> None:
        """ """
        a = self.objs["a"]
        b = self.objs["b"]
        aspectRatio = np.maximum(a / b, b / a)
        minB, maxB = np.percentile(aspectRatio, (50, 95))
        img = griddata(
            (self.objs["x"], self.objs["y"]),
            aspectRatio,
            (self.xm, self.ym),
            method="linear",
            fill_value=np.min(aspectRatio),
        )
        self.roundnessGrid = uniform_filter(img, size=[self.filterConstH, self.filterConstW])
        self.roundnessPercentile = np.percentile(aspectRatio, 90)
        self.roundnessMin = minB
        self.roundnessMax = maxB
        self.signals.roundness.emit()

    def workerCalcTiltValuesSquare(self) -> None:
        """ """
        stepY = int(self.h / 3)
        stepX = int(self.w / 3)

        xRange = [0, stepX, 2 * stepX, 3 * stepX]
        yRange = [0, stepY, 2 * stepY, 3 * stepY]
        x = self.objs["x"]
        y = self.objs["y"]
        segHFR = np.zeros((3, 3))
        for ix in range(3):
            for iy in range(3):
                xMin = xRange[ix]
                xMax = xRange[ix + 1]
                yMin = yRange[iy]
                yMax = yRange[iy + 1]
                hfr = self.hfr[(x > xMin) & (x < xMax) & (y > yMin) & (y < yMax)]
                med_hfr = np.median(hfr)
                segHFR[ix][iy] = med_hfr
        self.hfrSegSquare = segHFR
        self.signals.hfrSquare.emit()

    def workerCalcTiltValuesTriangle(self) -> None:
        """ """
        x = self.objs["x"] - self.w / 2
        y = self.objs["y"] - self.h / 2
        radius = min(self.h / 2, self.w / 2)
        mask1 = np.sqrt(self.h * self.h + self.w * self.w) * 0.25 < radius
        mask2 = np.sqrt(self.h * self.h + self.w * self.w) > radius
        segHFR = np.zeros(36)
        angles = np.mod(np.arctan2(y, x), 2 * np.pi)
        rangeA = np.radians(range(0, 361, 10))
        for i in range(36):
            mask3 = rangeA[i] < angles
            mask4 = rangeA[i + 1] > angles
            hfrVal = self.hfr[mask1 & mask2 & mask3 & mask4]
            if len(hfrVal) > 0:
                segHFR[i] = np.median(hfrVal)
        self.hfrSegTriangle = np.concatenate([segHFR, segHFR])
        self.signals.hfrTriangle.emit()

    def calcAberrationInspectView(self) -> None:
        """ """
        size = self.ABERRATION_SIZE
        if self.w < 3 * size or self.h < 3 * size:
            self.aberrationImage = self.image
            return

        dw = int((self.w - 3 * size) / 2)
        dh = int((self.h - 3 * size) / 2)

        img = np.delete(self.image, np.s_[size : size + dh], axis=0)
        img = np.delete(img, np.s_[size * 2 : size * 2 + dh], axis=0)
        img = np.delete(img, np.s_[size : size + dw], axis=1)
        img = np.delete(img, np.s_[size * 2 : size * 2 + dw], axis=1)
        self.aberrationImage = img
        self.signals.aberration.emit()

    def calcBackground(self) -> None:
        """ """
        maxB = np.max(self.backSignal) / self.bkg.globalback
        minB = np.min(self.backSignal) / self.bkg.globalback
        img = self.backSignal / self.bkg.globalback
        self.background = uniform_filter(img, size=[self.filterConstH, self.filterConstW])
        self.backgroundMin = minB
        self.backgroundMax = maxB
        self.signals.background.emit()

    def calcBackgroundRMS(self) -> None:
        """ """
        self.backgroundRMS = uniform_filter(
            self.backRMS, size=[self.filterConstH, self.filterConstW]
        )
        self.signals.backgroundRMS.emit()

    def runCalcs(self) -> None:
        """ """
        if len(self.hfr) < 10:
            return
        self.baseCalcs()
        self.workerGetHFR()
        self.workerCalcTiltValuesSquare()
        self.workerCalcTiltValuesTriangle()
        self.workerGetRoundness()
        self.calcAberrationInspectView()
        self.calcBackground()
        self.calcBackgroundRMS()

    def workerCalcPhotometry(self) -> None:
        """ """
        self.bkg = sep.Background(self.image, bw=32, bh=32)
        image_sub = self.image - self.bkg
        self.backRMS = self.bkg.rms()
        self.backSignal = self.bkg.back()

        try:
            objs = sep.extract(
                image_sub,
                self.sepThreshold,
                err=self.backRMS,
                filter_kernel=None,
                minarea=7,
            )
        except Exception as e:
            self.log.error(e)
            self.objs = None
            self.objsAll = None
            self.hfr = None
            self.hfrAll = None
            return

        objsRaw = len(objs)

        # limiting the resulting object by some constraints
        r = np.sqrt(objs["a"] * objs["a"] + objs["b"] * objs["b"])
        mask = (r < 15) & (r > 0.8)
        objs = objs[mask]
        objsSelect = len(objs)

        # equivalent to FLUX_AUTO of sextractor
        PHOT_AUTOPARAMS = [2.5, 3.5]

        kronRad, krFlag = sep.kron_radius(
            image_sub, objs["x"], objs["y"], objs["a"], objs["b"], objs["theta"], 6.0
        )

        flux, fluxErr, flag = sep.sum_ellipse(
            image_sub,
            objs["x"],
            objs["y"],
            objs["a"],
            objs["b"],
            objs["theta"],
            PHOT_AUTOPARAMS[0] * kronRad,
            subpix=1,
        )

        flag |= krFlag
        r_min = PHOT_AUTOPARAMS[1] / 2

        useCircle = kronRad * np.sqrt(objs["a"] * objs["b"]) < r_min
        cFlux, cFluxErr, cFlag = sep.sum_circle(
            image_sub, objs["x"][useCircle], objs["y"][useCircle], r_min, subpix=1
        )

        flux[useCircle] = cFlux
        fluxErr[useCircle] = cFluxErr
        flag[useCircle] = cFlag

        # equivalent of FLUX_RADIUS
        PHOT_FLUXFRAC = [0.5, 1.0]

        radius, _ = sep.flux_radius(
            image_sub,
            objs["x"],
            objs["y"],
            6.0 * objs["a"],
            PHOT_FLUXFRAC,
            normflux=flux,
            subpix=5,
        )

        self.objsAll = objs
        self.hfrAll = radius[:, 0]

        # limiting the resulting object by checking the S/N values
        b = []
        for x, y in zip(objs["x"], objs["y"]):
            b.append(self.backSignal[int(y)][int(x)])

        # calculate sn based on optimized version of
        # http://www1.phys.vt.edu/~jhs/phys3154/snr20040108.pdf
        sn = flux / np.sqrt(np.abs(b * radius[:, 1] * radius[:, 1] * np.pi))

        # pure version of source compared to use in stellarsolver
        # starNumPixels = np.abs(b * radius[:, 1] * radius[:, 1] * np.pi)
        # varSky = self.bkg.globalrms * self.bkg.globalrms
        # sn = flux / np.sqrt(flux + starNumPixels * varSky * (1 + 1 / (32 * 32)))

        mask = sn > self.snTarget
        objs = objs[mask]
        radius = radius[:, 0]
        radius = radius[mask]
        objsSN = len(objs)

        # and we need a min and max of HFR
        mask = radius < 10
        self.objs = objs[mask]
        self.hfr = radius[mask]
        self.runCalcs()
        objsHFR = len(self.objs)
        self.log.info(f"Raw:{objsRaw}, Select:{objsSelect}, SN:{objsSN}, HFR:{objsHFR}")

    def unlockPhotometry(self) -> None:
        """ """
        self.lock.unlock()

    def processPhotometry(self, image: object, snTarget: float) -> None:
        """ """
        self.image = image
        self.snTarget = self.SN[snTarget]
        self.sepThreshold = self.SEP[snTarget]

        if not self.lock.tryLock():
            return

        self.worker = Worker(self.workerCalcPhotometry)
        self.worker.signals.result.connect(lambda: self.signals.sepFinished.emit())
        self.worker.signals.finished.connect(self.unlockPhotometry)
        self.threadPool.start(self.worker)
