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
import os
import logging
from pathlib import Path

# external packages
from PySide6.QtCore import Signal, QObject
import numpy as np
import cv2
from astropy.io import fits
from xisf import XISF
from astropy import wcs

# local import
from base.tpool import Worker
from mountcontrol.convert import valueToFloat


class FileHandlerSignals(QObject):
    """ """

    imageLoaded = Signal()


class FileHandler:
    """ """

    log = logging.getLogger("MW4")

    def __init__(self, app, imagePath="", flipH=False, flipV=False):
        self.threadPool = app.threadPool
        self.signals = FileHandlerSignals()
        self.worker: Worker = None

        self.imagePath = imagePath
        self.flipH = flipH
        self.flipV = flipV
        self.image = None
        self.header = None
        self.wcs = None
        self.hasCelestial = False
        self.sizeX = 0
        self.sizeY = 0

    def debayerImage(self, pattern: str) -> bool:
        """ """
        if pattern == "GBRG":
            R = self.image[1::2, 0::2]
            B = self.image[0::2, 1::2]
            G0 = self.image[0::2, 0::2]
            G1 = self.image[1::2, 1::2]

        elif pattern == "RGGB":
            R = self.image[0::2, 0::2]
            B = self.image[1::2, 1::2]
            G0 = self.image[0::2, 1::2]
            G1 = self.image[1::2, 0::2]

        elif pattern == "GRBG":
            R = self.image[0::2, 1::2]
            B = self.image[1::2, 0::2]
            G0 = self.image[0::2, 0::2]
            G1 = self.image[1::2, 1::2]

        elif pattern == "BGGR":
            R = self.image[1::2, 1::2]
            B = self.image[0::2, 0::2]
            G0 = self.image[0::2, 1::2]
            G1 = self.image[1::2, 0::2]

        else:
            self.log.info("Unknown debayer pattern, keep it")
            return False

        h, w = self.image.shape
        self.image = 0.2989 * R + 0.5870 * (G0 + G1) / 2 + 0.1140 * B
        self.image = cv2.resize(self.image, (w, h))
        return True

    def cleanImageFormat(self) -> None:
        """ """
        if not self.flipV:
            self.image = np.flipud(self.image)
        if self.flipH:
            self.image = np.fliplr(self.image)
        self.image = (self.image / np.max(self.image) * 65536.0).astype("float32")

    def checkValidImageFormat(self) -> bool:
        """ """
        if self.image is None or len(self.image) == 0:
            self.log.debug("No image data in FITS")
            self.image = None
            self.header = None
            return False
        if self.header is None:
            self.log.debug("No header data in FITS")
            self.image = None
            return False
        if self.header.get("NAXIS") != 2:
            self.log.debug("Incompatible format in FITS")
            self.image = None
            self.header = None
            return False
        return True

    def loadFITS(self) -> None:
        """ """
        with fits.open(self.imagePath) as fitsHandle:
            self.image = fitsHandle[0].data
            self.header = fitsHandle[0].header

    @staticmethod
    def convHeaderXISF2FITS(header: dict) -> fits.Header:
        """ """
        hdu = fits.PrimaryHDU()
        fitsHeaderNew = hdu.header
        fitsHeaderNew["NAXIS"] = 2
        fitsHeaderNew["NAXIS1"] = header["geometry"][0]
        fitsHeaderNew["NAXIS2"] = header["geometry"][1]

        fitHeaderXisf = header["FITSKeywords"]
        for key in fitHeaderXisf:
            if key in ["SIMPLE", "EXTEND", "NAXIS", "NAXIS1", "NAXIS2"]:
                continue
            value = fitHeaderXisf[key][0].get("value", "")
            valueFloat = valueToFloat(value)
            value = value if valueFloat is None else valueFloat
            comment = fitHeaderXisf[key][0].get("comment", "")
            fitsHeaderNew.append((key, value, comment))
        return fitsHeaderNew

    def loadXISF(self) -> None:
        """ """
        header = {}
        self.image = XISF.read(self.imagePath, image_metadata=header)[:, :, -1]
        self.header = self.convHeaderXISF2FITS(header)

    def workerLoadImage(self, imagePath: Path) -> None:
        """ """
        self.imagePath = imagePath
        _, ext = os.path.splitext(self.imagePath)

        if ext in [".fits", ".fit"]:
            self.loadFITS()
        elif ext in [".xisf"]:
            self.loadXISF()

        isValid = self.checkValidImageFormat()
        if not isValid:
            self.signals.imageLoaded.emit()
            return

        self.cleanImageFormat()
        bayerPattern = self.header.get("BAYERPAT", "").strip()
        if bayerPattern:
            self.debayerImage(bayerPattern)
            self.log.debug(f"Image has bayer pattern: {bayerPattern}")

        self.wcs = wcs.WCS(self.header)
        self.hasCelestial = self.wcs.has_celestial
        self.sizeY, self.sizeX = self.wcs.array_shape
        self.signals.imageLoaded.emit()

    def loadImage(
        self, imagePath: Path = Path(""), flipH: bool = False, flipV: bool = False
    ) -> None:
        """ """
        if not imagePath.is_file():
            return

        self.image = None
        self.imagePath = imagePath
        self.flipH = flipH
        self.flipV = flipV

        self.worker = Worker(self.workerLoadImage, imagePath)
        self.threadPool.start(self.worker)
