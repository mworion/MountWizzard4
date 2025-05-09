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
import platform
from pathlib import Path
from functools import partial

# external packages
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QListView, QComboBox, QLineEdit
from PySide6.QtWidgets import QCheckBox, QDoubleSpinBox

if platform.system() == "Windows":
    import win32com.client

# local import
from base.indiClass import IndiClass
from base.alpacaClass import AlpacaClass
from base.sgproClass import SGProClass
from base.ninaClass import NINAClass
from gui.utilities import toolsQtWidget
from gui.widgets.devicePopup_ui import Ui_DevicePopup
from gui.utilities.toolsQtWidget import changeStyleDynamic, clickable


class DevicePopup(toolsQtWidget.MWidget):
    """ """

    def __init__(self, parentWidget, app=None, driver=None, deviceType=None, data=None):
        super().__init__()
        self.app = app
        self.data = data
        self.driver = driver
        self.deviceType = deviceType
        self.msg = app.msg

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

        self.ui.cancel.clicked.connect(self.close)
        self.ui.ok.clicked.connect(self.storeConfig)
        self.ui.indiDiscover.clicked.connect(self.discoverIndiDevices)
        self.ui.alpacaDiscover.clicked.connect(self.discoverAlpacaDevices)
        self.ui.sgproDiscover.clicked.connect(self.discoverSGProDevices)
        self.ui.ninaDiscover.clicked.connect(self.discoverNINADevices)
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

    def initConfig(self) -> None:
        """ """
        self.setWindowTitle(f"Setup driver for {self.deviceType}")
        self.populateTabs()
        self.selectTabs()
        framework = self.data.get("framework", "")
        if framework in self.platesolvers:
            self.checkApp(framework, self.platesolvers[framework]["appPath"].text())
            self.checkIndex(framework, self.platesolvers[framework]["indexPath"].text())

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
                if isinstance(frameworkData[element], str):
                    frameworkData[element] = ui.text()
                elif isinstance(frameworkData[element], int):
                    frameworkData[element] = int(ui.text())
                else:
                    frameworkData[element] = float(ui.text())

            elif isinstance(ui, QCheckBox):
                frameworkData[element] = ui.isChecked()
            elif isinstance(ui, QDoubleSpinBox):
                frameworkData[element] = ui.value()

    def readFramework(self) -> None:
        """ """
        index = self.ui.tab.currentIndex()
        framework = self.ui.tab.widget(index).objectName()
        self.data["framework"] = framework

    def storeConfig(self) -> None:
        """ """
        self.readFramework()
        self.readTabs()
        self.returnValues["indiCopyConfig"] = self.ui.indiCopyConfig.isChecked()
        self.returnValues["alpacaCopyConfig"] = self.ui.alpacaCopyConfig.isChecked()
        self.returnValues["close"] = "ok"
        self.returnValues["driver"] = self.driver
        self.close()

    def updateIndiDeviceNameList(self, deviceNames: list[str]) -> None:
        """ """
        self.ui.indiDeviceList.clear()
        self.ui.indiDeviceList.setView(QListView())
        for deviceName in deviceNames:
            self.ui.indiDeviceList.addItem(deviceName)

    def discoverIndiDevices(self) -> None:
        """ """
        indi = IndiClass(app=self.app, data=self.data)
        indi.hostaddress = self.ui.indiHostAddress.text()
        indi.port = self.ui.indiPort.text()

        changeStyleDynamic(self.ui.indiDiscover, "running", True)
        deviceNames = indi.discoverDevices(deviceType=self.deviceType)
        changeStyleDynamic(self.ui.indiDiscover, "running", False)

        if not deviceNames:
            self.msg.emit(2, "INDI", "Device", "No devices found")
            return

        for deviceName in deviceNames:
            self.msg.emit(0, "INDI", "Device discovered", f"{deviceName}")

        self.updateIndiDeviceNameList(deviceNames=deviceNames)

    def updateAlpacaDeviceNameList(self, deviceNames: list[str]) -> None:
        """ """
        self.ui.alpacaDeviceList.clear()
        self.ui.alpacaDeviceList.setView(QListView())
        for deviceName in deviceNames:
            self.ui.alpacaDeviceList.addItem(deviceName)

    def discoverAlpacaDevices(self) -> None:
        """ """
        alpaca = AlpacaClass(app=self.app, data=self.data)
        alpaca.hostaddress = self.ui.alpacaHostAddress.text()
        alpaca.port = self.ui.alpacaPort.text()
        alpaca.apiVersion = 1

        changeStyleDynamic(self.ui.alpacaDiscover, "running", True)
        deviceNames = alpaca.discoverDevices(deviceType=self.deviceType)
        changeStyleDynamic(self.ui.alpacaDiscover, "running", False)

        if not deviceNames:
            self.msg.emit(2, "ALPACA", "Device", "No devices found")
            return

        for deviceName in deviceNames:
            self.msg.emit(0, "ALPACA", "Device discovered", f"{deviceName}")

        self.updateAlpacaDeviceNameList(deviceNames=deviceNames)

    def updateSGProDeviceNameList(self, deviceNames: list[str]) -> None:
        """ """
        self.ui.sgproDeviceList.clear()
        self.ui.sgproDeviceList.setView(QListView())
        for deviceName in deviceNames:
            self.ui.sgproDeviceList.addItem(deviceName)

    def discoverSGProDevices(self) -> None:
        """ """
        sgpro = SGProClass(app=self.app, data=self.data)
        sgpro.DEVICE_TYPE = "Camera"

        changeStyleDynamic(self.ui.sgproDiscover, "running", True)
        deviceNames = sgpro.discoverDevices()
        if not deviceNames:
            self.msg.emit(2, "SGPRO", "Device", "No devices found")

        deviceNames.insert(0, "SGPro controlled")
        changeStyleDynamic(self.ui.sgproDiscover, "running", False)

        for deviceName in deviceNames:
            self.msg.emit(0, "SGPRO", "Device discovered", f"{deviceName}")

        self.updateSGProDeviceNameList(deviceNames=deviceNames)

    def updateNINADeviceNameList(self, deviceNames: list[str]) -> None:
        """ """
        self.ui.ninaDeviceList.clear()
        self.ui.ninaDeviceList.setView(QListView())
        for deviceName in deviceNames:
            self.ui.ninaDeviceList.addItem(deviceName)

    def discoverNINADevices(self) -> None:
        """ """
        nina = NINAClass(app=self.app, data=self.data)
        nina.DEVICE_TYPE = "Camera"

        changeStyleDynamic(self.ui.ninaDiscover, "running", True)
        deviceNames = nina.discoverDevices()
        if not deviceNames:
            self.msg.emit(2, "N.I.N.A.", "Device", "No devices found")

        deviceNames.insert(0, "N.I.N.A. controlled")
        changeStyleDynamic(self.ui.ninaDiscover, "running", False)

        for deviceName in deviceNames:
            self.msg.emit(0, "N.I.N.A.", "Device discovered", f"{deviceName}")

        self.updateNINADeviceNameList(deviceNames=deviceNames)

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
        deviceName = self.ui.ascomDevice.text()
        try:
            chooser = win32com.client.Dispatch("ASCOM.Utilities.Chooser")
            chooser.DeviceType = self.deviceType
            deviceName = chooser.Choose(deviceName)

        except Exception as e:
            self.log.critical(f"Error: {e}")
            return

        self.ui.ascomDevice.setText(deviceName)
