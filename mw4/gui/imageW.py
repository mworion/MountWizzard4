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
import matplotlib.pyplot as plt
import numpy as np
# local import
from mw4.gui import widget
from mw4.gui.widgets import image_ui


class ImageWindow(widget.MWidget):
    """
    the image window class handles fits image loading, stretching, zooming and handles
    the gui interface for display. both wcs and pixel coordinates will be used.

    """

    __all__ = ['ImageWindow',
               ]
    version = '0.9'
    logger = logging.getLogger(__name__)
    signalShowImage = PyQt5.QtCore.pyqtSignal()
    signalSolveImage = PyQt5.QtCore.pyqtSignal()

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.ui = image_ui.Ui_ImageDialog()
        self.ui.setupUi(self)
        self.initUI()
        self.imageFileName = ''
        self.imageData = None
        self.folder = ''

        self.colorMaps = ['gray', 'plasma', 'rainbow', 'nipy_spectral']

        self.imageMat = self.embedMatplot(self.ui.image)
        self.imageMat.parentWidget().setStyleSheet(self.BACK_BG)

        self.initConfig()
        self.showWindow()

    def initConfig(self):
        """
        initConfig read the key out of the configuration dict and stores it to the gui
        elements. if some initialisations have to be proceeded with the loaded persistent
        data, they will be launched as well in this method. if not entry is already in the
        config dict, it will be created first.
        default values will be set in case of missing parameters.
        screen size will be set as well as the window position. if the window position is
        out of the current screen size (because of copy configs or just because the screen
        resolution was changed) the window will be repositioned so that it will be visible.

        :return: True for test purpose
        """

        if 'imageW' not in self.app.config:
            self.app.config['imageW'] = {}
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

        self.setupDropDownGui()
        self.ui.color.setCurrentIndex(config.get('color', 0))
        self.ui.zoom.setCurrentIndex(config.get('zoom', 0))
        self.ui.stretch.setCurrentIndex(config.get('stretch', 0))

        self.imageFileName = config.get('imageFileName', '')
        full, short, ext = self.extractNames([self.imageFileName])
        self.ui.imageFileName.setText(short)
        self.folder = self.app.mwGlob.get('imageDir', '')
        self.ui.checkUsePixel.setChecked(config.get('checkUsePixel', True))
        self.ui.checkUseWCS.setChecked(config.get('checkUseWCS', False))

        return True

    def storeConfig(self):
        """
        storeConfig writes the keys to the configuration dict and stores. if some
        saving has to be proceeded to persistent data, they will be launched as
        well in this method.

        :return: True for test purpose
        """

        config = self.app.config['imageW']
        config['winPosX'] = self.pos().x()
        config['winPosY'] = self.pos().y()
        config['height'] = self.height()
        config['width'] = self.width()
        config['color'] = self.ui.color.currentIndex()
        config['zoom'] = self.ui.zoom.currentIndex()
        config['stretch'] = self.ui.stretch.currentIndex()
        config['imageFileName'] = self.imageFileName
        config['checkUsePixel'] = self.ui.checkUsePixel.isChecked()
        config['checkUseWCS'] = self.ui.checkUseWCS.isChecked()

        return True

    def closeEvent(self, closeEvent):
        """
        closeEvent overlays the window close event of qt. first it stores all persistent
        data for the windows and its functions, than removes al signal / slot connections
        removes the matplotlib embedding and finally calls the parent calls for handling
        the framework close event.

        :param closeEvent:
        :return:
        """

        self.storeConfig()
        # gui signals
        self.ui.load.clicked.disconnect(self.selectImage)
        self.ui.color.currentIndexChanged.disconnect(self.showFitsImage)
        self.ui.stretch.currentIndexChanged.disconnect(self.showFitsImage)
        self.ui.zoom.currentIndexChanged.disconnect(self.showFitsImage)
        self.ui.checkUseWCS.clicked.disconnect(self.showFitsImage)
        self.ui.checkUsePixel.clicked.disconnect(self.showFitsImage)
        self.ui.solve.clicked.disconnect(self.solveImage)
        self.signalShowImage.disconnect(self.showFitsImage)
        self.signalSolveImage.disconnect(self.solveImage)

        plt.close(self.imageMat.figure)

        super().closeEvent(closeEvent)

    def showWindow(self):
        """
        showWindow prepares all data for showing the window, plots the image and show it.
        afterwards all necessary signal / slot connections will be established.

        :return: true for test purpose
        """

        self.showFitsImage()
        self.show()

        # gui signals
        self.ui.load.clicked.connect(self.selectImage)
        self.ui.color.currentIndexChanged.connect(self.showFitsImage)
        self.ui.stretch.currentIndexChanged.connect(self.showFitsImage)
        self.ui.zoom.currentIndexChanged.connect(self.showFitsImage)
        self.ui.checkUseWCS.clicked.connect(self.showFitsImage)
        self.ui.checkUsePixel.clicked.connect(self.showFitsImage)
        self.ui.solve.clicked.connect(self.solveImage)
        self.signalShowImage.connect(self.showFitsImage)
        self.signalSolveImage.connect(self.solveImage)

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
        be loaded, just the full filepath will be stored. if succeeding, the signal for
        displaying the image will be emitted.

        :return: success
        """

        loadFilePath, name, ext = self.openFile(self,
                                                'Select image file',
                                                self.folder,
                                                'FITS files (*.fit*)',
                                                enableDir=True,
                                                )
        if not name:
            return False

        self.ui.imageFileName.setText(name)
        self.imageFileName = loadFilePath
        self.app.message.emit(f'Image [{name}] selected', 0)
        self.ui.checkUsePixel.setChecked(True)
        self.folder = os.path.dirname(loadFilePath)
        self.signalShowImage.emit()

        return True

    def solveImage(self):
        """
        solveImage calls astrometry for solving th actual image in a threading manner.
        as result the gui will be active while the solving process takes part a
        background task. if the check update fits is selected the solution will be
        stored in the image header as well.
        solveImage will disable gui elements which might interfere when doing solve
        in background and sets the signal / slot connection for receiving the signal
        for finishing. this is linked to a second method solveDone, which is basically
        the partner method for handling this async behaviour of the gui.
        finally it emit a message about the start of solving

        :return:
        """

        updateFits = self.ui.checkUpdateFits.isChecked()
        self.app.astrometry.solveThreading(fitsPath=self.imageFileName,
                                           timeout=10,
                                           updateFits=updateFits,
                                           )
        self.changeStyleDynamic(self.ui.solve, 'running', 'true')
        self.ui.expose.setEnabled(False)
        self.ui.exposeN.setEnabled(False)
        self.ui.stop.setEnabled(False)
        self.ui.load.setEnabled(False)

        self.app.astrometry.signals.solveDone.connect(self.solveDone)

        self.app.message.emit(f'Solving: [{self.imageFileName}]', 0)

        return True

    def solveDone(self, result):
        """
        solveDone is the partner method for solveImage. it enables the gui elements back
        removes the signal / slot connection for receiving solving results, checks the
        solving result itself and emits messages about the result. if solving succeeded,
        solveDone will redraw the image in the image window.

        :param result: result (named tuple)
        :return: success
        """

        self.changeStyleDynamic(self.ui.solve, 'running', 'false')
        self.ui.expose.setEnabled(True)
        self.ui.exposeN.setEnabled(True)
        self.ui.stop.setEnabled(True)
        self.ui.load.setEnabled(True)

        self.app.astrometry.signals.solveDone.disconnect(self.solveDone)

        if not result[0]:
            self.app.message.emit('Solving error', 2)
            return False

        r = result[1]
        text = f'Ra: {r.ra} Dec: {r.dec} Angle: {r.angle} Scale: {r.scale}'
        self.app.message.emit('Solved: ' + text, 0)
        self.signalShowImage.emit()

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
                  header.get('MPSAS', 0),
                  )
        self.ui.sqm.setText(f'{sqm:5.2f}')

        flipped = header.get('FLIPPED', False)
        self.ui.checkIsFlipped.setChecked(flipped)

        if 'CTYPE1' in header:
            wcsObject = wcs.WCS(header)
            hasCelestial = wcsObject.has_celestial
            hasDistortion = wcsObject.has_distortion
        else:
            wcsObject = None
            hasCelestial = False
            hasDistortion = False

        self.ui.checkHasDistortion.setChecked(hasDistortion)
        self.ui.checkHasWCS.setChecked(hasCelestial)
        self.ui.checkUseWCS.setEnabled(hasDistortion)

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

        colorMapIndex = self.ui.color.currentIndex()
        colorMap = self.colorMaps[colorMapIndex]

        return colorMap

    def setupDistorted(self, figure=None, wcsObject=None):
        """
        setupDistorted tries to setup all necessary context for displaying the image with
        wcs distorted coordinates.
        still plenty of work to be done, because very often the labels are not shown

        :param figure:
        :param wcsObject:
        :return: axes object to plot onto
        """

        figure.clf()
        figure.subplots_adjust(left=0.1, right=0.9, bottom=0.1, top=0.9)

        axe = figure.add_subplot(1, 1, 1, projection=wcsObject, facecolor=None)
        axe.coords.frame.set_color(self.M_BLUE)

        axe0 = axe.coords[0]
        axe1 = axe.coords[1]
        axe0.grid(True, color=self.M_BLUE, ls='solid', alpha=0.5)
        axe1.grid(True, color=self.M_BLUE, ls='solid', alpha=0.5)
        axe0.tick_params(colors=self.M_BLUE, labelsize=12)
        axe1.tick_params(colors=self.M_BLUE, labelsize=12)
        axe0.set_axislabel('Right Ascension',
                           color=self.M_BLUE,
                           fontsize=12,
                           fontweight='bold')
        axe1.set_axislabel('Declination',
                           color=self.M_BLUE,
                           fontsize=12,
                           fontweight='bold')
        axe0.set_ticks(number=10)
        axe1.set_ticks(number=10)
        axe0.set_ticks_position('lr')
        axe0.set_ticklabel_position('lr')
        axe0.set_axislabel_position('lr')
        axe1.set_ticks_position('tb')
        axe1.set_ticklabel_position('tb')
        axe1.set_axislabel_position('tb')
        return axe

    def setupNormal(self, figure=None, image=None):
        """
        setupNormal build the image widget to show it with pixels as axes. the center of
        the image will have coordinates 0,0.

        :param figure:
        :param image:
        :return: axes object to plot onto
        """

        figure.clf()
        figure.subplots_adjust(left=0.1, right=0.95, bottom=0.1, top=0.95)

        axe = figure.add_subplot(1, 1, 1, facecolor=None)
        axe.grid(True, color=self.M_BLUE, ls='solid', alpha=0.5)
        axe.tick_params(axis='x', which='major', colors=self.M_BLUE, labelsize=12)
        axe.tick_params(axis='y', which='major', colors=self.M_BLUE, labelsize=12)

        sizeY, sizeX = image.shape
        midX = int(sizeX / 2)
        midY = int(sizeY / 2)
        number = 10

        valueX, _ = np.linspace(-midX, midX, num=number, retstep=True)
        textX = list((str(int(x)) for x in valueX))
        ticksX = list((x + midX for x in valueX))
        axe.set_xticklabels(textX)
        axe.set_xticks(ticksX)

        valueY, _ = np.linspace(-midY, midY, num=number, retstep=True)
        textY = list((str(int(x)) for x in valueY))
        ticksY = list((x + midY for x in valueY))
        axe.set_yticklabels(textY)
        axe.set_yticks(ticksY)

        axe.set_xlabel(xlabel='Pixel', color=self.M_BLUE, fontsize=12, fontweight='bold')
        axe.set_ylabel(ylabel='Pixel', color=self.M_BLUE, fontsize=12, fontweight='bold')
        return axe

    def showFitsImage(self):
        """
        showFitsImage shows the fits image. therefore it calculates color map, stretch,
        zoom and other topics.

        :return: success
        """

        imagePath = self.imageFileName
        if not imagePath:
            return False
        if not os.path.isfile(imagePath):
            return False

        with fits.open(imagePath, mode='update') as fitsHandle:
            self.imageData = fitsHandle[0].data
            header = fitsHandle[0].header

            # correct faulty headers, because some imaging programs did not
            # interpret the Keywords in the right manner (SGPro)

            if header.get('CTYPE1', '').endswith('DEF'):
                header['CTYPE1'] = header['CTYPE1'].replace('DEF', 'TAN')
            if header.get('CTYPE2', '').endswith('DEF'):
                header['CTYPE2'] = header['CTYPE2'].replace('DEF', 'TAN')

        # check the data content and capabilities
        hasDistortion, wcsObject = self.writeHeaderToGui(header=header)

        # process the image for viewing
        self.imageData = self.zoomImage(image=self.imageData, wcsObject=wcsObject)
        norm = self.stretchImage(image=self.imageData)
        colorMap = self.colorImage()

        # check which type of presentation we would like to have
        if hasDistortion and self.ui.checkUseWCS.isChecked():
            axe = self.setupDistorted(figure=self.imageMat.figure, wcsObject=wcsObject)
        else:
            axe = self.setupNormal(figure=self.imageMat.figure, image=self.imageData)

        # finally show it
        axe.imshow(self.imageData, norm=norm, cmap=colorMap, origin='lower')
        axe.figure.canvas.draw()

        return True
