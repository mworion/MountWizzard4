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
from astropy.io import fits
from astropy import wcs
from astropy.nddata import Cutout2D
from astropy.visualization import AsymmetricPercentileInterval
from astropy.visualization import SqrtStretch
from astropy.visualization import ImageNormalize
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
    version = '0.2'
    logger = logging.getLogger(__name__)

    BACK = 'background-color: transparent;'
    BLUE = '#2090C0'

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.showStatus = False
        self.imageFileName = ''
        self.image = None

        self.ui = image_ui.Ui_ImageDialog()
        self.ui.setupUi(self)
        self.initUI()

        self.setupDropDownGui()

        self.imageMat = self.embedMatplot(self.ui.image)
        self.imageMat.parentWidget().setStyleSheet(self.BACK)

        self.ui.load.clicked.connect(self.selectImage)
        self.ui.color.currentIndexChanged.connect(self.showFitsImage)
        self.ui.stretch.currentIndexChanged.connect(self.showFitsImage)
        self.ui.zoom.currentIndexChanged.connect(self.showFitsImage)
        self.ui.checkUseWCS.clicked.connect(self.showFitsImage)
        self.ui.solve.clicked.connect(self.solveImage)
        self.app.plateSolve.signals.solveDone.connect(self.solveDone)

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
        self.showFitsImage()
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
        self.showFitsImage()
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

    def selectImage(self):
        """
        selectImage does a dialog to choose a FITS file for viewing. The file will not
        be loaded, just the full filepath will be stored.

        :return: success
        """

        folder = self.app.mwGlob['imageDir']
        loadFilePath, name, ext = self.openFile(self,
                                                'Select image file',
                                                folder,
                                                'FITS files (*.fit*)',
                                                enableDir=True,
                                                )
        if not name:
            return False
        self.ui.imageFileName.setText(name)
        self.imageFileName = loadFilePath
        self.showFitsImage()
        self.app.message.emit('Image [{0}] selected'.format(name), 0)
        return True

    def solveImage(self):
        self.app.plateSolve.solveFits(fitsPath=self.imageFileName)
        self.changeStyleDynamic(self.ui.solve, 'running', 'true')
        self.ui.expose.setEnabled(False)
        self.ui.exposeN.setEnabled(False)
        self.ui.load.setEnabled(False)

    def solveDone(self):
        self.changeStyleDynamic(self.ui.solve, 'running', 'false')
        self.ui.expose.setEnabled(True)
        self.ui.exposeN.setEnabled(True)
        self.ui.load.setEnabled(True)
        self.showFitsImage()

    def writeHeaderToGui(self, header=None):
        """

        :param header: header of fits file
        :return: hasCelestial, hasDistortion
        """

        name = header.get('OBJECT', '').upper()
        ra = header.get('RA', 0) * 24 / 360
        dec = header.get('DEC', 0)
        scale = header.get('SCALE', 0)
        ccdTemp = header.get('CCD-TEMP', 0)
        expTime = header.get('EXPOSURE', 0)
        filterCCD = header.get('FILTER', 0)
        binX = header.get('XBINNING', 0)
        binY = header.get('YBINNING', 0)
        sqm = max(header.get('SQM', 0),
                  header.get('SKY-QLTY', 0),
                  )
        rotation = header.get('ANGLE', 0)
        self.ui.object.setText(f'{name}')
        self.ui.ra.setText(f'{ra:8.4f}')
        self.ui.dec.setText(f'{dec:8.4f}')
        self.ui.rotation.setText(f'{rotation:5.2f}')
        self.ui.scale.setText(f'{scale:5.3f}')
        self.ui.ccdTemp.setText(f'{ccdTemp:4.1f}')
        self.ui.expTime.setText(f'{expTime:5.1f}')
        self.ui.filter.setText(f'{filterCCD}')
        self.ui.binX.setText(f'{binX:1.0f}')
        self.ui.binY.setText(f'{binY:1.0f}')
        self.ui.sqm.setText(f'{sqm:5.2f}')

        wcsObject = wcs.WCS(header)
        hasCelestial = wcsObject.has_celestial
        status = ('true' if hasCelestial else 'false')
        self.changeStyleDynamic(self.ui.hasCelestial, 'running', status)

        hasDistortion = wcsObject.has_distortion
        self.ui.checkUseWCS.setEnabled(hasDistortion)
        status = ('true' if hasDistortion else 'false')
        self.changeStyleDynamic(self.ui.hasDistortion, 'running', status)

        for key, value in header.items():
            pass
            # print(key, value)
        # print(wcsObject)

        return hasDistortion, wcsObject

    def zoomImage(self, image=None):
        """

        :param image:
        :return:
        """

        zoomIndex = self.ui.zoom.currentIndex()
        if zoomIndex == 0:
            return image

        sizeX, sizeY = image.shape
        factor = np.exp2(zoomIndex)
        position = (int(sizeX / 2), int(sizeY / 2))
        size = (int(sizeX / factor), int(sizeY / factor))
        cutout = Cutout2D(image, position=position, size=size, copy=True)

        return cutout.data

    def stretchImage(self, image=None):
        """
        stretchImage take the actual image and calculated norm based on the min, max
        derived from interval

        :param image: image
        :return: norm for plot
        """

        stretchIndex = self.ui.stretch.currentIndex()

        if stretchIndex == 0:
            interval = AsymmetricPercentileInterval(98, 99.998)
        elif stretchIndex == 1:
            interval = AsymmetricPercentileInterval(25, 99.95)
        elif stretchIndex == 2:
            interval = AsymmetricPercentileInterval(12, 99.9)
        else:
            interval = AsymmetricPercentileInterval(1, 99.8)

        vmin, vmax = interval.get_limits(image)

        norm = ImageNormalize(image,
                              vmin=vmin,
                              vmax=vmax,
                              stretch=SqrtStretch(),
                              )
        return norm

    def colorImage(self):
        """
        colorImage take the index from gui and generates the colormap for image show
        command from matplotlib

        :return: color map
        """

        colorMaps = ['gray', 'plasma', 'rainbow', 'nipy_spectral']
        colorMapIndex = self.ui.color.currentIndex()
        colorMap = colorMaps[colorMapIndex]
        return colorMap

    def setupDistorted(self, wcsObject=None):
        """

        :param wcsObject:
        :return:
        """

        self.imageMat.figure.clf()
        self.imageMat.figure.add_subplot(111,
                                         projection=wcsObject,
                                         )
        axes = self.imageMat.figure.axes[0]
        axe0 = axes.coords[0]
        axe1 = axes.coords[1]
        # axe0.set_major_formatter('dd:mm:ss.s')
        # axe1.set_major_formatter('dd:mm')
        axe0.grid(True,
                  color=self.BLUE,
                  ls='solid',
                  alpha=0.8,
                  )
        axe1.grid(True,
                  color=self.BLUE,
                  ls='solid',
                  alpha=0.8,
                  )
        axe0.tick_params(colors=self.BLUE,
                         labelsize=12,
                         )
        axe1.tick_params(colors=self.BLUE,
                         labelsize=12,
                         )
        axe0.set_axislabel('Coordinates',
                           color=self.BLUE,
                           fontsize=12,
                           fontweight='bold',
                           )
        axe1.set_axislabel('Coordinates',
                           color=self.BLUE,
                           fontsize=12,
                           fontweight='bold',
                           )
        return axes

    def setupNormal(self):
        """

        :return:
        """

        self.imageMat.figure.clf()
        self.imageMat.figure.add_subplot(111,
                                         )
        axes = self.imageMat.figure.axes[0]
        axes.grid(True,
                  color=self.BLUE,
                  ls='solid',
                  alpha=0.8,
                  )
        axes.tick_params(axis='x',
                         which='major',
                         colors=self.BLUE,
                         labelsize=12,
                         )
        axes.tick_params(axis='y',
                         which='major',
                         colors=self.BLUE,
                         labelsize=12,
                         )
        axes.set_xlabel(xlabel='Pixel',
                        color=self.BLUE,
                        fontsize=12,
                        fontweight='bold',
                        )
        axes.set_ylabel(ylabel='Pixel',
                        color=self.BLUE,
                        fontsize=12,
                        fontweight='bold',
                        )
        return axes

    def clearImage(self, hasDistortion=False, wcsObject=None):
        """
        clearImage clears the view port and setups all necessary topic to show the image.
        this includes the axis, label etc.

        :param wcsObject:
        :param hasDistortion:
        :return: axes object
        """

        if hasDistortion and self.ui.checkUseWCS.isChecked():
            axes = self.setupDistorted(wcsObject=wcsObject)
        else:
            axes = self.setupNormal()
        return axes

    def showFitsImage(self):
        """
        showFitsImage shows the fits image. therefore it calculates color map, stretch,
        zoom and other topics.

        :return: success
        """

        if not self.showStatus:
            return False

        if not os.path.isfile(self.imageFileName):
            return False

        with fits.open(self.imageFileName) as fitsHandle:
            self.image = fitsHandle[0].data
            header = fitsHandle[0].header

        hasDistortion, wcsObject = self.writeHeaderToGui(header=header)
        axes = self.clearImage(hasDistortion=hasDistortion, wcsObject=wcsObject)

        image = self.zoomImage(image=self.image)
        norm = self.stretchImage(image=image)
        colorMap = self.colorImage()

        axes.imshow(image,
                    norm=norm,
                    cmap=colorMap,
                    origin='lower',
                    )

        axes.figure.canvas.draw()
        return True
