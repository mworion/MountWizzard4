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
import datetime

# external packages
import PyQt5.QtCore
import PyQt5.QtWidgets
from skyfield.api import wgs84

# local import
from base import transform
from mountcontrol.convert import convertLatToAngle, convertLonToAngle
from mountcontrol.convert import formatLatToText, formatLonToText


class Mount(object):
    """
    """

    def __init__(self):
        self.typeConnectionTexts = ['RS-232',
                                    'GPS/RS-232',
                                    'LAN',
                                    'WiFi',
                                    ]

        ms = self.app.mount.signals
        ms.locationDone.connect(self.updateLocGUI)
        ms.pointDone.connect(self.updatePointGUI)
        ms.settingDone.connect(self.updateSettingGUI)
        self.app.update1s.connect(self.showOffset)

        self.ui.park.clicked.connect(self.changePark)
        self.ui.flipMount.clicked.connect(self.flipMount)
        self.ui.tracking.clicked.connect(self.changeTracking)
        self.ui.setLunarTracking.clicked.connect(self.setLunarTracking)
        self.ui.setSiderealTracking.clicked.connect(self.setSiderealTracking)
        self.ui.setSolarTracking.clicked.connect(self.setSolarTracking)
        self.ui.stop.clicked.connect(self.stop)

        self.clickable(self.ui.meridianLimitTrack).connect(self.setMeridianLimitTrack)
        self.clickable(self.ui.meridianLimitSlew).connect(self.setMeridianLimitSlew)
        self.clickable(self.ui.horizonLimitHigh).connect(self.setHorizonLimitHigh)
        self.clickable(self.ui.horizonLimitLow).connect(self.setHorizonLimitLow)
        self.clickable(self.ui.slewRate).connect(self.setSlewRate)
        self.clickable(self.ui.siteLatitude).connect(self.setLatitude)
        self.clickable(self.ui.siteLongitude).connect(self.setLongitude)
        self.clickable(self.ui.siteElevation).connect(self.setElevation)
        self.clickable(self.ui.statusUnattendedFlip).connect(self.setUnattendedFlip)
        self.clickable(self.ui.statusDualAxisTracking).connect(self.setDualAxisTracking)
        self.clickable(self.ui.statusWOL).connect(self.setWOL)
        self.clickable(self.ui.statusRefraction).connect(self.setRefraction)
        self.ui.virtualStop.raise_()
        self.ui.virtualStop.clicked.connect(self.virtualStop)

    def initConfig(self):
        """
        :return: True for test purpose
        """
        config = self.app.config.get('mainW', {})
        self.ui.checkJ2000.setChecked(config.get('checkJ2000', False))
        self.ui.checkJNow.setChecked(config.get('checkJNow', False))
        self.updateLocGUI(self.app.mount.obsSite)
        return True

    def storeConfig(self):
        """
        :return: True for test purpose
        """
        config = self.app.config['mainW']
        config['checkJ2000'] = self.ui.checkJ2000.isChecked()
        config['checkJNow'] = self.ui.checkJNow.isChecked()
        return True

    def updatePointGUI(self, obs):
        """
        :param obs:
        :return:    True if ok for testing
        """
        isJ2000 = self.ui.checkJ2000.isChecked()
        isValid = obs.raJNow is not None
        isValid = isValid and obs.decJNow is not None
        isValid = isValid and obs.timeJD is not None
        if isJ2000 and isValid:
            ra, dec = transform.JNowToJ2000(obs.raJNow, obs.decJNow, obs.timeJD)
        else:
            ra = obs.raJNow
            dec = obs.decJNow

        self.guiSetText(self.ui.RA, 'HSTR', ra)
        self.guiSetText(self.ui.RAfloat, 'H5.4f', ra)
        self.guiSetText(self.ui.DEC, 'DSTR', dec)
        self.guiSetText(self.ui.DECfloat, 'D5.4f', dec)
        self.guiSetText(self.ui.HA, 'HSTR', obs.haJNow)
        self.guiSetText(self.ui.HAfloat, 'H5.4f', obs.haJNow)
        self.guiSetText(self.ui.ALT, 'D5.2f', obs.Alt)
        self.guiSetText(self.ui.AZ, 'D5.2f', obs.Az)
        self.guiSetText(self.ui.pierside, 's', obs.pierside)
        self.guiSetText(self.ui.timeSidereal, 'HSTR', obs.timeSidereal)
        return True

    def updateSettingGUI(self, sett):
        """
        :param sett:
        :return:    True if ok for testing
        """
        ui = self.ui.UTCExpire
        self.guiSetText(ui, 's', sett.UTCExpire)
        if sett.UTCExpire is not None:
            now = datetime.datetime.now()
            expire = datetime.datetime.strptime(sett.UTCExpire, '%Y-%m-%d')
            deltaYellow = datetime.timedelta(days=30)
            if now > expire:
                self.changeStyleDynamic(ui, 'char', 'red')
                self.changeStyleDynamic(ui, 'color', 'red')
            elif now > expire - deltaYellow:
                self.changeStyleDynamic(ui, 'char', '')
                self.changeStyleDynamic(ui, 'color', 'red')
            else:
                self.changeStyleDynamic(ui, 'color', '')
                self.changeStyleDynamic(ui, 'char', '')

        ui = self.ui.statusUnattendedFlip
        self.guiSetText(ui, 's', sett.statusUnattendedFlip)
        self.guiSetStyle(ui, 'status', sett.statusUnattendedFlip, ['', 'on', ''])

        ui = self.ui.statusDualAxisTracking
        self.guiSetText(ui, 's', sett.statusDualAxisTracking)
        self.guiSetStyle(ui, 'status', sett.statusDualAxisTracking, ['', 'on', ''])

        ui = self.ui.statusRefraction
        self.guiSetText(ui, 's', sett.statusRefraction)
        self.guiSetStyle(ui, 'status', sett.statusRefraction, ['', 'on', ''])

        ui = self.ui.statusGPSSynced
        self.guiSetText(ui, 's', sett.gpsSynced)
        self.guiSetStyle(ui, 'status', sett.gpsSynced, ['', 'on', ''])

        ui = self.ui.statusWOL
        self.guiSetText(ui, 's', sett.wakeOnLan)
        self.guiSetStyle(ui, 'status', sett.wakeOnLan, ['', 'on', ''])

        ui = self.ui.statusWebInterface
        self.guiSetText(ui, 's', sett.webInterfaceStat)
        self.guiSetStyle(ui, 'status', sett.webInterfaceStat, ['', 'on', ''])

        if sett.typeConnection is not None:
            text = self.typeConnectionTexts[sett.typeConnection]
            self.ui.mountTypeConnection.setText(text)

        self.guiSetText(self.ui.slewRate, '2.0f', sett.slewRate)
        self.guiSetText(self.ui.timeToFlip, '3.0f', sett.timeToFlip)
        self.guiSetText(self.ui.timeToMeridian, '3.0f', sett.timeToMeridian())
        self.guiSetText(self.ui.refractionTemp, '+4.1f', sett.refractionTemp)
        self.guiSetText(self.ui.refractionTemp1, '+4.1f', sett.refractionTemp)
        self.guiSetText(self.ui.refractionPress, '6.1f', sett.refractionPress)
        self.guiSetText(self.ui.refractionPress1, '6.1f', sett.refractionPress)
        self.guiSetText(self.ui.meridianLimitTrack, '3.0f', sett.meridianLimitTrack)
        self.guiSetText(self.ui.meridianLimitSlew, '3.0f', sett.meridianLimitSlew)
        self.guiSetText(self.ui.horizonLimitLow, '3.0f', sett.horizonLimitLow)
        self.guiSetText(self.ui.horizonLimitHigh, '3.0f', sett.horizonLimitHigh)

        if self.app.mount.obsSite.status is None:
            self.changeStyleDynamic(self.ui.followSat, 'running', False)
            self.changeStyleDynamic(self.ui.setLunarTracking, 'running', False)
            self.changeStyleDynamic(self.ui.setSiderealTracking, 'running', False)
            self.changeStyleDynamic(self.ui.setSolarTracking, 'running', False)

        elif self.app.mount.obsSite.status == 10:
            self.changeStyleDynamic(self.ui.followSat, 'running', True)
            self.changeStyleDynamic(self.ui.setLunarTracking, 'running', False)
            self.changeStyleDynamic(self.ui.setSiderealTracking, 'running', False)
            self.changeStyleDynamic(self.ui.setSolarTracking, 'running', False)

        elif sett.checkRateLunar():
            self.changeStyleDynamic(self.ui.followSat, 'running', False)
            self.changeStyleDynamic(self.ui.setLunarTracking, 'running', True)
            self.changeStyleDynamic(self.ui.setSiderealTracking, 'running', False)
            self.changeStyleDynamic(self.ui.setSolarTracking, 'running', False)

        elif sett.checkRateSidereal():
            self.changeStyleDynamic(self.ui.followSat, 'running', False)
            self.changeStyleDynamic(self.ui.setLunarTracking, 'running', False)
            self.changeStyleDynamic(self.ui.setSiderealTracking, 'running', True)
            self.changeStyleDynamic(self.ui.setSolarTracking, 'running', False)

        elif sett.checkRateSolar():
            self.changeStyleDynamic(self.ui.followSat, 'running', False)
            self.changeStyleDynamic(self.ui.setLunarTracking, 'running', False)
            self.changeStyleDynamic(self.ui.setSiderealTracking, 'running', False)
            self.changeStyleDynamic(self.ui.setSolarTracking, 'running', True)
        return True

    def updateLocGUI(self, obs):
        """
        :param obs:
        :return:    True if ok for testing
        """
        if obs is None:
            return False
        location = obs.location
        if location is None:
            return False

        self.ui.siteLongitude.setText(formatLonToText(location.longitude))
        self.ui.siteLatitude.setText(formatLatToText(location.latitude))
        self.ui.siteElevation.setText(str(location.elevation.m))
        return True

    def checkMount(self):
        """
        :return:
        """
        msg = PyQt5.QtWidgets.QMessageBox
        isMount = self.deviceStat.get('mount', False)
        isObsSite = self.app.mount.obsSite is not None
        isSetting = self.app.mount.setting is not None
        if not isMount or not isObsSite or not isSetting:
            msg.critical(self,
                         'Error Message',
                         'Value cannot be set when mount not connected !')
            return False
        else:
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
                self.app.message.emit('Cannot stop tracking', 2)
            else:
                self.app.message.emit('Stopped tracking', 0)

        else:
            suc = obs.startTracking()
            if not suc:
                self.app.message.emit('Cannot start tracking', 2)
            else:
                self.app.message.emit('Started tracking', 0)

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
                self.app.message.emit('Cannot unpark mount', 2)
            else:
                self.app.message.emit('Mount unparked', 0)
        else:
            suc = obs.park()
            if not suc:
                self.app.message.emit('Cannot park mount', 2)
            else:
                self.app.message.emit('Mount parked', 0)

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
            self.app.message.emit('Cannot set tracking to Lunar', 2)
            return False
        else:
            self.app.message.emit('Tracking set to Lunar', 0)
            return True

    def setSiderealTracking(self):
        """
        :return:
        """
        if not self.checkMount():
            return False

        sett = self.app.mount.setting
        suc = sett.setSiderealTracking()
        if not suc:
            self.app.message.emit('Cannot set tracking to Sidereal', 2)
        else:
            self.app.message.emit('Tracking set to Sidereal', 0)
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
            self.app.message.emit('Cannot set tracking to Solar', 2)
            return False
        else:
            self.app.message.emit('Tracking set to Solar', 0)
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
            self.app.message.emit('Cannot flip mount', 2)
            return False
        else:
            self.app.message.emit('Mount flipped', 0)
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
            self.app.message.emit('Cannot stop mount', 2)
            return False
        else:
            self.app.message.emit('Mount stopped', 0)
            return True

    def virtualStop(self):
        """
        :return:
        """
        if self.ui.activateVirtualStop.isChecked():
            self.stop()

    def setMeridianLimitTrack(self):
        """
        :return:    success as bool if value could be changed
        """
        if not self.checkMount():
            return False

        sett = self.app.mount.setting
        actValue = sett.meridianLimitTrack
        dlg = PyQt5.QtWidgets.QInputDialog()
        value, ok = dlg.getInt(self,
                               'Set Meridian Limit Track',
                               'Value (1-30):',
                               actValue,
                               1,
                               30,
                               1,
                               )

        if not ok:
            return False
        if sett.setMeridianLimitTrack(value):
            self.app.message.emit(f'Meridian Lim Track: [{value}]', 0)
            return True
        else:
            self.app.message.emit('Meridian Limit Track cannot be set', 2)
            return False

    def setMeridianLimitSlew(self):
        """
        :return:    success as bool if value could be changed
        """
        if not self.checkMount():
            return False

        sett = self.app.mount.setting
        actValue = sett.meridianLimitSlew
        dlg = PyQt5.QtWidgets.QInputDialog()
        value, ok = dlg.getInt(self,
                               'Set Meridian Limit Slew',
                               'Value (0-30):',
                               actValue,
                               0,
                               30,
                               1,
                               )

        if not ok:
            return False
        if sett.setMeridianLimitSlew(value):
            self.app.message.emit(f'Meridian Limit Slew: [{value}]', 0)
            return True
        else:
            self.app.message.emit('Meridian Limit Slew cannot be set', 2)
            return False

    def setHorizonLimitHigh(self):
        """
        :return:    success as bool if value could be changed
        """
        if not self.checkMount():
            return False

        sett = self.app.mount.setting
        actValue = sett.horizonLimitHigh
        dlg = PyQt5.QtWidgets.QInputDialog()
        value, ok = dlg.getInt(self,
                               'Set Horizon Limit High',
                               'Value (0-90):',
                               actValue,
                               0,
                               90,
                               1,
                               )

        if not ok:
            return False
        if sett.setHorizonLimitHigh(value):
            self.app.message.emit(f'Horizon Limit High:  [{value}]', 0)
            return True
        else:
            self.app.message.emit('Horizon Limit High cannot be set', 2)
            return False

    def setHorizonLimitLow(self):
        """
        :return:    success as bool if value could be changed
        """
        if not self.checkMount():
            return False

        sett = self.app.mount.setting
        actValue = sett.horizonLimitLow
        dlg = PyQt5.QtWidgets.QInputDialog()
        value, ok = dlg.getInt(self,
                               'Set Horizon Limit Low',
                               'Value (-5 - 90):',
                               actValue,
                               -5,
                               90,
                               1,
                               )

        if not ok:
            return False
        if sett.setHorizonLimitLow(value):
            self.app.message.emit(f'Horizon Limit Low:   [{value}]', 0)
            return True
        else:
            self.app.message.emit('Horizon Limit Low cannot be set', 2)
            return False

    def setSlewRate(self):
        """
        :return:    success as bool if value could be changed
        """
        if not self.checkMount():
            return False

        sett = self.app.mount.setting
        actValue = sett.slewRate
        minRate = sett.slewRateMin
        maxRate = sett.slewRateMax
        dlg = PyQt5.QtWidgets.QInputDialog()
        value, ok = dlg.getInt(self,
                               'Set Slew Rate',
                               f'Value ({minRate}-{maxRate}):',
                               actValue,
                               minRate,
                               maxRate,
                               1,
                               )

        if not ok:
            return False
        if sett.setSlewRate(value):
            self.app.message.emit(f'Slew Rate:           [{value}]', 0)
            return True
        else:
            self.app.message.emit('Slew Rate cannot be set', 2)
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
        self.app.message.emit(t, 0)
        return True

    def setLongitude(self):
        """
        :return:    success as bool if value could be changed
        """
        obs = self.app.mount.obsSite
        if obs.location is None:
            return False

        dlg = PyQt5.QtWidgets.QInputDialog()
        value, ok = dlg.getText(self,
                                'Set Site Longitude',
                                'Format: <dd[EW] mm ss.s> or <[+-]d.d>, East is '
                                'positive',
                                PyQt5.QtWidgets.QLineEdit.Normal,
                                self.ui.siteLongitude.text(),
                                )
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

        dlg = PyQt5.QtWidgets.QInputDialog()
        value, ok = dlg.getText(self,
                                'Set Site Latitude',
                                'Format: <dd[SN] mm ss.s> or <[+-]d.d>',
                                PyQt5.QtWidgets.QLineEdit.Normal,
                                self.ui.siteLatitude.text(),
                                )
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

        dlg = PyQt5.QtWidgets.QInputDialog()
        value, ok = dlg.getDouble(self,
                                  'Set Site Elevation',
                                  'Format: d.d',
                                  obs.location.elevation.m,
                                  0,
                                  8000,
                                  1,
                                  )
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
        dlg = PyQt5.QtWidgets.QInputDialog()
        value, ok = dlg.getItem(self,
                                'Set Unattended Flip',
                                'Value: On / Off',
                                ['ON', 'OFF'],
                                0,
                                False,
                                )
        if not ok:
            return False
        suc = sett.setUnattendedFlip(value == 'ON')
        if suc:
            self.app.message.emit(f'Unattended flip      [{value}]', 0)
        else:
            self.app.message.emit('Unattended flip cannot be set', 2)
        return suc

    def setDualAxisTracking(self):
        """
        :return:    success as bool if value could be changed
        """
        if not self.checkMount():
            return False

        sett = self.app.mount.setting
        dlg = PyQt5.QtWidgets.QInputDialog()
        value, ok = dlg.getItem(self,
                                'Set Dual Axis Tracking',
                                'Value: On / Off',
                                ['ON', 'OFF'],
                                0,
                                False,
                                )
        if not ok:
            return False

        suc = sett.setDualAxisTracking(value == 'ON')
        if suc:
            self.app.message.emit(f'DualAxis tracking    [{value}]', 0)
        else:
            self.app.message.emit('DualAxis tracking cannot be set', 2)
        return suc

    def setWOL(self):
        """
        :return:    success as bool if value could be changed
        """
        if not self.checkMount():
            return False

        sett = self.app.mount.setting
        dlg = PyQt5.QtWidgets.QInputDialog()
        value, ok = dlg.getItem(self,
                                'Set Wake On Lan',
                                'Value: On / Off',
                                ['ON', 'OFF'],
                                0,
                                False,
                                )
        if not ok:
            return False

        suc = sett.setWOL(value == 'ON')
        if suc:
            self.app.message.emit(f'Wake On Lan          [{value}]', 0)
        else:
            self.app.message.emit('Wake On Lan cannot be set', 2)
        return suc

    def setRefraction(self):
        """
        :return:    success as bool if value could be changed
        """
        if not self.checkMount():
            return False

        sett = self.app.mount.setting
        dlg = PyQt5.QtWidgets.QInputDialog()
        value, ok = dlg.getItem(self,
                                'Set Refraction Correction',
                                'Value: On / Off',
                                ['ON', 'OFF'],
                                0,
                                False,
                                )
        if not ok:
            return False

        suc = sett.setRefraction(value == 'ON')
        if suc:
            self.app.message.emit(f'Refraction corr.     [{value}]', 0)
        else:
            self.app.message.emit('Refraction correction cannot be set', 2)
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
            self.changeStyleDynamic(ui, 'char', '')
            self.changeStyleDynamic(ui, 'color', '')
        elif abs(delta) < 100:
            self.changeStyleDynamic(ui, 'char', '')
            self.changeStyleDynamic(ui, 'color', '')
        elif abs(delta) < 500:
            self.changeStyleDynamic(ui, 'char', 'yellow')
            self.changeStyleDynamic(ui, 'color', '')
        else:
            self.changeStyleDynamic(ui, 'char', 'red')
            self.changeStyleDynamic(ui, 'color', 'red')
        return True
