# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from mw4.base.ascomClass import AscomClass
from mw4.logic.focuser.focuserAlpacaAscomBase import FocuserAlpacaAscomBase


class FocuserAscom(FocuserAlpacaAscomBase, AscomClass):
    pass
