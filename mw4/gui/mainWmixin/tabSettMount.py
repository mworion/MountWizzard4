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
import ipaddress

# external packages
import wakeonlan

# local import
from mountcontrol.mount import checkFormatMAC


class SettMount(object):
    """
    """

    def __init__(self):
        self.ui.mountOn.clicked.connect(self.mountBoot)
        self.app.mountOn.connect(self.mountBoot)
        self.ui.mountOff.clicked.connect(self.mountShutdown)
        self.app.mountOff.connect(self.mountShutdown)
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
        self.ui.copyFromTelescopeDriver.clicked.connect(self.updateTelescopeParametersToGui)
        self.app.update3s.connect(self.updateTelescopeParametersToGuiCyclic)

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
        self.ui.syncTimeNone.setChecked(config.get('syncTimeNone', True))
        self.ui.syncTimeCont.setChecked(config.get('syncTimeCont', False))
        self.ui.syncTimeNotTrack.setChecked(config.get('syncTimeNotTrack', False))
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
        config['syncTimeNone'] = self.ui.syncTimeNone.isChecked()
        config['syncTimeCont'] = self.ui.syncTimeCont.isChecked()
        config['syncTimeNotTrack'] = self.ui.syncTimeNotTrack.isChecked()
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
            self.msg.emit(0, 'Mount', 'Command',
                          'Sent boot command to mount')
        else:
            self.msg.emit(2, 'Mount', 'Command', 'Mount cannot be booted')
        return suc

    def mountShutdown(self):
        """
        :return:
        """
        suc = self.app.mount.shutdown()
        if suc:
            self.msg.emit(0, 'Mount', 'Command', 'Shutting mount down')
        else:
            self.msg.emit(2, 'Mount', 'Command', 'Mount cannot be shutdown')
        return suc

    def bootRackComp(self):
        """
        :return:
        """
        MAC = self.ui.rackCompMAC.text()
        MAC = checkFormatMAC(MAC)
        if MAC is not None:
            wakeonlan.send_magic_packet(MAC)
            self.msg.emit(0, 'Rack', 'Command',
                          'Sent boot command to rack computer')
            return True
        else:
            self.msg.emit(2, 'Rack', 'Command',
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

        host = self.ui.mountHost.text()
        if not host:
            return False
        try:
            ipaddress.ip_address(host)
        except Exception as e:
            self.msg.emit(2, 'Mount', 'Setting error', f'{e}')
            return False

        self.app.mount.host = (host, port)
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
        self.ui.syncTimeNone.setEnabled(enableSync)
        self.ui.syncTimeCont.setEnabled(enableSync)
        self.ui.syncTimeNotTrack.setEnabled(enableSync)
        self.ui.clockOffset.setEnabled(enableSync)
        self.ui.clockOffsetMS.setEnabled(enableSync)
        if enableSync:
            self.app.mount.startClockTimer()
        else:
            self.app.mount.stopClockTimer()
        return True

    def syncClock(self):
        """
        :return:
        """
        noSync = self.ui.syncTimeNone.isChecked()
        if noSync:
            return False
        if not self.deviceStat['mount']:
            return False

        doSyncNotTrack = self.ui.syncTimeNotTrack.isChecked()
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
            self.msg.emit(2, 'System', 'Clock',
                          'Cannot adjust mount clock')
            return False

        self.msg.emit(0, 'System', 'Clock',
                      f'Correction: [{-delta} ms]')
        return True

    def updateTelescopeParametersToGui(self):
        """
        updateTelescopeParametersToGui takes the information gathered from the
        driver and programs them into gui for later use.

        :return: true for test purpose
        """

        value = self.app.telescope.data.get(
            'TELESCOPE_INFO.TELESCOPE_FOCAL_LENGTH', 0)
        if value is not None:
            value = float(value)
            self.ui.focalLength.setValue(value)

        value = self.app.telescope.data.get('TELESCOPE_INFO.TELESCOPE_APERTURE',
                                            0)
        if value is not None:
            value = float(value)
            self.ui.aperture.setValue(value)

        return True

    def updateTelescopeParametersToGuiCyclic(self):
        """
        :return:
        """
        if not self.ui.automaticTelescope.isChecked():
            return False
        self.updateTelescopeParametersToGui()
        return True
