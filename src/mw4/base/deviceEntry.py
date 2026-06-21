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
from dataclasses import dataclass, field
from typing import Any


@dataclass
class DeviceEntry:
    name: str
    instance: Any | None
    deviceType: str | None
    isConfigurable: bool
    stat: bool | None = field(default=None)

    @property
    def signals(self) -> Any:
        if self.instance is None:
            raise AttributeError(f"Device '{self.name}' instance is None")
        return self.instance.signals

    @property
    def data(self) -> Any:
        if self.instance is None:
            raise AttributeError(f"Device '{self.name}' instance is None")
        return self.instance.data

    @property
    def run(self) -> Any:
        if self.instance is None:
            raise AttributeError(f"Device '{self.name}' instance is None")
        return self.instance.run

    @property
    def framework(self) -> Any:
        if self.instance is None:
            raise AttributeError(f"Device '{self.name}' instance is None")
        return self.instance.framework

    @property
    def obsSite(self) -> Any:
        if self.instance is None:
            raise AttributeError(f"Device '{self.name}' instance is None")
        return self.instance.obsSite

    @property
    def setting(self) -> Any:
        if self.instance is None:
            raise AttributeError(f"Device '{self.name}' instance is None")
        return self.instance.setting

    @property
    def location(self) -> Any:
        if self.instance is None:
            raise AttributeError(f"Device '{self.name}' instance is None")
        return self.instance.obsSite.location

    @property
    def timeJD(self) -> Any:
        if self.instance is None:
            raise AttributeError(f"Device '{self.name}' instance is None")
        return self.instance.obsSite.timeJD

    @property
    def model(self) -> Any:
        if self.instance is None:
            raise AttributeError(f"Device '{self.name}' instance is None")
        return self.instance.model

    @property
    def geometry(self) -> Any:
        if self.instance is None:
            raise AttributeError(f"Device '{self.name}' instance is None")
        return self.instance.geometry

    @property
    def firmware(self) -> Any:
        if self.instance is None:
            raise AttributeError(f"Device '{self.name}' instance is None")
        return self.instance.firmware

    @property
    def satellite(self) -> Any:
        if self.instance is None:
            raise AttributeError(f"Device '{self.name}' instance is None")
        return self.instance.satellite
