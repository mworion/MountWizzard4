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
# written in python3, (c) 2019-2021 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages
import wakeonlan

# local import


class SettMount(object):
    """
    """

    def __init__(self):
        self.ui.mountOn.clicked.connect(self.mountBoot)
        self.ui.mountOff.clicked.connect(self.mountShutdown)
        self.ui.mountHost.editingFinished.connect(self.mountHost)
        self.ui.port3492.clicked.connect(self.mountHost)
        self.ui.port3490.clicked.connect(self.mountHost)
        self.ui.mountMAC.editingFinished.connect(self.mountMAC)
        self.ui.bootRackComp.clicked.connect(self.bootRackComp)
        self.app.mount.signals.settingDone.connect(self.setMountMAC)
        self.app.mount.signals.firmwareDone.connect(self.updateFwGui)
        self.ui.settleTimeMount.valueChanged.connect(self.setMountSettlingTime)

    def initConfig(self):
        """
        :return:
        """
        config = self.app.config['mainW']
        self.ui.mountHost.setText(config.get('mountHost', ''))
        self.ui.port3492.setChecked(config.get('port3492', True))
        self.mountHost()
        self.ui.mountMAC.setText(config.get('mountMAC', ''))
        self.mountMAC()
        self.ui.mountWolAddress.setText(config.get('mountWolAddress',
                                                   '255.255.255.255'))
        self.ui.mountWolPort.setText(config.get('mountWolPort', '9'))
        self.ui.rackCompMAC.setText(config.get('rackCompMAC', ''))
        self.ui.settleTimeMount.setValue(config.get('settleTimeMount', 0))
        return True

    def storeConfig(self):
        """
        :return:
        """
        config = self.app.config['mainW']
        config['mountHost'] = self.ui.mountHost.text()
        config['mountMAC'] = self.ui.mountMAC.text()
        config['mountWolAddress'] = self.ui.mountWolAddress.text()
        config['mountWolPort'] = self.ui.mountWolPort.text()
        config['rackCompMAC'] = self.ui.rackCompMAC.text()
        config['settleTimeMount'] = self.ui.settleTimeMount.value()
        config['port3492'] = self.ui.port3492.isChecked()
        return True

    def mountBoot(self):
        """
        :return:
        """
        bAddress = self.ui.mountWolAddress.text().strip()
        bPort = self.ui.mountWolPort.text().strip()
        bPort = (int(bPort) if bPort else 0)
        if self.app.mount.bootMount(bAddress=bAddress,
                                    bPort=bPort):
            self.app.message.emit('Sent boot command to mount', 0)
            return True

        else:
            self.app.message.emit('Mount cannot be booted', 2)
            return False

    def mountShutdown(self):
        """
        :return:
        """
        if self.app.mount.shutdown():
            self.app.message.emit('Shutting mount down', 0)
            return True

        else:
            self.app.message.emit('Mount cannot be shutdown', 2)
            return False

    def checkFormatMAC(self, value):
        """
        :param      value: string with mac address
        :return:    checked string in upper cases
        """
        if not value:
            self.log.info('wrong MAC value: {0}'.format(value))
            return None
        if not isinstance(value, str):
            self.log.info('wrong MAC value: {0}'.format(value))
            return None

        value = value.upper()
        value = value.replace('.', ':')
        value = value.split(':')
        if len(value) != 6:
            self.log.info('wrong MAC value: {0}'.format(value))
            return None

        for chunk in value:
            if len(chunk) != 2:
                self.log.info('wrong MAC value: {0}'.format(value))
                return None

            for char in chunk:
                if char not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
                                'A', 'B', 'C', 'D', 'E', 'F']:
                    self.log.info('wrong MAC value: {0}'.format(value))
                    return None

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
        if self.ui.port3492.isChecked():
            port = 3492
        else:
            port = 3490

        self.app.mount.host = (self.ui.mountHost.text(), port)
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
        self.ui.mountMAC.setText(self.app.mount.MAC)
        return True

    def setMountSettlingTime(self):
        """
        :return: true for test purpose
        """
        self.app.mount.settlingTime = self.ui.settleTimeMount.value()
        return True

    def updateFwGui(self, fw):
        """
        :return:    True if ok for testing
        """
        self.guiSetText(self.ui.product, 's', fw.product)
        self.guiSetText(self.ui.vString, 's', fw.vString)
        self.guiSetText(self.ui.fwdate, 's', fw.date)
        self.guiSetText(self.ui.fwtime, 's', fw.time)
        self.guiSetText(self.ui.hardware, 's', fw.hardware)
        return True
