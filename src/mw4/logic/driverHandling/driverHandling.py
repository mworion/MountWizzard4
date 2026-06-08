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
        config = self.app.config.get("SettingDevice", {})
        for entry in self.dReg.configurable():
            for framework in entry.instance.run:
                if not hasattr(entry.instance.run[framework], "config"):
                    continue
                for field in fields(entry.instance.run[framework].config):
                    if entry.name not in config:
                        continue
                    if field.name not in config[entry.instance.DEVICE_TYPE]:
                        continue
                    value = config[entry.instance.DEVICE_TYPE][field.name]
                    setattr(entry.instance.run[framework].config, field.name, value)
        self.startDevices()

    def storeConfig(self) -> None:
        config = {}
        for entry in self.dReg.configurable():
            cfg = {}
            for framework in entry.instance.run:
                if not hasattr(entry.instance.run[framework], "config"):
                    continue
                for field in fields(entry.instance.run[framework].config):
                    cfg[field.name] = getattr(entry.instance.run[framework].config, field.name)
            config[entry.name] = cfg
        self.app.config["SettingDevice"] = config

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
        self.dReg[device].startCommunication()

    def startDevices(self) -> None:
        for entry in self.dReg.configurable():
            self.startDevice(entry.name)
