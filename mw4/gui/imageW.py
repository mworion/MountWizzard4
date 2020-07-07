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
# written in python 3, (c) 2019, 2020 by mworion
#
# Licence APL2.0
#
###########################################################
import mw4.base.packageConfig as Config
# standard libraries
import os

# external packages
import PyQt5.QtWidgets
from astropy.io import fits
from astropy import wcs
from astropy.nddata import Cutout2D
from astropy.visualization import MinMaxInterval
from astropy.visualization import AsinhStretch
from astropy.visualization import imshow_norm
from astropy.stats import sigma_clipped_stats
from photutils import CircularAperture
from photutils import DAOStarFinder

import matplotlib.pyplot as plt
from skyfield.api import Angle
import numpy as np
import cv2

# local import
from mw4.base import transform
from mw4.gui import widget
from mw4.gui.widgets import image_ui
from mw4.base.tpool import Worker


class ImageWindowSignals(PyQt5.QtCore.QObject):
    """
    The CameraSignals class offers a list of signals to be used and instantiated by
    the Mount class to get signals for triggers for finished tasks to
    enable a gui to update their values transferred to the caller back.

    This has to be done in a separate class as the signals have to be subclassed from
    QObject and the Mount class itself is subclassed from object
    """

    __all__ = ['ImageWindowSignals']

    showCurrent = PyQt5.QtCore.pyqtSignal()
    solveImage = PyQt5.QtCore.pyqtSignal(object)


