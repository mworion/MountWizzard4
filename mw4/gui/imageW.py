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
import os
# external packages
import PyQt5
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
        self.imageFileName = ''

        self.ui = image_ui.Ui_ImageDialog()
        self.ui.setupUi(self)
        self.initUI()

        self.setupDropDownGui()

        self.imageMat = self.embedMatplot(self.ui.image)
        self.imageMat.parentWidget().setStyleSheet(self.BACK)
        self.clearRect(self.imageMat, True)

        self.ui.load.clicked.connect(self.loadImage)

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
        self.ui.color.setCurrentIndex(config.get('color', 0))
        self.ui.zoom.setCurrentIndex(config.get('zoom', 0))
        self.ui.stretch.setCurrentIndex(config.get('stretch', 0))
        self.imageFileName = config.get('imageFileName', '')
        full, short, ext = self.extractNames([self.imageFileName])
        self.ui.imageFileName.setText(short)
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
        config['color'] = self.ui.color.currentIndex()
        config['zoom'] = self.ui.zoom.currentIndex()
        config['stretch'] = self.ui.stretch.currentIndex()
        config['imageFileName'] = self.imageFileName
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

    def setupDropDownGui(self):
        """
        setupDropDownGui handles the population of list for image handling.

        :return: success for test
        """

        self.ui.color.clear()
        self.ui.color.setView(PyQt5.QtWidgets.QListView())
        self.ui.color.addItem('Grey')
        self.ui.color.addItem('Cool')
        self.ui.color.addItem('Rainbow')
        self.ui.color.addItem('Spectral')

        self.ui.zoom.clear()
        self.ui.zoom.setView(PyQt5.QtWidgets.QListView())
        self.ui.zoom.addItem('Zoom 1x')
        self.ui.zoom.addItem('Zoom 2x')
        self.ui.zoom.addItem('Zoom 4x')
        self.ui.zoom.addItem('Zoom 8x')

        self.ui.stretch.clear()
        self.ui.stretch.setView(PyQt5.QtWidgets.QListView())
        self.ui.stretch.addItem('Low')
        self.ui.stretch.addItem('Mid')
        self.ui.stretch.addItem('High')
        self.ui.stretch.addItem('Super')

        return True

    def loadImage(self):
        folder = self.app.mwGlob['imageDir']
        loadFilePath, name, ext = self.openFile(self,
                                                'Open image file',
                                                folder,
                                                'FITS files (*.fit*)',
                                                enableDir=True,
                                                )
        if not name:
            return False
        # suc = self.app.loadConfig(name=name)
        suc = True
        if suc:
            self.ui.imageFileName.setText(name)
            self.imageFileName = loadFilePath
            self.app.message.emit('Image [{0}] loaded'.format(name), 0)
        else:
            self.app.message.emit('Image [{0}] cannot no be loaded'.format(name), 2)
        return True
