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
from dataclasses import dataclass, field
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


@dataclass
class DeviceEntry:
    """Holds all metadata for one registered device driver."""

    name: str
    instance: Any | None
    deviceType: str | None
    isConfigurable: bool
    stat: bool | None = field(default=None)

    # ------------------------------------------------------------------
    # Convenience properties for quick access to common instance attributes
    # ------------------------------------------------------------------
    @property
    def signals(self) -> Any:
        """Convenience property to access instance.signals directly."""
        if self.instance is None:
            raise AttributeError(f"Device '{self.name}' instance is None")
        return self.instance.signals

    @property
    def data(self) -> Any:
        """Convenience property to access instance.data directly."""
        if self.instance is None:
            raise AttributeError(f"Device '{self.name}' instance is None")
        return self.instance.data

    @property
    def framework(self) -> Any:
        """Convenience property to access instance.framework directly."""
        if self.instance is None:
            raise AttributeError(f"Device '{self.name}' instance is None")
        return self.instance.framework

    @property
    def run(self) -> Any:
        """Convenience property to access instance.run directly."""
        if self.instance is None:
            raise AttributeError(f"Device '{self.name}' instance is None")
        return self.instance.run

    @property
    def obsSite(self) -> Any:
        """Convenience property to access instance.obsSite directly (mount-specific)."""
        if self.instance is None:
            raise AttributeError(f"Device '{self.name}' instance is None")
        return self.instance.obsSite

    @property
    def setting(self) -> Any:
        """Convenience property to access instance.setting directly (mount-specific)."""
        if self.instance is None:
            raise AttributeError(f"Device '{self.name}' instance is None")
        return self.instance.setting

    @property
    def location(self) -> Any:
        """Convenience property to access instance.obsSite.location directly
        (mount-specific)."""
        if self.instance is None:
            raise AttributeError(f"Device '{self.name}' instance is None")
        return self.instance.obsSite.location

    @property
    def timeJD(self) -> Any:
        """Convenience property to access instance.obsSite.timeJD directly
        (mount-specific)."""
        if self.instance is None:
            raise AttributeError(f"Device '{self.name}' instance is None")
        return self.instance.obsSite.timeJD


