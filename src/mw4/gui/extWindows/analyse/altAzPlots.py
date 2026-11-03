# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import numpy as np
from mw4.gui.extWindows.analyse.plotHelpers import linkViews
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from mw4.gui.extWindows.analyse.analyseW import AnalyseWindow


class AltAzPlots:
    def __init__(self, parentWindow: "AnalyseWindow") -> None:
        self.ui = parentWindow.ui
        self.app = parentWindow.app
        self.data = parentWindow.analyseData
        self.plots = [
            self.ui.raRawErrors,
            self.ui.decRawErrors,
            self.ui.raErrors,
            self.ui.decErrors,
        ]

    def drawTab(self) -> None:
        for plot, errors in zip(
            self.plots,
            (self.data.errorRA_S, self.data.errorDEC_S, self.data.errorRA, self.data.errorDEC),
            strict=True,
        ):
            self.drawAltAzErrorChart(plot, errors)
        self.drawHorizon()
        linkViews(self.plots, self.ui.linkViews.isChecked(), linkY=True)

    def colorChange(self) -> None:
        for plot in self.plots:
            plot.colorChange()

    def drawAltAzErrorChart(self, plot: Any, errors: np.ndarray) -> None:
        isoLevels = 20 if self.ui.showISO.isChecked() else 0
        plot.p[0].setLabel("bottom", "Azimuth [deg]")
        plot.p[0].setLabel("left", "Altitude [deg]")
        ticks = [(x, f"{x}") for x in range(30, 360, 30)]
        plot.p[0].getAxis("bottom").setTicks([ticks])
        plot.p[0].getAxis("top").setTicks([ticks])
        plot.plot(
            self.data.azimuth,
            self.data.altitude,
            z=errors,
            data=errors,
            range={"xMin": 0, "yMin": 0, "xMax": 360, "yMax": 90},
            tip="Az: {x:0.0f}\nAlt: {y:0.1f}\nError: {data:0.1f}".format,
            isoLevels=isoLevels,
        )

    def drawHorizon(self) -> None:
        if not self.ui.showHorizon.isChecked():
            return
        for plot in self.plots:
            plot.drawHorizon(self.app.buildPoint.horizonP)
