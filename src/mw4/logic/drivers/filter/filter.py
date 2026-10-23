# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from mw4.base import platformInfo
from mw4.base.appProtocol import HasThreadPool
from mw4.logic.drivers.filter.filterAlpaca import FilterAlpaca
from mw4.logic.drivers.filter.filterIndi import FilterIndi
from mw4.logic.drivers.frameworks.deviceFacade import DeviceFacade
from mw4.logic.drivers.frameworks.driverProtocols import FilterDriver

if platformInfo.IS_WINDOWS:
    from mw4.logic.drivers.filter.filterAscom import FilterAscom


class Filter(DeviceFacade[HasThreadPool, FilterDriver]):
    DEVICE_TYPE = "filterwheel"

    def __init__(self, app: HasThreadPool) -> None:
        super().__init__(app)
        self.buildBackends(
            {
                "indi": FilterIndi,
                "alpaca": FilterAlpaca,
            },
            {
                "ascom": lambda: FilterAscom(self),
            },
        )

    def sendFilterNumber(self, filterNumber: int = 1) -> None:
        if self.framework not in self.run:
            return
        self.run[self.framework].sendFilterNumber(filterNumber=filterNumber)
