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
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import webbrowser
import time
from functools import partial

# external packages
from PySide6.QtWidgets import QInputDialog, QLineEdit
from PySide6.QtGui import QTextCursor
from skyfield.api import wgs84

# local import
from gui.utilities.toolsQtWidget import MWidget, sleepAndEvents
from gui.utilities.slewInterface import SlewInterface
from mountcontrol.convert import convertLatToAngle, convertLonToAngle
from mountcontrol.convert import convertRaToAngle, convertDecToAngle
from mountcontrol.convert import formatHstrToText, formatDstrToText
from mountcontrol.convert import valueToFloat
from mountcontrol.connection import Connection


class Mount(MWidget, SlewInterface):
    """
    """

    def __init__(self, mainW):
        super().__init__()

        self.mainW = mainW
        self.app = mainW.app
        self.msg = mainW.app.msg
        self.ui = mainW.ui

        self.slewSpeeds = {
            'max': {'button': self.ui.slewSpeedMax,
                    'func': self.app.mount.setting.setSlewSpeedMax},
            'high': {'button': self.ui.slewSpeedHigh,
                     'func': self.app.mount.setting.setSlewSpeedHigh},
            'med': {'button': self.ui.slewSpeedMed,
                    'func': self.app.mount.setting.setSlewSpeedMed},
            'low': {'button': self.ui.slewSpeedLow,
                    'func': self.app.mount.setting.setSlewSpeedLow}}

        self.setupMoveClassic = {
            'N': {'button': self.ui.moveNorth,
                  'coord': [1, 0]},
            'NE': {'button': self.ui.moveNorthEast,
                   'coord': [1, 1]},
            'E': {'button': self.ui.moveEast,
                  'coord': [0, 1]},
            'SE': {'button': self.ui.moveSouthEast,
                   'coord': [-1, 1]},
            'S': {'button': self.ui.moveSouth,
                  'coord': [-1, 0]},
            'SW': {'button': self.ui.moveSouthWest,
                   'coord': [-1, -1]},
            'W': {'button': self.ui.moveWest,
                  'coord': [0, -1]},
            'NW': {'button': self.ui.moveNorthWest,
                   'coord': [1, -1]},
            'STOP': {'button': self.ui.stopMoveAll,
                     'coord': [0, 0]}}

        self.setupMoveAltAz = {
            'N': {'button': self.ui.moveNorthAltAz,
                  'coord': [1, 0]},
            'NE': {'button': self.ui.moveNorthEastAltAz,
                   'coord': [1, 1]},
            'E': {'button': self.ui.moveEastAltAz,
                  'coord': [0, 1]},
            'SE': {'button': self.ui.moveSouthEastAltAz,
                   'coord': [-1, 1]},
            'S': {'button': self.ui.moveSouthAltAz,
                  'coord': [-1, 0]},
            'SW': {'button': self.ui.moveSouthWestAltAz,
                   'coord': [-1, -1]},
            'W': {'button': self.ui.moveWestAltAz,
                  'coord': [-1, 0]},
            'NW': {'button': self.ui.moveNorthWestAltAz,
                   'coord': [1, -1]}}

        self.setupStepsizes = {'Stepsize 0.25°': 0.25,
                               'Stepsize 0.5°': 0.5,
                               'Stepsize 1.0°': 1,
                               'Stepsize 2.0°': 2,
                               'Stepsize 5.0°': 5,
                               'Stepsize 10°': 10,
                               'Stepsize 20°': 20}

        self.targetAlt = None
        self.targetAz = None
        self.slewSpeedSelected = None

        self.ui.mountCommandTable.clicked.connect(self.openCommandProtocol)
        self.ui.mountUpdateTimeDelta.clicked.connect(self.openUpdateTimeDelta)
        self.ui.mountUpdateFirmware.clicked.connect(self.openUpdateFirmware)
        self.ui.mountDocumentation.clicked.connect(self.openMountDocumentation)
        self.app.gameABXY.connect(self.changeParkGameController)
        self.app.gameABXY.connect(self.stopGameController)
        self.app.gameABXY.connect(self.changeTrackingGameController)
        self.app.gameABXY.connect(self.flipMountGameController)
        self.ui.stopMoveAll.clicked.connect(self.stopMoveAll)
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
        self.setupGuiMount()

    def initConfig(self):
        """
        """
        config = self.app.config.get('mainW', {})
        self.ui.coordsJ2000.setChecked(config.get('coordsJ2000', False))
        self.ui.coordsJNow.setChecked(config.get('coordsJNow', False))
        self.ui.slewSpeedMax.setChecked(config.get('slewSpeedMax', True))
        self.ui.slewSpeedHigh.setChecked(config.get('slewSpeedHigh', False))
        self.ui.slewSpeedMed.setChecked(config.get('slewSpeedMed', False))
        self.ui.slewSpeedLow.setChecked(config.get('slewSpeedLow', False))
        self.ui.moveDuration.setCurrentIndex(config.get('moveDuration', 0))
        self.ui.moveStepSizeAltAz.setCurrentIndex(config.get('moveStepSizeAltAz', 0))
        self.mainW.mainWindowAddons.addons['MountSett'].updateLocGUI(self.app.mount.obsSite)

    def storeConfig(self):
        """
        """
        config = self.app.config['mainW']
        config['coordsJ2000'] = self.ui.coordsJ2000.isChecked()
        config['coordsJNow'] = self.ui.coordsJNow.isChecked()
        config['slewSpeedMax'] = self.ui.slewSpeedMax.isChecked()
        config['slewSpeedHigh'] = self.ui.slewSpeedHigh.isChecked()
        config['slewSpeedMed'] = self.ui.slewSpeedMed.isChecked()
        config['slewSpeedLow'] = self.ui.slewSpeedLow.isChecked()
        config['moveDuration'] = self.ui.moveDuration.currentIndex()
        config['moveStepSizeAltAz'] = self.ui.moveStepSizeAltAz.currentIndex()

    def setupIcons(self):
        """
        """
        self.wIcon(self.ui.moveNorth, 'north')
        self.wIcon(self.ui.moveEast, 'east')
        self.wIcon(self.ui.moveSouth, 'south')
        self.wIcon(self.ui.moveWest, 'west')
        self.wIcon(self.ui.moveNorthEast, 'northEast')
        self.wIcon(self.ui.moveNorthWest, 'northWest')
        self.wIcon(self.ui.moveSouthEast, 'southEast')
        self.wIcon(self.ui.moveSouthWest, 'southWest')
        self.wIcon(self.ui.moveNorthAltAz, 'north')
        self.wIcon(self.ui.moveEastAltAz, 'east')
        self.wIcon(self.ui.moveSouthAltAz, 'south')
        self.wIcon(self.ui.moveWestAltAz, 'west')
        self.wIcon(self.ui.moveNorthEastAltAz, 'northEast')
        self.wIcon(self.ui.moveNorthWestAltAz, 'northWest')
        self.wIcon(self.ui.moveSouthEastAltAz, 'southEast')
        self.wIcon(self.ui.moveSouthWestAltAz, 'southWest')
        self.wIcon(self.ui.stopMoveAll, 'stop_m')
        self.wIcon(self.ui.moveAltAzAbsolute, 'target')
        self.wIcon(self.ui.moveRaDecAbsolute, 'target')

    def setupGuiMount(self):
        """
        """
        for direction in self.setupMoveClassic:
            self.setupMoveClassic[direction]['button'].clicked.connect(
                partial(self.moveClassicUI, direction))

        for direction in self.setupMoveAltAz:
            self.setupMoveAltAz[direction]['button'].clicked.connect(
                partial(self.moveAltAzUI, direction))

        for speed in self.slewSpeeds:
            self.slewSpeeds[speed]['button'].clicked.connect(
                partial(self.setSlewSpeed, speed))

        self.ui.moveStepSizeAltAz.clear()
        for text in self.setupStepsizes:
            self.ui.moveStepSizeAltAz.addItem(text)

    def changeTrackingGameController(self, value):
        """
        """
        if value == 0b00000100:
            self.changeTracking()

    def changeTracking(self):
        """
        """
        obs = self.app.mount.obsSite
        if obs.status == 0:
            suc = obs.stopTracking()
            if not suc:
                self.msg.emit(2, 'Mount', 'Command', 'Cannot stop tracking')
            else:
                self.msg.emit(0, 'Mount', 'Command', 'Stopped tracking')
        else:
            suc = obs.startTracking()
            if not suc:
                self.msg.emit(2, 'Mount', 'Command', 'Cannot start tracking')
            else:
                self.msg.emit(0, 'Mount', 'Command', 'Started tracking')
        return True

    def changeParkGameController(self, value):
        """
        """
        if value == 0b00000001:
            self.changePark()

    def changePark(self):
        """
        """
        obs = self.app.mount.obsSite
        if obs.status == 5:
            suc = obs.unpark()
            if not suc:
                self.msg.emit(2, 'Mount', 'Command', 'Cannot unpark mount')
            else:
                self.msg.emit(0, 'Mount', 'Command', 'Mount unparked')
        else:
            suc = obs.park()
            if not suc:
                self.msg.emit(2, 'Mount', 'Command', 'Cannot park mount')
            else:
                self.msg.emit(0, 'Mount', 'Command', 'Mount parked')
        return True

    def setLunarTracking(self):
        """
        """
        if not self.checkMount():
            return False

        sett = self.app.mount.setting
        suc = sett.setLunarTracking()
        if not suc:
            self.msg.emit(2, 'Mount', 'Command', 'Cannot set tracking to Lunar')
        else:
            self.msg.emit(0, 'Mount', 'Command', 'Tracking set to Lunar')
        return suc

    def setSiderealTracking(self):
        """
        """
        if not self.checkMount():
            return False

        sett = self.app.mount.setting
        suc = sett.setSiderealTracking()
        if not suc:
            self.msg.emit(2, 'Mount', 'Command', 'Cannot set tracking to Sidereal')
        else:
            self.msg.emit(0, 'Mount', 'Command', 'Tracking set to Sidereal')
        return suc

    def setSolarTracking(self):
        """
        """
        sett = self.app.mount.setting
        suc = sett.setSolarTracking()
        if not suc:
            self.msg.emit(2, 'Mount', 'Command', 'Cannot set tracking to Solar')
        else:
            self.msg.emit(0, 'Mount', 'Command', 'Tracking set to Solar')
        return suc

    def flipMountGameController(self, value):
        """
        """
        if value == 0b00000010:
            self.flipMount()

    def flipMount(self):
        """
        """
        obs = self.app.mount.obsSite
        suc = obs.flip()
        if not suc:
            self.msg.emit(2, 'Mount', 'Command', 'Cannot flip mount')
        else:
            self.msg.emit(0, 'Mount', 'Command', 'Mount flipped')
        return suc

    def stopGameController(self, value):
        """
        """
        if value == 0b00001000:
            self.stop()

    def stop(self):
        """
        """
        obs = self.app.mount.obsSite
        suc = obs.stop()
        if not suc:
            self.msg.emit(2, 'Mount', 'Command', 'Cannot stop mount')
        else:
            self.msg.emit(0, 'Mount', 'Command', 'Mount stopped')
        return suc

    def openCommandProtocol(self):
        """
        """
        url = 'http://' + self.ui.mountHost.text() + '/manuals/command-protocol.pdf'
        if not webbrowser.open(url, new=0):
            self.msg.emit(2, 'System', 'Mount', 'Browser failed')
        else:
            self.msg.emit(0, 'System', 'Mount', 'command protocol opened')

    def openUpdateTimeDelta(self):
        """
        """
        url = 'http://' + self.ui.mountHost.text() + '/updatetime.html'
        if not webbrowser.open(url, new=0):
            self.msg.emit(2, 'System', 'Mount', 'Browser failed')
        else:
            self.msg.emit(0, 'System', 'Mount', 'update time delta opened')

    def openUpdateFirmware(self):
        """
        """
        url = 'http://' + self.ui.mountHost.text() + '/updatefirmware.html'
        if not webbrowser.open(url, new=0):
            self.msg.emit(2, 'System', 'Mount', 'Browser failed')
        else:
            self.msg.emit(0, 'System', 'Mount', 'update firmware opened')

    def openMountDocumentation(self):
        """
        """
        mountStrings = self.app.mount.firmware.product.split()
        if len(mountStrings) != 2:
            self.msg.emit(2, 'System', 'Mount', 'Browser failed')
            return False
        mountType = mountStrings[1]
        host = self.ui.mountHost.text()
        url = f'http://{host}/manuals/{mountType}-en.pdf'
        if not webbrowser.open(url, new=0):
            self.msg.emit(2, 'System', 'Mount', 'Browser failed')
        else:
            self.msg.emit(0, 'System', 'Mount', 'mount manual opened')
        return True

    def stopMoveAll(self):
        """
        """
        for uiR in self.setupMoveClassic:
            self.changeStyleDynamic(
                self.setupMoveClassic[uiR]['button'], 'running', False)
        self.app.mount.obsSite.stopMoveAll()

    def moveDuration(self):
        """
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

    def moveClassicUI(self, direction):
        """
        """
        if not self.app.deviceStat.get('mount'):
            return False

        self.moveClassic(direction)
        return True

    def moveClassic(self, direction):
        """
        """
        uiList = self.setupMoveClassic
        for key in uiList:
            self.changeStyleDynamic(uiList[key]['button'], 'running', False)

        self.changeStyleDynamic(uiList[direction]['button'], 'running', True)

        coord = uiList[direction]['coord']
        if coord[0] == 1:
            self.app.mount.obsSite.moveNorth()
        elif coord[0] == -1:
            self.app.mount.obsSite.moveSouth()
        elif coord[0] == 0:
            self.app.mount.obsSite.stopMoveNorth()
            self.app.mount.obsSite.stopMoveSouth()

        if coord[1] == 1:
            self.app.mount.obsSite.moveEast()
        elif coord[1] == -1:
            self.app.mount.obsSite.moveWest()
        elif coord[1] == 0:
            self.app.mount.obsSite.stopMoveEast()
            self.app.mount.obsSite.stopMoveWest()

        self.moveDuration()

    def setSlewSpeed(self, speed):
        """
        """
        self.slewSpeeds[speed]['func']()

    def moveAltAzDefault(self):
        """
        :return:
        """
        self.targetAlt = None
        self.targetAz = None
        for key in self.setupMoveAltAz:
            self.changeStyleDynamic(self.setupMoveAltAz[key]['button'], 'running', False)
        return True

    def moveAltAzUI(self, direction):
        """
        """
        if not self.app.deviceStat.get('mount'):
            return

        self.moveAltAz(self.setupMoveAltAz[direction]['coord'])

    def moveAltAzGameController(self, value):
        """
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
        """
        alt = self.app.mount.obsSite.Alt
        az = self.app.mount.obsSite.Az
        if alt is None or az is None:
            return False

        uiList = self.setupMoveAltAz
        self.changeStyleDynamic(uiList[direction]['button'], 'running', True)

        key = list(self.setupStepsizes)[self.ui.moveStepSizeAltAz.currentIndex()]
        step = self.setupStepsizes[key]

        coord = self.setupMoveAltAz[direction]['coord']
        if self.targetAlt is None or self.targetAz is None:
            targetAlt = self.targetAlt = alt.degrees + coord[0] * step
            targetAz = self.targetAz = az.degrees + coord[1] * step
        else:
            targetAlt = self.targetAlt = self.targetAlt + coord[0] * step
            targetAz = self.targetAz = self.targetAz + coord[1] * step

        targetAz = targetAz % 360
        suc = self.slewTargetAltAz(targetAlt, targetAz)
        return suc

    def setRA(self):
        """
        """
        dlg = QInputDialog()
        value, ok = dlg.getText(self.mainW,
                                'Set telescope RA',
                                'Format: <dd[H] mm ss.s> in hours or <[+]d.d> in '
                                'degrees',
                                QLineEdit.EchoMode.Normal,
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
        """
        dlg = QInputDialog()
        value, ok = dlg.getText(self.mainW,
                                'Set telescope DEC',
                                'Format: <dd[Deg] mm ss.s> or <[+]d.d> in degrees',
                                QLineEdit.EchoMode.Normal,
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
        """
        value = self.ui.moveCoordinateRa.text()
        ra = convertRaToAngle(value)
        if ra is None:
            return False

        value = self.ui.moveCoordinateDec.text()
        dec = convertDecToAngle(value)
        if dec is None:
            return False

        suc = self.slewTargetRaDec(ra, dec)
        return suc

    def commandRaw(self):
        """
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
        self.ui.commandOutput.moveCursor(QTextCursor.MoveOperation.End)