class ImageWindow(widget.MWidget):
    """
    the image window class handles fits image loading, stretching, zooming and handles
    the gui interface for display. both wcs and pixel coordinates will be used.

    """

    __all__ = ['ImageWindow',
               ]

    def __init__(self, app):
        super().__init__()

        self.app = app
        self.threadPool = app.threadPool
        self.ui = image_ui.Ui_ImageDialog()
        self.ui.setupUi(self)
        self.initUI()
        self.signals = ImageWindowSignals()

        self.imageFileName = ''
        self.imageFileNameOld = ''
        self.expTime = 1
        self.binning = 1

        self.image = None
        self.header = None
        self.imageStack = None
        self.numberStack = 0
        self.colorMap = None
        self.stretch = None
        self.sources = None
        self.mean = None
        self.median = None
        self.std = None
        self.folder = ''

        self.deviceStat = {
            'expose': False,
            'exposeN': False,
            'solve': False,
        }
        self.view = {0: 'Image',
                     1: 'Image & WCS coordinates',
                     2: 'Image & detected sources',
                     3: 'Photometry - Sharpness',
                     4: 'Photometry - Roundness',
                     5: 'Photometry - Flux',
                     }

        self.colorMaps = {'Grey': 'gray',
                          'Cool': 'plasma',
                          'Rainbow': 'rainbow',
                          'Spectral': 'nipy_spectral',
                          }

        self.stretchValues = {'Low X': 0.2,
                              'Low': 0.1,
                              'Mid': 0.5,
                              'High': 0.025,
                              'Super': 0.005,
                              'Super X': 0.0025,
                              }

        self.zoomLevel = {' 1x Zoom': 1,
                          ' 2x Zoom': 2,
                          ' 4x Zoom': 4,
                          ' 8x Zoom': 8,
                          '16x Zoom': 16,
                          }

        self.imageMat = self.embedMatplot(self.ui.image, constrainedLayout=False)
        self.imageMat.parentWidget().setStyleSheet(self.BACK_BG)
        self.fig = self.imageMat.figure
        self.axe = None
        self.axeCB = None

        # cyclic updates
        self.app.update1s.connect(self.updateWindowsStats)

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
        self.ui.view.setCurrentIndex(config.get('view', 0))

        self.ui.stretch.setCurrentIndex(config.get('stretch', 0))
        self.imageFileName = config.get('imageFileName', '')
        self.folder = self.app.mwGlob.get('imageDir', '')
        self.ui.checkStackImages.setChecked(config.get('checkStackImages', False))
        self.ui.checkShowCrosshair.setChecked(config.get('checkShowCrosshair', False))
        self.ui.checkShowGrid.setChecked(config.get('checkShowGrid', True))
        self.ui.checkAutoSolve.setChecked(config.get('checkAutoSolve', False))
        self.ui.checkEmbedData.setChecked(config.get('checkEmbedData', False))

        return True

    def storeConfig(self):
        """
        storeConfig writes the keys to the configuration dict and stores. if some
        saving has to be proceeded to persistent data, they will be launched as
        well in this method.

        :return: True for test purpose
        """
        if 'imageW' not in self.app.config:
            self.app.config['imageW'] = {}
        config = self.app.config['imageW']
        config['winPosX'] = self.pos().x()
        config['winPosY'] = self.pos().y()
        config['height'] = self.height()
        config['width'] = self.width()
        config['color'] = self.ui.color.currentIndex()
        config['zoom'] = self.ui.zoom.currentIndex()
        config['view'] = self.ui.view.currentIndex()
        config['stretch'] = self.ui.stretch.currentIndex()
        config['imageFileName'] = self.imageFileName
        config['checkStackImages'] = self.ui.checkStackImages.isChecked()
        config['checkShowCrosshair'] = self.ui.checkShowCrosshair.isChecked()
        config['checkShowGrid'] = self.ui.checkShowGrid.isChecked()
        config['checkAutoSolve'] = self.ui.checkAutoSolve.isChecked()
        config['checkEmbedData'] = self.ui.checkEmbedData.isChecked()

        return True

    def showWindow(self):
        """
        showWindow prepares all data for showing the window, plots the image and show it.
        afterwards all necessary signal / slot connections will be established.

        :return: true for test purpose
        """

        self.show()
        self.showCurrent()

        # gui signals
        self.ui.load.clicked.connect(self.selectImage)
        self.ui.color.currentIndexChanged.connect(self.preparePlot)
        self.ui.stretch.currentIndexChanged.connect(self.preparePlot)
        self.ui.zoom.currentIndexChanged.connect(self.showCurrent)
        self.ui.view.currentIndexChanged.connect(self.preparePlot)
        self.ui.checkShowGrid.clicked.connect(self.preparePlot)
        self.ui.checkShowCrosshair.clicked.connect(self.preparePlot)
        self.ui.solve.clicked.connect(self.solveCurrent)
        self.ui.expose.clicked.connect(self.exposeImage)
        self.ui.exposeN.clicked.connect(self.exposeImageN)
        self.ui.abortImage.clicked.connect(self.abortImage)
        self.ui.abortSolve.clicked.connect(self.abortSolve)
        self.signals.showCurrent.connect(self.showCurrent)
        self.signals.solveImage.connect(self.solveImage)
        self.app.showImage.connect(self.showImage)

        return True

    def closeEvent(self, closeEvent):
        """
        closeEvent overlays the window close event of qt. first it stores all persistent
        data for the windows and its functions, than removes al signal / slot connections
        removes the matplotlib embedding and finally calls the parent calls for handling
        the framework close event.

        :param closeEvent:
        :return: True for test purpose
        """

        self.storeConfig()

        # gui signals
        self.ui.load.clicked.disconnect(self.selectImage)
        self.ui.color.currentIndexChanged.disconnect(self.preparePlot)
        self.ui.stretch.currentIndexChanged.disconnect(self.preparePlot)
        self.ui.zoom.currentIndexChanged.disconnect(self.showCurrent)
        self.ui.view.currentIndexChanged.disconnect(self.preparePlot)
        self.ui.checkShowGrid.clicked.disconnect(self.preparePlot)
        self.ui.checkShowCrosshair.clicked.disconnect(self.preparePlot)
        self.ui.solve.clicked.disconnect(self.solveCurrent)
        self.ui.expose.clicked.disconnect(self.exposeImage)
        self.ui.exposeN.clicked.disconnect(self.exposeImageN)
        self.ui.abortImage.clicked.disconnect(self.abortImage)
        self.ui.abortSolve.clicked.disconnect(self.abortSolve)
        self.signals.showCurrent.disconnect(self.showCurrent)
        self.signals.solveImage.disconnect(self.solveImage)

        self.app.showImage.disconnect(self.showImage)

        plt.close(self.imageMat.figure)
        super().closeEvent(closeEvent)

    def setupDropDownGui(self):
        """
        setupDropDownGui handles the population of list for image handling.

        :return: success for test
        """

        self.ui.color.clear()
        self.ui.color.setView(PyQt5.QtWidgets.QListView())
        for text in self.colorMaps:
            self.ui.color.addItem(text)

        self.ui.zoom.clear()
        self.ui.zoom.setView(PyQt5.QtWidgets.QListView())
        for text in self.zoomLevel:
            self.ui.zoom.addItem(text)

        self.ui.stretch.clear()
        self.ui.stretch.setView(PyQt5.QtWidgets.QListView())
        for text in self.stretchValues:
            self.ui.stretch.addItem(text)

        self.ui.view.clear()
        self.ui.view.setView(PyQt5.QtWidgets.QListView())
        for text in self.view:
            self.ui.view.addItem(self.view[text])

        return True

    def updateWindowsStats(self):
        """
        updateWindowsStats changes dynamically the enable and disable of user gui elements
        depending of the actual state of processing

        :return: true for test purpose

        """

        if self.deviceStat['expose']:
            self.ui.exposeN.setEnabled(False)
            self.ui.load.setEnabled(False)
            self.ui.abortImage.setEnabled(True)

        elif self.deviceStat['exposeN']:
            self.ui.expose.setEnabled(False)
            self.ui.load.setEnabled(False)
            self.ui.abortImage.setEnabled(True)

        else:
            self.ui.solve.setEnabled(True)
            self.ui.expose.setEnabled(True)
            self.ui.exposeN.setEnabled(True)
            self.ui.load.setEnabled(True)
            self.ui.abortImage.setEnabled(False)

        if self.deviceStat['solve']:
            self.ui.abortSolve.setEnabled(True)
        else:
            self.ui.abortSolve.setEnabled(False)

        if not self.app.deviceStat['camera']:
            self.ui.expose.setEnabled(False)
            self.ui.exposeN.setEnabled(False)

        if not self.app.deviceStat['astrometry']:
            self.ui.solve.setEnabled(False)

        if self.deviceStat['expose']:
            self.changeStyleDynamic(self.ui.expose, 'running', 'true')

        elif self.deviceStat['exposeN']:
            self.changeStyleDynamic(self.ui.exposeN, 'running', 'true')

        else:
            self.changeStyleDynamic(self.ui.expose, 'running', 'false')
            self.changeStyleDynamic(self.ui.exposeN, 'running', 'false')

        if self.deviceStat['solve']:
            self.changeStyleDynamic(self.ui.solve, 'running', 'true')
        else:
            self.changeStyleDynamic(self.ui.solve, 'running', 'false')

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
        self.folder = os.path.dirname(loadFilePath)
        self.app.showImage.emit(self.imageFileName)

        return True

    def setupDistorted(self):
        """
        setupDistorted tries to setup all necessary context for displaying the image with
        wcs distorted coordinates.
        still plenty of work to be done, because very often the labels are not shown

        :return: true for test purpose
        """

        self.fig.clf()
        self.axe = self.fig.add_subplot(1, 1, 1,
                                        projection=wcs.WCS(self.header, relax=True),
                                        facecolor=self.M_GREY_LIGHT)

        self.fig.subplots_adjust(bottom=0.1, top=0.9, left=0.1, right=0.85)
        self.axeCB = None

        self.axe.coords.frame.set_color(self.M_BLUE)

        axe0 = self.axe.coords[0]
        axe1 = self.axe.coords[1]

        if self.ui.checkShowGrid.isChecked():
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

        return True

    def setupNormal(self):
        """
        setupNormal build the image widget to show it with pixels as axes. the center of
        the image will have coordinates 0,0.

        :return: True for test purpose
        """

        self.fig.clf()
        self.axe = self.fig.add_subplot(1, 1, 1,
                                        facecolor=self.M_GREY_LIGHT)

        self.fig.subplots_adjust(bottom=0.1, top=0.9, left=0.1, right=0.85)
        self.axeCB = self.fig.add_axes([0.88, 0.1, 0.02, 0.8])

        factor = self.zoomLevel[self.ui.zoom.currentText()]
        sizeX = self.header.get('NAXIS1', 1) / factor
        sizeY = self.header.get('NAXIS2', 1) / factor
        midX = int(sizeX / 2)
        midY = int(sizeY / 2)
        number = 10

        if self.ui.checkShowCrosshair.isChecked():
            self.axe.axvline(midX, color=self.M_RED)
            self.axe.axhline(midY, color=self.M_RED)

        if self.ui.checkShowGrid.isChecked():
            self.axe.grid(True, color=self.M_BLUE, ls='solid', alpha=0.5)

        self.axe.tick_params(axis='x', which='major', colors=self.M_BLUE, labelsize=12)
        self.axe.tick_params(axis='y', which='major', colors=self.M_BLUE, labelsize=12)

        valueX, _ = np.linspace(-midX, midX, num=number, retstep=True)
        textX = list((str(int(x)) for x in valueX))
        ticksX = list((x + midX for x in valueX))
        self.axe.set_xticklabels(textX)
        self.axe.set_xticks(ticksX)

        valueY, _ = np.linspace(-midY, midY, num=number, retstep=True)
        textY = list((str(int(x)) for x in valueY))
        ticksY = list((x + midY for x in valueY))
        self.axe.set_yticklabels(textY)
        self.axe.set_yticks(ticksY)

        self.axe.set_xlabel(xlabel='Pixel', color=self.M_BLUE, fontsize=12, fontweight='bold')
        self.axe.set_ylabel(ylabel='Pixel', color=self.M_BLUE, fontsize=12, fontweight='bold')

        self.axe.set_xlim(0, sizeX)
        self.axe.set_ylim(0, sizeY)

        return True

    def colorImage(self):
        """
        colorImage take the index from gui and generates the colormap for image show
        command from matplotlib

        :return: True
        """

        fallback = list(self.colorMaps.keys())[0]
        self.colorMap = self.colorMaps.get(self.ui.color.currentText(), fallback)

        return True

    def stretchImage(self):
        """
        stretchImage take the actual image and calculated norm based on the min, max
        derived from interval which is calculated with AsymmetricPercentileInterval.

        :return: True
        """

        fallback = list(self.stretchValues.keys())[0]
        value = self.stretchValues.get(self.ui.stretch.currentText(), fallback)

        self.stretch = AsinhStretch(a=value)

        return True

    def imagePlot(self):
        """
        different image views

        The object centers are in pixels and the magnitude estimate measures the ratio of
        the maximum density enhancement to the detection threshold. Sharpness is
        typically around .5 to .8 for a star with a fwhm psf similar to the pattern star.
        Both s-round and g-round are close to zero for a truly round star. Id is the
        sequence number of the star in the list.

        :return:
        """

        if self.sources:
            positions = np.transpose((self.sources['xcentroid'],
                                      self.sources['ycentroid']))
            x = self.sources['xcentroid']
            y = self.sources['ycentroid']
            imageDisp = self.image - self.mean
        else:
            positions = None
            imageDisp = self.image

        if self.ui.view.currentIndex() in [0, 1, 2]:
            imageDisp[imageDisp < 0] = 0
            img = imshow_norm(imageDisp,
                              ax=self.axe,
                              origin='lower',
                              interval=MinMaxInterval(),
                              stretch=self.stretch,
                              cmap=self.colorMap,
                              aspect='auto')

            if self.axeCB:
                colorbar = self.fig.colorbar(img[0], cax=self.axeCB)
                colorbar.set_label('Value [pixel value]', color=self.M_BLUE, fontsize=12)
                yTicks = plt.getp(colorbar.ax.axes, 'yticklabels')
                plt.setp(yTicks, color=self.M_BLUE, fontweight='bold')

        if self.ui.view.currentIndex() == 2 and positions is not None:
            apertures = CircularAperture(positions, r=10.0)
            apertures.plot(axes=self.axe, color=self.M_BLUE, lw=1.0, alpha=0.8)

        if self.ui.view.currentIndex() == 3 and self.sources:
            sharpness = self.sources['sharpness']
            area = 50 * (1 - sharpness) + 3
            scatter = self.axe.scatter(x, y, c=sharpness,
                                       vmin=0, vmax=1,
                                       s=area,
                                       cmap='RdYlGn')

            colorbar = self.fig.colorbar(scatter, cax=self.axeCB)
            colorbar.set_label('Sharpness [target -> 0.5 - 0.8]', color=self.M_BLUE, fontsize=12)
            yTicks = plt.getp(colorbar.ax.axes, 'yticklabels')
            plt.setp(yTicks, color=self.M_BLUE, fontweight='bold')

        if self.ui.view.currentIndex() == 4 and self.sources:
            r1 = self.sources['roundness1']
            r2 = self.sources['roundness2']
            rg = np.sqrt(r1 * r1 + r2 * r2)
            area = 50 * rg + 3
            scatter = self.axe.scatter(x, y, c=rg,
                                       vmin=0, vmax=1,
                                       s=area,
                                       cmap='RdYlGn_r')

            colorbar = self.fig.colorbar(scatter, cax=self.axeCB)
            colorbar.set_label('Roundness [target -> 0]', color=self.M_BLUE, fontsize=12)
            yTicks = plt.getp(colorbar.ax.axes, 'yticklabels')
            plt.setp(yTicks, color=self.M_BLUE, fontweight='bold')

        if self.ui.view.currentIndex() == 5 and self.sources:
            flux = np.log(self.sources['flux'])
            area = 3 * flux
            scatter = self.axe.scatter(x, y, c=flux,
                                       s=area,
                                       cmap='viridis')

            colorbar = self.fig.colorbar(scatter, cax=self.axeCB)
            colorbar.set_label('Flux [log(x)]', color=self.M_BLUE, fontsize=12)
            yTicks = plt.getp(colorbar.ax.axes, 'yticklabels')
            plt.setp(yTicks, color=self.M_BLUE, fontweight='bold')

        self.axe.figure.canvas.draw()

        return True

    def writeHeaderDataToGUI(self):
        """
        writeHeaderDataToGUI tries to read relevant values from FITS header and possible
        replace values and write them to the imageW gui

        :return: True for test purpose
        """

        name = self.header.get('OBJECT', '').upper()
        self.ui.object.setText(f'{name}')

        ra = Angle(degrees=self.header.get('RA', 0))
        dec = Angle(degrees=self.header.get('DEC', 0))

        # ra will be in hours
        self.ui.ra.setText(f'{ra.hstr(warn=False)}')
        self.ui.dec.setText(f'{dec.dstr()}')

        scale = self.header.get('SCALE', 0)
        rotation = self.header.get('ANGLE', 0)
        self.ui.scale.setText(f'{scale:5.3f}')
        self.ui.rotation.setText(f'{rotation:6.3f}')

        ccdTemp = self.header.get('CCD-TEMP', 0)
        self.ui.ccdTemp.setText(f'{ccdTemp:4.1f}')

        expTime1 = self.header.get('EXPOSURE', 0)
        expTime2 = self.header.get('EXPTIME', 0)
        expTime = max(expTime1, expTime2)
        self.ui.expTime.setText(f'{expTime:5.1f}')

        filterCCD = self.header.get('FILTER', 0)
        self.ui.filter.setText(f'{filterCCD}')

        binX = self.header.get('XBINNING', 0)
        binY = self.header.get('YBINNING', 0)
        self.ui.binX.setText(f'{binX:1.0f}')
        self.ui.binY.setText(f'{binY:1.0f}')

        sqm = max(self.header.get('SQM', 0),
                  self.header.get('SKY-QLTY', 0),
                  self.header.get('MPSAS', 0),
                  )
        self.ui.sqm.setText(f'{sqm:5.2f}')

        flipped = bool(self.header.get('FLIPPED', False))
        self.ui.isFlipped.setEnabled(flipped)

        return True

    def preparePlot(self):
        """
        wcs header, stretch, color, distortion, select plot mode

        :return:
        """

        if self.image is None:
            return False
        if self.header is None:
            return False

        self.updateWindowsStats()

        # check if distortion is in header
        if 'CTYPE1' in self.header:
            wcsObject = wcs.WCS(self.header, relax=True)
            hasCelestial = wcsObject.has_celestial
            hasDistortion = wcsObject.has_distortion
        else:
            hasCelestial = False
            hasDistortion = False

        self.ui.hasDistortion.setEnabled(hasDistortion)
        self.ui.hasWCS.setEnabled(hasCelestial)

        if hasDistortion:
            self.ui.view.view().setRowHidden(1, False)
        else:
            self.ui.view.view().setRowHidden(1, True)

        useWCS = (self.ui.view.currentIndex() == 1)

        if hasDistortion and useWCS:
            self.setupDistorted()
        else:
            self.setupNormal()

        self.writeHeaderDataToGUI()
        self.stretchImage()
        self.colorImage()
        self.imagePlot()

        return True

    def workerPhotometry(self):
        """

        :return:
        """

        self.mean, self.median, self.std = sigma_clipped_stats(self.image, sigma=3.0)
        daoFind = DAOStarFinder(fwhm=2.5, threshold=5.0 * self.std)
        self.sources = daoFind(self.image - self.median)

        return True

    def prepareImage(self):
        """
        background, source extraction

        :return:
        """

        if Config.featureFlags['imageAdv'] and not self.sources:
            worker = Worker(self.workerPhotometry)
            worker.signals.finished.connect(self.preparePlot)
            self.threadPool.start(worker)

        self.preparePlot()

        return True

    def stackImages(self):
        """

        :return:
        """

        if not self.ui.checkStackImages.isChecked():
            self.imageStack = None
            self.ui.numberStacks.setText('single')
            return False

        if np.shape(self.image) != np.shape(self.imageStack):
            self.imageStack = None

        self.ui.numberStacks.setText(f'mean of: {self.numberStack:4.0f}')

        if self.imageStack is None:
            self.imageStack = self.image
            self.numberStack = 1
        else:
            self.imageStack = np.add(self.imageStack, self.image)
            self.numberStack += 1

        self.image = self.imageStack / self.numberStack

        return True

    def zoomImage(self):
        """
        zoomImage cutouts a portion of the original image to zoom in the image itself.
        it returns a copy of the image with an updated wcs content. we have to be careful
        about the use of Cutout2D, because they are mixing x and y coordinates. so position
        is in (x, y), but size ind in (y, x)

        :return: true
        """

        sizeY, sizeX = self.image.shape

        fallback = list(self.zoomLevel.keys())[0]
        factor = self.zoomLevel.get(self.ui.zoom.currentText(), fallback)

        if factor == 1:
            return

        position = (int(sizeX / 2), int(sizeY / 2))
        size = (int(sizeY / factor), int(sizeX / factor))

        self.image = Cutout2D(self.image,
                              position=position,
                              size=size,
                              wcs=wcs.WCS(self.header, relax=True),
                              copy=True).data

        return True

    def showImage(self, imagePath=''):
        """
        tho idea of processing the image data until it is shown on screen is to split the
        pipeline in several atomic steps, which follow each other. each step is calling the
        next one and depending which user interaction is done and how the use case for
        changing the view is the entrance of the pipeline is chosen adequately.

        so we have step 1 loading data and processing if to final monochrome and sized format
        - loading data
        - debayer if necessary
        - getting header data and cleaning it up
        - zoom and stack

        :param imagePath:
        :return:
        """

        if not imagePath:
            return False
        if not os.path.isfile(imagePath):
            return False

        self.imageFileName = imagePath
        full, short, ext = self.extractNames([imagePath])
        self.ui.imageFileName.setText(short)

        with fits.open(imagePath, mode='update') as fitsHandle:
            self.image = fitsHandle[0].data
            self.header = fitsHandle[0].header

        if self.image is None:
            return False
        if self.header is None:
            return False

        # todo: if it's an exposure directly, I get a bayer mosaic ??
        if 'BAYERPAT' in self.header and len(self.image.shape) > 2:
            self.image = cv2.cvtColor(self.image, cv2.COLOR_BAYER_BG2GRAY)

        # correct faulty headers, because some imaging programs did not
        # interpret the Keywords in the right manner (SGPro)
        if self.header.get('CTYPE1', '').endswith('DEF'):
            self.header['CTYPE1'] = self.header['CTYPE1'].replace('DEF', 'TAN')
        if self.header.get('CTYPE2', '').endswith('DEF'):
            self.header['CTYPE2'] = self.header['CTYPE2'].replace('DEF', 'TAN')

        self.zoomImage()
        self.stackImages()
        self.sources = None
        self.prepareImage()

        return True

    def showCurrent(self):
        """

        :return: true for test purpose
        """

        self.showImage(self.imageFileName)

        return True

    def exposeRaw(self):
        """
        exposeImage gathers all necessary parameters and starts exposing

        :return: True for test purpose
        """

        subFrame = self.app.mainW.ui.subFrame.value()
        fastReadout = self.app.mainW.ui.checkFastDownload.isChecked()

        time = self.app.mount.obsSite.timeJD.utc_strftime('%Y-%m-%d-%H-%M-%S')
        fileName = time + '-exposure.fits'
        imagePath = self.app.mwGlob['imageDir'] + '/' + fileName
        focalLength = self.app.mainW.ui.focalLength.value()

        self.imageFileNameOld = self.imageFileName

        self.app.camera.expose(imagePath=imagePath,
                               expTime=self.expTime,
                               binning=self.binning,
                               subFrame=subFrame,
                               fastReadout=fastReadout,
                               focalLength=focalLength
                               )

        self.app.message.emit(f'Exposing:            [{os.path.basename(imagePath)}]', 0)
        text = f'Duration:{self.expTime:3.0f}s  Bin:{self.binning:1.0f}  Sub:{subFrame:3.0f}%'
        self.app.message.emit(f'                     {text}', 0)

        return True

    def exposeImageDone(self, imagePath=''):
        """
        exposeImageDone is the partner method to exposeImage. it resets the gui elements
        to it's default state and disconnects the signal for the callback. finally when
        all elements are done it emits the showContent signal.

        :param imagePath:
        :return: True for test purpose
        """

        self.deviceStat['expose'] = False
        self.app.camera.signals.saved.disconnect(self.exposeImageDone)
        self.app.message.emit(f'Exposed:             [{os.path.basename(imagePath)}]', 0)

        if self.ui.checkAutoSolve.isChecked():
            self.signals.solveImage.emit(imagePath)
        else:
            self.app.showImage.emit(imagePath)

        return True

    def exposeImage(self):
        """
        exposeImage disables all gui elements which could interfere when having a running
        exposure. it connects the callback for downloaded image and presets all necessary
        parameters for imaging

        :return: success
        """

        self.expTime = self.app.mainW.ui.expTime.value()
        self.binning = self.app.mainW.ui.binning.value()

        self.imageStack = None
        self.deviceStat['expose'] = True
        self.ui.checkStackImages.setChecked(False)
        self.app.camera.signals.saved.connect(self.exposeImageDone)

        self.exposeRaw()

        return True

    def exposeImageNDone(self, imagePath=''):
        """
        exposeImageNDone is the partner method to exposeImage. it resets the gui elements
        to it's default state and disconnects the signal for the callback. finally when
        all elements are done it emits the showContent signal.

        :param imagePath:
        :return: True for test purpose
        """

        self.app.message.emit(f'Exposed:            [{os.path.basename(imagePath)}]', 0)

        if self.ui.checkAutoSolve.isChecked():
            self.signals.solveImage.emit(imagePath)
        else:
            self.app.showImage.emit(imagePath)

        self.exposeRaw()

        return True

    def exposeImageN(self):
        """
        exposeImageN disables all gui elements which could interfere when having a running
        exposure. it connects the callback for downloaded image and presets all necessary
        parameters for imaging

        :return: success
        """

        self.expTime = self.app.mainW.ui.expTimeN.value()
        self.binning = self.app.mainW.ui.binningN.value()

        self.imageStack = None
        self.deviceStat['exposeN'] = True
        self.app.camera.signals.saved.connect(self.exposeImageNDone)

        self.exposeRaw()

        return True

    def abortImage(self):
        """
        abortImage stops the exposure and resets the gui and the callback signals to default
        values

        :return: True for test purpose
        """

        self.app.camera.abort()

        # for disconnection we have to split which slots were connected to disable the
        # right ones
        if self.deviceStat['expose']:
            self.app.camera.signals.saved.disconnect(self.exposeImageDone)
        if self.deviceStat['exposeN']:
            self.app.camera.signals.saved.disconnect(self.exposeImageNDone)

        # last image file was nor stored, so getting last valid it back
        self.imageFileName = self.imageFileNameOld
        self.deviceStat['expose'] = False
        self.deviceStat['exposeN'] = False
        self.app.message.emit('Exposing aborted', 2)

        return True

    def solveDone(self, result=None):
        """
        solveDone is the partner method for solveImage. it enables the gui elements back
        removes the signal / slot connection for receiving solving results, checks the
        solving result itself and emits messages about the result. if solving succeeded,
        solveDone will redraw the image in the image window.

        :param result: result (named tuple)
        :return: success
        """

        self.deviceStat['solve'] = False
        self.app.astrometry.signals.done.disconnect(self.solveDone)

        if not result:
            self.app.message.emit('Solving error, result missing', 2)
            return False

        if result['success']:
            text = f'Solved :             '
            text += f'RA: {transform.convertToHMS(result["raJ2000S"])} '
            text += f'({result["raJ2000S"].hours:4.3f}), '
            text += f'DEC: {transform.convertToDMS(result["decJ2000S"])} '
            text += f'({result["decJ2000S"].degrees:4.3f}), '
            self.app.message.emit(text, 0)
            text = f'                     '
            text += f'Angle: {result["angleS"]:3.0f}, '
            text += f'Scale: {result["scaleS"]:4.3f}, '
            text += f'Error: {result["errorRMS_S"]:4.1f}'
            self.app.message.emit(text, 0)
        else:
            text = f'Solving error:       {result.get("message")}'
            self.app.message.emit(text, 2)
            return False

        isStack = self.ui.checkStackImages.isChecked()
        isAutoSolve = self.ui.checkAutoSolve.isChecked()
        if not isStack or isAutoSolve:
            self.app.showImage.emit(result['solvedPath'])

        return True

    def solveImage(self, imagePath=''):
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

        :param imagePath:
        :return:
        """

        if not imagePath:
            return False
        if not os.path.isfile(imagePath):
            return False

        updateFits = self.ui.checkEmbedData.isChecked()
        self.app.astrometry.solveThreading(fitsPath=imagePath,
                                           updateFits=updateFits,
                                           )
        self.deviceStat['solve'] = True
        self.app.astrometry.signals.done.connect(self.solveDone)
        self.app.message.emit(f'Solving:             [{os.path.basename(imagePath)}]', 0)

        return True

    def solveCurrent(self):
        """

        :return: true for test purpose
        """

        self.signals.solveImage.emit(self.imageFileName)
        return True

    def abortSolve(self):
        """
        abortSolve stops the exposure and resets the gui and the callback signals to default
        values

        :return: success
        """
        suc = self.app.astrometry.abort()

        return suc
