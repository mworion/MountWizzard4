# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from mw4.base import platformInfo
from mw4.base.appProtocol import HasThreadPool
from mw4.logic.drivers.focuser.focuserAlpaca import FocuserAlpaca
from mw4.logic.drivers.focuser.focuserIndi import FocuserIndi
from mw4.logic.drivers.frameworks.deviceFacade import DeviceFacade
from mw4.logic.drivers.frameworks.driverProtocols import FocuserDriver

if platformInfo.IS_WINDOWS:
    from mw4.logic.drivers.focuser.focuserAscom import FocuserAscom


class Focuser(DeviceFacade[HasThreadPool, FocuserDriver]):
    DEVICE_TYPE = "focuser"

    def __init__(self, app: HasThreadPool) -> None:
        super().__init__(app)
        self.buildBackends(
            {
                "indi": FocuserIndi,
                "alpaca": FocuserAlpaca,
            },
            {
                "ascom": lambda: FocuserAscom(self),
            },
        )

    def move(self, position: int) -> None:
        self.run[self.framework].move(position=position)

    def halt(self) -> None:
        self.run[self.framework].halt()
