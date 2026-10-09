# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from mw4.gui.mainWaddon.tabAddon import TabAddon
from typing import Any


class SatData(TabAddon):
    satellites: Any = None
