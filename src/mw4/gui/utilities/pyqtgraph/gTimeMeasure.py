# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import pyqtgraph as pg
from datetime import UTC
from datetime import datetime as dt
from typing import Any


class TimeMeasure(pg.AxisItem):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def tickStrings(self, values: list[float], scale: float, spacing: float) -> list[str]:
        ticks = []
        for x in values:
            if x < 0:
                continue
            lStr = dt.fromtimestamp(x, tz=UTC).strftime("%H:%M:%S")
            ticks.append(lStr)
        return ticks
