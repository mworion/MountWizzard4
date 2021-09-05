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
# written in python3, (c) 2019-2021 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
import os

# external packages
import PyQt5.QtWidgets
from PyQt5.QtCore import QMutex
import numpy as np
from scipy.interpolate import griddata
from scipy.ndimage import uniform_filter
from astropy.io import fits
from astropy import wcs
from astropy.nddata import Cutout2D
from astropy.visualization import MinMaxInterval
from astropy.visualization import AsinhStretch
from astropy.visualization import imshow_norm
from matplotlib.patches import Ellipse
import matplotlib.pyplot as plt
from colour_demosaicing import demosaicing_CFA_Bayer_bilinear
import sep

# local import
from mountcontrol.convert import convertToDMS, convertToHMS
from base.fitsHeader import getCoordinates, getSQM, getExposure, getScale
from gui.utilities import toolsQtWidget
from gui.widgets import image_ui
from base.tpool import Worker


class ImageWindowSignals(PyQt5.QtCore.QObject):
    """
    """
    __all__ = ['ImageWindowSignals']
    solveImage = PyQt5.QtCore.pyqtSignal(object)


class ImageWindow(toolsQtWidget.MWidget):
    """
    """
    __all__ = ['ImageWindow']

    def __init__(self, app):
        super().__init__()

        self.app = app
        self.threadPool = app.threadPool
        self.ui = image_ui.Ui_ImageDialog()
        self.ui.setupUi(self)
        self.signals = ImageWindowSignals()

        self.imageFileName = ''
        self.imageFileNameOld = ''
        self.expTime = 1
        self.binning = 1
        self.image = None
        self.folder = ''
        self.header = None
        self.imageStack = None
        self.numberStack = 0
        self.colorMap = None
        self.stretch = None
        self.objs = None
        self.bk_back = None
        self.bk_rms = None
        self.flux = None
        self.radius = None

        self.deviceStat = {
            'expose': False,
            'exposeN': False,
            'solve': False,
        }
        self.view = {0: 'Image Raw',
                     1: 'Image with Sources',
                     2: 'Photometry: HFD value',
                     3: 'Photometry: Eccentricity',
                     4: 'Photometry: Background level',
                     5: 'Photometry: Background noise',
                     6: 'Photometry: Flux',
                     7: 'Photometry: HFD Contour',
                     }

        self.colorMaps = {'Grey': 'gray',
                          'Cool': 'plasma',
                          'Rainbow': 'rainbow',
                          'Spectral': 'nipy_spectral',
                          }

        self.stretchValues = {'Low XX': 0.2,
                              'Low X': 0.1,
                              'Low': 0.05,
                              'Mid': 0.025,
                              'High': 0.005,
                              'Super ': 0.0025,
                              'Super X': 0.001,
                              'Super XX': 0.0005,
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

        self.app.update1s.connect(self.updateWindowsStats)

    def initConfig(self):
        """
        :return: True for test purpose
        """
        if 'imageW' not in self.app.config:
            self.app.config['imageW'] = {}
        config = self.app.config['imageW']
        height = config.get('height', 600)
        width = config.get('width', 800)
        self.resize(width, height)
        x = config.get('winPosX', 0)
        y = config.get('winPosY', 0)
        if x > self.screenSizeX - width:
            x = 0
        if y > self.screenSizeY - height:
            y = 0
        if x != 0 and y != 0:
            self.move(x, y)

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
        showWindow prepares all data for showing the window, plots the image and
        show it. afterwards all necessary signal / slot connections will be
        established.

        :return: true for test purpose
        """
        self.ui.load.clicked.connect(self.selectImage)
        self.ui.color.currentIndexChanged.connect(self.preparePlot)
        self.ui.stretch.currentIndexChanged.connect(self.preparePlot)
        self.ui.zoom.currentIndexChanged.connect(self.showCurrent)
        self.ui.view.currentIndexChanged.connect(self.preparePlot)
        self.ui.checkUseWCS.clicked.connect(self.preparePlot)
        self.ui.checkShowGrid.clicked.connect(self.preparePlot)
        self.ui.checkShowCrosshair.clicked.connect(self.preparePlot)
        self.ui.solve.clicked.connect(self.solveCurrent)
        self.ui.expose.clicked.connect(self.exposeImage)
        self.ui.exposeN.clicked.connect(self.exposeImageN)
        self.ui.checkStackImages.clicked.connect(self.clearStack)
        self.ui.abortImage.clicked.connect(self.abortImage)
        self.ui.abortSolve.clicked.connect(self.abortSolve)
        self.signals.solveImage.connect(self.solveImage)
        self.app.showImage.connect(self.showImage)
        self.show()
        self.showCurrent()
        return True

    def closeEvent(self, closeEvent):
        """
        closeEvent overlays the window close event of qt. first it stores all
        persistent data for the windows and its functions, than removes al signal
        / slot connections removes the matplotlib embedding and finally calls the
        parent calls for handling the framework close event.

        :param closeEvent:
        :return: True for test purpose
        """
        self.storeConfig()
        self.ui.load.clicked.disconnect(self.selectImage)
        self.ui.color.currentIndexChanged.disconnect(self.preparePlot)
        self.ui.stretch.currentIndexChanged.disconnect(self.preparePlot)
        self.ui.zoom.currentIndexChanged.disconnect(self.showCurrent)
        self.ui.view.currentIndexChanged.disconnect(self.preparePlot)
        self.ui.checkUseWCS.clicked.disconnect(self.preparePlot)
        self.ui.checkShowGrid.clicked.disconnect(self.preparePlot)
        self.ui.checkShowCrosshair.clicked.disconnect(self.preparePlot)
        self.ui.solve.clicked.disconnect(self.solveCurrent)
        self.ui.expose.clicked.disconnect(self.exposeImage)
        self.ui.exposeN.clicked.disconnect(self.exposeImageN)
        self.ui.checkStackImages.clicked.disconnect(self.clearStack)
        self.ui.abortImage.clicked.disconnect(self.abortImage)
        self.ui.abortSolve.clicked.disconnect(self.abortSolve)
        self.signals.solveImage.disconnect(self.solveImage)
        self.app.showImage.disconnect(self.showImage)
        plt.close(self.imageMat.figure)
        super().closeEvent(closeEvent)

    def setupDropDownGui(self):
        """
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
        for menuNumber in self.view:
            self.ui.view.addItem(self.view[menuNumber])

        return True

    def updateWindowsStats(self):
        """
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
        :return: success
        """
        val = self.openFile(self, 'Select image file', self.folder,
                            'FITS files (*.fit*)', enableDir=True)
        loadFilePath, name, ext = val
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
        setupDistorted tries to setup all necessary context for displaying the
        image with wcs distorted coordinates.

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
        :return: True for test purpose
        """
        self.fig.clf()
        self.axe = self.fig.add_subplot(1, 1, 1,
                                        facecolor=self.M_GREY_LIGHT)

        self.fig.subplots_adjust(bottom=0.1, top=0.9, left=0.1, right=0.85)
        self.axeCB = self.fig.add_axes([0.88, 0.1, 0.02, 0.8])
        self.axe.spines['bottom'].set_color(self.M_BLUE)
        self.axe.spines['top'].set_color(self.M_BLUE)
        self.axe.spines['left'].set_color(self.M_BLUE)
        self.axe.spines['right'].set_color(self.M_BLUE)

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

        self.axe.tick_params(axis='x', which='major',
                             colors=self.M_BLUE, labelsize=12)
        self.axe.tick_params(axis='y', which='major',
                             colors=self.M_BLUE, labelsize=12)

        valueX, _ = np.linspace(-midX, midX, num=number, retstep=True)
        textX = list((str(int(x)) for x in valueX))
        ticksX = list((x + midX for x in valueX))
        self.axe.set_xticks(ticksX)
        self.axe.set_xticklabels(textX)

        valueY, _ = np.linspace(-midY, midY, num=number, retstep=True)
        textY = list((str(int(x)) for x in valueY))
        ticksY = list((x + midY for x in valueY))
        self.axe.set_yticks(ticksY)
        self.axe.set_yticklabels(textY)

        self.axe.set_xlabel(xlabel='Pixel', color=self.M_BLUE,
                            fontsize=12, fontweight='bold')
        self.axe.set_ylabel(ylabel='Pixel', color=self.M_BLUE,
                            fontsize=12, fontweight='bold')

        self.axe.set_xlim(0, sizeX)
        self.axe.set_ylim(0, sizeY)
        return True

    def colorImage(self):
        """
        :return: True
        """
        fallback = list(self.colorMaps.keys())[0]
        self.colorMap = self.colorMaps.get(self.ui.color.currentText(), fallback)
        return True

    def stretchImage(self):
        """
        :return: True
        """
        fallback = list(self.stretchValues.keys())[0]
        value = self.stretchValues.get(self.ui.stretch.currentText(),
                                       self.stretchValues[fallback])
        self.stretch = AsinhStretch(a=value)
        return True

    def imagePlot(self):
        """
        :return:
        """
        if self.objs is not None:
            imageDisp = self.image - self.bk_back

        else:
            imageDisp = self.image

        if self.ui.view.currentIndex() in [0, 1, 2, 3]:
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
                colorbar.set_label('Value [pixel value]',
                                   color=self.M_BLUE,
                                   fontsize=12)
                yTicks = plt.getp(colorbar.ax.axes, 'yticklabels')
                plt.setp(yTicks, color=self.M_BLUE, fontweight='bold')

        if self.ui.view.currentIndex() == 1 and self.objs is not None:
            for i in range(len(self.objs)):
                e = Ellipse(xy=(self.objs['x'][i], self.objs['y'][i]),
                            width=6 * self.objs['a'][i],
                            height=6 * self.objs['b'][i],
                            angle=self.objs['theta'][i] * 180. / np.pi)
                e.set_facecolor('none')
                e.set_edgecolor(self.M_BLUE)
                self.axe.add_artist(e)

        if self.ui.view.currentIndex() == 2 and self.radius is not None:
            draw = self.radius.argsort()[-50:][::-1]
            for i in draw:
                e = Ellipse(xy=(self.objs['x'][i], self.objs['y'][i]),
                            width=6 * self.objs['a'][i],
                            height=6 * self.objs['b'][i],
                            angle=self.objs['theta'][i] * 180.0 / np.pi)
                e.set_facecolor('none')
                e.set_edgecolor(self.M_BLUE)
                self.axe.add_artist(e)
                posX = self.objs['x'][i] + self.objs['a'][i] + 5
                posY = self.objs['b'][i] + self.objs['y'][i] + 5
                self.axe.annotate(f'{self.radius[i]:2.1f}',
                                  xy=(posX, posY),
                                  color=self.M_BLUE,
                                  fontweight='bold')

        if self.ui.view.currentIndex() == 3 and self.objs is not None:
            a = self.objs['a']
            b = self.objs['b']
            eccentricity = np.sqrt(1 - b ** 2 / a ** 2)
            area = 5
            scatter = self.axe.scatter(self.objs['x'], self.objs['y'],
                                       c=eccentricity, s=area, cmap='gnuplot2')

            colorbar = self.fig.colorbar(scatter, cax=self.axeCB)
            colorbar.set_label('Eccentricity []', color=self.M_BLUE,
                               fontsize=12)
            yTicks = plt.getp(colorbar.ax.axes, 'yticklabels')
            plt.setp(yTicks, color=self.M_BLUE, fontweight='bold')

        if self.ui.view.currentIndex() == 4 and self.bk_back is not None:
            img = imshow_norm(self.bk_back,
                              ax=self.axe,
                              origin='lower',
                              interval=MinMaxInterval(),
                              stretch=self.stretch,
                              cmap=self.colorMap,
                              aspect='auto')
            if self.axeCB:
                colorbar = self.fig.colorbar(img[0], cax=self.axeCB)
                colorbar.set_label('Background level [adu]',
                                   color=self.M_BLUE,
                                   fontsize=12)
                yTicks = plt.getp(colorbar.ax.axes, 'yticklabels')
                plt.setp(yTicks, color=self.M_BLUE, fontweight='bold')

        if self.ui.view.currentIndex() == 5 and self.bk_rms is not None:
            img = imshow_norm(self.bk_rms,
                              ax=self.axe,
                              origin='lower',
                              interval=MinMaxInterval(),
                              stretch=self.stretch,
                              cmap=self.colorMap,
                              aspect='auto')
            if self.axeCB:
                colorbar = self.fig.colorbar(img[0], cax=self.axeCB)
                colorbar.set_label('Background noise [adu]',
                                   color=self.M_BLUE,
                                   fontsize=12)
                yTicks = plt.getp(colorbar.ax.axes, 'yticklabels')
                plt.setp(yTicks, color=self.M_BLUE,
                         fontweight='bold')

        if self.ui.view.currentIndex() == 6 and self.flux is not None:
            flux = np.log(self.flux)
            area = 3 * flux
            scatter = self.axe.scatter(self.objs['x'], self.objs['y'],
                                       c=flux, s=area, cmap=self.colorMap)

            colorbar = self.fig.colorbar(scatter, cax=self.axeCB)
            colorbar.set_label('Flux [log(x)]', color=self.M_BLUE, fontsize=12)
            yTicks = plt.getp(colorbar.ax.axes, 'yticklabels')
            plt.setp(yTicks, color=self.M_BLUE, fontweight='bold')

        if self.ui.view.currentIndex() == 7 and self.radius is not None and \
                self.objs is not None:

            x = self.objs['x']
            y = self.objs['y']
            z = self.radius
            width = imageDisp.shape[1]
            height = imageDisp.shape[0]
            X, Y = np.meshgrid(range(0, width, int(width / 250)),
                               range(0, height, int(height / 250)))
            Z = griddata((x, y), z, (X, Y), method='linear', fill_value=np.mean(z))
            Z = uniform_filter(Z, size=25)
            self.axe.contourf(X, Y, Z, 20)

            if self.axeCB:
                self.axeCB.axis('off')

        self.axe.figure.canvas.draw()
        return True

    def writeHeaderDataToGUI(self):
        """
        :return: True for test purpose
        """
        name = self.header.get('OBJECT', '').upper()
        self.ui.object.setText(f'{name}')

        ra, dec = getCoordinates(header=self.header)

        self.ui.ra.setText(f'{self.formatHstrToText(ra)}')
        self.ui.dec.setText(f'{self.formatDstrToText(dec)}')

        scale = getScale(header=self.header)
        rotation = self.header.get('ANGLE', 0)
        self.ui.scale.setText(f'{scale:5.3f}')
        self.ui.rotation.setText(f'{rotation:6.3f}')

        value = self.header.get('CCD-TEMP', 0)
        self.guiSetText(self.ui.ccdTemp, '4.1f', value)

        value = getExposure(header=self.header)
        self.guiSetText(self.ui.expTime, '5.1f', value)

        value = self.header.get('FILTER', 0)
        value = f'{value}'
        self.guiSetText(self.ui.filter, 's', value)

        value = self.header.get('XBINNING', 0)
        self.guiSetText(self.ui.binX, '1.0f', value)
        value = self.header.get('YBINNING', 0)
        self.guiSetText(self.ui.binY, '1.0f', value)

        value = getSQM(header=self.header)
        self.guiSetText(self.ui.sqm, '5.2f', value)

        flipped = bool(self.header.get('FLIPPED', False))
        self.ui.isFlipped.setEnabled(flipped)

        return True

    def workerPreparePlot(self):
        """
        :return:
        """
        self.updateWindowsStats()
        if 'CTYPE1' in self.header:
            wcsObject = wcs.WCS(self.header, relax=True)
            hasCelestial = wcsObject.has_celestial
            hasDistortion = wcsObject.has_distortion

        else:
            hasCelestial = False
            hasDistortion = False

        self.ui.hasDistortion.setEnabled(hasDistortion)
        self.ui.checkUseWCS.setEnabled(hasDistortion)
        self.ui.hasWCS.setEnabled(hasCelestial)

        canWCS = self.ui.view.currentIndex() in [0, 1, 2]
        useWCS = self.ui.checkUseWCS.isChecked()

        if hasDistortion and useWCS and canWCS:
            self.setupDistorted()
        else:
            self.setupNormal()

        self.writeHeaderDataToGUI()
        self.stretchImage()
        self.colorImage()
        self.imagePlot()
        return True

    def preparePlot(self):
        """
        :return:
        """
        worker = Worker(self.workerPreparePlot)
        self.threadPool.start(worker)
        return True

    def workerPhotometry(self):
        """
        :return:
        """
        bkg = sep.Background(self.image)
        self.bk_back = bkg.back()
        self.bk_rms = bkg.rms()
        image_sub = self.image - bkg
        self.objs = sep.extract(image_sub, 1.5, err=bkg.globalrms)
        self.flux, _, _ = sep.sum_circle(image_sub,
                                         self.objs['x'],
                                         self.objs['y'],
                                         3.0,
                                         err=bkg.globalrms,
                                         gain=1.0)
        self.radius, _ = sep.flux_radius(image_sub,
                                         self.objs['x'],
                                         self.objs['y'],
                                         6.0 * self.objs['a'],
                                         0.5,
                                         normflux=self.flux,
                                         subpix=5)
        return True

    def prepareImageForPhotometry(self):
        """
        :return:
        """
        if not self.objs:
            worker = Worker(self.workerPhotometry)
            worker.signals.finished.connect(self.preparePlot)
            self.threadPool.start(worker)
        else:
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

        if self.imageStack is None:
            self.imageStack = self.image
            self.numberStack = 1
        else:
            self.imageStack = np.add(self.imageStack, self.image)
            self.numberStack += 1

        self.image = self.imageStack / self.numberStack
        self.ui.numberStacks.setText(f'mean of: {self.numberStack:4.0f}')
        return True

    def clearStack(self):
        """
        :return:
        """
        if not self.ui.checkStackImages.isChecked():
            self.imageStack = None
            self.numberStack = 0
            self.ui.numberStacks.setText('single')
            return False

        return True

    def zoomImage(self):
        """
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
        tho idea of processing the image data until it is shown on screen is
        to split the pipeline in several atomic steps, which follow each other.
        each step is calling the next one and depending which user interaction is
        done and how the use case for changing the view is the entrance of the
        pipeline is chosen adequately.

        so we have step 1 loading data and processing if to final monochrome and
        sized format
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
            
        if self.image is None or self.image == []:
            return False
        if self.header is None:
            return False

        self.image = self.image.astype('float32')

        if 'BAYERPAT' in self.header:
            self.image = demosaicing_CFA_Bayer_bilinear(self.image)
            self.image = np.dot(self.image, [0.2989, 0.5870, 0.1140])

        # correct faulty headers, because some imaging programs did not
        # interpret the Keywords in the right manner (SGPro)
        if self.header.get('CTYPE1', '').endswith('DEF'):
            self.header['CTYPE1'] = self.header['CTYPE1'].replace('DEF', 'TAN')

        if self.header.get('CTYPE2', '').endswith('DEF'):
            self.header['CTYPE2'] = self.header['CTYPE2'].replace('DEF', 'TAN')

        self.zoomImage()
        self.stackImages()
        self.objs = None
        self.prepareImageForPhotometry()
        return True

    def showCurrent(self):
        """
        :return: true for test purpose
        """
        self.showImage(self.imageFileName)
        return True

    def exposeRaw(self):
        """
        :return: True for test purpose
        """
        subFrame = self.app.camera.subFrame
        fastReadout = self.app.camera.checkFastDownload

        time = self.app.mount.obsSite.timeJD.utc_strftime('%Y-%m-%d-%H-%M-%S')
        fileName = time + '-exposure.fits'
        imagePath = self.app.mwGlob['imageDir'] + '/' + fileName
        focalLength = self.app.telescope.focalLength

        self.imageFileNameOld = self.imageFileName
        self.app.camera.expose(imagePath=imagePath,
                               expTime=self.expTime,
                               binning=self.binning,
                               subFrame=subFrame,
                               fastReadout=fastReadout,
                               focalLength=focalLength
                               )

        text = f'Exposing:            [{os.path.basename(imagePath)}]'
        self.app.message.emit(text, 0)
        text = f'Duration:{self.expTime:3.0f}s  '
        text += f'Bin:{self.binning:1.0f}  Sub:{subFrame:3.0f}%'
        self.app.message.emit(f'                     {text}', 0)

        return True

    def exposeImageDone(self, imagePath=''):
        """
        :param imagePath:
        :return: True for test purpose
        """
        self.deviceStat['expose'] = False
        self.app.camera.signals.saved.disconnect(self.exposeImageDone)
        text = f'Exposed:             [{os.path.basename(imagePath)}]'
        self.app.message.emit(text, 0)

        if self.ui.checkAutoSolve.isChecked():
            self.signals.solveImage.emit(imagePath)
        else:
            self.app.showImage.emit(imagePath)

        return True

    def exposeImage(self):
        """
        :return: success
        """
        self.expTime = self.app.camera.expTime
        self.binning = self.app.camera.binning
        self.imageStack = None
        self.deviceStat['expose'] = True
        self.ui.checkStackImages.setChecked(False)
        self.app.camera.signals.saved.connect(self.exposeImageDone)
        self.ui.numberStacks.setText('...')
        self.exposeRaw()
        return True

    def exposeImageNDone(self, imagePath=''):
        """
        :param imagePath:
        :return: True for test purpose
        """
        text = f'Exposed:             [{os.path.basename(imagePath)}]'
        self.app.message.emit(text, 0)

        if self.ui.checkAutoSolve.isChecked():
            self.signals.solveImage.emit(imagePath)
        else:
            self.app.showImage.emit(imagePath)

        self.exposeRaw()
        return True

    def exposeImageN(self):
        """
        :return: success
        """
        self.expTime = self.app.camera.expTimeN
        self.binning = self.app.camera.binningN
        self.imageStack = None
        self.deviceStat['exposeN'] = True
        self.app.camera.signals.saved.connect(self.exposeImageNDone)
        self.ui.numberStacks.setText('...')
        self.exposeRaw()
        return True

    def abortImage(self):
        """
        :return: True for test purpose
        """
        self.app.camera.abort()
        # for disconnection we have to split which slots were connected to
        # disable the right ones
        if self.deviceStat['expose']:
            self.app.camera.signals.saved.disconnect(self.exposeImageDone)

        if self.deviceStat['exposeN']:
            self.app.camera.signals.saved.disconnect(self.exposeImageNDone)

        # last image file was not stored, so getting last valid it back
        self.imageFileName = self.imageFileNameOld
        self.deviceStat['expose'] = False
        self.deviceStat['exposeN'] = False
        self.app.message.emit('Exposing aborted', 2)
        return True

    def solveDone(self, result=None):
        """
        :param result: result (named tuple)
        :return: success
        """
        self.deviceStat['solve'] = False
        self.app.astrometry.signals.done.disconnect(self.solveDone)

        if not result:
            self.app.message.emit('Solving error, result missing', 2)
            return False

        if result['success']:
            text = 'Solved :             '
            text += f'RA: {convertToHMS(result["raJ2000S"])} '
            text += f'({result["raJ2000S"].hours:4.3f}), '
            text += f'DEC: {convertToDMS(result["decJ2000S"])} '
            text += f'({result["decJ2000S"].degrees:4.3f}), '
            self.app.message.emit(text, 0)
            text = '                     '
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
        :param imagePath:
        :return:
        """
        if not imagePath:
            return False
        if not os.path.isfile(imagePath):
            return False

        updateFits = self.ui.checkEmbedData.isChecked()
        self.app.astrometry.signals.done.connect(self.solveDone)
        self.app.astrometry.solveThreading(fitsPath=imagePath,
                                           updateFits=updateFits,
                                           )
        self.deviceStat['solve'] = True
        text = f'Solving:             [{os.path.basename(imagePath)}]'
        self.app.message.emit(text, 0)
        return True

    def solveCurrent(self):
        """
        :return: true for test purpose
        """
        self.signals.solveImage.emit(self.imageFileName)
        return True

    def abortSolve(self):
        """
        :return: success
        """
        suc = self.app.astrometry.abort()
        return suc
