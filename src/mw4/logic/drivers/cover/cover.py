# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from mw4.base import platformInfo
from mw4.base.appProtocol import HasThreadPool
from mw4.logic.drivers.cover.coverAlpaca import CoverAlpaca
from mw4.logic.drivers.cover.coverIndi import CoverIndi
from mw4.logic.drivers.frameworks.deviceFacade import DeviceFacade

if platformInfo.IS_WINDOWS:
    from mw4.logic.drivers.cover.coverAscom import CoverAscom


class Cover(DeviceFacade):
    DEVICE_TYPE = "covercalibrator"

    def __init__(self, app: HasThreadPool) -> None:
        super().__init__(app)
        self.buildBackends(
            {
                "indi": CoverIndi,
                "alpaca": CoverAlpaca,
            },
            {
                "ascom": lambda: CoverAscom(self),
            },
        )

    def closeCover(self) -> None:
        self.run[self.framework].closeCover()

    def openCover(self) -> None:
        self.run[self.framework].openCover()

    def haltCover(self) -> None:
        self.run[self.framework].haltCover()
