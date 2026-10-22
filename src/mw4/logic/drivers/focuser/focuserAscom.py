# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from mw4.logic.drivers.focuser.focuserAlpacaAscomBase import FocuserAlpacaAscomBase
from mw4.logic.drivers.frameworks.ascomClass import AscomClass


class FocuserAscom(FocuserAlpacaAscomBase, AscomClass):
    pass
