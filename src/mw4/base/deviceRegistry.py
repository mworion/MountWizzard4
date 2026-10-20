# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import logging
from collections.abc import Iterator
from dataclasses import fields
from mw4.base.appProtocol import AppProtocol
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
from typing import Any, Literal, overload


class DeviceRegistry(QObject):
    log = logging.getLogger("MW4")

    def __init__(self, app: AppProtocol, mount: MountDevice | None = None) -> None:
        super().__init__()
        self.app = app
        self.signalsToName: dict[int, str] = {}
        if mount is None:
            mount = MountDevice(app, verbose=True)
        self.d: dict[str, DeviceEntry[Any]] = {
            "mount": DeviceEntry(
                name="mount",
                instance=mount,
                deviceType="10micron",
                isConfigurable=False,
            ),
        }

    def addDevices(self, app: AppProtocol) -> None:
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
    # Typed access, backed by self.d so replaced entries never drift
    # ------------------------------------------------------------------
    @property
    def mount(self) -> DeviceEntry[MountDevice]:
        return self.d["mount"]

    @property
    def camera(self) -> DeviceEntry[Camera]:
        return self.d["camera"]

    @property
    def cover(self) -> DeviceEntry[Cover]:
        return self.d["cover"]

    @property
    def directWeather(self) -> DeviceEntry[DirectWeather]:
        return self.d["directWeather"]

    @property
    def dome(self) -> DeviceEntry[Dome]:
        return self.d["dome"]

    @property
    def filter(self) -> DeviceEntry[Filter]:
        return self.d["filter"]

    @property
    def focuser(self) -> DeviceEntry[Focuser]:
        return self.d["focuser"]

    @property
    def hidController(self) -> DeviceEntry[HidController]:
        return self.d["hidController"]

    @property
    def lightPanel(self) -> DeviceEntry[LightPanel]:
        return self.d["lightPanel"]

    @property
    def measure(self) -> DeviceEntry[MeasureData]:
        return self.d["measure"]

    @property
    def plateSolve(self) -> DeviceEntry[PlateSolve]:
        return self.d["plateSolve"]

    @property
    def power(self) -> DeviceEntry[PegasusUPB]:
        return self.d["power"]

    @property
    def relay(self) -> DeviceEntry[KMRelay]:
        return self.d["relay"]

    @property
    def refraction(self) -> DeviceEntry[None]:
        return self.d["refraction"]

    @property
    def remote(self) -> DeviceEntry[Remote]:
        return self.d["remote"]

    @property
    def seeingWeather(self) -> DeviceEntry[SeeingWeather]:
        return self.d["seeingWeather"]

    @property
    def sensor1Weather(self) -> DeviceEntry[SensorWeather]:
        return self.d["sensor1Weather"]

    @property
    def sensor2Weather(self) -> DeviceEntry[SensorWeather]:
        return self.d["sensor2Weather"]

    @property
    def sensor3Weather(self) -> DeviceEntry[SensorWeather]:
        return self.d["sensor3Weather"]

    @property
    def sensor4Weather(self) -> DeviceEntry[SensorWeather]:
        return self.d["sensor4Weather"]

    @property
    def telescope(self) -> DeviceEntry[Telescope]:
        return self.d["telescope"]

    # ------------------------------------------------------------------
    # Mapping protocol — keeps membership tests and dynamic key lookups working
    # ------------------------------------------------------------------
    def __iter__(self) -> Iterator[str]:
        return iter(self.d)

    @overload
    def __getitem__(self, name: Literal["mount"]) -> DeviceEntry[MountDevice]: ...

    @overload
    def __getitem__(self, name: Literal["camera"]) -> DeviceEntry[Camera]: ...

    @overload
    def __getitem__(self, name: Literal["cover"]) -> DeviceEntry[Cover]: ...

    @overload
    def __getitem__(self, name: Literal["directWeather"]) -> DeviceEntry[DirectWeather]: ...

    @overload
    def __getitem__(self, name: Literal["dome"]) -> DeviceEntry[Dome]: ...

    @overload
    def __getitem__(self, name: Literal["filter"]) -> DeviceEntry[Filter]: ...

    @overload
    def __getitem__(self, name: Literal["focuser"]) -> DeviceEntry[Focuser]: ...

    @overload
    def __getitem__(self, name: Literal["hidController"]) -> DeviceEntry[HidController]: ...

    @overload
    def __getitem__(self, name: Literal["lightPanel"]) -> DeviceEntry[LightPanel]: ...

    @overload
    def __getitem__(self, name: Literal["measure"]) -> DeviceEntry[MeasureData]: ...

    @overload
    def __getitem__(self, name: Literal["plateSolve"]) -> DeviceEntry[PlateSolve]: ...

    @overload
    def __getitem__(self, name: Literal["power"]) -> DeviceEntry[PegasusUPB]: ...

    @overload
    def __getitem__(self, name: Literal["relay"]) -> DeviceEntry[KMRelay]: ...

    @overload
    def __getitem__(self, name: Literal["refraction"]) -> DeviceEntry[None]: ...

    @overload
    def __getitem__(self, name: Literal["remote"]) -> DeviceEntry[Remote]: ...

    @overload
    def __getitem__(self, name: Literal["seeingWeather"]) -> DeviceEntry[SeeingWeather]: ...

    @overload
    def __getitem__(self, name: Literal["sensor1Weather"]) -> DeviceEntry[SensorWeather]: ...

    @overload
    def __getitem__(self, name: Literal["sensor2Weather"]) -> DeviceEntry[SensorWeather]: ...

    @overload
    def __getitem__(self, name: Literal["sensor3Weather"]) -> DeviceEntry[SensorWeather]: ...

    @overload
    def __getitem__(self, name: Literal["sensor4Weather"]) -> DeviceEntry[SensorWeather]: ...

    @overload
    def __getitem__(self, name: Literal["telescope"]) -> DeviceEntry[Telescope]: ...

    @overload
    def __getitem__(self, name: str) -> DeviceEntry[Any]: ...

    def __getitem__(self, name: str) -> DeviceEntry[Any]:
        return self.d[name]

    def __contains__(self, name: object) -> bool:
        return name in self.d

    def configurable(self) -> Iterator[DeviceEntry[Any]]:
        for entry in self.d.values():
            if entry.isConfigurable and entry.instance is not None:
                yield entry

    def realDrivers(self) -> Iterator[DeviceEntry[Any]]:
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

    def writeConfigToSingleDevice(self, device: str, cfg: dict[str, dict[str, Any]]) -> None:
        self.d[device].instance.framework = cfg.get("framework", "")
        for framework in self.d[device].run:
            if not hasattr(self.d[device].run[framework], "config"):
                continue
            if framework not in cfg:
                continue
            for field in fields(self.d[device].run[framework].config):
                if field.name not in cfg[framework]:
                    continue
                value = cfg[framework][field.name]
                setattr(self.d[device].run[framework].config, field.name, value)

    def writeConfigToAllDevices(self, cfg: dict[str, dict[str, dict[str, Any]]]) -> None:
        for entry in self.configurable():
            if entry.name not in cfg:
                continue
            self.writeConfigToSingleDevice(entry.name, cfg[entry.name])

    def initConfig(self) -> None:
        self.writeConfigToAllDevices(self.app.config.get("SettingDevice", {}))
        self.writeConfigToSingleDevice("mount", self.app.config.get("SettingDeviceMount", {}))
        self.d["mount"].instance.framework = "10micron"

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
        self.log.debug("Stopping all devices")
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
        self.log.debug("Starting all devices")
        for entry in self.configurable():
            self.startDevice(entry.name)

    def deviceConnected(self, *_args: Any) -> None:
        name = self.signalsToName.get(id(self.sender()))
        if name is None:
            return
        deviceName = _args[0] if _args else ""
        self.setStat(name, True)
        self.app.signals.ui.msg.emit(0, "Driver", "Device connected", f"{deviceName}::{name}")

    def deviceDisconnected(self, *_args: Any) -> None:
        name = self.signalsToName.get(id(self.sender()))
        if name is None:
            return
        deviceName = _args[0] if _args else ""
        self.setStat(name, False)
        self.app.signals.ui.msg.emit(0, "Driver", "Device disconnected", f"{deviceName}::{name}")
