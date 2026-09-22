############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10_micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2026 by mworion
# License APL2.0
#
###########################################################
"""Qt adapter around the pure photometry core.

The adapter owns the Qt signals and all presentation state, orchestrates the
pure-core background estimation and source extraction, builds the display grids
and emits the signals the image window connects to. All source data is exposed
as flat, index-aligned arrays (xCoord, yCoord, aAxis, bAxis, theta, hfr).
"""

import logging
import numpy as np
from mw4.base.tpool import Worker, startWorker
from mw4.logic.photometry.photometry_core import (
    Background,
    estimateBackground,
    extractSources,
)
from PySide6.QtCore import QObject, Signal
from scipy.interpolate import griddata
from scipy.ndimage import uniform_filter
from typing import Any, ClassVar


class PhotometrySignals(QObject):
    hfr = Signal()
    hfrSquare = Signal()
    hfrTriangle = Signal()
    aberration = Signal()
    roundness = Signal()
    background = Signal()
    backgroundRMS = Signal()
    photometryFinished = Signal(object)


class Photometry:
    log = logging.getLogger("MW4")
    ABERRATION_SIZE = 250
    FILTER_SCALE = 10
    SN: ClassVar = [30, 20, 15, 10, 10]
    SEP: ClassVar = [3.0, 3.0, 2.5, 2.5, 2.0]

    def __init__(self, parent: Any, image: np.ndarray, snSelector: int = 0) -> None:
        self.threadPool = parent.app.threadPool
        self.signals = PhotometrySignals()

        self.image: np.ndarray = image
        self.aberrationImage: np.ndarray = image
        self.snTarget = self.SN[snSelector]
        self.sepThreshold = self.SEP[snSelector]
        self.workerCalcPhotometry: Worker | None = None

        self.bkg: Background | None = None

        self.xCoord: np.ndarray = np.zeros(0)
        self.yCoord: np.ndarray = np.zeros(0)
        self.aAxis: np.ndarray = np.zeros(0)
        self.bAxis: np.ndarray = np.zeros(0)
        self.theta: np.ndarray = np.zeros(0)
        self.elongation: np.ndarray = np.zeros(0)

        self.xm: np.ndarray = np.array([])
        self.ym: np.ndarray = np.array([])
        self.h: int = 0
        self.w: int = 0
        self.filterConstW: int = 1
        self.filterConstH: int = 1
        self.roundnessGrid: np.ndarray = np.zeros(0)
        self.roundnessMin: float = 0
        self.roundnessMax: float = 1
        self.roundnessPercentile: float = 1
        self.background: np.ndarray = np.zeros(0)
        self.backgroundMin: float = 0
        self.backgroundMax: float = 1
        self.backgroundRMS: np.ndarray = np.zeros(0)
        self.backSignal: np.ndarray = np.zeros(0)
        self.backRMS: np.ndarray = np.zeros(0)

        self.hfr: np.ndarray = np.zeros(30)
        self.hfrMin: float = 1
        self.hfrMax: float = 1
        self.hfrPercentile: float = 1
        self.hfrMedian: float = 1
        self.hfrGrid = np.zeros((30, 30))
        self.hfrInner: float = 1
        self.hfrOuter: float = 1
        self.hfrSegTriangle = np.zeros((3, 3))
        self.hfrSegSquare = np.zeros((3, 3))

    def baseCalcs(self) -> None:
        self.h, self.w = self.image.shape
        self.filterConstW = int(self.w / (self.FILTER_SCALE * 3))
        self.filterConstH = int(self.h / (self.FILTER_SCALE * 3))
        rangeX = np.linspace(0, self.w, int(self.w / self.FILTER_SCALE))
        rangeY = np.linspace(0, self.h, int(self.h / self.FILTER_SCALE))
        self.xm, self.ym = np.meshgrid(rangeX, rangeY)
        x = self.xCoord - self.w / 2
        y = self.yCoord - self.h / 2
        radius = np.sqrt(x * x + y * y)
        maskOuter = np.sqrt(self.h * self.h / 4 + self.w * self.w / 4) * 0.75 < radius
        maskInner = np.sqrt(self.h * self.h / 4 + self.w * self.w / 4) * 0.25 > radius
        outerHFR = self.hfr[maskOuter]
        innerHFR = self.hfr[maskInner]
        self.hfrOuter = float(np.median(outerHFR)) if outerHFR.size > 0 else np.nan
        self.hfrInner = float(np.median(innerHFR)) if innerHFR.size > 0 else np.nan
        self.hfrPercentile = np.percentile(self.hfr, 90)
        self.hfrMedian = np.median(self.hfr)

    def runnerGetHFR(self) -> None:
        img = griddata(
            (self.xCoord, self.yCoord),
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

    def runnerGetRoundness(self) -> None:
        # 8.3: elongation (a/b) taken directly from the SourceCatalog
        aspectRatio = self.elongation
        minB, maxB = np.percentile(aspectRatio, (50, 95))
        img = griddata(
            (self.xCoord, self.yCoord),
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

    def runnerCalcTiltValuesSquare(self) -> None:
        stepY = int(self.h / 3)
        stepX = int(self.w / 3)

        xRange = [0, stepX, 2 * stepX, 3 * stepX]
        yRange = [0, stepY, 2 * stepY, 3 * stepY]
        x = self.xCoord
        y = self.yCoord
        segHFR = np.zeros((3, 3))
        for ix in range(3):
            for iy in range(3):
                xMin = xRange[ix]
                xMax = xRange[ix + 1]
                yMin = yRange[iy]
                yMax = yRange[iy + 1]
                hfr = self.hfr[(x > xMin) & (x < xMax) & (y > yMin) & (y < yMax)]
                if hfr.size > 0:
                    segHFR[ix][iy] = np.median(hfr)
        self.hfrSegSquare = segHFR
        self.signals.hfrSquare.emit()

    def runnerCalcTiltValuesTriangle(self) -> None:
        x = self.xCoord - self.w / 2
        y = self.yCoord - self.h / 2
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
            if hfrVal.size > 0:
                segHFR[i] = np.median(hfrVal)
        self.hfrSegTriangle = np.concatenate([segHFR, segHFR])
        self.signals.hfrTriangle.emit()

    def calcAberrationInspectView(self) -> None:
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
        maxB = float(np.max(self.backSignal)) / self.bkg.globalback
        minB = float(np.min(self.backSignal)) / self.bkg.globalback
        img = self.backSignal / self.bkg.globalback
        self.background = uniform_filter(img, size=[self.filterConstH, self.filterConstW])
        self.backgroundMin = minB
        self.backgroundMax = maxB
        self.signals.background.emit()

    def calcBackgroundRMS(self) -> None:
        self.backgroundRMS = uniform_filter(
            self.backRMS, size=[self.filterConstH, self.filterConstW]
        )
        self.signals.backgroundRMS.emit()

    def runCalcs(self) -> None:
        if len(self.hfr) < 10:
            return
        self.baseCalcs()
        self.runnerGetHFR()
        self.runnerCalcTiltValuesSquare()
        self.runnerCalcTiltValuesTriangle()
        self.runnerGetRoundness()
        self.calcAberrationInspectView()
        self.calcBackground()
        self.calcBackgroundRMS()

    def emptyResult(self) -> None:
        self.xCoord = np.zeros(0)
        self.yCoord = np.zeros(0)
        self.aAxis = np.zeros(0)
        self.bAxis = np.zeros(0)
        self.theta = np.zeros(0)
        self.hfr = np.zeros(0)
        self.elongation = np.zeros(0)

    def runnerCalcPhotometry(self) -> None:
        self.bkg = estimateBackground(self.image)
        imageSub = self.image - self.bkg.back()
        self.backRMS = self.bkg.rms()
        self.backSignal = self.bkg.back()

        threshold = self.sepThreshold * self.backRMS
        try:
            result = extractSources(imageSub, self.backRMS, threshold, self.snTarget)
        except (ValueError, RuntimeError, IndexError) as e:
            self.log.error(e)
            self.emptyResult()
            return

        if result is None:
            self.log.error("No sources detected")
            self.emptyResult()
            return

        sources, counts = result
        self.xCoord = sources.xCoord
        self.yCoord = sources.yCoord
        self.aAxis = sources.aAxis
        self.bAxis = sources.bAxis
        self.theta = sources.theta
        self.hfr = sources.hfr
        self.elongation = sources.elongation
        self.runCalcs()
        self.log.info(
            f"Raw:{counts.raw}, Select:{counts.select}, "
            f"SN:{counts.signalNoise}, HFR:{counts.hfr}"
        )

    def processPhotometry(self, image: np.ndarray, snTarget: int) -> None:
        self.image = image.astype(np.float32)
        self.snTarget = self.SN[snTarget]
        self.sepThreshold = self.SEP[snTarget]
        self.workerCalcPhotometry = startWorker(
            self.workerCalcPhotometry,
            self.threadPool,
            self.runnerCalcPhotometry,
            resultMethod=self.signals.photometryFinished.emit,
        )
