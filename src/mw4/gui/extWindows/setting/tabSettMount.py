############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10_micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2026 by mworion
# License APL2.0
#
###########################################################
import socket
import wakeonlan
from mw4.base.ethernet import checkFormatMAC
from mw4.gui.utilities.qtHelpers import changeStyleDynamic, guiSetText
from mw4.mountcontrol.firmware import Firmware
from mw4.mountcontrol.setting import Setting
from typing import Any


class SettMount:
    def __init__(self, parentW: Any) -> None:
        self.parentW = parentW
        self.app = parentW.app
        self.msg = parentW.app.msg
        self.ui = parentW.ui

        self.ui.mountOn.clicked.connect(self.mountBoot)
        self.ui.mountOff.clicked.connect(self.mountShutdown)
        self.app.mountOn.connect(self.mountBoot)
        self.app.mountOff.connect(self.mountShutdown)
        self.ui.mountHost.editingFinished.connect(self.mountHost)
        self.ui.port3492.clicked.connect(self.mountHost)
        self.ui.port3490.clicked.connect(self.mountHost)
        self.ui.mountMAC.editingFinished.connect(self.mountMAC)
        self.ui.bootRackComp.clicked.connect(self.bootRackComp)
        self.ui.clockSync.stateChanged.connect(self.toggleClockSync)
        self.app.dReg["mount"].signals.settingDone.connect(self.setMountMAC)
        self.app.dReg["mount"].signals.firmwareDone.connect(self.setMountCapabilities)
        self.app.dReg["mount"].signals.firmwareDone.connect(self.updateFwGui)
        self.app.dReg["mount"].signals.mountIsUp.connect(self.showMountStatus)
        self.app.update30s.connect(self.syncClock)

    def initConfig(self) -> None:
        config = self.app.config.get("SettingDeviceMount", {})
        self.ui.mountHost.setText(config.get("mountHost", ""))
        self.ui.port3492.setChecked(config.get("port3492", True))
        self.mountHost()
        self.ui.mountMAC.setText(config.get("mountMAC", ""))
        self.mountMAC()
        self.ui.mountWolAddress.setText(config.get("mountWolAddress", "255.255.255.255"))
        self.ui.mountWolPort.setText(config.get("mountWolPort", "9"))
        self.ui.rackCompMAC.setText(config.get("rackCompMAC", ""))
        self.ui.automaticWOL.setChecked(config.get("automaticWOL", False))
        self.ui.syncTimeNone.setChecked(config.get("syncTimeNone", True))
        self.ui.syncTimeCont.setChecked(config.get("syncTimeCont", False))
        self.ui.syncTimeNotTrack.setChecked(config.get("syncTimeNotTrack", False))
        self.ui.clockSync.setChecked(config.get("clockSync", False))
        self.app.dReg["mount"].instance.getFW()
        self.toggleClockSync()
        if self.ui.automaticWOL.isChecked():
            self.mountBoot()

    def storeConfig(self) -> None:
        self.app.config["SettingDeviceMount"] = {}
        config = self.app.config["SettingDeviceMount"]
        config["mountHost"] = self.ui.mountHost.text()
        config["mountMAC"] = self.ui.mountMAC.text()
        config["mountWolAddress"] = self.ui.mountWolAddress.text()
        config["mountWolPort"] = self.ui.mountWolPort.text()
        config["rackCompMAC"] = self.ui.rackCompMAC.text()
        config["port3492"] = self.ui.port3492.isChecked()
        config["automaticWOL"] = self.ui.automaticWOL.isChecked()
        config["syncTimeNone"] = self.ui.syncTimeNone.isChecked()
        config["syncTimeCont"] = self.ui.syncTimeCont.isChecked()
        config["syncTimeNotTrack"] = self.ui.syncTimeNotTrack.isChecked()
        config["clockSync"] = self.ui.clockSync.isChecked()

    def closeEvent(self) -> None:
        self.app.dReg["mount"].signals.settingDone.disconnect(self.setMountMAC)
        self.app.dReg["mount"].signals.firmwareDone.disconnect(self.setMountCapabilities)
        self.app.dReg["mount"].signals.firmwareDone.disconnect(self.updateFwGui)

    def setupIcons(self) -> None:
        self.parentW.wIcon(self.ui.mountOn, "power-on")
        self.parentW.wIcon(self.ui.mountOff, "power-off")

    def setMountCapabilities(self, fw) -> None:
        self.ui.GroupWOL.setEnabled(self.app.dReg["mount"].firmware.isHW2012())

    def mountBoot(self) -> None:
        bAddress = self.ui.mountWolAddress.text().strip()
        bPort = self.ui.mountWolPort.text().strip()
        bPort = int(bPort) if bPort else 0
        if self.app.dReg["mount"].instance.bootMount(bAddress=bAddress, bPort=bPort):
            self.msg.emit(0, "Mount", "Command", "Sent boot command to mount")
        else:
            self.msg.emit(2, "Mount", "Command", "Mount cannot be booted")

    def mountShutdown(self) -> None:
        self.app.dReg.setStat("mount", False)
        if self.app.dReg["mount"].instance.shutdown():
            self.msg.emit(0, "Mount", "Command", "Shutting mount down")
        else:
            self.msg.emit(2, "Mount", "Command", "Mount cannot be shutdown")

    def bootRackComp(self) -> None:
        MAC = checkFormatMAC(self.ui.rackCompMAC.text())
        if MAC:
            wakeonlan.send_magic_packet(MAC)
            self.msg.emit(0, "Rack", "Command", "Sent boot command to rack computer")
        else:
            self.msg.emit(2, "Rack", "Command", "Rack computer cannot be booted")

    def mountHost(self) -> None:
        port = 3492 if self.ui.port3492.isChecked() else 3490
        host = self.ui.mountHost.text()
        if not host:
            return
        try:
            socket.gethostbyname(host)
        except Exception as e:
            self.msg.emit(2, "Mount", "Setting error", f"{e}")
            return

        self.app.dReg["mount"].instance.host = (host, port)
        self.app.hostChanged.emit()

    def mountMAC(self) -> None:
        self.app.dReg["mount"].instance.MAC = self.ui.mountMAC.text()

    def setMountMAC(self, sett: Setting | None = None) -> None:
        if sett is None:
            return
        if sett.addressLanMAC is None:
            return
        if not sett.addressLanMAC:
            return

        self.app.dReg["mount"].instance.MAC = sett.addressLanMAC
        self.ui.mountMAC.setText(self.app.dReg["mount"].instance.MAC)

    def showMountStatus(self, status: bool) -> None:
        changeStyleDynamic(self.ui.mountOn, "run", status)
        changeStyleDynamic(self.ui.mountOff, "run", not status)
        self.ui.use10micronDef.setEnabled(status)

    def updateFwGui(self, fw: Firmware) -> None:
        guiSetText(self.ui.product, "s", fw.product)
        guiSetText(self.ui.vString, "s", fw.vString.public)
        guiSetText(self.ui.fwdate, "s", fw.date)
        guiSetText(self.ui.fwtime, "s", fw.time)
        guiSetText(self.ui.hardware, "s", fw.hardware)

    def toggleClockSync(self) -> None:
        enableSyncTimer = self.ui.clockSync.isChecked()
        self.ui.syncTimeNone.setEnabled(enableSyncTimer)
        self.ui.syncTimeCont.setEnabled(enableSyncTimer)
        self.ui.syncTimeNotTrack.setEnabled(enableSyncTimer)
        if enableSyncTimer:
            self.app.dReg["mount"].instance.startMountClockTimer()
        else:
            self.app.dReg["mount"].instance.stopMountClockTimer()

    def syncClock(self) -> None:
        if self.ui.syncTimeNone.isChecked():
            return
        if not self.app.dReg["mount"].stat:
            return

        doSyncNotTrack = self.ui.syncTimeNotTrack.isChecked()
        mountTracks = self.app.dReg["mount"].obsSite.status in [0, 10]
        if doSyncNotTrack and mountTracks:
            return

        delta = self.app.dReg["mount"].obsSite.timeDiff * 1000
        if abs(delta) < 10:
            return

        delta = int(max(min(delta, 999), -999))

        if self.app.dReg["mount"].obsSite.adjustClock(delta):
            self.msg.emit(0, "System", "Clock", f"Correction: [{-delta} ms]")
        else:
            self.msg.emit(2, "System", "Clock", "Cannot adjust mount clock")
