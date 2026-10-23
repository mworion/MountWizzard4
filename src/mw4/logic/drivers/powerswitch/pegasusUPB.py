# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from mw4.base.appProtocol import HasThreadPool
from mw4.logic.drivers.frameworks.deviceFacade import DeviceFacade
from mw4.logic.drivers.frameworks.driverProtocols import PowerSwitchDriver
from mw4.logic.drivers.powerswitch.pegasusUPBAlpaca import PegasusUPBAlpaca
from mw4.logic.drivers.powerswitch.pegasusUPBAscom import PegasusUPBAscom
from mw4.logic.drivers.powerswitch.pegasusUPBIndi import PegasusUPBIndi


class PegasusUPB(DeviceFacade[HasThreadPool, PowerSwitchDriver]):
    DEVICE_TYPE = "switch"

    def __init__(self, app: HasThreadPool) -> None:
        super().__init__(app)
        self.buildBackends(
            {
                "indi": PegasusUPBIndi,
                "alpaca": PegasusUPBAlpaca,
            },
            {
                "ascom": lambda: PegasusUPBAscom(self),
            },
        )

    def togglePowerPort(self, port: str) -> None:
        self.run[self.framework].togglePowerPort(port=port)

    def toggleHubUSB(self) -> None:
        self.run[self.framework].toggleHubUSB()

    def togglePortUSB(self, port: str) -> None:
        self.run[self.framework].togglePortUSB(port=port)

    def sendDew(self, port: str, value: float) -> None:
        self.run[self.framework].sendDew(port=port, value=value)

    def sendAdjustableOutput(self, value: float) -> None:
        self.run[self.framework].sendAdjustableOutput(value=value)

    def reboot(self) -> None:
        self.run[self.framework].reboot()
