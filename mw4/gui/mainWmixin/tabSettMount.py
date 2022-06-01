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
        self.app.update30s.connect(self.syncClock)
        self.ui.clockSync.stateChanged.connect(self.toggleClockSync)

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
        self.ui.automaticTelescope.setChecked(config.get('automaticTelescope', False))
        self.ui.automaticWOL.setChecked(config.get('automaticWOL', False))
        self.ui.syncTimePC2Mount.setChecked(config.get('syncTimePC2Mount', False))
        self.ui.clockSync.setChecked(config.get('clockSync', False))
        self.toggleClockSync()

        if self.ui.automaticWOL.isChecked():
            self.mountBoot()
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
        config['automaticTelescope'] = self.ui.automaticTelescope.isChecked()
        config['automaticWOL'] = self.ui.automaticWOL.isChecked()
        config['syncTimePC2Mount'] = self.ui.syncTimePC2Mount.isChecked()
        config['clockSync'] = self.ui.clockSync.isChecked()

        return True

    def mountBoot(self):
        """
        :return:
        """
        bAddress = self.ui.mountWolAddress.text().strip()
        bPort = self.ui.mountWolPort.text().strip()
        bPort = (int(bPort) if bPort else 0)
        suc = self.app.mount.bootMount(bAddress=bAddress, bPort=bPort)
        if suc:
            self.app.mes.emit(0, 'Mount', 'Command',
                              'Sent boot command to mount')
        else:
            self.app.mes.emit(2, 'Mount', 'Command', 'Mount cannot be booted')
        return suc

    def mountShutdown(self):
        """
        :return:
        """
        suc = self.app.mount.shutdown()
        if suc:
            self.app.mes.emit(0, 'Mount', 'Command', 'Shutting mount down')
        else:
            self.app.mes.emit(2, 'Mount', 'Command', 'Mount cannot be shutdown')
        return suc

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
            self.app.mes.emit(0, 'Rack', 'Command',
                              'Sent boot command to rack computer')
            return True
        else:
            self.app.mes.emit(2, 'Rack', 'Command',
                              'Rack computer cannot be booted')
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
        self.app.hostChanged.emit()
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

    def toggleClockSync(self):
        """
        :return:
        """
        enableSync = self.ui.clockSync.isChecked()
        self.ui.syncTimePC2Mount.setEnabled(enableSync)
        self.ui.syncNotTracking.setEnabled(enableSync)
        self.ui.clockOffset.setEnabled(enableSync)
        self.ui.clockOffsetMS.setEnabled(enableSync)
        self.ui.timeDeltaPC2Mount.setEnabled(enableSync)
        if enableSync:
            self.app.mount.startClockTimer()
        else:
            self.app.mount.stopClockTimer()
        return True

    def syncClock(self):
        """
        :return:
        """
        doSync = self.ui.syncTimePC2Mount.isChecked()
        if not doSync:
            return False
        if not self.deviceStat['mount']:
            return False

        doSyncNotTrack = self.ui.syncNotTracking.isChecked()
        mountTracks = self.app.mount.obsSite.status in [0, 10]
        if doSyncNotTrack and mountTracks:
            return False

        delta = self.app.mount.obsSite.timeDiff * 1000
        if abs(delta) < 10:
            return False

        if delta > 999:
            delta = 999
        if delta < -999:
            delta = -999

        delta = int(delta)
        suc = self.app.mount.obsSite.adjustClock(delta)
        if not suc:
            self.app.mes.emit(2, 'System', 'Clock',
                              'Cannot adjust mount clock')
            return False

        self.app.mes.emit(0, 'System', 'Clock',
                          f'Correction: [{-delta} ms]')
        return True
