# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from mw4.base import platformInfo
from mw4.base.appProtocol import HasThreadPool
from mw4.base.driverProtocol import FrameworkDriver
from mw4.logic.drivers.environment.sensorWeatherAlpaca import SensorWeatherAlpaca
from mw4.logic.drivers.environment.sensorWeatherBoltwood import SensorWeatherBoltwood
from mw4.logic.drivers.environment.sensorWeatherIndi import SensorWeatherIndi
from mw4.logic.drivers.environment.sensorWeatherOnline import SensorWeatherOnline
from mw4.logic.drivers.frameworks.deviceFacade import DeviceFacade

if platformInfo.IS_WINDOWS:
    from mw4.logic.drivers.environment.sensorWeatherAscom import SensorWeatherAscom


class SensorWeather(DeviceFacade[HasThreadPool, FrameworkDriver]):
    DEVICE_TYPE = "observingconditions"

    def __init__(self, app: HasThreadPool) -> None:
        super().__init__(app)
        self.buildBackends(
            {
                "indi": SensorWeatherIndi,
                "alpaca": SensorWeatherAlpaca,
                "boltwood": SensorWeatherBoltwood,
                "online": SensorWeatherOnline,
            },
            {
                "ascom": lambda: SensorWeatherAscom(self),
            },
        )
