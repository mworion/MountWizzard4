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
#
# Licence APL2.0
#
###########################################################
# standard libraries
import os

# external packages
import PyQt5.QtWidgets
import numpy as np
from astropy.io import fits
import sep
from PIL import Image

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

        self.barItem = None
        self.imageItem = None

        self.imageFileName = ''
        self.imageFileNameOld = ''
        self.expTime = 1
        self.binning = 1
        self.image = None
        self.folder = ''
        self.header = None
        self.imageStack = None
        self.numberStack = 0
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

        self.ui.color.setCurrentIndex(config.get('color', 0))
        self.ui.view.setCurrentIndex(config.get('view', 0))
        self.imageFileName = config.get('imageFileName', '')
        self.folder = self.app.mwGlob.get('imageDir', '')
        self.ui.checkStackImages.setChecked(config.get('checkStackImages', False))
        self.ui.showCrosshair.setChecked(config.get('showCrosshair', False))
        self.ui.checkAutoSolve.setChecked(config.get('checkAutoSolve', False))
        self.ui.checkEmbedData.setChecked(config.get('checkEmbedData', False))
        self.setCrosshair()
        return True

    def storeConfig(self):
        """
        :return: True for test purpose
        """
        if 'imageW' not in self.app.config:
            self.app.config['imageW'] = {}
        config = self.app.config['imageW']
        config['winPosX'] = max(self.pos().x(), 0)
        config['winPosY'] = max(self.pos().y(), 0)
        config['height'] = self.height()
        config['width'] = self.width()
        config['color'] = self.ui.color.currentIndex()
        config['view'] = self.ui.view.currentIndex()
        config['imageFileName'] = self.imageFileName
        config['checkStackImages'] = self.ui.checkStackImages.isChecked()
        config['showCrosshair'] = self.ui.showCrosshair.isChecked()
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
        self.ui.color.currentIndexChanged.connect(self.setBarColor)
        self.ui.view.currentIndexChanged.connect(self.setImage)
        self.ui.showCrosshair.clicked.connect(self.setCrosshair)
        self.ui.solve.clicked.connect(self.solveCurrent)
        self.ui.expose.clicked.connect(self.exposeImage)
        self.ui.exposeN.clicked.connect(self.exposeImageN)
        self.ui.checkStackImages.clicked.connect(self.clearStack)
        self.ui.abortImage.clicked.connect(self.abortImage)
        self.ui.abortSolve.clicked.connect(self.abortSolve)
        self.signals.solveImage.connect(self.solveImage)
        self.app.showImage.connect(self.showImage)
        self.app.colorChange.connect(self.colorChange)
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
        self.ui.color.currentIndexChanged.disconnect(self.setBarColor)
        self.ui.view.currentIndexChanged.disconnect(self.setImage)
        self.ui.showCrosshair.clicked.disconnect(self.setCrosshair)
        self.ui.solve.clicked.disconnect(self.solveCurrent)
        self.ui.expose.clicked.disconnect(self.exposeImage)
        self.ui.exposeN.clicked.disconnect(self.exposeImageN)
        self.ui.checkStackImages.clicked.disconnect(self.clearStack)
        self.ui.abortImage.clicked.disconnect(self.abortImage)
        self.ui.abortSolve.clicked.disconnect(self.abortSolve)
        self.signals.solveImage.disconnect(self.solveImage)
        self.app.showImage.disconnect(self.showImage)
        self.app.colorChange.disconnect(self.colorChange)
        super().closeEvent(closeEvent)

    def colorChange(self):
        """
        :return:
        """
        self.setStyleSheet(self.mw4Style)
        self.showCurrent()
        return True

    def updateWindowsStats(self):
        """
        :return: true for test purpose
        """
        if self.deviceStat.get('expose', False):
            self.ui.exposeN.setEnabled(False)
            self.ui.load.setEnabled(False)
            self.ui.abortImage.setEnabled(True)
        elif self.deviceStat.get('exposeN', False):
            self.ui.expose.setEnabled(False)
            self.ui.load.setEnabled(False)
            self.ui.abortImage.setEnabled(True)
        else:
            self.ui.solve.setEnabled(True)
            self.ui.expose.setEnabled(True)
            self.ui.exposeN.setEnabled(True)
            self.ui.load.setEnabled(True)
            self.ui.abortImage.setEnabled(False)

        if self.deviceStat.get('solve', False):
            self.ui.abortSolve.setEnabled(True)
        else:
            self.ui.abortSolve.setEnabled(False)

        if not self.app.deviceStat.get('camera', False):
            self.ui.expose.setEnabled(False)
            self.ui.exposeN.setEnabled(False)

        if not self.app.deviceStat.get('astrometry', False):
            self.ui.solve.setEnabled(False)

        if self.deviceStat.get('expose', False):
            self.changeStyleDynamic(self.ui.expose, 'running', True)
        elif self.deviceStat.get('exposeN', False):
            self.changeStyleDynamic(self.ui.exposeN, 'running', True)
        else:
            self.changeStyleDynamic(self.ui.expose, 'running', False)
            self.changeStyleDynamic(self.ui.exposeN, 'running', False)

        if self.deviceStat.get('solve', False):
            self.changeStyleDynamic(self.ui.solve, 'running', True)
        else:
            self.changeStyleDynamic(self.ui.solve, 'running', False)

        return True

    def selectImage(self):
        """
        :return: success
        """
        val = self.openFile(self, 'Select image file', self.folder,
                            'FITS files (*.fit*)', enableDir=True)
        loadFilePath, name, ext = val
        if not name:
            self.app.message.emit('No image selected', 0)
            return False

        self.ui.imageFileName.setText(name)
        self.imageFileName = loadFilePath
        self.app.message.emit(f'Image selected:      [{name}]', 0)
        self.folder = os.path.dirname(loadFilePath)
        if self.ui.checkAutoSolve.isChecked():
            self.signals.solveImage.emit(self.imageFileName)
        self.app.showImage.emit(self.imageFileName)
        return True

    def setBarColor(self):
        """
        :return:
        """
        cMap = ['CET-L2', 'plasma', 'cividis', 'magma', 'CET-D1A']
        colorMap = cMap[self.ui.color.currentIndex()]
        self.ui.image.setColorMap(colorMap)
        return True

    def setCrosshair(self):
        """
        :return:
        """
        self.ui.image.showCrosshair(self.ui.showCrosshair.isChecked())
        return True

    def setImage(self):
        """
        :return:
        """
        self.setBarColor()
        self.setCrosshair()
        if self.ui.view.currentIndex() == 0:
            self.ui.image.setImage(imageDisp=self.image)
            self.log.debug('Show 0')

        elif self.ui.view.currentIndex() == 1:
            if self.objs is None:
                self.log.debug('Show 1, no SEP data')
                return False

            self.ui.image.setImage(imageDisp=self.image)
            for i in range(len(self.objs)):
                self.ui.image.addEllipse(self.objs['x'][i], self.objs['y'][i],
                                         self.objs['a'][i], self.objs['b'][i],
                                         self.objs['theta'][i])

        elif self.ui.view.currentIndex() == 2:
            if self.objs is None or self.radius is None:
                self.log.debug('Show 2, no SEP radius data')
                return False

            self.ui.image.setImage(imageDisp=self.image)
            draw = self.radius.argsort()[-50:][::-1]
            for i in draw:
                self.ui.image.addEllipse(self.objs['x'][i], self.objs['y'][i],
                                         self.objs['a'][i], self.objs['b'][i],
                                         self.objs['theta'][i])
                self.ui.image.addValueAnnotation(self.objs['x'][i], self.objs['y'][i],
                                                 self.radius[i])
        return True

    def workerPreparePhotometry(self):
        """
        :return:
        """
        bkg = sep.Background(self.image)
        self.bk_back = bkg.back()
        self.bk_rms = bkg.rms()
        image_sub = self.image - bkg
        self.objs = sep.extract(image_sub, 1.5, err=bkg.globalrms,
                                filter_type='conv',
                                minarea=10)
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

    def preparePhotometry(self):
        """
        :return:
        """
        if self.objs is None:
            worker = Worker(self.workerPreparePhotometry)
            worker.signals.finished.connect(self.setImage)
            self.threadPool.start(worker)
        else:
            self.setImage()
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

    def debayerImage(self, image, pattern):
        """
        :param: image:
        :param: pattern:
        :return:
        """
        w = image.shape[0]
        h = image.shape[1]
        if pattern == 'GBRG':
            R = image[1::2, 0::2]
            B = image[0::2, 1::2]
            G0 = image[0::2, 0::2]
            G1 = image[1::2, 1::2]

        elif pattern == 'RGGB':
            R = image[0::2, 0::2]
            B = image[1::2, 1::2]
            G0 = image[0::2, 1::2]
            G1 = image[1::2, 0::2]

        elif pattern == 'GRBG':
            R = image[0::2, 1::2]
            B = image[1::2, 0::2]
            G0 = image[0::2, 0::2]
            G1 = image[1::2, 1::2]

        elif pattern == 'BGGR':
            R = image[1::2, 1::2]
            B = image[0::2, 0::2]
            G0 = image[0::2, 1::2]
            G1 = image[1::2, 0::2]

        else:
            self.log.info('Unknown debayer pattern, keep it')
            return image

        image = 0.2989 * R + 0.5870 * (G0 + G1) / 2 + 0.1140 * B
        image = np.array(Image.fromarray(image).resize((h, w)))
        return image

    def writeHeaderDataToGUI(self, header):
        """
        :param header:
        :return: True for test purpose
        """
        self.guiSetText(self.ui.object, 's', header.get('OBJECT', '').upper())
        ra, dec = getCoordinates(header=header)
        self.guiSetText(self.ui.ra, 'HSTR', ra)
        self.guiSetText(self.ui.dec, 'DSTR', dec)
        self.guiSetText(self.ui.scale, '5.3f', getScale(header=header))
        self.guiSetText(self.ui.rotation, '6.3f', header.get('ANGLE'))
        self.guiSetText(self.ui.ccdTemp, '4.1f', header.get('CCD-TEMP'))
        self.guiSetText(self.ui.expTime, '5.1f', getExposure(header=header))
        self.guiSetText(self.ui.filter, 's', header.get('FILTER'))
        self.guiSetText(self.ui.binX, '1.0f', header.get('XBINNING'))
        self.guiSetText(self.ui.binY, '1.0f', header.get('YBINNING'))
        self.guiSetText(self.ui.sqm, '5.2f', getSQM(header=header))
        return True

    def workerLoadImage(self):
        """
        :return:
        """
        full, short, ext = self.extractNames([self.imageFileName])
        self.ui.imageFileName.setText(short)

        with fits.open(self.imageFileName, mode='update') as fitsHandle:
            self.image = fitsHandle[0].data
            self.header = fitsHandle[0].header

        if self.image is None or len(self.image) == 0:
            self.log.debug('No image data in FITS')
            return False
        if self.header is None:
            self.log.debug('No header data in FITS')
            return False

        self.image = np.flipud(self.image).astype('float32')
        bayerPattern = self.header.get('BAYERPAT', '')
        if bayerPattern:
            self.image = self.debayerImage(self.image, bayerPattern)
            self.log.debug(f'Image has bayer pattern: {bayerPattern}')

        self.updateWindowsStats()
        self.writeHeaderDataToGUI(self.header)
        self.stackImages()
        self.objs = None
        return True

    def showImage(self, imagePath=''):
        """
        :param: imagePath:
        :return:
        """
        if not imagePath:
            return False
        if not os.path.isfile(imagePath):
            return False

        self.imageFileName = imagePath
        worker = Worker(self.workerLoadImage)
        worker.signals.finished.connect(self.preparePhotometry)
        self.threadPool.start(worker)
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
        suc = self.app.camera.expose(imagePath=imagePath,
                                     expTime=self.expTime,
                                     binning=self.binning,
                                     subFrame=subFrame,
                                     fastReadout=fastReadout,
                                     focalLength=focalLength
                                     )
        if not suc:
            text = f'Cannot expose:       [{os.path.basename(imagePath)}]'
            self.abortImage()
            self.app.message.emit(text, 2)
            return False

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
        self.app.showImage.emit(imagePath)
        return True

    def exposeImage(self):
        """
        :return: success
        """
        self.expTime = self.app.camera.expTime
        self.binning = int(self.app.camera.binning)
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
        self.app.showImage.emit(imagePath)
        self.exposeRaw()
        return True

    def exposeImageN(self):
        """
        :return: success
        """
        self.expTime = self.app.camera.expTimeN
        self.binning = int(self.app.camera.binningN)
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
                                           updateFits=updateFits)
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
