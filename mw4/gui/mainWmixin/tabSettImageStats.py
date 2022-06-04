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

# external packages
from PyQt5.QtWidgets import QInputDialog
import numpy as np

# local import


class SettImageStats:
    """
    """

    def __init__(self):
        self.ui.aperture.valueChanged.connect(self.updateImageStats)
        self.ui.focalLength.valueChanged.connect(self.updateImageStats)
        self.app.update1s.connect(self.updateImageStats)

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
        else:
            resolutionX = None
            resolutionY = None

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
        else:
            FOVX = None
            FOVY = None

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

        return True
