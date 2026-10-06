# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from mw4.gui.utilities.pyqtgraph.gCustomViewBox import CustomViewBox
from mw4.gui.utilities.pyqtgraph.gPlotBase import PlotBase
from typing import Any


class Hemisphere(PlotBase):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.p.append(self.addPlot(viewBox=CustomViewBox()))
        self.setupItems()
        self.p[1].getViewBox().setAspectLocked(True)
        self.p[1].setVisible(False)
