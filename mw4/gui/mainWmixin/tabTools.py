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
# Licence APL2.0
#
###########################################################
# standard libraries
import os
import time
from pathlib import Path

# external packages
from PyQt5.QtWidgets import QLineEdit, QListView, QApplication, QInputDialog
from PyQt5.QtGui import QTextCursor
from astropy.io import fits

# local import
from base.transform import J2000ToJNow
from gui.utilities.toolsQtWidget import sleepAndEvents
from mountcontrol.convert import convertRaToAngle, convertDecToAngle
from mountcontrol.convert import formatHstrToText, formatDstrToText
from mountcontrol.convert import valueToFloat
from mountcontrol.connection import Connection


class Tools(object):
    """
    """

    def __init__(self):
        self.targetAlt = None
        self.targetAz = None
        self.selectorsDropDowns = {'rename1': self.ui.rename1,
                                   'rename2': self.ui.rename2,
                                   'rename3': self.ui.rename3,
                                   'rename4': self.ui.rename4,
                                   'rename5': self.ui.rename5,
                                   'rename6': self.ui.rename6,
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
                                 self.ui.stopMoveAll: [0, 0],
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
        self.slewSpeedSelected = None
        self.setupGui()

        self.ui.renameStart.clicked.connect(self.renameRunGUI)
        self.ui.renameInputSelect.clicked.connect(self.chooseDir)
        self.ui.stopMoveAll.clicked.connect(self.stopMoveAll)
        self.ui.slewSpeedMax.clicked.connect(self.setSlewSpeed)
        self.ui.slewSpeedHigh.clicked.connect(self.setSlewSpeed)
        self.ui.slewSpeedMed.clicked.connect(self.setSlewSpeed)
        self.ui.slewSpeedLow.clicked.connect(self.setSlewSpeed)
        self.ui.moveAltAzAbsolute.clicked.connect(self.moveAltAzAbsolute)
        self.ui.moveRaDecAbsolute.clicked.connect(self.moveRaDecAbsolute)
        self.clickable(self.ui.moveCoordinateRa).connect(self.setRA)
        self.ui.moveCoordinateRa.textEdited.connect(self.setRA)
        self.ui.moveCoordinateRa.returnPressed.connect(self.setRA)
        self.clickable(self.ui.moveCoordinateDec).connect(self.setDEC)
        self.ui.moveCoordinateDec.textEdited.connect(self.setDEC)
        self.ui.moveCoordinateDec.returnPressed.connect(self.setDEC)
        self.ui.commandInput.returnPressed.connect(self.commandRaw)
        self.app.mount.signals.slewFinished.connect(self.moveAltAzDefault)
        self.app.gameDirection.connect(self.moveAltAzGameController)
        self.app.game_sR.connect(self.moveClassicGameController)

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
        self.ui.newObjectName.setText(config.get('newObjectName', ''))
        self.ui.includeSubdirs.setChecked(config.get('includeSubdirs', False))
        for name, ui in self.selectorsDropDowns.items():
            ui.setCurrentIndex(config.get(name, 0))

        self.ui.renameProgress.setValue(0)
        self.ui.slewSpeedMax.setChecked(config.get('slewSpeedMax', True))
        self.ui.slewSpeedHigh.setChecked(config.get('slewSpeedHigh', False))
        self.ui.slewSpeedMed.setChecked(config.get('slewSpeedMed', False))
        self.ui.slewSpeedLow.setChecked(config.get('slewSpeedLow', False))
        self.ui.moveDuration.setCurrentIndex(config.get('moveDuration', 0))
        self.ui.moveStepSizeAltAz.setCurrentIndex(config.get('moveStepSizeAltAz', 0))
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
        config['newObjectName'] = self.ui.newObjectName.text()
        config['includeSubdirs'] = self.ui.includeSubdirs.isChecked()
        for name, ui in self.selectorsDropDowns.items():
            config[name] = ui.currentIndex()

        config['slewSpeedMax'] = self.ui.slewSpeedMax.isChecked()
        config['slewSpeedHigh'] = self.ui.slewSpeedHigh.isChecked()
        config['slewSpeedMed'] = self.ui.slewSpeedMed.isChecked()
        config['slewSpeedLow'] = self.ui.slewSpeedLow.isChecked()
        config['moveDuration'] = self.ui.moveDuration.currentIndex()
        config['moveStepSizeAltAz'] = self.ui.moveStepSizeAltAz.currentIndex()
        return True

    def setupGui(self):
        """
        :return: success for test
        """

        for name, selectorUI in self.selectorsDropDowns.items():
            selectorUI.clear()
            selectorUI.setView(QListView())
            for headerEntry in self.fitsHeaderKeywords:
                selectorUI.addItem(headerEntry)

        for ui in self.setupMoveClassic:
            ui.clicked.connect(self.moveClassicUI)

        for ui in self.setupMoveAltAz:
            ui.clicked.connect(self.moveAltAzUI)

        self.ui.moveStepSizeAltAz.clear()
        for text in self.setupStepsizes:
            self.ui.moveStepSizeAltAz.addItem(text)
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

    @staticmethod
    def convertHeaderEntry(entry='', fitsKey=''):
        """
        convertHeaderEntry takes the fitsHeader entry and reformat it to a
        reasonable string.

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
            chunk = f'Bin{entry:1.0f}'
        elif fitsKey == 'CCD-TEMP':
            chunk = f'Temp{entry:03.0f}'
        elif fitsKey == 'FRAME':
            chunk = f'{entry}'
        elif fitsKey == 'FILTER':
            chunk = f'{entry}'
        elif fitsKey == 'EXPTIME':
            chunk = f'Exp{entry:1.0f}s'
        else:
            chunk = ''

        return chunk

    def processSelectors(self, fitsHeader=None, selection=''):
        """
        processSelectors takes the selection for a fileName chunk and runs through the
        possible list of valid fits header keys. if there is more than one valid fitsKey,
        it automatically selects only the first on for conversion.

        :param fitsHeader:
        :param selection: str entry from the drop-down selector
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
        renameFile opens the given FITS file and retrieves its header. if valid it
        runs through selectors of the drop-down lists and checks all header keys to
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
        includeSubdirs = self.ui.includeSubdirs.isChecked()
        if not os.path.isdir(pathDir):
            self.msg.emit(2, 'Tools', 'Rename error',
                          'No valid input directory given')
            return False

        if includeSubdirs:
            search = '**/*.fit*'
        else:
            search = '*.fit*'

        numberFiles = self.getNumberFiles(pathDir, search=search)
        if not numberFiles:
            self.msg.emit(2, 'Tools', 'Rename error',
                          'No files to rename')
            return False

        for i, fileName in enumerate(Path(pathDir).glob(search)):
            self.ui.renameProgress.setValue(int(100 * (i + 1) / numberFiles))
            QApplication.processEvents()
            suc = self.renameFile(fileName=fileName)
            if not suc:
                self.msg.emit(2, 'Tools', 'Rename error',
                              f'{fileName} could not be renamed')

        self.msg.emit(0, 'Tools', 'Rename',
                      f'{numberFiles:d} images were renamed')

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

    def stopMoveAll(self):
        """
        :return: success
        """
        for uiR in self.setupMoveClassic:
            self.changeStyleDynamic(uiR, 'running', False)
        self.app.mount.obsSite.stopMoveAll()
        return True

    def moveDuration(self):
        """
        :return:
        """
        if self.ui.moveDuration.currentIndex() == 1:
            sleepAndEvents(10000)
        elif self.ui.moveDuration.currentIndex() == 2:
            sleepAndEvents(5000)
        elif self.ui.moveDuration.currentIndex() == 3:
            sleepAndEvents(2000)
        elif self.ui.moveDuration.currentIndex() == 4:
            sleepAndEvents(1000)
        else:
            return False
        self.stopMoveAll()
        return True

    def moveClassicGameController(self, decVal, raVal):
        """
        :return:
        """
        dirRa = 0
        dirDec = 0
        if raVal < 64:
            dirRa = 1
        elif raVal > 192:
            dirRa = -1
        if decVal < 64:
            dirDec = -1
        elif decVal > 192:
            dirDec = 1

        direction = [dirRa, dirDec]
        if direction == [0, 0]:
            self.stopMoveAll()
        else:
            self.moveClassic(direction)
        return True

    def moveClassicUI(self):
        """
        :return:
        """
        if not self.deviceStat.get('mount'):
            return False

        ui = self.sender()
        direction = self.setupMoveClassic[ui]
        self.moveClassic(direction)
        return True

    def moveClassic(self, direction):
        """
        :return:
        """
        uiList = self.setupMoveClassic
        for uiR in uiList:
            self.changeStyleDynamic(uiR, 'running', False)

        key = next(key for key, value in uiList.items() if value == direction)
        self.changeStyleDynamic(key, 'running', True)

        if direction[0] == 1:
            self.app.mount.obsSite.moveNorth()
        elif direction[0] == -1:
            self.app.mount.obsSite.moveSouth()
        elif direction[0] == 0:
            self.app.mount.obsSite.stopMoveNorth()
            self.app.mount.obsSite.stopMoveSouth()

        if direction[1] == 1:
            self.app.mount.obsSite.moveEast()
        elif direction[1] == -1:
            self.app.mount.obsSite.moveWest()
        elif direction[1] == 0:
            self.app.mount.obsSite.stopMoveEast()
            self.app.mount.obsSite.stopMoveWest()

        self.moveDuration()
        return True

    def setSlewSpeed(self):
        """
        :return: success
        """
        ui = self.sender()
        if ui not in self.slewSpeeds:
            return False

        self.slewSpeeds[ui]()
        return True

    def slewSelectedTargetWithDome(self, slewType='normal'):
        """
        :param slewType:
        :return: success
        """
        azimuthT = self.app.mount.obsSite.AzTarget
        altitudeT = self.app.mount.obsSite.AltTarget

        if azimuthT is None or altitudeT is None:
            return False

        azimuthT = azimuthT.degrees
        altitudeT = altitudeT.degrees

        if self.app.deviceStat['dome']:
            delta = self.app.dome.slewDome(altitude=altitudeT,
                                           azimuth=azimuthT)
            geoStat = 'Geometry corrected' if delta else 'Equal mount'
            text = f'{geoStat}'
            text += ', az: {azimuthT:3.1f} delta: {delta:3.1f}'
            self.msg.emit(0, 'Tools', 'Slewing dome', text)

        suc = self.app.mount.obsSite.startSlewing(slewType=slewType)
        if suc:
            t = f'Az:[{azimuthT:3.1f}], Alt:[{altitudeT:3.1f}]'
            self.msg.emit(0, 'Tools', 'Slewing mount', t)
        else:
            t = f'Cannot slew to Az:[{azimuthT:3.1f}], Alt:[{altitudeT:3.1f}]'
            self.msg.emit(2, 'Tools', 'Slewing error', t)
        return suc

    def slewTargetAltAz(self, alt, az):
        """
        :param alt:
        :param az:
        :return:
        """
        suc = self.app.mount.obsSite.setTargetAltAz(alt_degrees=alt,
                                                    az_degrees=az)
        if not suc:
            t = f'Cannot slew to Az:[{az:3.1f}], Alt:[{alt:3.1f}]'
            self.msg.emit(2, 'Tools', 'Slewing error', t)
            return False

        suc = self.slewSelectedTargetWithDome(slewType='keep')
        return suc

    def moveAltAzDefault(self):
        """
        :return:
        """
        self.targetAlt = None
        self.targetAz = None
        for ui in self.setupMoveAltAz:
            self.changeStyleDynamic(ui, 'running', False)
        return True

    def moveAltAzUI(self):
        """
        :return:
        """
        if not self.deviceStat.get('mount'):
            return False

        ui = self.sender()
        directions = self.setupMoveAltAz[ui]
        self.moveAltAz(directions)

    def moveAltAzGameController(self, value):
        """
        :param value:
        :return:
        """
        if value == 0b00000000:
            direction = [1, 0]
        elif value == 0b00000010:
            direction = [0, 1]
        elif value == 0b00000100:
            direction = [-1, 0]
        elif value == 0b00000110:
            direction = [0, -1]
        else:
            return False
        self.moveAltAz(direction)
        return True

    def moveAltAz(self, direction):
        """
        :param direction:
        :return:
        """
        alt = self.app.mount.obsSite.Alt
        az = self.app.mount.obsSite.Az
        if alt is None or az is None:
            return False

        uiList = self.setupMoveAltAz
        key = next(key for key, value in uiList.items() if value == direction)
        self.changeStyleDynamic(key, 'running', True)

        key = list(self.setupStepsizes)[self.ui.moveStepSizeAltAz.currentIndex()]
        step = self.setupStepsizes[key]

        if self.targetAlt is None or self.targetAz is None:
            targetAlt = self.targetAlt = alt.degrees + direction[0] * step
            targetAz = self.targetAz = az.degrees + direction[1] * step
        else:
            targetAlt = self.targetAlt = self.targetAlt + direction[0] * step
            targetAz = self.targetAz = self.targetAz + direction[1] * step

        targetAz = targetAz % 360
        suc = self.slewTargetAltAz(targetAlt, targetAz)
        return suc

    def setRA(self):
        """
        :return:    success as bool if value could be changed
        """
        dlg = QInputDialog()
        value, ok = dlg.getText(self,
                                'Set telescope RA',
                                'Format: <dd[H] mm ss.s> in hours or <[+]d.d> in '
                                'degrees',
                                QLineEdit.Normal,
                                self.ui.moveCoordinateRa.text(),
                                )
        if not ok:
            return False

        value = convertRaToAngle(value)
        if value is None:
            self.ui.moveCoordinateRaFloat.setText('')
            return False

        text = formatHstrToText(value)
        self.ui.moveCoordinateRa.setText(text)
        self.ui.moveCoordinateRaFloat.setText(f'{value.hours:2.4f}')
        return True

    def setDEC(self):
        """
        :return:    success as bool if value could be changed
        """
        dlg = QInputDialog()
        value, ok = dlg.getText(self,
                                'Set telescope DEC',
                                'Format: <dd[Deg] mm ss.s> or <[+]d.d> in degrees',
                                QLineEdit.Normal,
                                self.ui.moveCoordinateDec.text(),
                                )
        if not ok:
            return False

        value = convertDecToAngle(value)
        if value is None:
            self.ui.moveCoordinateDecFloat.setText('')
            return False

        text = formatDstrToText(value)
        self.ui.moveCoordinateDec.setText(text)
        self.ui.moveCoordinateDecFloat.setText(f'{value.degrees:2.4f}')
        return True

    def moveAltAzAbsolute(self):
        """
        :return:
        """
        alt = self.ui.moveCoordinateAlt.text()
        alt = valueToFloat(alt)
        if alt is None:
            return False

        az = self.ui.moveCoordinateAz.text()
        az = valueToFloat(az)
        if az is None:
            return False

        az = (az + 360) % 360
        suc = self.slewTargetAltAz(alt, az)
        return suc

    def moveRaDecAbsolute(self):
        """
        :return:
        """
        value = self.ui.moveCoordinateRa.text()
        ra = convertRaToAngle(value)
        if ra is None:
            return False

        value = self.ui.moveCoordinateDec.text()
        dec = convertDecToAngle(value)
        if dec is None:
            return False

        timeJD = self.app.mount.obsSite.timeJD
        if timeJD is None:
            return False

        raJNow, decJNow = J2000ToJNow(ra, dec, timeJD)
        self.app.mount.obsSite.setTargetRaDec(ra=raJNow,
                                              dec=decJNow)
        suc = self.slewSelectedTargetWithDome(slewType='keep')
        return suc

    def commandRaw(self):
        """
        :return:
        """
        host = self.app.mount.host
        conn = Connection(host)
        cmd = self.ui.commandInput.text()
        self.ui.commandStatus.clear()
        self.ui.commandOutput.clear()
        startTime = time.time()
        sucSend, sucRec, val = conn.communicateRaw(cmd)
        endTime = time.time()
        delta = endTime - startTime
        self.ui.commandOutput.clear()
        if sucSend:
            t = 'Command OK\n'
            self.ui.commandStatus.insertPlainText(t)
        if sucRec:
            t = f'Receive OK, took {delta:2.3f}s'
            self.ui.commandStatus.insertPlainText(t)
        else:
            t = f'Receive ERROR, took {delta:2.3f}s'
            self.ui.commandStatus.insertPlainText(t)

        self.ui.commandOutput.insertPlainText(val + '\n')
        self.ui.commandOutput.moveCursor(QTextCursor.End)
        return True
