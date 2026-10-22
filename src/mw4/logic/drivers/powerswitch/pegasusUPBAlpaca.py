# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from mw4.logic.drivers.frameworks.alpacaClass import AlpacaClass
from mw4.logic.drivers.powerswitch.pegasusUPBAlpacaAscomBase import PegasusUPBAlpacaAscomBase


class PegasusUPBAlpaca(PegasusUPBAlpacaAscomBase, AlpacaClass):
    pass
