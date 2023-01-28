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
# written in python3, (c) 2019-2023 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import os

# external packages
import pyqtgraph as pg
from PyQt5.QtCore import pyqtSignal, QObject, Qt
from PyQt5.QtGui import QFont, QGuiApplication, QCursor
from skyfield.api import Angle

# local import
from mountcontrol.convert import convertToDMS, convertToHMS
from base.fitsHeader import getCoordinates, getSQM, getExposure, getScale
from gui.utilities import toolsQtWidget
from gui.utilities.slewInterface import SlewInterface
from gui.widgets import image_ui
from logic.file.fileHandler import FileHandler
from logic.photometry.photometry import Photometry
from gui.extWindows.image.imageTabs import ImageTabs


class ImageWindowSignals(QObject):
    """
    """
    __all__ = ['ImageWindowSignals']
    solveImage = pyqtSignal(object)


class ImageWindow(toolsQtWidget.MWidget, ImageTabs, SlewInterface):
    """
    """
    __all__ = ['ImageWindow']

    TILT = {'none': 5,
            'almost none': 10,
            'mild': 15,
            'moderate': 20,
            'severe': 30,
            'extreme': 1000}

    def __init__(self, app):
        super().__init__()

        self.app = app
        self.msg = app.msg
        self.threadPool = app.threadPool
        self.ui = image_ui.Ui_ImageDialog()
        self.ui.setupUi(self)
        self.signals = ImageWindowSignals()
        self.photometry = Photometry(app=app)
        self.fileHandler = FileHandler(app=app)

        self.barItem = None
        self.imageItem = None
        self.imageSourceRange = None
        self.imageFileName = ''
        self.imageFileNameOld = ''
        self.expTime = 1
        self.binning = 1
        self.folder = ''
        self.result = None
        self.pen = pg.mkPen(color=self.M_BLUE, width=2)
        self.penPink = pg.mkPen(color=self.M_PINK + '80', width=5)
        self.fontText = QFont(self.window().font().family(), 16)
        self.fontAnno = QFont(self.window().font().family(), 10, italic=True)
        self.fontText.setBold(True)

        self.deviceStat = {
            'expose': False,
            'exposeN': False,
            'solve': False,
        }

    def initConfig(self):
        """
        :return: True for test purpose
        """
        if 'imageW' not in self.app.config:
            self.app.config['imageW'] = {}
        config = self.app.config['imageW']

        self.positionWindow(config)
        self.setTabAndIndex(self.ui.tabImage, config, 'orderMain')
        self.ui.color.setCurrentIndex(config.get('color', 0))
        self.ui.snTarget.setCurrentIndex(config.get('snTarget', 0))
        self.ui.tabImage.setCurrentIndex(config.get('tabImage', 0))
        self.imageFileName = config.get('imageFileName', '')
        self.folder = self.app.mwGlob.get('imageDir', '')
        self.ui.showCrosshair.setChecked(config.get('showCrosshair', False))
        self.ui.aspectLocked.setChecked(config.get('aspectLocked', False))
        self.ui.autoSolve.setChecked(config.get('autoSolve', False))
        self.ui.embedData.setChecked(config.get('embedData', False))
        self.ui.photometryGroup.setChecked(config.get('photometryGroup', False))
        self.ui.isoLayer.setChecked(config.get('isoLayer', False))
        self.ui.flipH.setChecked(config.get('flipH', False))
        self.ui.flipV.setChecked(config.get('flipV', False))
        self.ui.showValues.setChecked(config.get('showValues', False))
        self.ui.offsetTiltAngle.setValue(config.get('offsetTiltAngle', 0))
        self.ui.timeTagImage.setChecked(config.get('timeTagImage', True))
        isMovable = self.app.config['mainW'].get('tabsMovable', False)
        self.enableTabsMovable(isMovable)
        self.setCrosshair()
        return True

    def storeConfig(self):
        """
        :return: True for test purpose
        """
        config = self.app.config
        if 'imageW' not in config:
            config['imageW'] = {}
        else:
            config['imageW'].clear()
        config = config['imageW']

        config['winPosX'] = max(self.pos().x(), 0)
        config['winPosY'] = max(self.pos().y(), 0)
        config['height'] = self.height()
        config['width'] = self.width()
        self.getTabAndIndex(self.ui.tabImage, config, 'tabMain')
        config['color'] = self.ui.color.currentIndex()
        config['snTarget'] = self.ui.snTarget.currentIndex()
        config['tabImage'] = self.ui.tabImage.currentIndex()
        config['imageFileName'] = self.imageFileName
        config['showCrosshair'] = self.ui.showCrosshair.isChecked()
        config['aspectLocked'] = self.ui.aspectLocked.isChecked()
        config['autoSolve'] = self.ui.autoSolve.isChecked()
        config['embedData'] = self.ui.embedData.isChecked()
        config['photometryGroup'] = self.ui.photometryGroup.isChecked()
        config['isoLayer'] = self.ui.isoLayer.isChecked()
        config['flipH'] = self.ui.flipH.isChecked()
        config['flipV'] = self.ui.flipV.isChecked()
        config['showValues'] = self.ui.showValues.isChecked()
        config['offsetTiltAngle'] = self.ui.offsetTiltAngle.value()
        config['timeTagImage'] = self.ui.timeTagImage.isChecked()
        return True

    def enableTabsMovable(self, isMovable):
        """
        :param isMovable:
        :return:
        """
        self.ui.tabImage.setMovable(isMovable)
        return True

    def showWindow(self):
        """
        showWindow prepares all data for showing the window, plots the image and
        show it. afterwards all necessary signal / slot connections will be
        established.

        :return: true for test purpose
        """
        self.fileHandler.signals.imageLoaded.connect(self.showTabImage)
        self.fileHandler.signals.imageLoaded.connect(self.processPhotometry)
        self.photometry.signals.sepFinished.connect(self.resultPhotometry)
        self.photometry.signals.hfr.connect(self.showTabHFR)
        self.photometry.signals.hfrSquare.connect(self.showTabTiltSquare)
        self.photometry.signals.hfrTriangle.connect(self.showTabTiltTriangle)
        self.photometry.signals.roundness.connect(self.showTabRoundness)
        self.photometry.signals.aberration.connect(self.showTabAberrationInspect)
        self.photometry.signals.aberration.connect(self.showTabImageSources)
        self.photometry.signals.background.connect(self.showTabBackground)
        self.photometry.signals.backgroundRMS.connect(self.showTabBackgroundRMS)

        self.app.update1s.connect(self.updateWindowsStats)
        self.ui.load.clicked.connect(self.selectImage)
        self.ui.color.currentIndexChanged.connect(self.setBarColor)
        self.ui.showCrosshair.clicked.connect(self.setCrosshair)
        self.ui.flipH.clicked.connect(self.showCurrent)
        self.ui.flipV.clicked.connect(self.showCurrent)
        self.ui.aspectLocked.clicked.connect(self.setAspectLocked)
        self.ui.photometryGroup.clicked.connect(self.processPhotometry)
        self.ui.isoLayer.clicked.connect(self.showTabHFR)
        self.ui.isoLayer.clicked.connect(self.showTabRoundness)
        self.ui.showValues.clicked.connect(self.showTabImageSources)
        self.ui.snTarget.currentIndexChanged.connect(self.processPhotometry)
        self.ui.solve.clicked.connect(self.solveCurrent)
        self.ui.expose.clicked.connect(self.exposeImage)
        self.ui.exposeN.clicked.connect(self.exposeImageN)
        self.ui.abortExpose.clicked.connect(self.abortExpose)
        self.ui.abortSolve.clicked.connect(self.abortSolve)
        self.ui.slewCenter.clicked.connect(self.slewCenter)
        self.ui.image.barItem.sigLevelsChangeFinished.connect(self.copyLevels)
        self.ui.offsetTiltAngle.valueChanged.connect(self.showTabTiltTriangle)
        self.signals.solveImage.connect(self.solveImage)
        self.app.colorChange.connect(self.colorChange)
        self.app.showImage.connect(self.showImage)
        self.app.operationRunning.connect(self.operationMode)
        self.app.tabsMovable.connect(self.enableTabsMovable)

        self.wIcon(self.ui.load, 'load')
        self.operationMode(self.app.statusOperationRunning)
        self.ui.image.p[0].getViewBox().callbackMDC = self.mouseDoubleClick
        self.ui.image.p[0].scene().sigMouseMoved.connect(self.mouseMoved)
        self.showCurrent()
        self.setAspectLocked()
        self.clearGui()
        self.show()
        return True

    def closeEvent(self, closeEvent):
        """
        :param closeEvent:
        :return: True for test purpose
        """
        self.storeConfig()
        super().closeEvent(closeEvent)

    def colorChange(self):
        """
        :return:
        """
        self.setStyleSheet(self.mw4Style)
        self.ui.image.colorChange()
        self.pen = pg.mkPen(color=self.M_BLUE)
        self.showCurrent()
        return True

    def clearGui(self):
        """
        :return:
        """
        self.ui.medianHFR.setText('')
        self.ui.hfrPercentile.setText('')
        self.ui.numberStars.setText('')
        self.ui.aspectRatioPercentile.setText('')
        tab = self.ui.tabImage
        tabIndex = self.getTabIndex(tab, 'Image')
        for i in range(0, self.ui.tabImage.count()):
            if i == tabIndex:
                continue
            self.ui.tabImage.setTabEnabled(i, False)
        return True

    def operationMode(self, status):
        """
        :param status:
        :return:
        """
        if status == 0:
            self.ui.groupImageActions.setEnabled(True)
        elif status != 6:
            self.ui.groupImageActions.setEnabled(False)
        return True

    def updateWindowsStats(self):
        """
        :return: true for test purpose
        """
        if self.deviceStat.get('expose', False):
            self.ui.exposeN.setEnabled(False)
            self.ui.load.setEnabled(False)
            self.ui.abortExpose.setEnabled(True)
        elif self.deviceStat.get('exposeN', False):
            self.ui.expose.setEnabled(False)
            self.ui.load.setEnabled(False)
            self.ui.abortExpose.setEnabled(True)
        else:
            self.ui.expose.setEnabled(True)
            self.ui.exposeN.setEnabled(True)
            self.ui.load.setEnabled(True)
            self.ui.abortExpose.setEnabled(False)

        isPlateSolve = bool(self.app.deviceStat.get('plateSolve', False))
        isSolving = bool(self.deviceStat.get('solve', False))
        isImage = self.imageFileName != ''

        self.ui.solve.setEnabled(isPlateSolve and isImage)
        self.ui.abortSolve.setEnabled(isPlateSolve and isImage and isSolving)

        if not self.app.deviceStat.get('camera', False):
            self.ui.expose.setEnabled(False)
            self.ui.exposeN.setEnabled(False)

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
        val = self.openFile(
            self, 'Select image file', self.folder,
            'All (*.fit* *.xisf);; FITS files (*.fit*);;XISF files (*.xisf)',
            enableDir=True)
        loadFilePath, name, ext = val
        if not name:
            self.msg.emit(0, 'Image', 'Loading', 'No image selected')
            return False

        self.imageFileName = loadFilePath
        self.msg.emit(0, 'Image', 'Image selected', f'{name}{ext}')
        self.folder = os.path.dirname(loadFilePath)
        if self.ui.autoSolve.isChecked():
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
        self.ui.imageSource.setColorMap(colorMap)
        self.ui.background.setColorMap(colorMap)
        self.ui.backgroundRMS.setColorMap(colorMap)
        self.ui.hfr.setColorMap(colorMap)
        self.ui.tiltSquare.setColorMap(colorMap)
        self.ui.tiltTriangle.setColorMap(colorMap)
        self.ui.roundness.setColorMap(colorMap)
        self.ui.aberration.setColorMap(colorMap)
        return True

    def copyLevels(self):
        """
        :return:
        """
        level = self.ui.image.barItem.levels()
        self.ui.tiltSquare.barItem.setLevels(level)
        self.ui.tiltTriangle.barItem.setLevels(level)
        self.ui.aberration.barItem.setLevels(level)
        self.ui.imageSource.barItem.setLevels(level)
        return True

    def setCrosshair(self):
        """
        :return:
        """
        self.ui.image.showCrosshair(self.ui.showCrosshair.isChecked())
        return True

    def setAspectLocked(self):
        """
        :return:
        """
        isLocked = self.ui.aspectLocked.isChecked()
        self.ui.image.p[0].setAspectLocked(isLocked)
        self.ui.imageSource.p[0].setAspectLocked(isLocked)
        self.ui.tiltSquare.p[0].setAspectLocked(isLocked)
        self.ui.tiltTriangle.p[0].setAspectLocked(isLocked)
        self.ui.background.p[0].setAspectLocked(isLocked)
        self.ui.backgroundRMS.p[0].setAspectLocked(isLocked)
        self.ui.hfr.p[0].setAspectLocked(isLocked)
        self.ui.roundness.p[0].setAspectLocked(isLocked)
        return True

    def getImageSourceRange(self):
        """
        :return:
        """
        vb = self.ui.imageSource.p[0].getViewBox()
        self.imageSourceRange = vb.viewRect()
        return True

    @staticmethod
    def clearImageTab(imageWidget):
        """
        :param imageWidget:
        :return:
        """
        imageWidget.p[0].clear()
        imageWidget.p[0].showAxes(False, showValues=False)
        imageWidget.p[0].setMouseEnabled(x=False, y=False)
        imageWidget.barItem.setVisible(False)
        return True

    def writeHeaderDataToGUI(self, header):
        """
        :param header:
        :return: True for test purpose
        """
        self.guiSetText(self.ui.object, 's', header.get('OBJECT', '').upper())
        ra, dec = getCoordinates(header=header)
        self.guiSetText(self.ui.ra, 'HSTR', ra)
        self.guiSetText(self.ui.raFloat, '2.5f', ra.hours)
        self.guiSetText(self.ui.dec, 'DSTR', dec)
        self.guiSetText(self.ui.decFloat, '2.5f', dec.degrees)
        self.guiSetText(self.ui.scale, '5.3f', getScale(header=header))
        self.guiSetText(self.ui.rotation, '6.2f', header.get('ANGLE'))
        self.guiSetText(self.ui.ccdTemp, '4.1f', header.get('CCD-TEMP'))
        self.guiSetText(self.ui.expTime, '5.1f', getExposure(header=header))
        self.guiSetText(self.ui.filter, 's', header.get('FILTER'))
        self.guiSetText(self.ui.binX, '1.0f', header.get('XBINNING'))
        self.guiSetText(self.ui.binY, '1.0f', header.get('YBINNING'))
        self.guiSetText(self.ui.sqm, '5.2f', getSQM(header=header))
        return True

    def resultPhotometry(self):
        """
        :return:
        """
        if self.photometry.objs is None:
            self.msg.emit(2, 'Image', 'Photometry error', 'Too low pixel stack')
        else:
            self.msg.emit(0, 'Image', 'Photometry', 'SEP done')
        return True

    def processPhotometry(self):
        """
        :return:
        """
        isPhotometry = self.ui.photometryGroup.isChecked()
        if self.fileHandler.image is None or not isPhotometry:
            self.clearGui()
            return False

        self.ui.showValues.setEnabled(isPhotometry)
        self.ui.isoLayer.setEnabled(isPhotometry)
        snTarget = self.ui.snTarget.currentIndex()

        self.photometry.processPhotometry(image=self.fileHandler.image,
                                          snTarget=snTarget)
        return True

    def showImage(self, imagePath=''):
        """
        :param: imagePath:
        :return:
        """
        if self.deviceStat['expose']:
            self.ui.image.setImage(None)
            self.clearGui()
        if not imagePath:
            return False
        imagePath = os.path.normpath(imagePath)
        if not os.path.isfile(imagePath):
            return False

        self.changeStyleDynamic(self.ui.headerGroup, 'running', True)
        self.setWindowTitle(f'Imaging:   {os.path.basename(imagePath)}')
        flipH = self.ui.flipH.isChecked()
        flipV = self.ui.flipV.isChecked()
        self.fileHandler.loadImage(imagePath=imagePath, flipH=flipH, flipV=flipV)
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
        fastReadout = self.app.camera.fastDownload

        time = self.app.mount.obsSite.timeJD.utc_strftime('%Y-%m-%d-%H-%M-%S')

        if self.ui.timeTagImage.isChecked():
            fileName = time + '-exposure.fits'
        else:
            fileName = 'exposure.fits'

        self.imageFileName = self.app.mwGlob['imageDir'] + '/' + fileName
        focalLength = self.app.telescope.focalLength
        self.imageFileNameOld = self.imageFileName
        suc = self.app.camera.expose(imagePath=self.imageFileName,
                                     expTime=self.expTime,
                                     binning=self.binning,
                                     subFrame=subFrame,
                                     fastReadout=fastReadout,
                                     focalLength=focalLength
                                     )
        if not suc:
            self.abortExpose()
            text = f'{os.path.basename(self.imageFileName)}'
            self.msg.emit(2, 'Image', 'Expose error', text)
            return False

        text = f'{os.path.basename(self.imageFileName)}'
        self.msg.emit(0, 'Image', 'Exposing', text)
        text = f'Duration:{self.expTime:3.0f}s  '
        self.msg.emit(0, '', '', f'{text}')
        text = f'Bin:{self.binning:1.0f}'
        self.msg.emit(0, '', '', f'{text}')
        text = f'Sub:{subFrame:3.0f}%'
        self.msg.emit(0, '', '', f'{text}')
        return True

    def exposeImageDone(self, imagePath=''):
        """
        :param imagePath:
        :return: True for test purpose
        """
        self.app.camera.signals.saved.disconnect(self.exposeImageDone)
        text = f'{os.path.basename(imagePath)}'
        self.msg.emit(0, 'Image', 'Exposed', text)
        self.imageFileName = imagePath

        if self.ui.autoSolve.isChecked():
            self.signals.solveImage.emit(imagePath)
        self.app.showImage.emit(imagePath)
        self.app.operationRunning.emit(0)
        self.deviceStat['expose'] = False
        return True

    def exposeImage(self):
        """
        :return: success
        """
        self.expTime = self.app.camera.expTime
        self.binning = int(self.app.camera.binning)
        self.deviceStat['expose'] = True
        self.app.camera.signals.saved.connect(self.exposeImageDone)
        self.app.operationRunning.emit(6)
        self.exposeRaw()
        return True

    def exposeImageNDone(self, imagePath=''):
        """
        :param imagePath:
        :return: True for test purpose
        """
        text = f'{os.path.basename(imagePath)}'
        self.msg.emit(0, 'Image', 'Exposed n', text)

        if self.ui.autoSolve.isChecked():
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
        self.deviceStat['exposeN'] = True
        self.app.camera.signals.saved.connect(self.exposeImageNDone)
        self.app.operationRunning.emit(6)
        self.exposeRaw()
        return True

    def abortExpose(self):
        """
        :return: True for test purpose
        """
        self.app.camera.abort()
        if self.deviceStat['expose']:
            self.app.camera.signals.saved.disconnect(self.exposeImageDone)
        if self.deviceStat['exposeN']:
            self.app.camera.signals.saved.disconnect(self.exposeImageNDone)

        # last image file was not stored, so getting last valid it back
        self.imageFileName = self.imageFileNameOld
        self.deviceStat['expose'] = False
        self.deviceStat['exposeN'] = False
        self.msg.emit(2, 'Image', 'Expose', 'Exposing aborted')
        self.app.operationRunning.emit(0)
        return True

    def solveDone(self, result=None):
        """
        :param result: result (named tuple)
        :return: success
        """
        self.deviceStat['solve'] = False
        self.app.plateSolve.signals.done.disconnect(self.solveDone)

        if not result:
            self.msg.emit(2, 'Image', 'Solving',
                          'Solving error, result missing')
            self.app.operationRunning.emit(0)
            return False
        if not result['success']:
            self.msg.emit(2, 'Image', 'Solving error',
                          f'{result.get("message")}')
            self.app.operationRunning.emit(0)
            return False

        text = f'RA: {convertToHMS(result["raJ2000S"])} '
        text += f'({result["raJ2000S"].hours:4.3f}), '
        self.msg.emit(0, 'Image', 'Solved', text)
        text = f'DEC: {convertToDMS(result["decJ2000S"])} '
        text += f'({result["decJ2000S"].degrees:4.3f}), '
        self.msg.emit(0, '', '', text)
        text = f'Angle: {result["angleS"]:3.0f}, '
        self.msg.emit(0, '', '', text)
        text = f'Scale: {result["scaleS"]:4.3f}, '
        self.msg.emit(0, '', '', text)
        text = f'Error: {result["errorRMS_S"]:4.1f}'
        self.msg.emit(0, '', '', text)

        if self.ui.embedData.isChecked():
            self.showCurrent()
        self.app.operationRunning.emit(0)
        return True

    def solveImage(self, imagePath=''):
        """
        :param imagePath:
        :return:
        """
        if not os.path.isfile(imagePath):
            self.app.operationRunning.emit(0)
            return False

        updateFits = self.ui.embedData.isChecked()
        self.app.plateSolve.signals.done.connect(self.solveDone)
        self.app.operationRunning.emit(6)
        self.app.plateSolve.solveThreading(fitsPath=imagePath,
                                           updateFits=updateFits)
        self.deviceStat['solve'] = True
        t = f'{os.path.basename(imagePath)}'
        self.msg.emit(0, 'Image', 'Solving', t)
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
        suc = self.app.plateSolve.abort()
        self.app.operationRunning.emit(0)
        return suc

    def mouseToWorld(self, mousePoint):
        """
        :param mousePoint:
        :return:
        """
        x = mousePoint.x()
        y = mousePoint.y()
        if self.fileHandler.flipH:
            x = self.fileHandler.sizeX - x
        if not self.fileHandler.flipV:
            y = self.fileHandler.sizeY - y

        ra, dec = self.fileHandler.wcs.wcs_pix2world(x, y, 0)
        ra = Angle(hours=float(ra / 360 * 24))
        dec = Angle(degrees=float(dec))
        return ra, dec

    def slewDirect(self, ra, dec):
        """
        :param ra:
        :param dec:
        :return:
        """
        question = '<b>Slewing to target</b>'
        question += '<br><br>Selected coordinates are:<br>'
        question += f'<font color={self.M_BLUE}> RA: {ra.hours:3.2f}h'
        question += f'   DEC: {dec.degrees:3.2f}°</font>'
        question += '<br><br>Would you like to start slewing?<br>'

        suc = self.messageDialog(self, 'Slewing mount', question)
        if not suc:
            return False

        suc = self.slewTargetRaDec(ra, dec)
        return suc

    def mouseMoved(self, pos):
        """
        :param pos:
        :return:
        """
        if not self.fileHandler.hasCelestial:
            return False

        plotItem = self.ui.image.p[0]
        vr = plotItem.getViewBox().viewRange()
        mousePoint = plotItem.getViewBox().mapSceneToView(pos)
        x = mousePoint.x()
        y = mousePoint.y()
        ra, dec = self.mouseToWorld(mousePoint)

        if vr[0][0] < x < vr[0][1] and vr[1][0] < y < vr[1][1]:
            self.guiSetText(self.ui.raMouse, 'HSTR', ra)
            self.guiSetText(self.ui.raMouseFloat, '2.5f', ra.hours)
            self.guiSetText(self.ui.decMouse, 'DSTR', dec)
            self.guiSetText(self.ui.decMouseFloat, '2.5f', dec.degrees)
            QGuiApplication.setOverrideCursor(QCursor(Qt.CrossCursor))
        else:
            self.ui.raMouse.setText('')
            self.ui.raMouseFloat.setText('')
            self.ui.decMouse.setText('')
            self.ui.decMouseFloat.setText('')
            QGuiApplication.setOverrideCursor(QCursor(Qt.ArrowCursor))
        return True

    def mouseDoubleClick(self, ev, mousePoint):
        """
        :param ev:
        :param mousePoint:
        :return:
        """
        if not self.fileHandler.hasCelestial:
            return False

        ra, dec = self.mouseToWorld(mousePoint)
        self.slewDirect(ra, dec)
        return True

    def slewCenter(self):
        """
        :return:
        """
        if not self.fileHandler.hasCelestial:
            return False

        ra, dec = getCoordinates(self.fileHandler.header)
        self.slewDirect(ra, dec)
        return True
