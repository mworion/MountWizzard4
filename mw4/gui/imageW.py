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
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
import os
# external packages
import PyQt5.QtWidgets
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
from mw4.base import transform
from mw4.definitions import Solution


class ImageWindowSignals(PyQt5.QtCore.QObject):
    """
    The CameraSignals class offers a list of signals to be used and instantiated by
    the Mount class to get signals for triggers for finished tasks to
    enable a gui to update their values transferred to the caller back.

    This has to be done in a separate class as the signals have to be subclassed from
    QObject and the Mount class itself is subclassed from object
    """

    __all__ = ['ImageWindowSignals']
    version = '0.101'

    showCurrent = PyQt5.QtCore.pyqtSignal()
    showImage = PyQt5.QtCore.pyqtSignal(object)
    solveImage = PyQt5.QtCore.pyqtSignal(object)


class ImageWindow(widget.MWidget):
    """
    the image window class handles fits image loading, stretching, zooming and handles
    the gui interface for display. both wcs and pixel coordinates will be used.

    """

    __all__ = ['ImageWindow',
               ]
    version = '0.101'
    logger = logging.getLogger(__name__)

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.ui = image_ui.Ui_ImageDialog()
        self.ui.setupUi(self)
        self.initUI()
        self.signals = ImageWindowSignals()

        self.imageFileName = ''
        self.imageFileNameOld = ''
        self.imageStack = None
        self.raStack = 0
        self.decStack = 0
        self.angleStack = 0
        self.scaleStack = 0
        self.numberStack = 0
        self.folder = ''

        self.deviceStat = {
            'expose': False,
            'exposeN': False,
            'solve': False,
        }
        self.colorMaps = {'Grey': 'gray',
                          'Cool': 'plasma',
                          'Rainbow': 'rainbow',
                          'Spectral': 'nipy_spectral',
                          }

        self.stretchValues = {'Low X': (98, 99.999),
                              'Low': (90, 99.995),
                              'Mid': (50, 99.99),
                              'High': (20, 99.98),
                              'Super': (10, 99.9),
                              'Super X': (1, 99.8),
                              }

        self.zoomLevel = {' 1x Zoom': 1,
                          ' 2x Zoom': 2,
                          ' 4x Zoom': 4,
                          ' 8x Zoom': 8,
                          '16x Zoom': 16,
                          }

        self.imageMat = self.embedMatplot(self.ui.image)
        self.imageMat.parentWidget().setStyleSheet(self.BACK_BG)

        self.initConfig()
        self.showWindow()
        self.app.update1s.connect(self.updateWindowsStats)

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
        self.folder = self.app.mwGlob.get('imageDir', '')
        self.ui.checkUseWCS.setChecked(config.get('checkUseWCS', False))
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

        config = self.app.config['imageW']
        config['winPosX'] = self.pos().x()
        config['winPosY'] = self.pos().y()
        config['height'] = self.height()
        config['width'] = self.width()
        config['color'] = self.ui.color.currentIndex()
        config['zoom'] = self.ui.zoom.currentIndex()
        config['stretch'] = self.ui.stretch.currentIndex()
        config['imageFileName'] = self.imageFileName
        config['checkUseWCS'] = self.ui.checkUseWCS.isChecked()
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

        self.showImage(self.imageFileName)
        self.show()

        # gui signals
        self.ui.load.clicked.connect(self.selectImage)
        self.ui.color.currentIndexChanged.connect(self.showCurrent)
        self.ui.stretch.currentIndexChanged.connect(self.showCurrent)
        self.ui.zoom.currentIndexChanged.connect(self.showCurrent)
        self.ui.checkUseWCS.clicked.connect(self.showCurrent)
        self.ui.checkShowGrid.clicked.connect(self.showCurrent)
        self.ui.checkShowCrosshair.clicked.connect(self.showCurrent)
        self.ui.solve.clicked.connect(self.solveCurrent)
        self.ui.expose.clicked.connect(self.exposeImage)
        self.ui.exposeN.clicked.connect(self.exposeImageN)
        self.ui.abortImage.clicked.connect(self.abortImage)
        self.ui.abortSolve.clicked.connect(self.abortSolve)
        self.signals.showCurrent.connect(self.showCurrent)
        self.signals.showImage.connect(self.showImage)
        self.signals.solveImage.connect(self.solveImage)

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
        self.ui.color.currentIndexChanged.disconnect(self.showCurrent)
        self.ui.stretch.currentIndexChanged.disconnect(self.showCurrent)
        self.ui.zoom.currentIndexChanged.disconnect(self.showCurrent)
        self.ui.checkUseWCS.clicked.disconnect(self.showCurrent)
        self.ui.checkShowGrid.clicked.disconnect(self.showCurrent)
        self.ui.checkShowCrosshair.clicked.disconnect(self.showCurrent)
        self.ui.solve.clicked.disconnect(self.solveCurrent)
        self.ui.expose.clicked.disconnect(self.exposeImage)
        self.ui.exposeN.clicked.disconnect(self.exposeImageN)
        self.ui.abortImage.clicked.disconnect(self.abortImage)
        self.ui.abortSolve.clicked.disconnect(self.abortSolve)
        self.signals.showCurrent.disconnect(self.showCurrent)
        self.signals.showImage.disconnect(self.showImage)
        self.signals.solveImage.disconnect(self.solveImage)

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

        if not self.app.mainW.deviceStat['imaging']:
            self.ui.expose.setEnabled(False)
            self.ui.exposeN.setEnabled(False)

        if not self.app.mainW.deviceStat['astrometry']:
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
        self.ui.checkUseWCS.setChecked(False)
        self.folder = os.path.dirname(loadFilePath)
        self.signals.showImage.emit(self.imageFileName)

        return True

    def writeHeaderToGUI(self, header=None):
        """
        writeHeaderToGUI tries to read relevant values from FITS header and possible
        replace values and write them to the imageW gui

        :param header: header of fits file
        :return: hasCelestial, hasDistortion
        """

        name = header.get('OBJECT', '').upper()
        self.ui.object.setText(f'{name}')

        ra = header.get('OBJCTRA', 0)
        ra = transform.convertToAngle(ra, isHours=True)
        dec = header.get('OBJCTDEC', 0)
        dec = transform.convertToAngle(dec, isHours=False)
        self.ui.ra.setText(f'{transform.convertToHMS(ra)}')
        self.ui.dec.setText(f'{transform.convertToDMS(dec)}')

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

        flipped = bool(header.get('FLIPPED', False))
        self.ui.isFlipped.setEnabled(flipped)

        # check if distortion is in header
        if 'CTYPE1' in header:
            wcsObject = wcs.WCS(header, relax=True)
            hasCelestial = wcsObject.has_celestial
            hasDistortion = wcsObject.has_distortion
        else:
            wcsObject = None
            hasCelestial = False
            hasDistortion = False

        self.ui.hasDistortion.setEnabled(hasDistortion)
        self.ui.hasWCS.setEnabled(hasCelestial)

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

        if image is None:
            return None

        sizeY, sizeX = image.shape
        factor = self.zoomLevel[self.ui.zoom.currentText()]
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

        if image is None:
            return None

        values = self.stretchValues[self.ui.stretch.currentText()]
        interval = AsymmetricPercentileInterval(*values)
        vmin, vmax = interval.get_limits(image)
        # cutout the noise
        delta = vmax - vmin
        vmin = min(vmin + delta * 0.01, vmax)

        norm = ImageNormalize(image,
                              vmin=vmin,
                              vmax=vmax,
                              stretch=SqrtStretch(),
                              )

        return norm, vmin, vmax

    def colorImage(self):
        """
        colorImage take the index from gui and generates the colormap for image show
        command from matplotlib

        :return: color map
        """

        colorMap = self.colorMaps[self.ui.color.currentText()]

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

        if figure is None:
            return False
        if wcsObject is None:
            return False

        figure.clf()
        figure.subplots_adjust(left=0.1, right=0.9, bottom=0.1, top=0.9)

        axe = figure.add_subplot(1, 1, 1, projection=wcsObject, facecolor=None)
        axe.coords.frame.set_color(self.M_BLUE)

        axe0 = axe.coords[0]
        axe1 = axe.coords[1]
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

        return figure, axe

    def setupNormal(self, figure=None, header=None):
        """
        setupNormal build the image widget to show it with pixels as axes. the center of
        the image will have coordinates 0,0.

        :param figure:
        :param header:
        :return: axes object to plot onto
        """

        if figure is None:
            return False
        if header is None:
            return False

        figure.clf()
        # figure.subplots_adjust(left=0.1, right=0.95, bottom=0.1, top=0.95)

        axe = figure.add_subplot(1, 1, 1, facecolor=None)

        axe.tick_params(axis='x', which='major', colors=self.M_BLUE, labelsize=12)
        axe.tick_params(axis='y', which='major', colors=self.M_BLUE, labelsize=12)

        factor = self.zoomLevel[self.ui.zoom.currentText()]
        sizeX = header.get('NAXIS1', 1) / factor
        sizeY = header.get('NAXIS2', 1) / factor
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

        if self.ui.checkShowCrosshair.isChecked():
            axe.axvline(midX, color=self.M_RED)
            axe.axhline(midY, color=self.M_RED)
        if self.ui.checkShowGrid.isChecked():
            axe.grid(True, color=self.M_BLUE, ls='solid', alpha=0.5)

        axe.set_xlabel(xlabel='Pixel', color=self.M_BLUE, fontsize=12, fontweight='bold')
        axe.set_ylabel(ylabel='Pixel', color=self.M_BLUE, fontsize=12, fontweight='bold')
        return figure, axe

    def stackImages(self, imageData=None, header=None):
        """

        :param imageData:
        :param header: is only used, when stacking with alignment
        :return:
        """

        if np.shape(imageData) != np.shape(self.imageStack):
            self.imageStack = None

        # if first image, we just store the data as reference frame
        if self.imageStack is None:
            self.imageStack = imageData
            self.numberStack = 1
            return imageData

        # now we are going to stack the results
        self.numberStack += 1
        self.imageStack = np.add(self.imageStack, imageData)
        return self.imageStack / self.numberStack

    def showImage(self, imagePath=''):
        """
        showImage shows the fits image. therefore it calculates color map, stretch,
        zoom and other topics.

        :param imagePath:
        :return: success
        """

        if not imagePath:
            return False
        if not os.path.isfile(imagePath):
            return False

        self.imageFileName = imagePath
        full, short, ext = self.extractNames([imagePath])
        self.ui.imageFileName.setText(short)

        with fits.open(imagePath, mode='update') as fitsHandle:
            imageData = fitsHandle[0].data
            header = fitsHandle[0].header

        # correct faulty headers, because some imaging programs did not
        # interpret the Keywords in the right manner (SGPro)
        if header.get('CTYPE1', '').endswith('DEF'):
            header['CTYPE1'] = header['CTYPE1'].replace('DEF', 'TAN')
        if header.get('CTYPE2', '').endswith('DEF'):
            header['CTYPE2'] = header['CTYPE2'].replace('DEF', 'TAN')

        if self.ui.checkStackImages.isChecked():
            imageData = self.stackImages(imageData=imageData, header=header)
            self.ui.numberStacks.setText(f'mean of: {self.numberStack:4.0f}')
        else:
            self.imageStack = None
            self.ui.numberStacks.setText('single')

        # check the data content and capabilities
        hasDistortion, wcsObject = self.writeHeaderToGUI(header=header)

        # process the image for viewing
        imageData = self.zoomImage(image=imageData, wcsObject=wcsObject)
        norm, iMin, iMax = self.stretchImage(image=imageData)
        colorMap = self.colorImage()

        # check the data content and capabilities
        useWCS = self.ui.checkUseWCS.isChecked()

        # check which type of presentation we would like to have
        if hasDistortion and useWCS:
            fig, axe = self.setupDistorted(figure=self.imageMat.figure, wcsObject=wcsObject)
        else:
            fig, axe = self.setupNormal(figure=self.imageMat.figure, header=header)

        # finally show it
        axe.imshow(imageData, norm=norm, cmap=colorMap, origin='lower')
        axe.figure.canvas.draw()

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

        expTime = self.app.mainW.ui.expTime.value()
        binning = self.app.mainW.ui.binning.value()
        subFrame = self.app.mainW.ui.subFrame.value()
        fastReadout = self.app.mainW.ui.checkFastDownload.isChecked()

        time = self.app.mount.obsSite.timeJD.utc_strftime('%Y-%m-%d-%H-%M-%S')
        fileName = time + '-exposure.fits'
        imagePath = self.app.mwGlob['imageDir'] + '/' + fileName

        self.imageFileNameOld = self.imageFileName

        self.app.imaging.expose(imagePath=imagePath,
                                expTime=expTime,
                                binning=binning,
                                subFrame=subFrame,
                                fastReadout=fastReadout,
                                )

        self.app.message.emit(f'Exposing: [{os.path.basename(imagePath)}]', 0)
        text = f'Duration: {expTime:3.0f}s  Bin: {binning:1.0f}  Sub: {subFrame:3.0f}%'
        self.app.message.emit(f'     {text}', 0)

        return True

    def exposeImageDone(self, imagePath=''):
        """
        exposeImageDone is the partner method to exposeImage. it resets the gui elements
        to it's default state and disconnects the signal for the callback. finally when
        all elements are done it emits the showImage signal.

        :param imagePath:
        :return: True for test purpose
        """

        self.deviceStat['expose'] = False
        self.app.imaging.signals.saved.disconnect(self.exposeImageDone)
        self.app.message.emit(f'Exposed: [{os.path.basename(imagePath)}]', 0)

        if self.ui.checkAutoSolve.isChecked():
            self.signals.solveImage.emit(imagePath)
        else:
            self.signals.showImage.emit(imagePath)

        return True

    def exposeImage(self):
        """
        exposeImage disables all gui elements which could interfere when having a running
        exposure. it connects the callback for downloaded image and presets all necessary
        parameters for imaging

        :return: success
        """

        self.imageStack = None
        self.deviceStat['expose'] = True
        self.ui.checkStackImages.setChecked(False)
        self.app.imaging.signals.saved.connect(self.exposeImageDone)
        self.exposeRaw()

        return True

    def exposeImageNDone(self, imagePath=''):
        """
        exposeImageNDone is the partner method to exposeImage. it resets the gui elements
        to it's default state and disconnects the signal for the callback. finally when
        all elements are done it emits the showImage signal.

        :param imagePath:
        :return: True for test purpose
        """

        self.app.message.emit(f'Exposed: [{os.path.basename(imagePath)}]', 0)

        if self.ui.checkAutoSolve.isChecked():
            self.signals.solveImage.emit(imagePath)
        else:
            self.signals.showImage.emit(imagePath)

        self.exposeRaw()

        return True

    def exposeImageN(self):
        """
        exposeImageN disables all gui elements which could interfere when having a running
        exposure. it connects the callback for downloaded image and presets all necessary
        parameters for imaging

        :return: success
        """

        self.imageStack = None
        self.deviceStat['exposeN'] = True
        self.app.imaging.signals.saved.connect(self.exposeImageNDone)
        self.exposeRaw()

        return True

    def abortImage(self):
        """
        abortImage stops the exposure and resets the gui and the callback signals to default
        values

        :return: True for test purpose
        """

        self.app.imaging.abort()

        # for disconnection we have to split which slots were connected to disable the
        # right ones
        if self.deviceStat['expose']:
            self.app.imaging.signals.saved.disconnect(self.exposeImageDone)
        if self.deviceStat['exposeN']:
            self.app.imaging.signals.saved.disconnect(self.exposeImageNDone)

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

        if not isinstance(result, Solution):
            self.app.message.emit(f'Solving result is malformed: {result}')
            return False

        if result.success:
            text = f'Solved : '
            text += f'Ra: {transform.convertToHMS(result.solve.raJ2000)} '
            text += f'({result.solve.raJ2000.hours:4.3f}), '
            text += f'Dec: {transform.convertToDMS(result.solve.decJ2000)} '
            text += f'({result.solve.decJ2000.degrees:4.3f}), '
            self.app.message.emit(text, 0)
            text = f'         '
            text += f'Angle: {result.solve.angle:3.0f}, '
            text += f'Scale: {result.solve.scale:4.3f}'
            self.app.message.emit(text, 0)
        else:
            message = result.message
            self.app.message.emit(f'Solving error: {message}', 2)
            return False

        isStack = self.ui.checkStackImages.isChecked()
        isAutoSolve = self.ui.checkAutoSolve.isChecked()
        if not isStack or isAutoSolve:
            self.signals.showImage.emit(result.solve.path)

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
        solveTimeout = self.app.mainW.ui.solveTimeout.value()
        searchRadius = self.app.mainW.ui.searchRadius.value()
        self.app.astrometry.solveThreading(fitsPath=imagePath,
                                           radius=searchRadius,
                                           timeout=solveTimeout,
                                           updateFits=updateFits,
                                           )
        self.deviceStat['solve'] = True
        self.app.astrometry.signals.done.connect(self.solveDone)
        self.app.message.emit(f'Solving: [{os.path.basename(imagePath)}]', 0)

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
