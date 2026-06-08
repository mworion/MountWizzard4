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
from dataclasses import fields
from typing import Any


class DriverHandling:
    def __init__(self, app: Any) -> None:
        self.app = app
        self.dReg = app.dReg

    def initConfig(self) -> None:
        cfgSetting = self.app.config.get("SettingDevice", {})
        for entry in self.dReg.configurable():
            if entry.name not in cfgSetting:
                continue
            for framework in entry.instance.run:
                if not hasattr(entry.instance.run[framework], "config"):
                    continue
                if framework not in cfgSetting[entry.name]:
                    continue
                for field in fields(entry.instance.run[framework].config):
                    if field.name not in cfgSetting[entry.name][framework]:
                        continue
                    value = cfgSetting[entry.name][framework][field.name]
                    setattr(entry.instance.run[framework].config, field.name, value)
        self.startDevices()

    def storeConfig(self) -> None:
        cfgSetting = {}
        for entry in self.dReg.configurable():
            cfgDevice = {}
            for framework in entry.instance.run:
                cfgFramework = {}
                if not hasattr(entry.instance.run[framework], "config"):
                    continue
                for field in fields(entry.instance.run[framework].config):
                    cfgFramework[field.name] = getattr(entry.instance.run[framework].config, field.name)
                cfgDevice[framework] = cfgFramework
            cfgSetting[entry.name] = cfgDevice
        self.app.config["SettingDevice"] = cfgSetting

    def stopDevice(self, device: str) -> None:
        self.dReg.setStat(device, None)
        self.dReg[device].stopCommunication()
        self.dReg[device].data.clear()

    def stopDevices(self) -> None:
        for entry in self.dReg.configurable():
            self.stopDdevice(entry.name)

    def startDevice(self, device: str) -> None:
        if not self.dReg[device].framework:
            return
        if not self.dReg[device].run[self.dReg[device].framework].config.deviceName:
            return
        self.dReg.setStat(device, True)
        self.dReg[device].startCommunication()

    def startDevices(self) -> None:
        for entry in self.dReg.configurable():
            self.startDevice(entry.name)
