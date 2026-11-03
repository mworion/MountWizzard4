# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from mw4.gui.extWindows.analyse.plotHelpers import pierColors
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mw4.gui.extWindows.analyse.analyseW import AnalyseWindow


class GeneralPlots:
    def __init__(self, parentWindow: "AnalyseWindow") -> None:
        self.parentWindow = parentWindow
        self.ui = parentWindow.ui
        self.data = parentWindow.analyseData
        self.plots = [
            self.ui.scaleImage,
            self.ui.modelPositions,
            self.ui.errorAscending,
            self.ui.errorDistribution,
        ]

    def drawTab(self) -> None:
        self.drawScaleImage()
        self.drawModelPositions()
        self.drawErrorAscending()
        self.drawErrorDistribution()

    def colorChange(self) -> None:
        for plot in self.plots:
            plot.colorChange()

    def drawScaleImage(self) -> None:
        self.ui.scaleImage.p[0].setLabel("bottom", "Star Number")
        self.ui.scaleImage.p[0].setLabel("left", "Image Scale [arcsec/pix]")
        self.ui.scaleImage.plot(
            self.data.errorIndex,
            self.data.scaleS,
            color=pierColors(self.data.pierside, self.parentWindow),
            data=self.data.pierside,
            tip="PointNo: {x:0.0f}\nScale: {y:0.1f}\nPier: {data}".format,
        )

    def drawErrorAscending(self) -> None:
        self.ui.errorAscending.p[0].setLabel("bottom", "Star count")
        self.ui.errorAscending.p[0].setLabel("left", "Error per Star [arcsec]")
        # Lists come from a model file on disk; keep the tolerant truncation.
        points = sorted(
            zip(self.data.errorRMS, self.data.errorIndex, self.data.pierside, strict=False),
            key=lambda point: point[0],
        )
        y = [point[0] for point in points]
        x = [point[1] for point in points]
        pierside = [point[2] for point in points]
        self.ui.errorAscending.plot(
            x,
            y,
            color=pierColors(pierside, self.parentWindow),
            data=pierside,
            tip="ErrorRMS: {y:0.1f}\nPier: {data}".format,
        )

    def drawModelPositions(self) -> None:
        self.ui.modelPositions.barItem.setLabel("right", "Error [RMS]")
        self.ui.modelPositions.plot(
            self.data.azimuth,
            self.data.altitude,
            z=self.data.errorRMS,
            ang=self.data.errorAngle,
            range={"xMin": -91, "yMin": -91, "xMax": 91, "yMax": 91},
            bar=True,
            data=self.data.errorRMS,
            reverse=True,
            tip="ErrorRMS: {data:0.1f}".format,
        )
        self.ui.modelPositions.plotLoc(self.data.latitude)

    def drawErrorDistribution(self) -> None:
        self.ui.errorDistribution.plot(
            self.data.errorAngle,
            self.data.errorRMS,
            color=pierColors(self.data.pierside, self.parentWindow),
            data=self.data.pierside,
            tip="ErrorRMS: {y:0.1f}\nPier: {data}".format,
        )
