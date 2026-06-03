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
from typing import Any


@dataclass
class DeviceEntry:
    """Holds all metadata for one registered device driver.

    Backwards-compatible dict-style access is provided so that existing call
    sites using ``entry["class"]``, ``entry["stat"]`` and
    ``entry["deviceType"]`` continue to work unchanged during migration.
    """

    name: str
    instance: Any | None
    deviceType: str | None
    isConfigurable: bool
    stat: bool | None = field(default=None)

    # ------------------------------------------------------------------
    # Legacy dict-style access (keeps old call sites working)
    # ------------------------------------------------------------------
    def __getitem__(self, key: str) -> Any:
        match key:
            case "class":
                return self.instance
            case "deviceType":
                return self.deviceType
            case "stat":
                return self.stat
            case _:
                raise KeyError(key)

    def __setitem__(self, key: str, value: Any) -> None:
        match key:
            case "class":
                self.instance = value
            case "deviceType":
                self.deviceType = value
            case "stat":
                self.stat = value
            case _:
                raise KeyError(key)

    def __contains__(self, key: object) -> bool:
        return key in ("class", "deviceType", "stat")

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self[key]
        except KeyError:
            return default


class DeviceRegistry:
    """Central registry of all device driver instances.

    ``drivers`` is the primary mapping from driver name to
    :class:`DeviceEntry`.  Because ``DeviceEntry`` supports dict-style
    item access (``entry["class"]``, ``entry["stat"]`` etc.) all legacy
    call sites continue to work without change.

    New call sites should prefer attribute access on ``DeviceEntry``
    (``entry.instance``, ``entry.stat``) and the iterator helpers
    provided here.
    """

    def __init__(self, app: Any) -> None:
        self.drivers: dict[str, DeviceEntry] = {
            "camera": DeviceEntry(
                name="camera",
                instance=Camera(app),
                deviceType="camera",
                isConfigurable=True,
            ),
            "cover": DeviceEntry(
                name="cover",
                instance=Cover(app),
                deviceType="covercalibrator",
                isConfigurable=True,
            ),
            "directWeather": DeviceEntry(
                name="directWeather",
                instance=DirectWeather(app),
                deviceType=None,
                isConfigurable=True,
            ),
            "dome": DeviceEntry(
                name="dome",
                instance=Dome(app),
                deviceType="dome",
                isConfigurable=True,
            ),
            "filter": DeviceEntry(
                name="filter",
                instance=Filter(app),
                deviceType="filterwheel",
                isConfigurable=True,
            ),
            "focuser": DeviceEntry(
                name="focuser",
                instance=Focuser(app),
                deviceType="focuser",
                isConfigurable=True,
            ),
            "lightPanel": DeviceEntry(
                name="lightPanel",
                instance=LightPanel(app),
                deviceType="covercalibrator",
                isConfigurable=True,
            ),
            "measure": DeviceEntry(
                name="measure",
                instance=MeasureData(app),
                deviceType=None,
                isConfigurable=True,
            ),
            "mount": DeviceEntry(
                name="mount",
                instance=app.mount,
                deviceType=None,
                isConfigurable=False,
            ),
            "plateSolve": DeviceEntry(
                name="plateSolve",
                instance=PlateSolve(app),
                deviceType="plateSolve",
                isConfigurable=True,
            ),
            "power": DeviceEntry(
                name="power",
                instance=PegasusUPB(app),
                deviceType="switch",
                isConfigurable=True,
            ),
            "relay": DeviceEntry(
                name="relay",
                instance=KMRelay(),
                deviceType=None,
                isConfigurable=True,
            ),
            "refraction": DeviceEntry(
                name="refraction",
                instance=None,
                deviceType=None,
                isConfigurable=False,
            ),
            "remote": DeviceEntry(
                name="remote",
                instance=Remote(app),
                deviceType=None,
                isConfigurable=True,
            ),
            "seeingWeather": DeviceEntry(
                name="seeingWeather",
                instance=SeeingWeather(app),
                deviceType="observingconditions",
                isConfigurable=True,
            ),
            "sensor1Weather": DeviceEntry(
                name="sensor1Weather",
                instance=SensorWeather(app),
                deviceType="observingconditions",
                isConfigurable=True,
            ),
            "sensor2Weather": DeviceEntry(
                name="sensor2Weather",
                instance=SensorWeather(app),
                deviceType="observingconditions",
                isConfigurable=True,
            ),
            "sensor3Weather": DeviceEntry(
                name="sensor3Weather",
                instance=SensorWeather(app),
                deviceType="observingconditions",
                isConfigurable=True,
            ),
            "sensor4Weather": DeviceEntry(
                name="sensor4Weather",
                instance=SensorWeather(app),
                deviceType="observingconditions",
                isConfigurable=True,
            ),
            "telescope": DeviceEntry(
                name="telescope",
                instance=Telescope(app),
                deviceType="telescope",
                isConfigurable=True,
            ),
        }

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
