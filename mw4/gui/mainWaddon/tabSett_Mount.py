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
# GUI with PySide for python
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import socket

# external packages
from PySide6.QtCore import QObject
import wakeonlan

# local import
from mountcontrol.setting import Setting
from mountcontrol.firmware import Firmware
from base.ethernet import checkFormatMAC
from gui.utilities.toolsQtWidget import guiSetText


class SettMount(QObject):
    """ """

    def __init__(self, mainW):
        super().__init__()
        self.mainW = mainW
        self.app = mainW.app
        self.msg = mainW.app.msg
        self.ui = mainW.ui

        self.ui.mountOn.clicked.connect(self.mountBoot)
        self.ui.mountOff.clicked.connect(self.mountShutdown)
        self.app.mountOn.connect(self.mountBoot)
        self.app.mountOff.connect(self.mountShutdown)
        self.ui.mountHost.editingFinished.connect(self.mountHost)
        self.ui.port3492.clicked.connect(self.mountHost)
        self.ui.port3490.clicked.connect(self.mountHost)
        self.ui.mountMAC.editingFinished.connect(self.mountMAC)
        self.ui.bootRackComp.clicked.connect(self.bootRackComp)
        self.ui.waitTimeMountFlip.valueChanged.connect(self.setWaitTimeFlip)
        self.ui.clockSync.stateChanged.connect(self.toggleClockSync)
        self.ui.copyFromTelescopeDriver.clicked.connect(self.updateTelescopeParametersToGui)
        self.app.mount.signals.settingDone.connect(self.setMountMAC)
        self.app.mount.signals.firmwareDone.connect(self.updateFwGui)
        self.app.update3s.connect(self.updateTelescopeParametersToGuiCyclic)
        self.app.update30s.connect(self.syncClock)

    def initConfig(self) -> None:
        """ """
        config = self.app.config["mainW"]
        self.ui.mountHost.setText(config.get("mountHost", ""))
        self.ui.port3492.setChecked(config.get("port3492", True))
        self.mountHost()
        self.ui.mountMAC.setText(config.get("mountMAC", ""))
        self.mountMAC()
        self.ui.mountWolAddress.setText(config.get("mountWolAddress", "255.255.255.255"))
        self.ui.mountWolPort.setText(config.get("mountWolPort", "9"))
        self.ui.rackCompMAC.setText(config.get("rackCompMAC", ""))
        self.ui.waitTimeMountFlip.setValue(config.get("waitTimeFlip", 0))
        self.ui.waitTimeExposure.setValue(config.get("waitTimeExposure", 0))
        self.ui.automaticTelescope.setChecked(config.get("automaticTelescope", False))
        self.ui.automaticWOL.setChecked(config.get("automaticWOL", False))
        self.ui.syncTimeNone.setChecked(config.get("syncTimeNone", True))
        self.ui.syncTimeCont.setChecked(config.get("syncTimeCont", False))
        self.ui.syncTimeNotTrack.setChecked(config.get("syncTimeNotTrack", False))
        self.ui.clockSync.setChecked(config.get("clockSync", False))
        self.toggleClockSync()

        if self.ui.automaticWOL.isChecked():
            self.mountBoot()

    def storeConfig(self) -> None:
        """ """
        config = self.app.config["mainW"]
        config["mountHost"] = self.ui.mountHost.text()
        config["mountMAC"] = self.ui.mountMAC.text()
        config["mountWolAddress"] = self.ui.mountWolAddress.text()
        config["mountWolPort"] = self.ui.mountWolPort.text()
        config["rackCompMAC"] = self.ui.rackCompMAC.text()
        config["waitTimeFlip"] = self.ui.waitTimeMountFlip.value()
        config["waitTimeExposure"] = self.ui.waitTimeExposure.value()
        config["port3492"] = self.ui.port3492.isChecked()
        config["automaticTelescope"] = self.ui.automaticTelescope.isChecked()
        config["automaticWOL"] = self.ui.automaticWOL.isChecked()
        config["syncTimeNone"] = self.ui.syncTimeNone.isChecked()
        config["syncTimeCont"] = self.ui.syncTimeCont.isChecked()
        config["syncTimeNotTrack"] = self.ui.syncTimeNotTrack.isChecked()
        config["clockSync"] = self.ui.clockSync.isChecked()

    def mountBoot(self) -> None:
        """ """
        bAddress = self.ui.mountWolAddress.text().strip()
        bPort = self.ui.mountWolPort.text().strip()
        bPort = int(bPort) if bPort else 0
        if self.app.mount.bootMount(bAddress=bAddress, bPort=bPort):
            self.msg.emit(0, "Mount", "Command", "Sent boot command to mount")
        else:
            self.msg.emit(2, "Mount", "Command", "Mount cannot be booted")

    def mountShutdown(self) -> None:
        """ """
        self.app.deviceStat["mount"] = False
        if self.app.mount.shutdown():
            self.msg.emit(0, "Mount", "Command", "Shutting mount down")
        else:
            self.msg.emit(2, "Mount", "Command", "Mount cannot be shutdown")

    def bootRackComp(self) -> None:
        """ """
        MAC = checkFormatMAC(self.ui.rackCompMAC.text())
        if MAC:
            wakeonlan.send_magic_packet(MAC)
            self.msg.emit(0, "Rack", "Command", "Sent boot command to rack computer")
        else:
            self.msg.emit(2, "Rack", "Command", "Rack computer cannot be booted")

    def mountHost(self) -> None:
        """ """
        port = 3492 if self.ui.port3492.isChecked() else 3490
        host = self.ui.mountHost.text()
        if not host:
            return
        try:
            socket.gethostbyname(host)
        except Exception as e:
            self.msg.emit(2, "Mount", "Setting error", f"{e}")
            return

        self.app.mount.host = (host, port)
        self.app.hostChanged.emit()

    def mountMAC(self) -> None:
        """ """
        self.app.mount.MAC = self.ui.mountMAC.text()

    def setMountMAC(self, sett: Setting = None) -> None:
        """ """
        if sett is None:
            return
        if sett.addressLanMAC is None:
            return
        if not sett.addressLanMAC:
            return

        self.app.mount.MAC = sett.addressLanMAC
        self.ui.mountMAC.setText(self.app.mount.MAC)

    def setWaitTimeFlip(self) -> None:
        """ """
        self.app.mount.waitTimeFlip = self.ui.waitTimeMountFlip.value()

    def updateFwGui(self, fw: Firmware) -> None:
        """ """
        guiSetText(self.ui.product, "s", fw.product)
        guiSetText(self.ui.vString, "s", fw.vString.public)
        guiSetText(self.ui.fwdate, "s", fw.date)
        guiSetText(self.ui.fwtime, "s", fw.time)
        guiSetText(self.ui.hardware, "s", fw.hardware)

    def toggleClockSync(self) -> None:
        """ """
        enableSyncTimer = self.ui.clockSync.isChecked()
        self.ui.syncTimeNone.setEnabled(enableSyncTimer)
        self.ui.syncTimeCont.setEnabled(enableSyncTimer)
        self.ui.syncTimeNotTrack.setEnabled(enableSyncTimer)
        self.ui.clockOffset.setEnabled(enableSyncTimer)
        self.ui.clockOffsetMS.setEnabled(enableSyncTimer)
        if enableSyncTimer:
            self.app.mount.startMountClockTimer()
        else:
            self.app.mount.stopMountClockTimer()

    def syncClock(self) -> None:
        """ """
        syncTimeNone = self.ui.syncTimeNone.isChecked()
        if syncTimeNone:
            return
        if not self.app.deviceStat["mount"]:
            return

        doSyncNotTrack = self.ui.syncTimeNotTrack.isChecked()
        mountTracks = self.app.mount.obsSite.status in [0, 10]
        if doSyncNotTrack and mountTracks:
            return

        delta = self.app.mount.obsSite.timeDiff * 1000
        if abs(delta) < 10:
            return

        if delta > 999:
            delta = 999
        if delta < -999:
            delta = -999

        if self.app.mount.obsSite.adjustClock(int(delta)):
            self.msg.emit(0, "System", "Clock", f"Correction: [{-delta} ms]")
        else:
            self.msg.emit(2, "System", "Clock", "Cannot adjust mount clock")

    def updateTelescopeParametersToGui(self) -> None:
        """ """
        data = self.app.telescope.data
        value = data.get("TELESCOPE_INFO.TELESCOPE_FOCAL_LENGTH", 0)
        if value is not None:
            value = float(value)
            self.ui.focalLength.setValue(value)

        value = data.get("TELESCOPE_INFO.TELESCOPE_APERTURE", 0)
        if value is not None:
            value = float(value)
            self.ui.aperture.setValue(value)

    def updateTelescopeParametersToGuiCyclic(self) -> None:
        """ """
        if self.ui.automaticTelescope.isChecked():
            self.updateTelescopeParametersToGui()
