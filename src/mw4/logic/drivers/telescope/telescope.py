# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from mw4.base import platformInfo
from mw4.base.appProtocol import HasThreadPool
from mw4.base.driverProtocol import FrameworkDriver
from mw4.logic.drivers.frameworks.deviceFacade import DeviceFacade
from mw4.logic.drivers.telescope.telescopeAlpaca import TelescopeAlpaca
from mw4.logic.drivers.telescope.telescopeIndi import TelescopeIndi

if platformInfo.IS_WINDOWS:
    from mw4.logic.drivers.telescope.telescopeAscom import TelescopeAscom


class Telescope(DeviceFacade[HasThreadPool, FrameworkDriver]):
    DEVICE_TYPE = "telescope"

    def __init__(self, app: HasThreadPool) -> None:
        super().__init__(app)
        self.buildBackends(
            {
                "indi": TelescopeIndi,
                "alpaca": TelescopeAlpaca,
            },
            {
                "ascom": lambda: TelescopeAscom(self),
            },
        )
