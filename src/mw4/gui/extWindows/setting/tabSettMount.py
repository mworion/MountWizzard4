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
import wakeonlan
from mw4.base.ethernet import checkFormatMAC
from mw4.gui.utilities.qtHelpers import changeStyleDynamic, guiSetText
from mw4.mountcontrol.firmware import Firmware
from mw4.mountcontrol.setting import Setting
from collections.abc import Any


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
        self.app.dReg["mount"].signals.settingDone.connect(self.setMountMAC)
        self.app.dReg["mount"].signals.firmwareDone.connect(self.setMountCapabilities)
        self.app.dReg["mount"].signals.firmwareDone.connect(self.updateFwGui)
        self.app.dReg["mount"].signals.mountIsUp.connect(self.showMountStatus)
        self.ui.bootRackComp.clicked.connect(self.bootRackComp)

    def initConfig(self) -> None:
        self.app.dReg["mount"].instance.getFW()
        config = self.app.config.get("SettingMount", {})
        self.ui.rackCompMAC.setText(config.get("rackCompMAC", "00:00:00:00:00"))
        self.ui.rackCompWolAddress.setText(config.get("rackCompWolAddress", "255.255.255.255"))
        self.ui.rackCompWolPort.setText(config.get("rackCompWolPort", "9"))
        self.ui.hostAddress.setText(self.app.dReg["mount"].instance.config.hostAddress)
        self.ui.port3492.setChecked(self.app.dReg["mount"].instance.config.port == 3492)
        self.ui.MAC.setText(self.app.dReg["mount"].instance.config.MAC)
        self.ui.wolAddress.setText(self.app.dReg["mount"].instance.config.wolAddress)
        self.ui.wolPort.setText(str(self.app.dReg["mount"].instance.config.wolPort))
        self.ui.wolAutomatic.setChecked(self.app.dReg["mount"].instance.config.wolAutomatic)
        self.ui.clockSync.setChecked(self.app.dReg["mount"].instance.config.clockSync)
        self.ui.syncTimeNone.setChecked(self.app.dReg["mount"].instance.config.syncTimeNone)
        self.ui.syncTimeCont.setChecked(self.app.dReg["mount"].instance.config.syncTimeCont)
        self.ui.syncTimeNotTrack.setChecked(
            self.app.dReg["mount"].instance.config.syncTimeNotTrack
        )
        self.ui.hostAddress.textChanged.connect(self.storeConfig)
        self.ui.MAC.textChanged.connect(self.storeConfig)
        self.ui.wolAddress.textChanged.connect(self.storeConfig)
        self.ui.wolPort.textChanged.connect(self.storeConfig)
        self.ui.wolAutomatic.clicked.connect(self.storeConfig)
        self.ui.port3492.clicked.connect(self.storeConfig)
        self.ui.port3490.clicked.connect(self.storeConfig)
        self.ui.clockSync.stateChanged.connect(self.toggleClockSync)

    def storeConfig(self) -> None:
        self.app.config["SettingMount"] = {}
        config = self.app.config["SettingMount"]
        config["rackCompMAC"] = self.ui.rackCompMAC.text()
        config["rackCompWolAddress"] = self.ui.rackCompWolAddress.text()
        config["rackCompWolPort"] = self.ui.rackCompWolPort.text()

        port = 3492 if self.ui.port3492.isChecked() else 3490
        host = self.ui.hostAddress.text()
        self.app.dReg["mount"].instance.config.hostAddress = host
        self.app.dReg["mount"].instance.config.port = port
        self.app.dReg["mount"].instance.config.MAC = self.ui.MAC.text()
        self.app.dReg["mount"].instance.config.wolAddress = self.ui.wolAddress.text()
        self.app.dReg["mount"].instance.config.wolPort = int(self.ui.wolPort.text())
        self.app.dReg["mount"].instance.config.wolAutomatic = self.ui.wolAutomatic.isChecked()
        self.app.dReg["mount"].instance.config.syncTimeNone = self.ui.syncTimeNone.isChecked()
        self.app.dReg["mount"].instance.config.syncTimeCont = self.ui.syncTimeCont.isChecked()
        self.app.dReg[
            "mount"
        ].instance.config.syncTimeNotTrack = self.ui.syncTimeNotTrack.isChecked()
        self.app.dReg["mount"].instance.config.clockSync = self.ui.clockSync.isChecked()

    def closeEvent(self) -> None:
        self.app.dReg["mount"].signals.settingDone.disconnect(self.setMountMAC)
        self.app.dReg["mount"].signals.firmwareDone.disconnect(self.setMountCapabilities)
        self.app.dReg["mount"].signals.firmwareDone.disconnect(self.updateFwGui)
        self.app.dReg["mount"].signals.mountIsUp.disconnect(self.showMountStatus)

    def setupIcons(self) -> None:
        self.parentW.wIcon(self.ui.mountOn, "power-on")
        self.parentW.wIcon(self.ui.mountOff, "power-off")

    def setMountCapabilities(self, fw) -> None:
        self.ui.GroupWOL.setEnabled(self.app.dReg["mount"].firmware.isHW2012())

    def mountBoot(self) -> None:
        if self.app.dReg["mount"].instance.bootMount():
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

    def setMountMAC(self, sett: Setting | None = None) -> None:
        if sett is None:
            return
        if not sett.addressLanMAC:
            return
        self.app.dReg["mount"].instance.config.MAC = sett.addressLanMAC
        self.ui.MAC.setText(self.app.dReg["mount"].instance.config.MAC)

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
