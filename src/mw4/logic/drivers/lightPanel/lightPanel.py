# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from mw4.base import platformInfo
from mw4.base.appProtocol import AppProtocol
from mw4.logic.drivers.frameworks.deviceFacade import DeviceFacade
from mw4.logic.drivers.lightPanel.lightPanelAlpaca import LightPanelAlpaca
from mw4.logic.drivers.lightPanel.lightPanelIndi import LightPanelIndi

if platformInfo.IS_WINDOWS:
    from mw4.logic.drivers.lightPanel.lightPanelAscom import LightPanelAscom


class LightPanel(DeviceFacade):
    DEVICE_TYPE = "covercalibrator"

    def __init__(self, app: AppProtocol) -> None:
        super().__init__(app)
        self.buildBackends(
            {
                "indi": LightPanelIndi,
                "alpaca": LightPanelAlpaca,
            },
            {
                "ascom": lambda: LightPanelAscom(self),
            },
        )

    def lightOn(self) -> None:
        self.run[self.framework].lightOn()

    def lightOff(self) -> None:
        self.run[self.framework].lightOff()

    def lightIntensity(self, value: float) -> None:
        self.run[self.framework].lightIntensity(value)
