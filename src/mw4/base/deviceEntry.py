# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from dataclasses import dataclass, field
from typing import Any


@dataclass
class DeviceEntry[T]:
    name: str
    instance: T
    deviceType: str | None
    isConfigurable: bool
    stat: bool | None = field(default=None)

    def requireInstance(self) -> Any:
        if self.instance is None:
            raise AttributeError(f"Device '{self.name}' instance is None")
        return self.instance

    @property
    def signals(self) -> Any:
        return self.requireInstance().signals

    @property
    def data(self) -> Any:
        return self.requireInstance().data

    @property
    def run(self) -> Any:
        return self.requireInstance().run

    @property
    def framework(self) -> Any:
        return self.requireInstance().framework

    @property
    def obsSite(self) -> Any:
        return self.requireInstance().obsSite

    @property
    def setting(self) -> Any:
        return self.requireInstance().setting

    @property
    def location(self) -> Any:
        return self.requireInstance().obsSite.location

    @property
    def timeJD(self) -> Any:
        return self.requireInstance().obsSite.timeJD

    @property
    def model(self) -> Any:
        return self.requireInstance().model

    @property
    def geometry(self) -> Any:
        return self.requireInstance().geometry

    @property
    def firmware(self) -> Any:
        return self.requireInstance().firmware

    @property
    def satellite(self) -> Any:
        return self.requireInstance().satellite

    @property
    def config(self) -> Any:
        instance = self.requireInstance()
        if not instance.framework:
            raise AttributeError(f"Device '{self.name}' instance.framework is None")
        return instance.run[instance.framework].config
