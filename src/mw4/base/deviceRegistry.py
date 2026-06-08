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
from collections.abc import Iterator
from dataclasses import fields
from mw4.base.deviceEntry import DeviceEntry
from mw4.logic.camera.camera import Camera
from mw4.logic.cover.cover import Cover
from mw4.logic.dome.dome import Dome
from mw4.logic.environment.directWeather import DirectWeather
from mw4.logic.environment.seeingWeather import SeeingWeather
from mw4.logic.environment.sensorWeather import SensorWeather
from mw4.logic.filter.filter import Filter
from mw4.logic.focuser.focuser import Focuser
from mw4.logic.lightPanel.lightPanel import LightPanel
from mw4.logic.measure.measure import MeasureData
from mw4.logic.plateSolve.plateSolve import PlateSolve
from mw4.logic.powerswitch.kmRelay import KMRelay
from mw4.logic.powerswitch.pegasusUPB import PegasusUPB
from mw4.logic.remote.remote import Remote
from mw4.logic.telescope.telescope import Telescope
from mw4.mountcontrol.mount import MountDevice
from typing import Any


class DeviceRegistry:

    def __init__(self, app: Any) -> None:
        self.app = app
        self.app.stopDevices.connect(self.stopDevices)

        if hasattr(app, "mount") and app.mount is not None:
            # Test only: tests inject mock mounts before calling registry
            mount_instance = app.mount
        else:
            mount_instance = MountDevice(app, verbose=True)
            app.mount = mount_instance

        self.d: dict[str, DeviceEntry] = {
            "mount": DeviceEntry(
                name="mount",
                instance=mount_instance,
                deviceType=None,
                isConfigurable=False,
            ),
        }

    def addDevices(self, app: Any) -> None:
        self.d["camera"] = DeviceEntry(
            name="camera",
            instance=Camera(app),  # Can access app.mount
            deviceType="camera",
            isConfigurable=True,
        )
        self.d["cover"] = DeviceEntry(
            name="cover",
            instance=Cover(app),
            deviceType="covercalibrator",
            isConfigurable=True,
        )
        self.d["directWeather"] = DeviceEntry(
            name="directWeather",
            instance=DirectWeather(app),
            deviceType=None,
            isConfigurable=True,
        )
        self.d["dome"] = DeviceEntry(
            name="dome",
            instance=Dome(app),
            deviceType="dome",
            isConfigurable=True,
        )
        self.d["filter"] = DeviceEntry(
            name="filter",
            instance=Filter(app),
            deviceType="filterwheel",
            isConfigurable=True,
        )
        self.d["focuser"] = DeviceEntry(
            name="focuser",
            instance=Focuser(app),
            deviceType="focuser",
            isConfigurable=True,
        )
        self.d["lightPanel"] = DeviceEntry(
            name="lightPanel",
            instance=LightPanel(app),
            deviceType="covercalibrator",
            isConfigurable=True,
        )
        self.d["measure"] = DeviceEntry(
            name="measure",
            instance=MeasureData(app),
            deviceType=None,
            isConfigurable=True,
        )
        self.d["plateSolve"] = DeviceEntry(
            name="plateSolve",
            instance=PlateSolve(app),
            deviceType="plateSolve",
            isConfigurable=True,
        )
        self.d["power"] = DeviceEntry(
            name="power",
            instance=PegasusUPB(app),
            deviceType="switch",
            isConfigurable=True,
        )
        self.d["relay"] = DeviceEntry(
            name="relay",
            instance=KMRelay(),
            deviceType=None,
            isConfigurable=True,
        )
        self.d["refraction"] = DeviceEntry(
            name="refraction",
            instance=None,
            deviceType=None,
            isConfigurable=False,
        )
        self.d["remote"] = DeviceEntry(
            name="remote",
            instance=Remote(app),
            deviceType=None,
            isConfigurable=True,
        )
        self.d["seeingWeather"] = DeviceEntry(
            name="seeingWeather",
            instance=SeeingWeather(app),  # Can access app.mount
            deviceType="observingconditions",
            isConfigurable=True,
        )
        self.d["sensor1Weather"] = DeviceEntry(
            name="sensor1Weather",
            instance=SensorWeather(app),
            deviceType="observingconditions",
            isConfigurable=True,
        )
        self.d["sensor2Weather"] = DeviceEntry(
            name="sensor2Weather",
            instance=SensorWeather(app),
            deviceType="observingconditions",
            isConfigurable=True,
        )
        self.d["sensor3Weather"] = DeviceEntry(
            name="sensor3Weather",
            instance=SensorWeather(app),
            deviceType="observingconditions",
            isConfigurable=True,
        )
        self.d["sensor4Weather"] = DeviceEntry(
            name="sensor4Weather",
            instance=SensorWeather(app),
            deviceType="observingconditions",
            isConfigurable=True,
        )
        self.d["telescope"] = DeviceEntry(
            name="telescope",
            instance=Telescope(app),
            deviceType="telescope",
            isConfigurable=True,
        )

    # ------------------------------------------------------------------
    # Mapping protocol — keeps ``"x" in dReg`` and ``dReg["x"]`` working
    # ------------------------------------------------------------------
    def __iter__(self) -> Iterator[str]:
        return iter(self.d)

    def __getitem__(self, name: str) -> DeviceEntry:
        return self.d[name]

    def __contains__(self, name: object) -> bool:
        return name in self.d

    def configurable(self) -> Iterator[DeviceEntry]:
        for entry in self.d.values():
            if entry.isConfigurable and entry.instance is not None:
                yield entry

    def setStat(self, name: str, value: bool | None) -> None:
        self.d[name].stat = value

    def collectConfigFromSingleDevice(self, device: str) -> dict[str, dict[str, Any]]:
        cfgDevice: dict [str, Any] = {}
        for framework in self.d[device].run:
            cfgFramework: dict [str, Any] = {}
            if not hasattr(self.d[device].run[framework], "config"):
                continue
            for field in fields(self.d[device].run[framework].config):
                value = getattr(self.d[device].run[framework].config, field.name)
                cfgFramework[field.name] = value
            cfgDevice[framework] = cfgFramework
        return cfgDevice

    def collectConfigFromAllDevices(self) -> dict[str, dict[str, dict[str, Any]]]:
        cfgSetting: dict[str, dict[str, dict[str, Any]]] = {}
        for entry in self.configurable():
            cfgSetting[entry.name] = self.collectConfigFromSingleDevice(entry.name)
        return cfgSetting
    
    def writeConfigToSingleDevice(self, device: str, cfgDevice: dict[str, dict[str, Any]]) -> None:
        for framework in self.d[device].run:
            if not hasattr(self.d[device].run[framework], "config"):
                continue
            if framework not in cfgDevice:
                continue
            for field in fields(self.d[device].run[framework].config):
                if field.name not in cfgDevice[framework]:
                    continue
                value = cfgDevice[framework][field.name]
                setattr(self.d[device].run[framework].config, field.name, value)

    def writeConfigToAllDevices(self, cfgSetting: dict[str, dict[str, dict[str, Any]]]) -> None:
        for entry in self.configurable():
            if entry.name not in cfgSetting:
                continue
            self.writeConfigToSingleDevice(entry.name, cfgSetting[entry.name])

    def initConfig(self) -> None:
        self.writeConfigToAllDevices(self.app.config.get("SettingDevice", {}))
        self.startDevices()

    def storeConfig(self) -> None:
        self.app.config["SettingDevice"] = self.collectConfigFromAllDevices()

    def stopDevice(self, device: str) -> None:
        if not self.d[device].framework:
            return
        if not self.d[device].run[self.d[device].framework].config.deviceName:
            return
        self.setStat(device, None)
        self.d[device].instance.stopCommunication()
        self.d[device].data.clear()

    def stopDevices(self) -> None:
        for entry in self.configurable():
            self.stopDevice(entry.name)

    def startDevice(self, device: str) -> None:
        if not self.d[device].framework:
            return
        if not self.d[device].run[self.d[device].framework].config.deviceName:
            return
        self.setStat(device, True)
        self.d[device].instance.startCommunication()

    def startDevices(self) -> None:
        for entry in self.configurable():
            self.startDevice(entry.name)
