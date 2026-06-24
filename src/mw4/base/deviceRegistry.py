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
from mw4.logic.hidController.hidController import HidController
from mw4.logic.lightPanel.lightPanel import LightPanel
from mw4.logic.measure.measure import MeasureData
from mw4.logic.plateSolve.plateSolve import PlateSolve
from mw4.logic.powerswitch.kmRelay import KMRelay
from mw4.logic.powerswitch.pegasusUPB import PegasusUPB
from mw4.logic.remote.remote import Remote
from mw4.logic.telescope.telescope import Telescope
from mw4.mountcontrol.mount import MountDevice
from PySide6.QtCore import QObject
from typing import Any


class DeviceRegistry(QObject):
    def __init__(self, app: Any) -> None:
        super().__init__()
        self.app = app
        self.signalsToName: dict[int, str] = {}

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
        deviceSpec: list[tuple[str, Any, str | None, bool]] = [
            ("camera", Camera, "camera", True),
            ("cover", Cover, "covercalibrator", True),
            ("directWeather", DirectWeather, None, True),
            ("dome", Dome, "dome", True),
            ("filter", Filter, "filterwheel", True),
            ("focuser", Focuser, "focuser", True),
            ("hidController", HidController, "hid", True),
            ("lightPanel", LightPanel, "covercalibrator", True),
            ("measure", MeasureData, None, True),
            ("plateSolve", PlateSolve, "plateSolve", True),
            ("power", PegasusUPB, "switch", True),
            ("relay", KMRelay, None, True),
            ("refraction", lambda _app: None, None, False),
            ("remote", Remote, None, True),
            ("seeingWeather", SeeingWeather, "observingconditions", True),
            ("sensor1Weather", SensorWeather, "observingconditions", True),
            ("sensor2Weather", SensorWeather, "observingconditions", True),
            ("sensor3Weather", SensorWeather, "observingconditions", True),
            ("sensor4Weather", SensorWeather, "observingconditions", True),
            ("telescope", Telescope, "telescope", True),
        ]
        for name, factory, deviceType, isConfigurable in deviceSpec:
            self.d[name] = DeviceEntry(
                name=name,
                instance=factory(app),
                deviceType=deviceType,
                isConfigurable=isConfigurable,
            )
        for entry in self.realDrivers():
            if hasattr(self.d[entry.name].instance, "signals"):
                sig = self.d[entry.name].signals
                self.signalsToName[id(sig)] = entry.name
                sig.deviceConnected.connect(self.deviceConnected)
                sig.deviceDisconnected.connect(self.deviceDisconnected)

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

    def realDrivers(self) -> Iterator[DeviceEntry]:
        for entry in self.d.values():
            if entry.instance is not None:
                yield entry

    def setStat(self, name: str, value: bool | None) -> None:
        self.d[name].stat = value

    def collectConfigFromSingleDevice(self, device: str) -> dict[str, dict[str, Any]]:
        cfgDevice: dict[str, Any] = {"framework": self.d[device].framework}
        for framework in self.d[device].run:
            cfgFramework: dict[str, Any] = {}
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

    def writeConfigToSingleDevice(
        self, device: str, cfgDevice: dict[str, dict[str, Any]]
    ) -> None:
        self.d[device].instance.framework = cfgDevice.get("framework", "")
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

    def writeConfigToAllDevices(
        self, cfgSetting: dict[str, dict[str, dict[str, Any]]]
    ) -> None:
        for entry in self.configurable():
            if entry.name not in cfgSetting:
                continue
            self.writeConfigToSingleDevice(entry.name, cfgSetting[entry.name])

    def initConfig(self) -> None:
        self.writeConfigToAllDevices(self.app.config.get("SettingDevice", {}))
        self.writeConfigToSingleDevice("mount", self.app.config.get("SettingDeviceMount", {}))
        self.startDevices()

    def storeConfig(self) -> None:
        self.app.config["SettingDevice"] = self.collectConfigFromAllDevices()
        self.app.config["SettingDeviceMount"] = self.collectConfigFromSingleDevice("mount")

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
        self.setStat(device, False)
        self.d[device].instance.startCommunication()

    def startDevices(self) -> None:
        for entry in self.configurable():
            self.startDevice(entry.name)

    def deviceConnected(self, *_args: Any) -> None:
        name = self.signalsToName.get(id(self.sender()))
        if name is None:
            return
        deviceName = _args[0] if _args else ""
        self.setStat(name, True)
        self.app.msg.emit(0, "Driver", "Device connected", f"{deviceName}::{name}")

    def deviceDisconnected(self, *_args: Any) -> None:
        name = self.signalsToName.get(id(self.sender()))
        if name is None:
            return
        deviceName = _args[0] if _args else ""
        self.setStat(name, False)
        self.app.msg.emit(0, "Driver", "Device disconnected", f"{deviceName}::{name}")
