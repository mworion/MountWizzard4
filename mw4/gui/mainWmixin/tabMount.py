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
import webbrowser
import time

# external packages
from PyQt5.QtWidgets import QInputDialog, QLineEdit
from PyQt5.QtGui import QTextCursor
from skyfield.api import wgs84

# local import
from gui.utilities.toolsQtWidget import sleepAndEvents
from gui.utilities.slewInterface import SlewInterface
from gui.mainWmixin.tabMountSett import MountSett
from mountcontrol.convert import convertLatToAngle, convertLonToAngle
from mountcontrol.convert import convertRaToAngle, convertDecToAngle
from mountcontrol.convert import formatHstrToText, formatDstrToText
from mountcontrol.convert import valueToFloat
from mountcontrol.connection import Connection


class Mount(SlewInterface, MountSett):
    """
    """

    def __init__(self):
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
        self.targetAlt = None
        self.targetAz = None
        self.slewSpeedSelected = None

        MountSett.__init__(self)

        self.ui.mountCommandTable.clicked.connect(self.openCommandProtocol)
        self.app.gameABXY.connect(self.changeParkGameController)
        self.app.gameABXY.connect(self.stopGameController)
        self.app.gameABXY.connect(self.changeTrackingGameController)
        self.app.gameABXY.connect(self.flipMountGameController)
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
        self.setupGuiMount()

    def initConfig(self):
        """
        :return: True for test purpose
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
        self.updateLocGUI(self.app.mount.obsSite)
        return True

    def storeConfig(self):
        """
        :return: True for test purpose
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
        return True

    def setupGuiMount(self):
        """
        :return: success for test
        """
        for ui in self.setupMoveClassic:
            ui.clicked.connect(self.moveClassicUI)

        for ui in self.setupMoveAltAz:
            ui.clicked.connect(self.moveAltAzUI)

        self.ui.moveStepSizeAltAz.clear()
        for text in self.setupStepsizes:
            self.ui.moveStepSizeAltAz.addItem(text)
        return True

    def checkMount(self):
        """
        :return:
        """
        isMount = self.deviceStat.get('mount', False)
        isObsSite = self.app.mount.obsSite is not None
        isSetting = self.app.mount.setting is not None
        if not isMount or not isObsSite or not isSetting:
            self.messageDialog(self, 'Error Message',
                               'Value cannot be set!\nMount is not connected!',
                               buttons=['Ok'], iconType=2)
            return False
        else:
            return True

    def changeTrackingGameController(self, value):
        """
        :param value:
        :return:
        """
        if value == 0b00000100:
            self.changeTracking()
        return True

    def changeTracking(self):
        """
        :return:
        """
        if not self.checkMount():
            return False

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
        :return:
        """
        if value == 0b00000001:
            self.changePark()
        return True

    def changePark(self):
        """
        :return:
        """
        if not self.checkMount():
            return False

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
        :return:
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
        :return:
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
        :return:
        """
        if not self.checkMount():
            return False

        sett = self.app.mount.setting
        suc = sett.setSolarTracking()
        if not suc:
            self.msg.emit(2, 'Mount', 'Command', 'Cannot set tracking to Solar')
        else:
            self.msg.emit(0, 'Mount', 'Command', 'Tracking set to Solar')
        return suc

    def flipMountGameController(self, value):
        """
        :param value:
        :return:
        """
        if value == 0b00000010:
            self.flipMount()
        return True

    def flipMount(self):
        """
        :return:
        """
        if not self.checkMount():
            return False

        obs = self.app.mount.obsSite
        suc = obs.flip()
        if not suc:
            self.msg.emit(2, 'Mount', 'Command', 'Cannot flip mount')
        else:
            self.msg.emit(0, 'Mount', 'Command', 'Mount flipped')
        return suc

    def stopGameController(self, value):
        """
        :param value:
        :return:
        """
        if value == 0b00001000:
            self.stop()
        return True

    def stop(self):
        """
        :return:
        """
        if not self.checkMount():
            return False

        obs = self.app.mount.obsSite
        suc = obs.stop()
        if not suc:
            self.msg.emit(2, 'Mount', 'Command', 'Cannot stop mount')
        else:
            self.msg.emit(0, 'Mount', 'Command', 'Mount stopped')
        return suc

    def setMeridianLimitTrack(self):
        """
        :return:    success as bool if value could be changed
        """
        if not self.checkMount():
            return False

        sett = self.app.mount.setting
        actValue = int(sett.meridianLimitTrack)
        dlg = QInputDialog()
        value, ok = dlg.getInt(
            self, 'Set Meridian Limit Track', 'Value (1-30):', actValue, 1, 30, 1)

        if not ok:
            return False
        if sett.setMeridianLimitTrack(value):
            self.msg.emit(0, 'Mount', 'Setting',
                          f'Meridian Lim Track: [{value}]')
            return True
        else:
            self.msg.emit(2, 'Mount', 'Setting',
                          'Meridian Limit Track cannot be set')
            return False

    def setMeridianLimitSlew(self):
        """
        :return:    success as bool if value could be changed
        """
        if not self.checkMount():
            return False

        sett = self.app.mount.setting
        actValue = int(sett.meridianLimitSlew)
        dlg = QInputDialog()
        value, ok = dlg.getInt(
            self, 'Set Meridian Limit Slew', 'Value (0-30):', actValue, 0, 30, 1)

        if not ok:
            return False
        if sett.setMeridianLimitSlew(value):
            self.msg.emit(0, 'Mount', 'Setting',
                          f'Meridian Lim Slew: [{value}]')
            return True
        else:
            self.msg.emit(2, 'Mount', 'Setting',
                          'Meridian Limit Slew cannot be set')
            return False

    def setHorizonLimitHigh(self):
        """
        :return:    success as bool if value could be changed
        """
        if not self.checkMount():
            return False

        sett = self.app.mount.setting
        actValue = int(sett.horizonLimitHigh)
        dlg = QInputDialog()
        value, ok = dlg.getInt(
            self, 'Set Horizon Limit High', 'Value (0-90):', actValue, 0, 90, 1)

        if not ok:
            return False
        if sett.setHorizonLimitHigh(value):
            self.msg.emit(0, 'Mount', 'Setting',
                          f'Horizon Limit High: [{value}]')
            return True
        else:
            self.msg.emit(2, 'Mount', 'Setting',
                          'Horizon Limit High cannot be set')
            return False

    def setHorizonLimitLow(self):
        """
        :return:    success as bool if value could be changed
        """
        if not self.checkMount():
            return False

        sett = self.app.mount.setting
        actValue = int(sett.horizonLimitLow)
        dlg = QInputDialog()
        value, ok = dlg.getInt(
            self, 'Set Horizon Limit Low', 'Value (-5 - 90):', actValue, -5, 90, 1,)

        if not ok:
            return False
        if sett.setHorizonLimitLow(value):
            self.msg.emit(0, 'Mount', 'Setting', f'Horizon Limit Low: [{value}]')
            return True
        else:
            self.msg.emit(2, 'Mount', 'Setting', 'Horizon Limit Low cannot be set')
            return False

    def setSlewRate(self):
        """
        :return:    success as bool if value could be changed
        """
        if not self.checkMount():
            return False

        sett = self.app.mount.setting
        actValue = int(sett.slewRate)
        minRate = int(sett.slewRateMin)
        maxRate = int(sett.slewRateMax)
        dlg = QInputDialog()
        value, ok = dlg.getInt(
            self, 'Set Slew Rate', f'Value ({minRate}...{maxRate}):',
            actValue, minRate, maxRate, 1)

        if not ok:
            return False
        if sett.setSlewRate(value):
            self.msg.emit(0, 'Mount', 'Setting', f'Slew Rate: [{value}]')
            return True
        else:
            self.msg.emit(2, 'Mount', 'Setting', 'Slew Rate cannot be set')
            return False

    def setLocationValues(self, lat=None, lon=None, elev=None):
        """
        :param lat:
        :param lon:
        :param elev:
        :return:
        """
        obs = self.app.mount.obsSite
        loc = obs.location
        lat = loc.latitude if lat is None else lat
        lon = loc.longitude if lon is None else lon
        elev = loc.elevation.m if elev is None else elev

        topo = wgs84.latlon(longitude_degrees=lon.degrees,
                            latitude_degrees=lat.degrees,
                            elevation_m=elev)

        if self.app.deviceStat['mount']:
            obs.setLocation(topo)
            self.app.mount.getLocation()
        else:
            obs.location = topo
            self.updateLocGUI(self.app.mount.obsSite)

        t = f'Location set to:     [{lat.degrees:3.2f} deg, '
        t += f'{lon.degrees:3.2f} deg, {elev:4.1f} m]'
        self.msg.emit(0, 'Mount', 'Setting', t)
        return True

    def setLongitude(self):
        """
        :return:    success as bool if value could be changed
        """
        obs = self.app.mount.obsSite
        if obs.location is None:
            return False

        dlg = QInputDialog()
        value, ok = dlg.getText(self,
                                'Set Site Longitude',
                                'Format: <dd[EW] mm ss.s> or <[+-]d.d>, East is '
                                'positive',
                                QLineEdit.Normal,
                                self.ui.siteLongitude.text())
        if not ok:
            return False

        value = convertLonToAngle(value)
        self.setLocationValues(lon=value)
        return True

    def setLatitude(self):
        """
        :return:    success as bool if value could be changed
        """
        obs = self.app.mount.obsSite
        if obs.location is None:
            return False

        dlg = QInputDialog()
        value, ok = dlg.getText(self,
                                'Set Site Latitude',
                                'Format: <dd[SN] mm ss.s> or <[+-]d.d>',
                                QLineEdit.Normal,
                                self.ui.siteLatitude.text())
        if not ok:
            return False

        value = convertLatToAngle(value)
        self.setLocationValues(lat=value)
        return True

    def setElevation(self):
        """
        :return:    success as bool if value could be changed
        """
        obs = self.app.mount.obsSite
        if obs.location is None:
            return False

        dlg = QInputDialog()
        value, ok = dlg.getDouble(
            self, 'Set Site Elevation', 'Format: d.d',
            obs.location.elevation.m, 0, 8000, 1)
        if not ok:
            return False

        self.setLocationValues(elev=value)
        return True

    def setUnattendedFlip(self):
        """
        :return:    success as bool if value could be changed
        """
        if not self.checkMount():
            return False

        sett = self.app.mount.setting
        dlg = QInputDialog()
        value, ok = dlg.getItem(
            self, 'Set Unattended Flip', 'Value: On / Off',
            ['ON', 'OFF'], 0, False)
        if not ok:
            return False
        suc = sett.setUnattendedFlip(value == 'ON')
        if suc:
            self.msg.emit(0, 'Mount', 'Setting', f'Unattended flip: [{value}]')
        else:
            self.msg.emit(2, 'Mount', 'Setting', 'Unattended flip cannot be set')
        return suc

    def setDualAxisTracking(self):
        """
        :return:    success as bool if value could be changed
        """
        if not self.checkMount():
            return False

        sett = self.app.mount.setting
        dlg = QInputDialog()
        value, ok = dlg.getItem(self,
                                'Set Dual Axis Tracking',
                                'Value: On / Off',
                                ['ON', 'OFF'],
                                0, False)
        if not ok:
            return False

        suc = sett.setDualAxisTracking(value == 'ON')
        if suc:
            self.msg.emit(0, 'Mount', 'Setting', f'DualAxis tracking: [{value}]')
        else:
            self.msg.emit(2, 'Mount', 'Setting', 'DualAxis tracking cannot be set')
        return suc

    def setWOL(self):
        """
        :return:    success as bool if value could be changed
        """
        if not self.checkMount():
            return False

        sett = self.app.mount.setting
        dlg = QInputDialog()
        value, ok = dlg.getItem(self,
                                'Set Wake On Lan',
                                'Value: On / Off',
                                ['ON', 'OFF'],
                                0, False)
        if not ok:
            return False

        suc = sett.setWOL(value == 'ON')
        if suc:
            self.msg.emit(0, 'Mount', 'Setting', f'Wake On Lan: [{value}]')
        else:
            self.msg.emit(2, 'Mount', 'Setting', 'Wake On Lan cannot be set')
        return suc

    def setRefractionTemp(self):
        """
        :return:
        """
        if not self.checkMount():
            return False

        sett = self.app.mount.setting
        actValue = sett.refractionTemp
        minVal = -40
        maxVal = 75
        dlg = QInputDialog()
        value, ok = dlg.getDouble(
            self, 'Set Refraction Temperature', f'Value ({minVal}...{maxVal}):',
            actValue, minVal, maxVal, 1)

        if not ok:
            return False
        if sett.setRefractionTemp(value):
            self.msg.emit(0, 'Mount', 'Setting', f'Refraction Temp: [{value}]')
            return True
        else:
            self.msg.emit(2, 'Mount', 'Setting', 'Refraction Temp cannot be set')
            return False

    def setRefractionPress(self):
        """
        :return:
        """
        if not self.checkMount():
            return False

        sett = self.app.mount.setting
        actValue = sett.refractionPress
        minVal = 500
        maxVal = 1300
        dlg = QInputDialog()
        value, ok = dlg.getDouble(
            self, 'Set Refraction Pressure', f'Value ({minVal}...{maxVal}):',
            actValue, minVal, maxVal, 1)

        if not ok:
            return False
        if sett.setRefractionPress(value):
            self.msg.emit(0, 'Mount', 'Setting', f'Refraction Press: [{value}]')
            return True
        else:
            self.msg.emit(2, 'Mount', 'Setting', 'Refraction Press cannot be set')
            return False

    def setRefraction(self):
        """
        :return:    success as bool if value could be changed
        """
        if not self.checkMount():
            return False

        sett = self.app.mount.setting
        dlg = QInputDialog()
        value, ok = dlg.getItem(self,
                                'Set Refraction Correction',
                                'Value: On / Off',
                                ['ON', 'OFF'],
                                0, False)
        if not ok:
            return False

        suc = sett.setRefraction(value == 'ON')
        if suc:
            self.msg.emit(0, 'Mount', 'Setting',
                          f'Refraction corr: [{value}]')
        else:
            self.msg.emit(2, 'Mount', 'Setting',
                          'Refraction correction cannot be set')
        return suc

    def showOffset(self):
        """
        :return:
        """
        connectSync = self.ui.clockSync.isChecked()
        delta = self.app.mount.obsSite.timeDiff * 1000
        ui = self.ui.timeDeltaPC2Mount
        if connectSync:
            text = f'{delta:4.0f}'
        else:
            text = '-'
        ui.setText(text)

        if not connectSync:
            self.changeStyleDynamic(ui, 'color', '')
        elif abs(delta) < 100:
            self.changeStyleDynamic(ui, 'color', '')
        elif abs(delta) < 500:
            self.changeStyleDynamic(ui, 'color', 'yellow')
        else:
            self.changeStyleDynamic(ui, 'color', 'red')

        timeJD = self.app.mount.obsSite.timeJD
        if timeJD is not None:
            text = timeJD.utc_strftime('%H:%M:%S')
            self.ui.timeUTC.setText(text)

        return True

    def openCommandProtocol(self):
        """
        :return:
        """
        url = 'http://' + self.ui.mountHost.text() + '/manuals/command-protocol.pdf'
        if not webbrowser.open(url, new=0):
            self.msg.emit(2, 'System', 'Mount', 'Browser failed')
        else:
            self.msg.emit(0, 'System', 'Mount', '10micron opened')
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

        suc = self.slewTargetRaDec(ra, dec)
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
