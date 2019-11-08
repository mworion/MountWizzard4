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
# Python  v3.7.4
#
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
# standard libraries
# external packages
import PyQt5
import wakeonlan
# local import


class SettMount(object):
    """
    """

    def __init__(self):
        self.typeConnectionTexts = ['serial RS-232 port',
                                    'GPS or GPS/RS-232 port',
                                    'cabled LAN port',
                                    'wireless LAN',
                                    ]

        self.ui.mountOn.clicked.connect(self.mountBoot)
        self.ui.mountOff.clicked.connect(self.mountShutdown)
        self.ui.mountHost.editingFinished.connect(self.mountHost)
        self.ui.mountMAC.editingFinished.connect(self.mountMAC)
        self.ui.bootRackComp.clicked.connect(self.bootRackComp)
        self.app.mount.signals.settingDone.connect(self.setMountMAC)
        self.ui.openWeatherMapKey.editingFinished.connect(self.setOpenWeatherMapAPIKey)

    def initConfig(self):
        """

        :return:
        """

        config = self.app.config['mainW']
        self.ui.mountHost.setText(config.get('mountHost', ''))
        self.mountHost()
        self.ui.mountMAC.setText(config.get('mountMAC', ''))
        self.mountMAC()
        self.ui.rackCompMAC.setText(config.get('rackCompMAC', ''))
        self.ui.openWeatherMapKey.setText(config.get('openWeatherMapKey', ''))
        self.setOpenWeatherMapAPIKey()

        return True

    def storeConfig(self):
        """

        :return:
        """

        config = self.app.config['mainW']
        config['mountHost'] = self.ui.mountHost.text()
        config['mountMAC'] = self.ui.mountMAC.text()
        config['rackCompMAC'] = self.ui.rackCompMAC.text()
        config['openWeatherMapKey'] = self.ui.openWeatherMapKey.text()

        return True

    def mountBoot(self):
        if self.app.mount.bootMount():
            self.app.message.emit('Sent boot command to mount', 0)
            return True
        else:
            self.app.message.emit('Mount cannot be booted', 2)
            return False

    def mountShutdown(self):
        if self.app.mount.shutdown():
            self.app.message.emit('Shutting mount down', 0)
            return True
        else:
            self.app.message.emit('Mount cannot be shutdown', 2)
            return False

    def checkFormatMAC(self, value):
        """
        checkFormatMAC makes some checks to ensure that the format of the string is ok for
        WOL package.

        :param      value: string with mac address
        :return:    checked string in upper cases
        """

        if not value:
            self.logger.error('wrong MAC value: {0}'.format(value))
            return None
        if not isinstance(value, str):
            self.logger.error('wrong MAC value: {0}'.format(value))
            return None
        value = value.upper()
        value = value.replace('.', ':')
        value = value.split(':')
        if len(value) != 6:
            self.logger.error('wrong MAC value: {0}'.format(value))
            return None
        for chunk in value:
            if len(chunk) != 2:
                self.logger.error('wrong MAC value: {0}'.format(value))
                return None
            for char in chunk:
                if char not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
                                'A', 'B', 'C', 'D', 'E', 'F']:
                    self.logger.error('wrong MAC value: {0}'.format(value))
                    return None
        # now we build the right format
        value = '{0:2s}:{1:2s}:{2:2s}:{3:2s}:{4:2s}:{5:2s}'.format(*value)
        return value

    def bootRackComp(self):
        """

        :return:
        """

        MAC = self.ui.rackCompMAC.text()
        MAC = self.checkFormatMAC(MAC)
        if MAC is not None:
            wakeonlan.send_magic_packet(MAC)
            self.app.message.emit('Sent boot command to rack computer', 0)
            return True
        else:
            self.app.message.emit('Rack computer cannot be booted', 2)
            return False

    def mountHost(self):
        """

        :return: true for test purpose
        """
        self.app.mount.host = self.ui.mountHost.text()
        return True

    def mountMAC(self):
        """

        :return: true for test purpose
        """
        self.app.mount.MAC = self.ui.mountMAC.text()
        return True

    def setMountMAC(self, sett=None):
        """

        :param sett:
        :return: true for test purpose
        """
        if sett is None:
            return False

        if sett.addressLanMAC is None:
            return False
        if not sett.addressLanMAC:
            return False
        self.app.mount.MAC = sett.addressLanMAC

        if self.app.mount.MAC is None:
            return False
        self.ui.mountMAC.setText(self.app.mount.MAC)

        if sett.typeConnection is None:
            return False
        if sett.typeConnection < 0:
            return False
        if sett.typeConnection > len(self.typeConnectionTexts):
            return False

        text = self.typeConnectionTexts[sett.typeConnection]
        self.ui.mountTypeConnection.setText(text)

        return True

    def setOpenWeatherMapAPIKey(self):
        """

        :return: success
        """

        weather = self.app.weather

        if not weather:
            return False

        weather.keyAPI = self.ui.openWeatherMapKey.text()

        return True
