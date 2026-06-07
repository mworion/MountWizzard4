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
from mw4.base.deviceRegistry import DeviceRegistry


class DriverHandling:
    def __init__(self, dReg: DeviceRegistry, driversData: dict) -> None:
        self.dReg = dReg
        self.driversData = driversData

    def initConfig(self) -> None:
        self.app.dHandling.loadDriversDataFromConfig(self.app.config)
        self.startDrivers()

    def addMissingFrameworksData(self, driver: str, config: dict) -> dict:
        for framework in self.dReg[driver].run:
            if framework not in config[driver]["frameworks"]:
                entry = self.dReg[driver].instance.defaultConfig["frameworks"][framework]
                config[driver]["frameworks"][framework] = entry
        return config

    def addMissingDefaultData(self, config: dict) -> dict:
        for entry in self.dReg.configurable():
            if entry.name not in config:
                config[entry.name] = {}
                config[entry.name].update(entry.instance.defaultConfig)
                continue
            config = self.addMissingFrameworksData(entry.name, config)
        return config

    def removeUnknownDriversData(self, config: dict) -> dict:
        for driver in list(config):
            if driver not in self.dReg.drivers:
                del config[driver]
        return config

    def loadDriversDataFromConfig(self, config: dict) -> None:
        self.driversData.clear()
        config = self.addMissingDefaultData(config)
        config = self.removeUnknownDriversData(config)
        self.driversData.update(config)

    def stopDriver(self, driver: str) -> None:
        self.dReg.setStat(driver, None)
        framework = self.dReg[driver].instance.framework
        if framework not in self.dReg[driver].run:
            return
        if self.dReg[driver].run[framework].deviceName == "":
            return
        self.dReg[driver].instance.stopCommunication()
        self.dReg[driver].data.clear()
        self.dReg[driver].run[framework].deviceName = ""

    def stopDrivers(self) -> None:
        for entry in self.dReg.configurable():
            self.stopDriver(driver=entry.name)

    def configDriver(self, driver: str) -> None:
        self.dReg.setStat(driver, False)
        framework = self.driversData[driver]["framework"]
        if self.driversData[driver]["framework"] not in self.dReg[driver].run:
            return

        frameworkConfig = self.driversData[driver]["frameworks"][framework]
        driverInstance = self.dReg[driver].run[framework]
        for attribute in frameworkConfig:
            setattr(driverInstance, attribute, frameworkConfig[attribute])

    def startDriver(self, driver: str) -> None:
        framework = self.driversData[driver]["framework"]
        if framework not in self.dReg[driver].run:
            return

        driverInstance = self.dReg[driver].instance
        loadConfig = self.driversData[driver]["frameworks"][framework].get("loadConfig", False)
        self.dReg[driver].instance.loadConfig = loadConfig
        self.dReg[driver].instance.framework = framework
        self.configDriver(driver)
        driverInstance.startCommunication()

    def startDrivers(self) -> None:
        for entry in self.dReg.configurable():
            if entry.name not in self.driversData:
                continue
            if self.driversData[entry.name]["framework"] == "":
                continue
            self.startDriver(entry.name)
