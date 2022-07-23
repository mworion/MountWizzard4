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
# Licence APL2.0
#
###########################################################
# standard libraries
import webbrowser

# external packages
import numpy as np
from range_key_dict import RangeKeyDict

# local import


class SettImageStats:
    """
    """
    WATNEY = RangeKeyDict({
        (0, 0.2): 'Passes 14 (watneyqdb-14-20)',
        (0.2, 0.3): 'Passes 12-13 (watneyqdb-12-13)',
        (0.3, 0.5): 'Passes 10-11 (watneyqdb-10-11)',
        (0.5, 0.8): 'Passes 8-9 (watneyqdb-08-09)',
        (0.8, 360): 'Passes 0-7 (watneyqdb-00-07)',
    })
    ASTAP = RangeKeyDict({
        (0, 1): 'H18 (exp. 10s - 20s)',
        (1, 10): 'H18 or H17 (exp. 3s - 10s)',
        (10, 20): 'V17 (exp. 1s - 3s)',
        (20, 360): 'W08 (epx. 1s - 3s)',
    })
    ASTROMETRY = RangeKeyDict({
        (0.033, 0.047): 'index-4200-*.fits',
        (0.047, 0.067): 'index-4201-*.fits',
        (0.067, 0.093): 'index-4202-*.fits',
        (0.093, 0.13): 'index-4203-*.fits',
        (0.13, 0.183): 'index-4204-*.fits',
        (0.183, 0.27): 'index-4205-*.fits',
        (0.27, 0.37): 'index-4206-*.fits',
        (0.37, 0.5): 'index-4207-*.fits',
        (0.5, 0.7): 'index-4208.fits',
        (0.7, 1.0): 'index-4209.fits',
        (1.0, 1.4): 'index-4210.fits',
        (1.4, 2.0): 'index-4211.fits',
        (2.0, 2.8): 'index-4212.fits',
        (2.8, 4): 'index-4213.fits',
        (4.0, 5.7): 'index-4214.fits',
        (5.7, 8.0): 'index-4215.fits',
        (8.0, 11.3): 'index-4216.fits',
        (11.3, 16.7): 'index-4217.fits',
        (16.7, 23.3): 'index-4218.fits',
        (23.3, 360): 'index-4219.fits',
    })

    def __init__(self):
        self.ui.aperture.valueChanged.connect(self.updateImageStats)
        self.ui.focalLength.valueChanged.connect(self.updateImageStats)
        self.ui.openWatneyCatalog.clicked.connect(self.openWatneyCatalog)
        self.ui.openASTAPCatalog.clicked.connect(self.openASTAPCatalog)
        self.ui.openAstrometryCatalog.clicked.connect(self.openAstrometryCatalog)
        self.app.update1s.connect(self.updateImageStats)
        self.fovHint = None
        self.scaleHint = None

    def updateImageStats(self):
        """
        updateImageStats reads the data from the classes and writes them to the gui.
        if a parameter is not set (no key entry) or None, the gui will show a '-'

        :return: true for test purpose
        """
        focalLength = self.ui.focalLength.value()
        aperture = self.ui.aperture.value()
        pixelSizeX = self.app.camera.data.get('CCD_INFO.CCD_PIXEL_SIZE_X', 0)
        pixelSizeY = self.app.camera.data.get('CCD_INFO.CCD_PIXEL_SIZE_Y', 0)
        pixelX = self.app.camera.data.get('CCD_INFO.CCD_MAX_X', 0)
        pixelY = self.app.camera.data.get('CCD_INFO.CCD_MAX_Y', 0)
        rotation = self.app.camera.data.get('CCD_ROTATION.CCD_ROTATION_VALUE', 0)

        if focalLength and pixelSizeX and pixelSizeY:
            resolutionX = pixelSizeX / focalLength * 206.265
            resolutionY = pixelSizeY / focalLength * 206.265
            self.scaleHint = np.sqrt(resolutionX * resolutionX + resolutionY * resolutionY)
        else:
            resolutionX = None
            resolutionY = None
            self.scaleHint = None

        if aperture:
            speed = focalLength / aperture
        else:
            speed = None

        if aperture:
            dawes = 116 / aperture
            rayleigh = 138 / aperture
            magLimit = 7.7 + (5 * np.log10(aperture / 10))
        else:
            dawes = None
            rayleigh = None
            magLimit = None

        if focalLength and pixelSizeY and pixelSizeY and pixelX and pixelY:
            FOVX = pixelSizeX / focalLength * 206.265 * pixelX / 3600
            FOVY = pixelSizeY / focalLength * 206.265 * pixelY / 3600
            self.fovHint = np.sqrt(FOVX * FOVX + FOVY * FOVY)
        else:
            FOVX = None
            FOVY = None
            self.fovHint = None

        if pixelSizeX and speed:
            focusCCD = speed * pixelSizeX
            focusRed = 4.88 * speed * speed * 0.650
            focusGreen = 4.88 * speed * speed * 0.510
            focusBlue = 4.88 * speed * speed * 0.475
        else:
            focusRed = None
            focusGreen = None
            focusBlue = None
            focusCCD = None

        self.guiSetText(self.ui.speed, '2.1f', speed)
        self.guiSetText(self.ui.pixelSizeX, '2.2f', pixelSizeX)
        self.guiSetText(self.ui.pixelSizeY, '2.2f', pixelSizeY)
        self.guiSetText(self.ui.pixelX, '5.0f', pixelX)
        self.guiSetText(self.ui.pixelY, '5.0f', pixelY)
        self.guiSetText(self.ui.rotation, '3.1f', rotation)
        self.guiSetText(self.ui.resolutionX, '2.2f', resolutionX)
        self.guiSetText(self.ui.resolutionY, '2.2f', resolutionY)
        self.guiSetText(self.ui.dawes, '2.2f', dawes)
        self.guiSetText(self.ui.rayleigh, '2.2f', rayleigh)
        self.guiSetText(self.ui.magLimit, '2.2f', magLimit)
        self.guiSetText(self.ui.FOVX, '2.2f', FOVX)
        self.guiSetText(self.ui.FOVY, '2.2f', FOVY)
        self.guiSetText(self.ui.focalLengthStats, '3.0f', focalLength)
        self.guiSetText(self.ui.apertureStats, '3.0f', aperture)
        self.guiSetText(self.ui.focusRed, '3.0f', focusRed)
        self.guiSetText(self.ui.focusGreen, '3.0f', focusGreen)
        self.guiSetText(self.ui.focusBlue, '3.0f', focusBlue)
        self.guiSetText(self.ui.focusCCD, '3.0f', focusCCD)

        hasFovHint = self.fovHint is not None
        if hasFovHint:
            watneyText = self.WATNEY[self.fovHint]
            astapText = self.ASTAP[self.fovHint]
            astrometryText = self.ASTROMETRY[self.fovHint]
        else:
            watneyText = None
            astapText = None
            astrometryText = None

        self.ui.openWatneyCatalog.setEnabled(hasFovHint)
        self.ui.openASTAPCatalog.setEnabled(hasFovHint)
        self.ui.openAstrometryCatalog.setEnabled(hasFovHint)

        self.guiSetText(self.ui.watneyIndex, 's', watneyText)
        self.guiSetText(self.ui.astapIndex, 's', astapText)
        self.guiSetText(self.ui.astrometryIndex, 's', astrometryText)

        return True

    def openWatneyCatalog(self):
        """
        :return:
        """
        url = 'https://github.com/Jusas/WatneyAstrometry/releases/tag/watneyqdb3'
        if not webbrowser.open(url, new=0):
            self.msg.emit(2, 'System', 'ImageStats', 'Browser failed')
        return True

    def openASTAPCatalog(self):
        """
        :return:
        """
        url = 'https://www.hnsky.org/astap.htm'
        if not webbrowser.open(url, new=0):
            self.msg.emit(2, 'System', 'ImageStats', 'Browser failed')
        return True

    def openAstrometryCatalog(self):
        """
        :return:
        """
        url = 'http://data.astrometry.net/4200/'
        if not webbrowser.open(url, new=0):
            self.msg.emit(2, 'System', 'ImageStats', 'Browser failed')
        return True
