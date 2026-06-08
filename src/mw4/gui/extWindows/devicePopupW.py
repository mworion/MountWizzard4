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
from functools import partial
from mw4.base.alpacaClass import AlpacaClass
from mw4.base.ascomClass import AscomClass
from mw4.base.indiClass import IndiClass
from mw4.gui.utilities.qtHelpers import changeStyleDynamic, getTabIndex, svg2pixmap
from mw4.gui.utilities.qtMain import MWidget
from mw4.gui.widgets.devicePopup_ui import Ui_DevicePopup
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QCheckBox, QComboBox, QDoubleSpinBox, QLineEdit, QListView
from typing import Any


class DevicePopup(MWidget):
    def __init__(self, parentWidget, device: str, framework: str, data: dict):
        super().__init__()
        self.app = parentWidget.app
        self.msg = parentWidget.app.msg
        self.data = data
        self.device = device
        self.framework = framework

        self.ui = Ui_DevicePopup()
        self.ui.setupUi(self.ws)
        self.setMinimumSize(500, 340)
        self.setMaximumSize(500, 340)
        self.titleBar.windowFixed = True
        self.setWindowTitle("Device Management")
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        x = parentWidget.x() + int((parentWidget.width() - self.width()) / 2)
        y = parentWidget.y() + int((parentWidget.height() - self.height()) / 2)
        self.move(x, y)
        pixmap = svg2pixmap("assets/icon/cogs.svg", self.M_PRIM)
        self.ui.iconPixmap.setPixmap(pixmap)

        self.returnValues: dict[str, Any] = {"close": "cancel"}
        self.framework2gui = {
            "indi": {
                "hostaddress": self.ui.indiHostAddress,
                "port": self.ui.indiPort,
                "deviceName": self.ui.indiDeviceList,
                "messages": self.ui.indiMessages,
                "loadConfig": self.ui.indiLoadConfig,
            },
            "alpaca": {
                "hostaddress": self.ui.alpacaHostAddress,
                "port": self.ui.alpacaPort,
                "deviceName": self.ui.alpacaDeviceList,
            },
            "ascom": {
                "deviceName": self.ui.ascomDevice,
            },
            "boltwood": {
                "filePath": self.ui.boltwoodPath,
            },
            "astrometry": {
                "deviceName": self.ui.astrometryDeviceList,
                "searchRadius": self.ui.astrometrySearchRadius,
                "timeout": self.ui.astrometryTimeout,
                "appPath": self.ui.astrometryAppPath,
                "indexPath": self.ui.astrometryIndexPath,
            },
            "astap": {
                "deviceName": self.ui.astapDeviceList,
                "searchRadius": self.ui.astapSearchRadius,
                "timeout": self.ui.astapTimeout,
                "appPath": self.ui.astapAppPath,
                "indexPath": self.ui.astapIndexPath,
            },
            "watney": {
                "deviceName": self.ui.watneyDeviceList,
                "searchRadius": self.ui.watneySearchRadius,
                "timeout": self.ui.watneyTimeout,
                "appPath": self.ui.watneyAppPath,
                "indexPath": self.ui.watneyIndexPath,
            },
            "online": {
                "apiKey": self.ui.onlineWeatherApiKey,
                "hostaddress": self.ui.onlineWeatherHostAddress,
            },
            "seeing": {
                "apiKey": self.ui.seeingWeatherApiKey,
                "hostaddress": self.ui.seeingWeatherHostAddress,
            },
            "relay": {
                "hostaddress": self.ui.relayHostAddress,
                "user": self.ui.relayUser,
                "password": self.ui.relayPassword,
            },
        }

        self.platesolvers = {
            "astrometry": {
                "appPath": self.ui.astrometryAppPath,
                "indexPath": self.ui.astrometryIndexPath,
                "selectAppPath": self.ui.selectAstrometryAppPath,
                "selectIndexPath": self.ui.selectAstrometryIndexPath,
            },
            "astap": {
                "appPath": self.ui.astapAppPath,
                "indexPath": self.ui.astapIndexPath,
                "selectAppPath": self.ui.selectAstapAppPath,
                "selectIndexPath": self.ui.selectAstapIndexPath,
            },
            "watney": {
                "appPath": self.ui.watneyAppPath,
                "indexPath": self.ui.watneyIndexPath,
                "selectAppPath": self.ui.selectWatneyAppPath,
                "selectIndexPath": self.ui.selectWatneyIndexPath,
            },
        }

        self.discovers: dict[str, dict[str, Any]] = {
            "indi": {
                "deviceList": self.ui.indiDeviceList,
                "hostaddress": self.ui.indiHostAddress,
                "button": self.ui.indiDiscover,
                "port": self.ui.indiPort,
                "class": IndiClass,
            },
            "alpaca": {
                "deviceList": self.ui.alpacaDeviceList,
                "hostaddress": self.ui.alpacaHostAddress,
                "button": self.ui.alpacaDiscover,
                "port": self.ui.alpacaPort,
                "class": AlpacaClass,
            },
        }

        self.ui.cancel.clicked.connect(self.close)
        self.ui.ok.clicked.connect(self.storeConfig)
        for framework in self.discovers:
            self.discovers[framework]["button"].clicked.connect(
                partial(self.discoverDevices, framework)
            )
        self.ui.ascomSelector.clicked.connect(self.selectAscomDriver)
        for framework in self.platesolvers:
            self.platesolvers[framework]["selectAppPath"].clicked.connect(
                partial(self.selectAppPath, framework)
            )
            self.platesolvers[framework]["selectIndexPath"].clicked.connect(
                partial(self.selectIndexPath, framework)
            )
            self.platesolvers[framework]["appPath"].textChanged.connect(
                partial(self.checkApp, framework)
            )
            self.platesolvers[framework]["indexPath"].textChanged.connect(
                partial(self.checkIndex, framework)
            )
        self.ui.selectBoltwoodPath.clicked.connect(self.selectBoltwoodPath)

    def initConfig(self) -> None:
        self.setWindowTitle(f"Setup driver for {self.device}")
        self.populateTabs()
        self.selectTabs()
        framework = self.data.get("framework", "")
        if framework in self.platesolvers:
            self.checkApp(framework, self.platesolvers[framework]["appPath"].text())
            self.checkIndex(framework, self.platesolvers[framework]["indexPath"].text())
        self.show()

    def storeConfig(self) -> None:
        self.readFramework()
        self.readTabs()
        self.returnValues["copyConfig"]: list = []
        if self.ui.indiCopyConfig.isChecked():
            self.returnValues["copyConfig"].append("indi")
        if self.ui.alpacaCopyConfig.isChecked():
            self.returnValues["copyConfig"].append("alpaca")
        self.returnValues["close"] = "ok"
        self.returnValues["device"] = self.device
        self.returnValues["framework"] = self.framework
        self.close()

    def selectTabs(self) -> None:
        tabIndex = getTabIndex(self.ui.tab, self.framework)
        self.ui.tab.setCurrentIndex(tabIndex)
        for index in range(0, self.ui.tab.count()):
            isVisible = self.ui.tab.widget(index).objectName() in self.data
            self.ui.tab.setTabVisible(index, isVisible)

    def populateTabs(self) -> None:
        for framework in self.data:
            for element in self.data[framework]:
                ui = self.framework2gui[framework].get(element)
                if isinstance(ui, QComboBox):
                    ui.clear()
                    ui.setView(QListView())
                    ui.addItem(self.data[framework]["deviceName"])
                elif isinstance(ui, QLineEdit):
                    ui.setText(f"{self.data[framework][element]}")
                elif isinstance(ui, QCheckBox):
                    ui.setChecked(self.data[framework][element])
                elif isinstance(ui, QDoubleSpinBox):
                    ui.setValue(self.data[framework][element])

    def readTabs(self) -> None:
        for element in self.data[self.framework]:
            ui = self.framework2gui[self.framework].get(element)
            if isinstance(ui, QComboBox):
                self.data[self.framework]["deviceName"] = ui.currentText()
            elif isinstance(ui, QLineEdit):
                if isinstance(self.data[self.framework][element], int):
                    self.data[self.framework][element] = int(ui.text())
                else:
                    self.data[self.framework][element] = ui.text()
            elif isinstance(ui, QCheckBox):
                self.data[self.framework][element] = ui.isChecked()
            elif isinstance(ui, QDoubleSpinBox):
                self.data[self.framework][element] = ui.value()

    def readFramework(self) -> None:
        index = self.ui.tab.currentIndex()
        self.framework = self.ui.tab.widget(index).objectName()

    def updateDeviceNameList(self, framework: str, deviceNames: list[str]) -> None:
        self.discovers[framework]["deviceList"].clear()
        self.discovers[framework]["deviceList"].setView(QListView())
        for deviceName in deviceNames:
            self.discovers[framework]["deviceList"].addItem(deviceName)

    def discoverDevices(self, framework: str, widget: object = None) -> None:
        hostaddress = self.discovers[framework]["hostaddress"].text()
        port = self.discovers[framework]["port"].text()

        changeStyleDynamic(self.discovers[framework]["button"], "run", True)
        deviceInstance = self.app.dReg[self.device].run[framework]
        deviceType = self.app.dReg[self.device].instance.DEVICE_TYPE
        deviceNames = deviceInstance.discoverDevices(deviceType, hostaddress, port)
        changeStyleDynamic(self.discovers[framework]["button"], "run", False)

        if not deviceNames:
            self.msg.emit(2, framework.upper(), "Device", "No devices found")
            return
        for deviceName in deviceNames:
            self.msg.emit(0, framework.upper(), "Device discovered", f"{deviceName}")
        self.updateDeviceNameList(framework, deviceNames)
        self.framework = framework

    def checkApp(self, framework: str, folder: str = "") -> None:
        frameworkClass = self.app.plateSolve.run[framework]
        sucApp = frameworkClass.checkAvailabilityProgram(Path(folder))
        colorP = "green" if sucApp else "red"
        changeStyleDynamic(self.platesolvers[framework]["appPath"], "color", colorP)

    def checkIndex(self, framework: str, folder: str = "") -> None:
        frameworkClass = self.app.plateSolve.run[framework]
        sucIndex = frameworkClass.checkAvailabilityIndex(Path(folder))
        colorI = "green" if sucIndex else "red"
        changeStyleDynamic(self.platesolvers[framework]["indexPath"], "color", colorI)

    def selectAppPath(self, framework: str) -> None:
        folder = Path(self.platesolvers[framework]["appPath"].text())
        appFolderPath = self.openDir(self, "Select App Path", folder)
        if not appFolderPath.is_dir():
            return
        self.platesolvers[framework]["appPath"].setText(str(appFolderPath))

    def selectIndexPath(self, framework: str) -> None:
        folder = Path(self.platesolvers[framework]["indexPath"].text())
        indexFolderPath = self.openDir(self, "Select Index Path", folder)
        if not indexFolderPath.is_dir():
            return
        self.platesolvers[framework]["indexPath"].setText(str(indexFolderPath))

    def selectAscomDriver(self) -> None:
        ascom = AscomClass(parent=self.parent)
        deviceName = ascom.selectAscomDriver(self.ui.ascomDevice.text(), self.deviceType)
        self.ui.ascomDevice.setText(deviceName)

    def selectBoltwoodPath(self) -> None:
        folder = Path(self.ui.boltwoodPath.text()).parent
        boltwoodFilePath = self.openFile(
            self, "Select Boltwood Filepath", folder, "All Files (*)"
        )
        if not boltwoodFilePath.is_file():
            return
        self.framework2gui["boltwood"]["filePath"].setText(str(boltwoodFilePath))
