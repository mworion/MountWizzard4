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

# external packages

# local import


class MountMain:
    """
    """
    def initConfig(self):
        """
        :return: True for test purpose
        """
        config = self.app.config.get('mainW', {})
        self.ui.coordsJ2000.setChecked(config.get('coordsJ2000', False))
        self.ui.coordsJNow.setChecked(config.get('coordsJNow', False))
        self.updateLocGUI(self.app.mount.obsSite)
        return True

    def storeConfig(self):
        """
        :return: True for test purpose
        """
        config = self.app.config['mainW']
        config['coordsJ2000'] = self.ui.coordsJ2000.isChecked()
        config['coordsJNow'] = self.ui.coordsJNow.isChecked()
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
