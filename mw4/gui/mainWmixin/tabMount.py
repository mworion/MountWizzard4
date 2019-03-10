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
# Python  v3.6.7
#
# Michael Würtenberger
# (c) 2018
#
# Licence APL2.0
#
###########################################################
# standard libraries
import datetime
# external packages
import PyQt5.QtCore
import PyQt5.QtWidgets
import PyQt5.uic
# local import
from mw4.base import transform


class Mount(object):
    """
    the main window class handles the main menu as well as the show and no show part of
    any other window. all necessary processing for functions of that gui will be linked
    to this class. therefore window classes will have a threadpool for managing async
    processing if needed.
    """

    def __init__(self):
        ms = self.app.mount.signals
        ms.pointDone.connect(self.updatePointGUI)
        ms.settDone.connect(self.updateSetStatGUI)
        ms.settDone.connect(self.updateTrackingGui)

        self.ui.park.clicked.connect(self.changePark)
        self.ui.tracking.clicked.connect(self.changeTracking)
        self.ui.setLunarTracking.clicked.connect(self.setLunarTracking)
        self.ui.setSiderealTracking.clicked.connect(self.setSiderealTracking)
        self.ui.setSolarTracking.clicked.connect(self.setSolarTracking)
        self.ui.stop.clicked.connect(self.stop)

    def initConfig(self):
        config = self.app.config['mainW']
        self.ui.checkJ2000.setChecked(config.get('checkJ2000', False))
        self.ui.checkJNow.setChecked(config.get('checkJNow', False))
        return True

    def storeConfig(self):
        config = self.app.config['mainW']
        config['checkJ2000'] = self.ui.checkJ2000.isChecked()
        config['checkJNow'] = self.ui.checkJNow.isChecked()
        return True

    def setupIcons(self):
        """
        setupIcons add icon from standard library to certain buttons for improving the
        gui of the app.

        :return:    True if success for test
        """
        self.wIcon(self.ui.stop, PyQt5.QtWidgets.QStyle.SP_MessageBoxWarning)
        return True

    def clearGUI(self):
        """
        clearGUI rewrites the gui in case of a special event needed for clearing up

        :return: success for test
        """
        self.updatePointGUI()
        self.updateTrackingGui()
        return True

    def updatePointGUI(self):
        """
        updatePointGUI update the gui upon events triggered be the reception of new data
        from the mount. the mount data is polled, so we use this signal as well for the
        update process.

        :return:    True if ok for testing
        """
        obs = self.app.mount.obsSite

        if obs.Alt is not None:
            self.ui.ALT.setText('{0:5.2f}'.format(obs.Alt.degrees))
        else:
            self.ui.ALT.setText('-')

        if obs.Az is not None:
            self.ui.AZ.setText('{0:5.2f}'.format(obs.Az.degrees))
        else:
            self.ui.AZ.setText('-')

        ra = obs.raJNow
        dec = obs.decJNow
        if self.ui.checkJ2000.isChecked():
            if ra is not None and dec is not None and obs.timeJD is not None:
                ra, dec = transform.JNowToJ2000(ra, dec, obs.timeJD)

        if ra is not None:
            raFormat = '{0:02.0f}:{1:02.0f}:{2:02.0f}'
            raText = raFormat.format(*ra.hms())
            self.ui.RA.setText(raText)
        else:
            self.ui.RA.setText('-')

        if dec is not None:
            decFormat = '{sign}{0:02.0f}:{1:02.0f}:{2:02.0f}'
            decText = decFormat.format(*dec.signed_dms()[1:4],
                                       sign='+' if dec.degrees > 0 else '-')
            self.ui.DEC.setText(decText)
        else:
            self.ui.DEC.setText('-')

        if obs.timeJD is not None:
            self.ui.timeJD.setText(obs.timeJD.utc_strftime('%H:%M:%S'))
        else:
            self.ui.timeJD.setText('-')

        if obs.pierside is not None:
            self.ui.pierside.setText('WEST' if obs.pierside == 'W' else 'EAST')
        else:
            self.ui.pierside.setText('-')

        if obs.timeSidereal is not None:
            self.ui.timeSidereal.setText(obs.timeSidereal[:8])
        else:
            self.ui.timeSidereal.setText('-')

        return True

    def updateSetStatGUI(self):
        """
        updateSetStatGUI update the gui upon events triggered be the reception of new
        settings from the mount. the mount data is polled, so we use this signal as well
        for the update process.

        :return:    True if ok for testing
        """

        sett = self.app.mount.sett

        if sett.UTCExpire is not None:
            ui = self.ui.UTCExpire
            ui.setText(sett.UTCExpire)
            # coloring if close to end:
            now = datetime.datetime.now()
            expire = datetime.datetime.strptime(sett.UTCExpire, '%Y-%m-%d')
            deltaYellow = datetime.timedelta(days=30)
            if now > expire:
                self.changeStyleDynamic(ui, 'color', 'red')
            elif now > expire - deltaYellow:
                self.changeStyleDynamic(ui, 'color', 'yellow')
            else:
                self.changeStyleDynamic(ui, 'color', '')
        else:
            self.ui.UTCExpire.setText('-')

        if sett.statusUnattendedFlip is not None:
            self.ui.statusUnattendedFlip.setText('ON' if sett.statusUnattendedFlip else 'OFF')
        else:
            self.ui.statusUnattendedFlip.setText('-')

        if sett.statusDualTracking is not None:
            self.ui.statusDualTracking.setText('ON' if sett.statusDualTracking else 'OFF')
        else:
            self.ui.statusDualTracking.setText('-')

        if sett.statusRefraction is not None:
            self.ui.statusRefraction.setText('ON' if sett.statusRefraction else 'OFF')
        else:
            self.ui.statusRefraction.setText('-')

        if sett.gpsSynced is not None:
            self.ui.statusGPSSynced.setText('YES' if sett.gpsSynced else 'NO')
        else:
            self.ui.statusGPSSynced.setText('-')

        return True

    def updateTrackingGui(self):
        """
        updateTrackingGui update the gui upon events triggered be the reception of new
        settings from the mount. the mount data is polled, so we use this signal as well
        for the update process.

        :return:    True if ok for testing
        """

        sett = self.app.mount.sett

        if sett.checkRateLunar():
            self.changeStyleDynamic(self.ui.setLunarTracking, 'running', 'true')
            self.changeStyleDynamic(self.ui.setSiderealTracking, 'running', 'false')
            self.changeStyleDynamic(self.ui.setSolarTracking, 'running', 'false')
        elif sett.checkRateSidereal():
            self.changeStyleDynamic(self.ui.setLunarTracking, 'running', 'false')
            self.changeStyleDynamic(self.ui.setSiderealTracking, 'running', 'true')
            self.changeStyleDynamic(self.ui.setSolarTracking, 'running', 'false')
        elif sett.checkRateSolar():
            self.changeStyleDynamic(self.ui.setLunarTracking, 'running', 'false')
            self.changeStyleDynamic(self.ui.setSiderealTracking, 'running', 'false')
            self.changeStyleDynamic(self.ui.setSolarTracking, 'running', 'true')

        return True

    def changeTracking(self):
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
        obs = self.app.mount.obsSite
        suc = obs.setLunarTracking()
        if not suc:
            self.app.message.emit('Cannot set tracking to Lunar', 2)
            return False
        else:
            self.app.message.emit('Tracking set to Lunar', 0)
            return True

    def setSiderealTracking(self):
        obs = self.app.mount.obsSite
        suc = obs.setSiderealTracking()
        if not suc:
            self.app.message.emit('Cannot set tracking to Sidereal', 2)
            return False
        else:
            self.app.message.emit('Tracking set to Sidereal', 0)
            return True

    def setSolarTracking(self):
        obs = self.app.mount.obsSite
        suc = obs.setSolarTracking()
        if not suc:
            self.app.message.emit('Cannot set tracking to Solar', 2)
            return False
        else:
            self.app.message.emit('Tracking set to Solar', 0)
            return True

    def stop(self):
        obs = self.app.mount.obsSite
        suc = obs.stop()
        if not suc:
            self.app.message.emit('Cannot stop mount', 2)
            return False
        else:
            self.app.message.emit('Mount stopped', 0)
            return True
