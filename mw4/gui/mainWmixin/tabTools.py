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

        self.slewSpeedSelected = None
        self.setupSelectorGui()

        self.ui.renameStart.clicked.connect(self.renameRunGUI)
        self.ui.renameInputSelect.clicked.connect(self.chooseDir)
        self.ui.stopMoveAll.clicked.connect(self.stopMoveAll)
        self.ui.moveNorth.clicked.connect(self.moveNorth)
        self.ui.moveEast.clicked.connect(self.moveEast)
        self.ui.moveSouth.clicked.connect(self.moveSouth)
        self.ui.moveWest.clicked.connect(self.moveWest)
        self.ui.moveNorthWest.clicked.connect(self.moveNorthWest)
        self.ui.moveNorthEast.clicked.connect(self.moveNorthEast)
        self.ui.moveSouthEast.clicked.connect(self.moveSouthEast)
        self.ui.moveSouthWest.clicked.connect(self.moveSouthWest)
        self.ui.slewSpeedMax.clicked.connect(self.setSlewSpeed)
        self.ui.slewSpeedHigh.clicked.connect(self.setSlewSpeed)
        self.ui.slewSpeedMed.clicked.connect(self.setSlewSpeed)
        self.ui.slewSpeedLow.clicked.connect(self.setSlewSpeed)

        self.ui.moveNorthAltAz.clicked.connect(self.moveNorthAltAz)
        self.ui.moveEastAltAz.clicked.connect(self.moveEastAltAz)
        self.ui.moveSouthAltAz.clicked.connect(self.moveSouthAltAz)
        self.ui.moveWestAltAz.clicked.connect(self.moveWestAltAz)
        self.ui.moveNorthWestAltAz.clicked.connect(self.moveNorthWestAltAz)
        self.ui.moveNorthEastAltAz.clicked.connect(self.moveNorthEastAltAz)
        self.ui.moveSouthEastAltAz.clicked.connect(self.moveSouthEastAltAz)
        self.ui.moveSouthWestAltAz.clicked.connect(self.moveSouthWestAltAz)

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

    def setupSelectorGui(self):
        """
        setupSelectorGui handles the dropdown lists for all devices possible in
        mountwizzard. therefore we add the necessary entries to populate the list.

        :return: success for test
        """

        for name, selectorUI in self.selectorsDropDowns.items():
            selectorUI.clear()
            selectorUI.setView(PyQt5.QtWidgets.QListView())
            for headerEntry in self.fitsHeaderKeywords:
                selectorUI.addItem(headerEntry)

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

    def moveNorth(self):
        """
        :return: success
        """
        self.app.mount.obsSite.moveNorth()
        self.changeStyleDynamic(self.ui.moveNorth, 'running', True)
        self.moveDuration()
        return True

    def moveEast(self):
        """
        :return: success
        """
        self.app.mount.obsSite.moveEast()
        self.changeStyleDynamic(self.ui.moveEast, 'running', True)
        self.moveDuration()
        return True

    def moveSouth(self):
        """
        :return: success
        """
        self.app.mount.obsSite.moveSouth()
        self.changeStyleDynamic(self.ui.moveSouth, 'running', True)
        self.moveDuration()
        return True

    def moveWest(self):
        """
        :return: success
        """
        self.app.mount.obsSite.moveWest()
        self.changeStyleDynamic(self.ui.moveWest, 'running', True)
        self.moveDuration()
        return True

    def moveNorthWest(self):
        """
        :return: success
        """
        self.app.mount.obsSite.moveWest()
        self.app.mount.obsSite.moveNorth()
        self.changeStyleDynamic(self.ui.moveNorthWest, 'running', True)
        self.moveDuration()
        return True

    def moveNorthEast(self):
        """
        :return: success
        """
        self.app.mount.obsSite.moveEast()
        self.app.mount.obsSite.moveNorth()
        self.changeStyleDynamic(self.ui.moveNorthEast, 'running', True)
        self.moveDuration()
        return True

    def moveSouthEast(self):
        """
        :return: success
        """
        self.app.mount.obsSite.moveEast()
        self.app.mount.obsSite.moveSouth()
        self.changeStyleDynamic(self.ui.moveSouthEast, 'running', True)
        self.moveDuration()
        return True

    def moveSouthWest(self):
        """
        :return: success
        """
        self.app.mount.obsSite.moveWest()
        self.app.mount.obsSite.moveSouth()
        self.changeStyleDynamic(self.ui.moveSouthWest, 'running', True)
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
        if self.sender() not in self.slewSpeeds:
            return False

        self.slewSpeeds[self.sender()]()
        return True

    def slewSelectedTarget(self, slewType='normal'):
        """
        :param slewType:
        :return: success
        """
        azimuthT = self.app.mount.obsSite.AzTarget.degrees
        altitudeT = self.app.mount.obsSite.AltTarget.degrees

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
        if Alt > 90:
            Alt = 90

        elif Alt < -5:
            Alt = -5

        Az = Az % 360
        self.app.mount.obsSite.setTargetAltAz(alt_degrees=Alt,
                                              az_degrees=Az)
        self.slewSelectedTarget(slewType='normal')
        return True

    def getStepsizeAltAz(self):
        """
        :return:
        """
        stepsizes = [0.5, 1, 2, 5, 10]
        index = self.ui.moveStepSizeAltAz.currentIndex()
        value = stepsizes[index]
        print(value)
        return value

    def moveNorthAltAz(self):
        """
        :return: success
        """
        actAlt = self.app.mount.obsSite.Alt.degrees
        actAz = self.app.mount.obsSite.Az.degrees
        step = self.getStepsizeAltAz()
        Alt = actAlt + step
        Az = actAz + 0
        self.slewTargetAltAz(Alt, Az)
        return True

    def moveNorthEastAltAz(self):
        """
        :return: success
        """
        actAlt = self.app.mount.obsSite.Alt.degrees
        actAz = self.app.mount.obsSite.Az.degrees
        step = self.getStepsizeAltAz()
        Alt = actAlt + step
        Az = actAz + step
        self.slewTargetAltAz(Alt, Az)
        return True

    def moveEastAltAz(self):
        """
        :return: success
        """
        actAlt = self.app.mount.obsSite.Alt.degrees
        actAz = self.app.mount.obsSite.Az.degrees
        step = self.getStepsizeAltAz()
        Alt = actAlt + 0
        Az = actAz + step
        self.slewTargetAltAz(Alt, Az)
        return True

    def moveSouthEastAltAz(self):
        """
        :return: success
        """
        actAlt = self.app.mount.obsSite.Alt.degrees
        actAz = self.app.mount.obsSite.Az.degrees
        step = self.getStepsizeAltAz()
        Alt = actAlt - step
        Az = actAz + step
        self.slewTargetAltAz(Alt, Az)
        return True

    def moveSouthAltAz(self):
        """
        :return: success
        """
        actAlt = self.app.mount.obsSite.Alt.degrees
        actAz = self.app.mount.obsSite.Az.degrees
        step = self.getStepsizeAltAz()
        Alt = actAlt - step
        Az = actAz + 0
        self.slewTargetAltAz(Alt, Az)
        return True

    def moveSouthWestAltAz(self):
        """
        :return: success
        """
        actAlt = self.app.mount.obsSite.Alt.degrees
        actAz = self.app.mount.obsSite.Az.degrees
        step = self.getStepsizeAltAz()
        Alt = actAlt - step
        Az = actAz - step
        self.slewTargetAltAz(Alt, Az)
        return True

    def moveWestAltAz(self):
        """
        :return: success
        """
        actAlt = self.app.mount.obsSite.Alt.degrees
        actAz = self.app.mount.obsSite.Az.degrees
        step = self.getStepsizeAltAz()
        Alt = actAlt - 0
        Az = actAz - step
        self.slewTargetAltAz(Alt, Az)
        return True

    def moveNorthWestAltAz(self):
        """
        :return: success
        """
        actAlt = self.app.mount.obsSite.Alt.degrees
        actAz = self.app.mount.obsSite.Az.degrees
        step = self.getStepsizeAltAz()
        Alt = actAlt + step
        Az = actAz - step
        self.slewTargetAltAz(Alt, Az)
        return True
