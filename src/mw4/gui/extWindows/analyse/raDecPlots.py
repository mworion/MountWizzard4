# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import numpy as np
from mw4.gui.extWindows.analyse.plotHelpers import linkViews, pierColors
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from mw4.gui.extWindows.analyse.analyseW import AnalyseWindow


class RaDecPlots:
    def __init__(self, parentWindow: "AnalyseWindow") -> None:
        self.parentWindow = parentWindow
        self.ui = parentWindow.ui
        self.data = parentWindow.analyseData
        self.plots = [
            self.ui.raRawErrorsRef,
            self.ui.decRawErrorsRef,
            self.ui.raErrorsRef,
            self.ui.decErrorsRef,
        ]

    def drawTab(self) -> None:
        self.drawRaRef(self.ui.raRawErrorsRef, self.data.errorRA_S)
        self.drawDecRef(self.ui.decRawErrorsRef, self.data.errorDEC_S)
        self.drawRaRef(self.ui.raErrorsRef, self.data.errorRA)
        self.drawDecRef(self.ui.decErrorsRef, self.data.errorDEC)
        isLinked = self.ui.linkViews.isChecked()
        linkViews([self.ui.raRawErrorsRef, self.ui.raErrorsRef], isLinked, linkY=False)
        linkViews([self.ui.decRawErrorsRef, self.ui.decErrorsRef], isLinked, linkY=False)

    def colorChange(self) -> None:
        for plot in self.plots:
            plot.colorChange()

    def drawRefChart(
        self,
        plot: Any,
        axis: str,
        tickRange: range,
        x: Any,
        y: Any,
        xRange: dict[str, int],
        tip: str,
    ) -> None:
        plot.p[0].setLabel("bottom", f"{axis} Encoder Abs [deg]")
        plot.p[0].setLabel("left", "Error per Star [arcsec]")
        ticks = [(t, f"{t}") for t in tickRange]
        plot.p[0].getAxis("bottom").setTicks([ticks])
        plot.p[0].getAxis("top").setTicks([ticks])
        plot.plot(
            x,
            y,
            color=pierColors(self.data.pierside, self.parentWindow),
            range=xRange,
            data=self.data.pierside,
            tip=tip.format,
        )

    def drawRaRef(self, plot: Any, errors: np.ndarray) -> None:
        self.drawRefChart(
            plot,
            "RA",
            range(30, 180, 30),
            self.data.angularPosRA,
            errors,
            {"xMin": 0, "xMax": 180},
            "AngularRA: {x:0.1f}\nErrorRA: {y:0.1f}\nPier: {data}",
        )

    def drawDecRef(self, plot: Any, errors: np.ndarray) -> None:
        # Lists come from a model file on disk; keep the tolerant truncation.
        y = [x if p == "W" else -x for x, p in zip(errors, self.data.pierside, strict=False)]
        self.drawRefChart(
            plot,
            "DEC",
            range(-80, 90, 20),
            self.data.angularPosDEC,
            y,
            {"xMin": -90, "xMax": 90},
            "AngularDEC: {x:0.1f}\nErrorDec: {y:0.1f}\nPier: {data}",
        )