class DeviceRegistry:
    """Central registry of all device driver instances.

    Uses :class:`DeviceEntry` for storing metadata about each device driver.
    Access drivers via attribute notation (``entry.instance``, ``entry.stat``)
    and the iterator helpers provided here.
    """

    def __init__(self, app: Any) -> None:
        # =====================================================================
        # PHASE 1: Create mount device (or use test mock if injected)
        # Production: app.mount does not exist yet → create MountDevice
        # Testing: test may have set app.mount = MockMount() → use it
        # =====================================================================
        if hasattr(app, "mount") and app.mount is not None:
            # Test only: tests inject mock mounts before calling registry
            mount_instance = app.mount
        else:
            # Production (normal case): create real mount device
            mount_instance = MountDevice(app, verbose=True)
            app.mount = mount_instance

        # =====================================================================
        # PHASE 2: Create all other devices (can now safely access app.mount)
        # =====================================================================
        self.drivers: dict[str, DeviceEntry] = {
            "mount": DeviceEntry(
                name="mount",
                instance=mount_instance,
                deviceType=None,
                isConfigurable=False,
            ),

        }

    # =====================================================================
    # PHASE 3: Create all other devices (can now safely access app.mount)
    # =====================================================================

    def addDevices(self, app: Any) -> None:
        self.drivers["camera"] = DeviceEntry(
                name="camera",
                instance=Camera(app),  # Can access app.mount
                deviceType="camera",
                isConfigurable=True,
            )
        self.drivers["cover"] = DeviceEntry(
                name="cover",
                instance=Cover(app),
                deviceType="covercalibrator",
                isConfigurable=True,
            )
        self.drivers["directWeather"] = DeviceEntry(
                name="directWeather",
                instance=DirectWeather(app),
                deviceType=None,
                isConfigurable=True,
            )
        self.drivers["dome"] = DeviceEntry(
                name="dome",
                instance=Dome(app),
                deviceType="dome",
                isConfigurable=True,
            )
        self.drivers["filter"] = DeviceEntry(
                name="filter",
                instance=Filter(app),
                deviceType="filterwheel",
                isConfigurable=True,
            )
        self.drivers["focuser"] = DeviceEntry(
                name="focuser",
                instance=Focuser(app),
                deviceType="focuser",
                isConfigurable=True,
            )
        self.drivers["lightPanel"] = DeviceEntry(
                name="lightPanel",
                instance=LightPanel(app),
                deviceType="covercalibrator",
                isConfigurable=True,
            )
        self.drivers["measure"] = DeviceEntry(
                name="measure",
                instance=MeasureData(app),
                deviceType=None,
                isConfigurable=True,
            )
        self.drivers["plateSolve"] = DeviceEntry(
                name="plateSolve",
                instance=PlateSolve(app),
                deviceType="plateSolve",
                isConfigurable=True,
            )
        self.drivers["power"] = DeviceEntry(
                name="power",
                instance=PegasusUPB(app),
                deviceType="switch",
                isConfigurable=True,
            )
        self.drivers["relay"] = DeviceEntry(
                name="relay",
                instance=KMRelay(),
                deviceType=None,
                isConfigurable=True,
            )
        self.drivers["refraction"] = DeviceEntry(
                name="refraction",
                instance=None,
                deviceType=None,
                isConfigurable=False,
            )
        self.drivers["remote"] = DeviceEntry(
                name="remote",
                instance=Remote(app),
                deviceType=None,
                isConfigurable=True,
            )
        self.drivers["seeingWeather"] = DeviceEntry(
                name="seeingWeather",
                instance=SeeingWeather(app),  # Can access app.mount
                deviceType="observingconditions",
                isConfigurable=True,
            )
        self.drivers["sensor1Weather"] = DeviceEntry(
                name="sensor1Weather",
                instance=SensorWeather(app),
                deviceType="observingconditions",
                isConfigurable=True,
            )
        self.drivers["sensor2Weather"] = DeviceEntry(
                name="sensor2Weather",
                instance=SensorWeather(app),
                deviceType="observingconditions",
                isConfigurable=True,
            )
        self.drivers["sensor3Weather"] = DeviceEntry(
                name="sensor3Weather",
                instance=SensorWeather(app),
                deviceType="observingconditions",
                isConfigurable=True,
            )
        self.drivers["sensor4Weather"] = DeviceEntry(
                name="sensor4Weather",
                instance=SensorWeather(app),
                deviceType="observingconditions",
                isConfigurable=True,
            )
        self.drivers["telescope"] = DeviceEntry(
                name="telescope",
                instance=Telescope(app),
                deviceType="telescope",
                isConfigurable=True,
            )

    # ------------------------------------------------------------------
    # Mapping protocol — keeps ``"x" in dReg`` and ``dReg["x"]`` working
    # ------------------------------------------------------------------
    def __iter__(self) -> Iterator[str]:
        return iter(self.drivers)

    def __getitem__(self, name: str) -> DeviceEntry:
        return self.drivers[name]

    def __contains__(self, name: object) -> bool:
        return name in self.drivers

    # ------------------------------------------------------------------
    # Intent-revealing iterators
    # ------------------------------------------------------------------
    def configurable(self) -> Iterator[DeviceEntry]:
        """Yield every entry that is user-configurable.

        Excludes ``mount``, ``refraction`` and any entry whose instance is
        ``None`` — exactly the condition that was previously repeated as
        ``if driver in ["mount"] or ...["class"] is None: continue``.
        """
        for entry in self.drivers.values():
            if entry.isConfigurable and entry.instance is not None:
                yield entry

    # ------------------------------------------------------------------
    # Stat helper
    # ------------------------------------------------------------------
    def setStat(self, name: str, value: bool | None) -> None:
        """Set the connection status for the named driver."""
        self.drivers[name].stat = value
