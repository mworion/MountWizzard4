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
# written in python3, (c) 2019, 2020 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import os
from pathlib import Path

# external packages
import PyQt5
from PyQt5.QtTest import QTest
from astropy.io import fits

# local import


class Tools(object):
    """
    """

    def __init__(self, app=None, ui=None, clickable=None):
        if app:
            self.app = app
            self.ui = ui
            self.clickable = clickable

        self.selectorsDropDowns = {'rename1': self.ui.rename1,
                                   'rename2': self.ui.rename2,
                                   'rename3': self.ui.rename3,
                                   'rename4': self.ui.rename4,
                                   'rename5': self.ui.rename5,
                                   }
        self.fitsHeaderKeywords = {'None': [''],
                                   'Datetime': ['DATE-OBS'],
                                   'Frame': ['FRAME', 'IMAGETYP'],
                                   'Filter': ['FILTER'],
                                   'Binning': ['XBINNING'],
                                   'Exp Time': ['EXPTIME'],
                                   'CCD Temp': ['CCD-TEMP'],
                                   }
        self.slewSpeeds = {self.ui.slewSpeedMax: self.app.mount.setting.setSlewSpeedMax,
                           self.ui.slewSpeedHigh: self.app.mount.setting.setSlewSpeedHigh,
                           self.ui.slewSpeedMed: self.app.mount.setting.setSlewSpeedMed,
                           self.ui.slewSpeedLow: self.app.mount.setting.setSlewSpeedLow,
                           }
        self.setupStepsizes = {'Stepsize 0.25°': 0.25,
                               'Stepsize 0.5°': 0.5,
                               'Stepsize 1.0°': 1,
                               'Stepsize 2.0°': 2,
                               'Stepsize 5.0°': 5,
                               'Stepsize 10°': 10,
                               'Stepsize 20°': 20,
                               }
        self.setupMoveClassic = {self.ui.moveNorth: [1, 0],
                                 self.ui.moveNorthEast: [1, 1],
                                 self.ui.moveEast: [0, 1],
                                 self.ui.moveSouthEast: [-1, 1],
                                 self.ui.moveSouth: [-1, 0],
                                 self.ui.moveSouthWest: [-1, -1],
                                 self.ui.moveWest: [0, -1],
                                 self.ui.moveNorthWest: [1, -1],
                                 }
        self.setupMoveAltAz = {self.ui.moveNorthAltAz: [1, 0],
                               self.ui.moveNorthEastAltAz: [1, 1],
                               self.ui.moveEastAltAz: [0, 1],
                               self.ui.moveSouthEastAltAz: [-1, 1],
                               self.ui.moveSouthAltAz: [-1, 0],
                               self.ui.moveSouthWestAltAz: [-1, -1],
                               self.ui.moveWestAltAz: [0, -1],
                               self.ui.moveNorthWestAltAz: [1, -1],
                               }
        self.setupMoveRaDec = {self.ui.moveNorthRaDec: [1, 0],
                               self.ui.moveNorthEastRaDec: [1, 1],
                               self.ui.moveEastRaDec: [0, 1],
                               self.ui.moveSouthEastRaDec: [-1, 1],
                               self.ui.moveSouthRaDec: [-1, 0],
                               self.ui.moveSouthWestRaDec: [-1, -1],
                               self.ui.moveWestRaDec: [0, -1],
                               self.ui.moveNorthWestRaDec: [1, -1],
                               }

        self.slewSpeedSelected = None
        self.setupGui()

        self.ui.renameStart.clicked.connect(self.renameRunGUI)
        self.ui.renameInputSelect.clicked.connect(self.chooseDir)
        self.ui.stopMoveAll.clicked.connect(self.stopMoveAll)
        self.ui.slewSpeedMax.clicked.connect(self.setSlewSpeed)
        self.ui.slewSpeedHigh.clicked.connect(self.setSlewSpeed)
        self.ui.slewSpeedMed.clicked.connect(self.setSlewSpeed)
        self.ui.slewSpeedLow.clicked.connect(self.setSlewSpeed)

    def initConfig(self):
        """
        initConfig read the key out of the configuration dict and stores it to the gui
        elements. if some initialisations have to be proceeded with the loaded persistent
        data, they will be launched as well in this method.

        :return: True for test purpose
        """
        config = self.app.config['mainW']
        defaultDir = self.app.mwGlob['imageDir']
        self.ui.renameDir.setText(config.get('renameDir', defaultDir))
        self.ui.renameText.setText(config.get('renameText', ''))
        self.ui.newObjectName.setText(config.get('newObjectName', ''))
        self.ui.checkIncludeSubdirs.setChecked(config.get('checkIncludeSubdirs', False))
        for name, ui in self.selectorsDropDowns.items():
            ui.setCurrentIndex(config.get(name, 0))

        self.ui.renameProgress.setValue(0)
        self.ui.slewSpeedMax.setChecked(config.get('slewSpeedMax', True))
        self.ui.slewSpeedHigh.setChecked(config.get('slewSpeedHigh', False))
        self.ui.slewSpeedMed.setChecked(config.get('slewSpeedMed', False))
        self.ui.slewSpeedLow.setChecked(config.get('slewSpeedLow', False))
        self.ui.moveDuration.setCurrentIndex(config.get('moveDuration', 0))
        self.ui.moveStepSizeAltAz.setCurrentIndex(config.get('moveStepSizeAltAz', 0))
        self.ui.moveStepSizeRaDec.setCurrentIndex(config.get('moveStepSizeRaDec', 0))

        return True

    def storeConfig(self):
        """
        storeConfig writes the keys to the configuration dict and stores. if some
        saving has to be proceeded to persistent data, they will be launched as
        well in this method.

        :return: True for test purpose
        """
        config = self.app.config['mainW']
        config['renameDir'] = self.ui.renameDir.text()
        config['renameText'] = self.ui.renameText.text()
        config['newObjectName'] = self.ui.newObjectName.text()
        config['checkIncludeSubdirs'] = self.ui.checkIncludeSubdirs.isChecked()
        for name, ui in self.selectorsDropDowns.items():
            config[name] = ui.currentIndex()

        config['slewSpeedMax'] = self.ui.slewSpeedMax.isChecked()
        config['slewSpeedHigh'] = self.ui.slewSpeedHigh.isChecked()
        config['slewSpeedMed'] = self.ui.slewSpeedMed.isChecked()
        config['slewSpeedLow'] = self.ui.slewSpeedLow.isChecked()
        config['moveDuration'] = self.ui.moveDuration.currentIndex()
        config['moveStepSizeAltAz'] = self.ui.moveStepSizeAltAz.currentIndex()
        config['moveStepSizeRaDec'] = self.ui.moveStepSizeRaDec.currentIndex()

        return True

    def setupGui(self):
        """
        :return: success for test
        """

        for name, selectorUI in self.selectorsDropDowns.items():
            selectorUI.clear()
            selectorUI.setView(PyQt5.QtWidgets.QListView())
            for headerEntry in self.fitsHeaderKeywords:
                selectorUI.addItem(headerEntry)

        self.ui.moveStepSizeAltAz.clear()
        for text in self.setupStepsizes:
            self.ui.moveStepSizeAltAz.addItem(text)

        self.ui.moveStepSizeRaDec.clear()
        for text in self.setupStepsizes:
            self.ui.moveStepSizeRaDec.addItem(text)

        for ui in self.setupMoveClassic:
            ui.clicked.connect(self.moveClassic)

        for ui in self.setupMoveAltAz:
            ui.clicked.connect(self.moveAltAz)

        for ui in self.setupMoveRaDec:
            ui.clicked.connect(self.moveRaDec)

        return True

    @staticmethod
    def getNumberFiles(pathDir='', search=''):
        """
        getNumberFiles counts the number of files to be valid for the renaming.

        :param pathDir: path to root directory to be scanned
        :param search: search string
        :return: number of files found
        """

        if not pathDir:
            return 0
        if not os.path.isdir(pathDir):
            return 0
        if not search:
            return 0

        number = sum(1 for _ in Path(pathDir).glob(search))
        return number

    def convertHeaderEntry(self, entry='', fitsKey=''):
        """
        convertHeaderEntry takes the fitsHeader entry and reformat it to a reasonable
        string.

        :param entry:
        :param fitsKey:
        :return:
        """

        if not fitsKey:
            return ''
        if not entry:
            return ''

        if fitsKey == 'DATE-OBS':
            chunk = entry.replace(':', '-')
            chunk = chunk.replace('T', '_')
            chunk = chunk.split('.')[0]
        elif fitsKey == 'XBINNING':
            chunk = f'Bin-{entry:1.0f}'
        elif fitsKey == 'CCD-TEMP':
            chunk = f'Temp{entry:03.0f}'
        elif fitsKey == 'FRAME':
            chunk = f'Frame-{entry}'
        elif fitsKey == 'FILTER':
            chunk = f'Filter-{entry}'
        elif fitsKey == 'EXPTIME':
            chunk = f'Exp-{entry:04.0f}s'
        elif fitsKey == 'RenameText':
            chunk = self.ui.renameText.text().upper()
        else:
            chunk = ''

        return chunk

    def processSelectors(self, fitsHeader=None, selection=''):
        """
        processSelectors takes the selection for a fileName chunk and runs through the
        possible list of valid fits header keys. if there is more than one valid fitsKey,
        it automatically selects only the first on for conversion.

        :param fitsHeader:
        :param selection: str entry from the drop down selector
        :return: nameChunk: part of the entry
        """

        if fitsHeader is None:
            return ''
        if not selection:
            return ''

        nameChunk = ''
        fitsKeywords = self.fitsHeaderKeywords[selection]
        for fitsKey in fitsKeywords:
            if fitsKey not in fitsHeader:
                continue
            nameChunk = self.convertHeaderEntry(entry=fitsHeader[fitsKey],
                                                fitsKey=fitsKey)
            break
        return nameChunk

    def renameFile(self, fileName=''):
        """
        renameFile opens the given FITS file and retrieves it's header. if valid it
        runs through selectors of the drop down lists and checks all header keys to
        get the new filename build. afterwards it renames the given file.

        :param fileName: fits file to be renamed
        :return: success
        """

        if not fileName:
            return False

        if not os.path.isfile(fileName):
            return False

        with fits.open(name=fileName) as fd:
            fitsHeader = fd[0].header

            # object should be in lower case. if not, it will be set
            newObjectName = self.ui.newObjectName.text().upper()
            if newObjectName:
                newFilename = newObjectName
            else:
                if 'OBJECT' in fitsHeader:
                    newFilename = fitsHeader['OBJECT'].upper()
                else:
                    newFilename = 'UNKNOWN'

            for _, selector in self.selectorsDropDowns.items():
                selection = selector.currentText()
                chunk = self.processSelectors(fitsHeader=fitsHeader,
                                              selection=selection
                                              )
                if chunk:
                    newFilename += f'_{chunk}'

            newFilename += '.fits'

            dirName = os.path.dirname(fileName)
            newFilename = f'{dirName}/{newFilename}'
            os.rename(fileName, newFilename)

        return True

    def renameRunGUI(self):
        """
        renameRunGUI retrieves a full list of files to be renamed and renames
        them on by one.

        :return: True for test purpose
        """

        pathDir = self.ui.renameDir.text()
        includeSubdirs = self.ui.checkIncludeSubdirs.isChecked()

        if not os.path.isdir(pathDir):
            self.app.message.emit('No valid input directory given', 2)
            return False

        if includeSubdirs:
            search = '**/*.fit*'
        else:
            search = '*.fit*'

        numberFiles = self.getNumberFiles(pathDir, search=search)
        if not numberFiles:
            self.app.message.emit('No files to rename', 0)
            return False

        for i, fileName in enumerate(Path(pathDir).glob(search)):
            self.ui.renameProgress.setValue(int(100 * (i + 1) / numberFiles))
            PyQt5.QtWidgets.QApplication.processEvents()
            suc = self.renameFile(fileName=fileName)
            if not suc:
                self.app.message.emit(f'{fileName} could not be renamed', 2)

        self.app.message.emit(f'{numberFiles:d} images were renamed', 0)

        return True

    def chooseDir(self):
        """
        chooseDir selects the input directory and sets the default value for the
        output directory as well

        :return: True for test purpose
        """
        folder = self.ui.renameDir.text()
        pathDir, _, _ = self.openDir(self, 'Choose Input Dir', folder,)
        if pathDir:
            self.ui.renameDir.setText(pathDir)
            self.ui.renameProgress.setValue(0)
        return True

    def moveDuration(self):
        """
        :return:
        """
        if self.ui.moveDuration.currentIndex() == 1:
            QTest.qWait(10000)

        elif self.ui.moveDuration.currentIndex() == 2:
            QTest.qWait(5000)

        elif self.ui.moveDuration.currentIndex() == 3:
            QTest.qWait(2000)

        elif self.ui.moveDuration.currentIndex() == 4:
            QTest.qWait(1000)

        else:
            return True

        self.stopMoveAll()
        return True

    def moveClassic(self):
        """
        :return:
        """
        ui = self.sender()
        if ui not in self.setupMoveClassic:
            return False

        self.changeStyleDynamic(ui, 'running', True)
        directions = self.setupMoveClassic[ui]

        if directions[0] == 1:
            self.app.mount.obsSite.moveNorth()
        elif directions[0] == -1:
            self.app.mount.obsSite.moveSouth()

        if directions[1] == 1:
            self.app.mount.obsSite.moveEast()
        elif directions[1] == -1:
            self.app.mount.obsSite.moveWest()

        self.moveDuration()
        return True

    def stopMoveAll(self):
        """
        :return: success
        """
        self.app.mount.obsSite.stopMoveAll()
        self.changeStyleDynamic(self.ui.moveNorth, 'running', False)
        self.changeStyleDynamic(self.ui.moveNorthEast, 'running', False)
        self.changeStyleDynamic(self.ui.moveEast, 'running', False)
        self.changeStyleDynamic(self.ui.moveSouthEast, 'running', False)
        self.changeStyleDynamic(self.ui.moveSouth, 'running', False)
        self.changeStyleDynamic(self.ui.moveSouthWest, 'running', False)
        self.changeStyleDynamic(self.ui.moveWest, 'running', False)
        self.changeStyleDynamic(self.ui.moveNorthWest, 'running', False)
        return True

    def setSlewSpeed(self):
        """
        setSlewSpeed reads the gui elements and calls the method in mount class to set the
        slew speed accordingly.

        :return: success
        """
        ui = self.sender()
        if ui not in self.slewSpeeds:
            return False

        self.slewSpeeds[ui]()
        return True

    def slewSelectedTarget(self, slewType='normal'):
        """
        :param slewType:
        :return: success
        """
        azimuthT = self.app.mount.obsSite.AzTarget
        altitudeT = self.app.mount.obsSite.AltTarget

        if azimuthT is None or altitudeT is None:
            return False

        azimuthT = altitudeT.degrees
        altitudeT = altitudeT.degrees

        if self.app.deviceStat['dome']:
            delta = self.app.dome.slewDome(altitude=altitudeT,
                                           azimuth=azimuthT)
            geoStat = 'Geometry corrected' if delta else 'Equal mount'
            text = f'Slewing dome:        {geoStat}, az: {azimuthT:3.1f} delta: {delta:3.1f}'
            self.app.message.emit(text, 0)

        suc = self.app.mount.obsSite.startSlewing(slewType=slewType)
        if suc:
            self.app.message.emit('Slewing mount', 0)

        else:
            self.app.message.emit('Cannot slew to: {0}, {1}'.format(azimuthT, altitudeT), 2)
        return suc

    def slewTargetAltAz(self, Alt, Az):
        """
        :param Alt:
        :param Az:
        :return:
        """
        # todo: constraints set in mount

        self.app.mount.obsSite.setTargetAltAz(alt_degrees=Alt,
                                              az_degrees=Az)
        self.slewSelectedTarget(slewType='normal')
        return True

    def moveAltAz(self):
        """
        :return:
        """
        ui = self.sender()
        if ui not in self.setupMoveAltAz:
            return False

        Alt = self.app.mount.obsSite.Alt
        Az = self.app.mount.obsSite.Az

        if Alt is None or Az is None:
            return False

        key = list(self.setupStepsizes)[self.ui.moveStepSizeAltAz.currentIndex()]
        step = self.setupStepsizes[key]
        directions = self.setupMoveAltAz[ui]
        targetAlt = Alt.degrees + directions[0] * step
        targetAz = Az.degrees + directions[1] * step

        if targetAlt > 90:
            targetAlt = 90

        elif targetAlt < -5:
            targetAlt = -5

        targetAz = targetAz % 360
        self.slewTargetAltAz(targetAlt, targetAz)
        return True

    def slewTargetRaDec(self, Ra, Dec):
        """
        :param Ra:
        :param Dec:
        :return:
        """
        self.app.mount.obsSite.setTargetRaDec(ra_hours=Ra,
                                              dec_degrees=Dec)
        self.slewSelectedTarget(slewType='normal')
        return True

    def moveRaDec(self):
        """
        :return:
        """
        ui = self.sender()
        if ui not in self.setupMoveRaDec:
            return False

        Ra = self.app.mount.obsSite.raJNow
        Dec = self.app.mount.obsSite.decJNow

        if Ra is None or Dec is None:
            return False

        key = list(self.setupStepsizes)[self.ui.moveStepSizeRaDec.currentIndex()]
        step = self.setupStepsizes[key]
        directions = self.setupMoveRaDec[ui]
        targetRa = Ra.hours + directions[0] * step * 24 / 360
        targetDec = Dec.degrees + directions[1] * step

        print(directions, targetRa, targetDec)

        self.slewTargetRaDec(targetRa, targetDec)
        return True
