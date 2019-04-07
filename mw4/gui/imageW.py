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
        self.imageMat.parentWidget().setStyleSheet(self.BACK_BG)

        self.ui.load.clicked.connect(self.selectImage)
        self.ui.color.currentIndexChanged.connect(self.showFitsImage)
        self.ui.stretch.currentIndexChanged.connect(self.showFitsImage)
        self.ui.zoom.currentIndexChanged.connect(self.showFitsImage)
        self.ui.checkUseWCS.clicked.connect(self.showFitsImage)
        self.ui.solve.clicked.connect(self.solveImage)
        self.app.astrometry.signals.solveDone.connect(self.solveDone)
        self.app.astrometry.signals.solveResult.connect(self.solveResult)

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
        if config.get('showStatus', False):
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

    def closeEvent(self, closeEvent):
        super().closeEvent(closeEvent)

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
        self.ui.stretch.addItem('SuperX')

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
        self.app.message.emit(f'Image [{name}] selected', 0)
        return True

    def solveImage(self):
        updateFits = self.ui.checkUpdateFits.isChecked()
        self.app.plateSolve.solveThreading(fitsPath=self.imageFileName,
                                           timeout=10,
                                           updateFits=updateFits,
                                           )
        self.changeStyleDynamic(self.ui.solve, 'running', 'true')
        self.ui.expose.setEnabled(False)
        self.ui.exposeN.setEnabled(False)
        self.ui.stop.setEnabled(False)
        self.ui.load.setEnabled(False)
        self.app.message.emit(f'Solving: [{self.imageFileName}]', 0)

    def solveDone(self):
        self.changeStyleDynamic(self.ui.solve, 'running', 'false')
        self.ui.expose.setEnabled(True)
        self.ui.exposeN.setEnabled(True)
        self.ui.stop.setEnabled(True)
        self.ui.load.setEnabled(True)
        self.showFitsImage()

    def solveResult(self, result):
        """

        :param result: result (named tuple)
        :return: success
        """

        if not result[0]:
            self.app.message.emit('Solving error', 2)
            return False
        r = result[1]
        text = f'Ra: {r.ra} Dec: {r.dec} Angle: {r.angle} Scale: {r.scale}'
        self.app.message.emit('Solved: ' + text, 0)
        return True

    def writeHeaderToGui(self, header=None):
        """
        writeHeaderToGui tries to read relevant values from FITS header and possible
        replace values and write them to the imageW gui

        :param header: header of fits file
        :return: hasCelestial, hasDistortion
        """

        name = header.get('OBJECT', '').upper()
        self.ui.object.setText(f'{name}')

        ra = header.get('RA', 0)
        dec = header.get('DEC', 0)
        if ra == 0 and dec == 0:
            ra = header.get('OBJCTRA', 0)
            dec = header.get('OBJCTDEC', 0)
            self.ui.ra.setText(f'{ra}')
            self.ui.dec.setText(f'{dec}')
        else:
            self.ui.ra.setText(f'{ra:8.5f}')
            self.ui.dec.setText(f'{dec:8.5f}')

        scale = header.get('SCALE', 0)
        rotation = header.get('ANGLE', 0)
        self.ui.scale.setText(f'{scale:5.3f}')
        self.ui.rotation.setText(f'{rotation:6.3f}')

        ccdTemp = header.get('CCD-TEMP', 0)
        self.ui.ccdTemp.setText(f'{ccdTemp:4.1f}')

        expTime1 = header.get('EXPOSURE', 0)
        expTime2 = header.get('EXPTIME', 0)
        expTime = max(expTime1, expTime2)
        self.ui.expTime.setText(f'{expTime:5.1f}')

        filterCCD = header.get('FILTER', 0)
        self.ui.filter.setText(f'{filterCCD}')

        binX = header.get('XBINNING', 0)
        binY = header.get('YBINNING', 0)
        self.ui.binX.setText(f'{binX:1.0f}')
        self.ui.binY.setText(f'{binY:1.0f}')

        sqm = max(header.get('SQM', 0),
                  header.get('SKY-QLTY', 0),
                  )
        self.ui.sqm.setText(f'{sqm:5.2f}')

        flipped = header.get('FLIPPED', False)

        if 'CTYPE1' in header:
            wcsObject = wcs.WCS(header)
            hasCelestial = wcsObject.has_celestial
            hasDistortion = wcsObject.has_distortion
        else:
            wcsObject = None
            hasCelestial = False
            hasDistortion = False

        self.changeStyleDynamic(self.ui.hasCelestial, 'running', hasCelestial)
        self.ui.checkUseWCS.setEnabled(hasDistortion)
        self.changeStyleDynamic(self.ui.hasDistortion, 'running', hasDistortion)
        self.changeStyleDynamic(self.ui.isFlipped, 'running', flipped)

        return hasDistortion, wcsObject

    def zoomImage(self, image=None, wcsObject=None):
        """
        zoomImage cutouts a portion of the original image to zoom in the image itself.
        it returns a copy of the image with an updated wcs content. we have to be careful
        about the use of Cutout2D, because they are mixing x and y coordinates. so position
        is in (x, y), but size ind in (y, x)

        :param image:
        :param wcsObject:
        :return:
        """

        zoomIndex = self.ui.zoom.currentIndex()
        if zoomIndex == 0:
            return image

        sizeY, sizeX = image.shape
        factor = np.exp2(zoomIndex)
        position = (int(sizeX / 2), int(sizeY / 2))
        size = (int(sizeY / factor), int(sizeX / factor))
        cutout = Cutout2D(image,
                          position=position,
                          size=size,
                          wcs=wcsObject,
                          copy=True,
                          )

        return cutout.data

    def stretchImage(self, image=None):
        """
        stretchImage take the actual image and calculated norm based on the min, max
        derived from interval which is calculated with AsymmetricPercentileInterval.

        :param image: image
        :return: norm for plot
        """

        stretchValues = [(98, 99.999),
                         (50, 99.99),
                         (20, 99.98),
                         (10, 99.9),
                         (1, 99.8),
                         ]
        stretchIndex = self.ui.stretch.currentIndex()

        interval = AsymmetricPercentileInterval(*stretchValues[stretchIndex])
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
        setupDistorted tries to setup all necessary context for displaying the image with
        wcs distorted coordinates.
        still plenty of work to be done, because very often the labels are not shown

        :param wcsObject:
        :return: axes object to plot onto
        """

        self.imageMat.figure.clf()
        self.imageMat.figure.add_subplot(111,
                                         projection=wcsObject,
                                         )
        axes = self.imageMat.figure.axes[0]
        axe0 = axes.coords[0]
        axe1 = axes.coords[1]
        axes.coords.frame.set_color(self.M_BLUE)

        axe0.grid(True,
                  color=self.M_BLUE,
                  ls='solid',
                  alpha=0.5,
                  )
        axe1.grid(True,
                  color=self.M_BLUE,
                  ls='solid',
                  alpha=0.5,
                  )

        axe0.tick_params(colors=self.M_BLUE,
                         labelsize=12,
                         )
        axe1.tick_params(colors=self.M_BLUE,
                         labelsize=12,
                         )

        axe0.set_axislabel('Coordinates',
                           color=self.M_BLUE,
                           fontsize=12,
                           fontweight='bold',
                           )
        axe1.set_axislabel('Coordinates',
                           color=self.M_BLUE,
                           fontsize=12,
                           fontweight='bold',
                           )
        axe0.set_ticks(number=20)
        axe1.set_ticks(number=20)
        return axes

    def setupNormal(self, image=None):
        """
        setupNormal build the image widget to show it with pixels as axes. the center of
        the image will have coordinates 0,0.

        :param image:
        :return: axes object to plot onto
        """

        self.imageMat.figure.clf()
        self.imageMat.figure.add_subplot(111,
                                         )
        axes = self.imageMat.figure.axes[0]
        axes.grid(True,
                  color=self.M_BLUE,
                  ls='solid',
                  alpha=0.5,
                  )
        axes.spines['bottom'].set_color(self.M_BLUE)
        axes.spines['top'].set_color(self.M_BLUE)
        axes.spines['left'].set_color(self.M_BLUE)
        axes.spines['right'].set_color(self.M_BLUE)

        sizeY, sizeX = image.shape
        midX = int(sizeX / 2)
        midY = int(sizeY / 2)
        number = 10

        valueX, _ = np.linspace(-midX, midX, num=number, retstep=True)
        textX = list((str(int(x)) for x in valueX))
        ticksX = list((x + midX for x in valueX))
        axes.set_xticklabels(textX)
        axes.set_xticks(ticksX)

        valueY, _ = np.linspace(-midY, midY, num=number, retstep=True)
        textY = list((str(int(x)) for x in valueY))
        ticksY = list((x + midY for x in valueY))
        axes.set_yticklabels(textY)
        axes.set_yticks(ticksY)

        axes.tick_params(axis='x',
                         which='major',
                         colors=self.M_BLUE,
                         labelsize=12,
                         )
        axes.tick_params(axis='y',
                         which='major',
                         colors=self.M_BLUE,
                         labelsize=12,
                         )

        axes.set_xlabel(xlabel='Pixel',
                        color=self.M_BLUE,
                        fontsize=12,
                        fontweight='bold',
                        )
        axes.set_ylabel(ylabel='Pixel',
                        color=self.M_BLUE,
                        fontsize=12,
                        fontweight='bold',
                        )
        return axes

    def clearImage(self, hasDistortion=False, wcsObject=None, image=None):
        """
        clearImage clears the view port and setups all necessary topic to show the image.
        this includes the axis, label etc.

        :param hasDistortion:
        :param wcsObject:
        :param image:
        :return: axes object
        """

        if hasDistortion and self.ui.checkUseWCS.isChecked():
            axes = self.setupDistorted(wcsObject=wcsObject)
        else:
            axes = self.setupNormal(image=image)
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

        with fits.open(self.imageFileName, mode='update') as fitsHandle:
            self.image = fitsHandle[0].data
            header = fitsHandle[0].header
            # correct faulty headers
            if header.get('CTYPE1', '').endswith('DEF'):
                header['CTYPE1'] = header['CTYPE1'].replace('DEF', 'TAN')
            if header.get('CTYPE2', '').endswith('DEF'):
                header['CTYPE2'] = header['CTYPE2'].replace('DEF', 'TAN')

        hasDistortion, wcsObject = self.writeHeaderToGui(header=header)
        image = self.zoomImage(image=self.image, wcsObject=wcsObject)
        norm = self.stretchImage(image=image)
        colorMap = self.colorImage()

        axes = self.clearImage(hasDistortion=hasDistortion,
                               wcsObject=wcsObject,
                               image=image)
        axes.imshow(image,
                    norm=norm,
                    cmap=colorMap,
                    origin='lower',
                    )

        axes.figure.canvas.draw()
        return True
