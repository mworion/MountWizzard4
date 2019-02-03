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
# Python  v3.6.7
#
# Michael Würtenberger
# (c) 2018
#
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
from datetime import datetime as dt
# external packages
import PyQt5
import numpy as np
# local import
from mw4.gui import widget
from mw4.gui.widgets import image_ui


class ImageWindow(widget.MWidget):
    """
    the image window class handles

    """

    __all__ = ['ImageWindow',
               ]
    version = '0.1'
    logger = logging.getLogger(__name__)

    BACK = 'background-color: transparent;'
    CYCLE_UPDATE_TASK = 1000
    NUMBER_POINTS = 500
    NUMBER_XTICKS = 8

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.showStatus = False
        self.ui = image_ui.Ui_ImageDialog()
        self.ui.setupUi(self)
        self.initUI()

        self.imageMat = self.embedMatplot(self.ui.image)
        self.imageMat.parentWidget().setStyleSheet(self.BACK)
        self.clearRect(self.imageMat, True)

        self.initConfig()

    def initConfig(self):
        if 'imageW' not in self.app.config:
            return False
        config = self.app.config['imageW']
        x = config.get('winPosX', 100)
        y = config.get('winPosY', 100)
        if x > self.screenSizeX:
            x = 0
        if y > self.screenSizeY:
            y = 0
        self.move(x, y)
        height = config.get('height', 600)
        width = config.get('width', 800)
        self.resize(width, height)
        if config.get('showStatus'):
            self.showWindow()
        return True

    def storeConfig(self):
        if 'imageW' not in self.app.config:
            self.app.config['imageW'] = {}
        config = self.app.config['imageW']
        config['winPosX'] = self.pos().x()
        config['winPosY'] = self.pos().y()
        config['height'] = self.height()
        config['width'] = self.width()
        config['showStatus'] = self.showStatus
        return True

    def resizeEvent(self, QResizeEvent):
        """
        resizeEvent changes the internal widget according to the resize of the window
        the formulae of the calculation is:
            spaces left right top button : 5 pixel
            widget start in height at y = 130

        :param QResizeEvent:
        :return: nothing
        """

        super().resizeEvent(QResizeEvent)
        space = 5
        startY = 130
        self.ui.image.setGeometry(space,
                                  startY - space,
                                  self.width() - 2 * space,
                                  self.height() - startY)

    def closeEvent(self, closeEvent):
        super().closeEvent(closeEvent)
        self.changeStyleDynamic(self.app.mainW.ui.openImageW, 'running', 'false')

    def toggleWindow(self):
        self.showStatus = not self.showStatus
        if self.showStatus:
            self.showWindow()
        else:
            self.close()

    def showWindow(self):
        self.showStatus = True
        self.show()
        self.changeStyleDynamic(self.app.mainW.ui.openImageW, 'running', 'true')
        return True
