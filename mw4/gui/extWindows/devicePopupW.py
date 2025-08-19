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
from pathlib import Path
from functools import partial

# external packages
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QListView, QComboBox, QLineEdit
from PySide6.QtWidgets import QCheckBox, QDoubleSpinBox

# local import
from base.indiClass import IndiClass
from base.alpacaClass import AlpacaClass
from base.ascomClass import AscomClass
from gui.utilities import toolsQtWidget
from gui.widgets.devicePopup_ui import Ui_DevicePopup
from gui.utilities.toolsQtWidget import changeStyleDynamic, clickable


class DevicePopup(toolsQtWidget.MWidget):
    """ """

    def __init__(self, parentWidget, parent, driver=None, deviceType=None, data=None):
        super().__init__()
        self.parent = parent
        self.app = parent.app
        self.msg = parent.app.msg
        self.data = data
        self.driver = driver
        self.deviceType = deviceType

        self.ui = Ui_DevicePopup()
        self.ui.setupUi(self)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        x = parentWidget.x() + int((parentWidget.width() - self.width()) / 2)
        y = parentWidget.y() + int((parentWidget.height() - self.height()) / 2)
        self.move(x, y)
        pixmap = self.svg2pixmap(":/icon/cogs.svg", self.M_PRIM)
        self.ui.iconPixmap.setPixmap(pixmap)

        self.returnValues = {"close": "cancel"}
        self.framework2gui = {
            "indi": {
                "hostaddress": self.ui.indiHostAddress,
                "port": self.ui.indiPort,
                "deviceList": self.ui.indiDeviceList,
                "messages": self.ui.indiMessages,
                "loadConfig": self.ui.indiLoadConfig,
                "updateRate": self.ui.indiUpdateRate,
            },
            "alpaca": {
                "hostaddress": self.ui.alpacaHostAddress,
                "port": self.ui.alpacaPort,
                "user": self.ui.alpacaUser,
                "password": self.ui.alpacaPassword,
                "deviceList": self.ui.alpacaDeviceList,
                "updateRate": self.ui.alpacaUpdateRate,
            },
            "ascom": {
                "deviceName": self.ui.ascomDevice,
            },
            "sgpro": {
                "deviceList": self.ui.sgproDeviceList,
            },
            "nina": {
                "deviceList": self.ui.ninaDeviceList,
            },
            "astrometry": {
                "deviceList": self.ui.astrometryDeviceList,
                "searchRadius": self.ui.astrometrySearchRadius,
                "timeout": self.ui.astrometryTimeout,
                "appPath": self.ui.astrometryAppPath,
                "indexPath": self.ui.astrometryIndexPath,
            },
            "astap": {
                "deviceList": self.ui.astapDeviceList,
                "searchRadius": self.ui.astapSearchRadius,
                "timeout": self.ui.astapTimeout,
                "appPath": self.ui.astapAppPath,
                "indexPath": self.ui.astapIndexPath,
            },
            "watney": {
                "deviceList": self.ui.watneyDeviceList,
                "searchRadius": self.ui.watneySearchRadius,
                "timeout": self.ui.watneyTimeout,
                "appPath": self.ui.watneyAppPath,
                "indexPath": self.ui.watneyIndexPath,
            },
            "onlineWeather": {
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
            },
            "astap": {
                "appPath": self.ui.astapAppPath,
                "indexPath": self.ui.astapIndexPath,
            },
            "watney": {
                "appPath": self.ui.watneyAppPath,
                "indexPath": self.ui.watneyIndexPath,
            },
        }

        self.discovers = {
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
            clickable(self.discovers[framework]["button"]).connect(
                partial(self.discoverDevices, framework)
            )

        self.ui.ascomSelector.clicked.connect(self.selectAscomDriver)

        for framework in self.platesolvers:
            clickable(self.platesolvers[framework]["appPath"]).connect(
                partial(self.selectAppPath, framework)
            )
            clickable(self.platesolvers[framework]["indexPath"]).connect(
                partial(self.selectIndexPath, framework)
            )
            self.platesolvers[framework]["appPath"].textChanged.connect(
                partial(self.checkApp, framework)
            )
            self.platesolvers[framework]["indexPath"].textChanged.connect(
                partial(self.checkIndex, framework)
            )

        self.initConfig()
        self.show()

    def initConfig(self) -> None:
        """ """
        self.setWindowTitle(f"Setup driver for {self.deviceType}")
        self.populateTabs()
        self.selectTabs()
        framework = self.data.get("framework", "")
        if framework in self.platesolvers:
            self.checkApp(framework, self.platesolvers[framework]["appPath"].text())
            self.checkIndex(framework, self.platesolvers[framework]["indexPath"].text())

    def storeConfig(self) -> None:
        """ """
        self.readFramework()
        self.readTabs()
        self.returnValues["indiCopyConfig"] = self.ui.indiCopyConfig.isChecked()
        self.returnValues["alpacaCopyConfig"] = self.ui.alpacaCopyConfig.isChecked()
        self.returnValues["close"] = "ok"
        self.returnValues["driver"] = self.driver
        self.close()

    def selectTabs(self) -> None:
        """ """
        firstFramework = next(iter(self.data["frameworks"]))
        framework = self.data.get("framework")
        if not framework:
            framework = firstFramework

        tabIndex = self.getTabIndex(self.ui.tab, framework)
        self.ui.tab.setCurrentIndex(tabIndex)

        for index in range(0, self.ui.tab.count()):
            isVisible = self.ui.tab.widget(index).objectName() in self.data["frameworks"]
            self.ui.tab.setTabVisible(index, isVisible)

    def populateTabs(self) -> None:
        """ """
        frameworks = self.data["frameworks"]
        for fw in frameworks:
            frameworkElements = frameworks[fw]
            for element in frameworkElements:
                ui = self.framework2gui[fw].get(element)

                if isinstance(ui, QComboBox):
                    ui.clear()
                    ui.setView(QListView())
                    for i, deviceName in enumerate(frameworks[fw][element]):
                        ui.addItem(deviceName)
                        if frameworks[fw]["deviceName"] == deviceName:
                            ui.setCurrentIndex(i)

                elif isinstance(ui, QLineEdit):
                    ui.setText(f"{frameworks[fw][element]}")

                elif isinstance(ui, QCheckBox):
                    ui.setChecked(frameworks[fw][element])

                elif isinstance(ui, QDoubleSpinBox):
                    ui.setValue(frameworks[fw][element])

    def readTabs(self) -> None:
        """ """
        framework = self.data["framework"]
        frameworkData = self.data["frameworks"][framework]

        for element in list(frameworkData):
            ui = self.framework2gui[framework].get(element)
            if isinstance(ui, QComboBox):
                frameworkData["deviceName"] = ui.currentText()
                frameworkData[element].clear()
                for index in range(ui.model().rowCount()):
                    frameworkData[element].append(ui.model().item(index).text())

            elif isinstance(ui, QLineEdit):
                if isinstance(frameworkData[element], int):
                    frameworkData[element] = int(ui.text())
                else:
                    frameworkData[element] = ui.text()

            elif isinstance(ui, QCheckBox):
                frameworkData[element] = ui.isChecked()
            elif isinstance(ui, QDoubleSpinBox):
                frameworkData[element] = ui.value()

    def readFramework(self) -> None:
        """ """
        index = self.ui.tab.currentIndex()
        framework = self.ui.tab.widget(index).objectName()
        self.data["framework"] = framework

    def updateDeviceNameList(self, framework: str, deviceNames: list[str]) -> None:
        self.discovers[framework]["deviceList"].clear()
        self.discovers[framework]["deviceList"].setView(QListView())
        for deviceName in deviceNames:
            self.discovers[framework]["deviceList"].addItem(deviceName)

    def discoverDevices(self, framework: str, widget) -> None:
        """ """
        device = self.discovers[framework]["class"](parent=self.parent)

        if framework in ["indi", "alpaca"]:
            device.hostaddress = self.discovers[framework]["hostaddress"].text()
            device.port = self.discovers[framework]["port"].text()

        changeStyleDynamic(self.discovers[framework]["button"], "running", True)
        deviceNames = device.discoverDevices(deviceType=self.deviceType)
        changeStyleDynamic(self.discovers[framework]["button"], "running", False)

        if not deviceNames:
            self.msg.emit(2, framework.upper(), "Device", "No devices found")
            return

        for deviceName in deviceNames:
            self.msg.emit(0, framework.upper(), "Device discovered", f"{deviceName}")

        self.updateDeviceNameList(framework, deviceNames)

    def checkApp(self, framework: str, folder: str = "") -> None:
        """ """
        frameworkClass = self.app.plateSolve.run[framework]
        sucApp = frameworkClass.checkAvailabilityProgram(Path(folder))
        colorP = "green" if sucApp else "red"
        changeStyleDynamic(self.platesolvers[framework]["appPath"], "color", colorP)

    def checkIndex(self, framework: str, folder: str = "") -> None:
        """ """
        frameworkClass = self.app.plateSolve.run[framework]
        sucIndex = frameworkClass.checkAvailabilityIndex(Path(folder))
        colorI = "green" if sucIndex else "red"
        changeStyleDynamic(self.platesolvers[framework]["indexPath"], "color", colorI)

    def selectAppPath(self, framework: str, folder: str = "") -> None:
        """ """
        appFolderPath = self.openDir(self, "Select App Path", Path(folder))
        if not appFolderPath.is_dir():
            return
        self.platesolvers[framework]["appPath"].setText(str(appFolderPath))

    def selectIndexPath(self, framework: str, folder: str = "") -> None:
        """ """
        indexFolderPath = self.openDir(self, "Select Index Path", Path(folder))
        if not indexFolderPath.is_dir():
            return
        self.platesolvers[framework]["indexPath"].setText(str(indexFolderPath))

    def selectAscomDriver(self) -> None:
        """ """
        ascom = AscomClass(parent=self.parent)
        deviceName = ascom.selectAscomDriver(self.ui.ascomDevice.text())
        self.ui.ascomDevice.setText(deviceName)
