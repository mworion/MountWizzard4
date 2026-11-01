# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import numpy as np
from typing import Any


class AnalysePlotsMixin:
    def pierColors(self, pierside: list[str]) -> list[str]:
        return [self.M_GREEN if p == "W" else self.M_YELLOW for p in pierside]

    def drawAltAzErrorChart(self, plot: Any, errors: np.ndarray) -> None:
        hasISO = self.ui.showISO.isChecked()
        isoLevels = 20 if hasISO else 0
        plot.p[0].setLabel("bottom", "Azimuth [deg]")
        plot.p[0].setLabel("left", "Altitude [deg]")
        ticks = [(x, f"{x}") for x in range(30, 360, 30)]
        plot.p[0].getAxis("bottom").setTicks([ticks])
        plot.p[0].getAxis("top").setTicks([ticks])
        plot.plot(
            self.azimuth,
            self.altitude,
            z=errors,
            data=errors,
            range={"xMin": 0, "yMin": 0, "xMax": 360, "yMax": 90},
            tip="Az: {x:0.0f}\nAlt: {y:0.1f}\nError: {data:0.1f}".format,
            isoLevels=isoLevels,
        )

    def drawRaRawErrors(self) -> None:
        self.drawAltAzErrorChart(self.ui.raRawErrors, self.errorRA_S)

    def drawDecRawErrors(self) -> None:
        self.drawAltAzErrorChart(self.ui.decRawErrors, self.errorDEC_S)

    def drawRaErrors(self) -> None:
        self.drawAltAzErrorChart(self.ui.raErrors, self.errorRA)

    def drawDecError(self) -> None:
        self.drawAltAzErrorChart(self.ui.decErrors, self.errorDEC)

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
            color=self.pierColors(self.pierside),
            range=xRange,
            data=self.pierside,
            tip=tip.format,
        )

    def drawRaRef(self, plot: Any, errors: np.ndarray) -> None:
        self.drawRefChart(
            plot,
            "RA",
            range(30, 180, 30),
            self.angularPosRA,
            errors,
            {"xMin": 0, "xMax": 180},
            "AngularRA: {x:0.1f}\nErrorRA: {y:0.1f}\nPier: {data}",
        )

    def drawDecRef(self, plot: Any, errors: np.ndarray) -> None:
        # lists come from a model file on disk; keep the tolerant truncation
        y = [x if p == "W" else -x for x, p in zip(errors, self.pierside, strict=False)]
        self.drawRefChart(
            plot,
            "DEC",
            range(-80, 90, 20),
            self.angularPosDEC,
            y,
            {"xMin": -90, "xMax": 90},
            "AngularDEC: {x:0.1f}\nErrorDec: {y:0.1f}\nPier: {data}",
        )

    def drawRaRawErrorsRef(self) -> None:
        self.drawRaRef(self.ui.raRawErrorsRef, self.errorRA_S)

    def drawDecRawErrorsRef(self) -> None:
        self.drawDecRef(self.ui.decRawErrorsRef, self.errorDEC_S)

    def drawRaErrorsRef(self) -> None:
        self.drawRaRef(self.ui.raErrorsRef, self.errorRA)

    def drawDecErrorsRef(self) -> None:
        self.drawDecRef(self.ui.decErrorsRef, self.errorDEC)

    def drawScaleImage(self) -> None:
        self.ui.scaleImage.p[0].setLabel("bottom", "Star Number")
        self.ui.scaleImage.p[0].setLabel("left", "Image Scale [arcsec/pix]")
        self.ui.scaleImage.plot(
            self.errorIndex,
            self.scaleS,
            color=self.pierColors(self.pierside),
            data=self.pierside,
            tip="PointNo: {x:0.0f}\nScale: {y:0.1f}\nPier: {data}".format,
        )

    def drawErrorAscending(self) -> None:
        self.ui.errorAscending.p[0].setLabel("bottom", "Star count")
        self.ui.errorAscending.p[0].setLabel("left", "Error per Star [arcsec]")
        # lists come from a model file on disk; keep the tolerant truncation
        points = sorted(
            zip(self.errorRMS, self.errorIndex, self.pierside, strict=False),
            key=lambda point: point[0],
        )
        y = [point[0] for point in points]
        x = [point[1] for point in points]
        pierside = [point[2] for point in points]
        self.ui.errorAscending.plot(
            x,
            y,
            color=self.pierColors(pierside),
            data=pierside,
            tip="ErrorRMS: {y:0.1f}\nPier: {data}".format,
        )

    def drawModelPositions(self) -> None:
        self.ui.modelPositions.barItem.setLabel("right", "Error [RMS]")
        self.ui.modelPositions.plot(
            self.azimuth,
            self.altitude,
            z=self.errorRMS,
            ang=self.errorAngle,
            range={"xMin": -91, "yMin": -91, "xMax": 91, "yMax": 91},
            bar=True,
            data=self.errorRMS,
            reverse=True,
            tip="ErrorRMS: {data:0.1f}".format,
        )
        self.ui.modelPositions.plotLoc(self.latitude)

    def drawErrorDistribution(self) -> None:
        self.ui.errorDistribution.plot(
            self.errorAngle,
            self.errorRMS,
            color=self.pierColors(self.pierside),
            data=self.pierside,
            tip="ErrorRMS: {y:0.1f}\nPier: {data}".format,
        )

    def drawHorizon(self) -> None:
        if not self.ui.showHorizon.isChecked():
            return

        for plot in [
            self.ui.raErrors,
            self.ui.decErrors,
            self.ui.raRawErrors,
            self.ui.decRawErrors,
        ]:
            plot.drawHorizon(self.app.buildPoint.horizonP)

    def linkViews(self, plots: list[Any], linkY: bool) -> None:
        isLinked = self.ui.linkViews.isChecked()
        views = [plot.p[0].getViewBox() for plot in plots]
        for sourceView in views:
            for targetView in views:
                if sourceView == targetView:
                    continue
                if isLinked:
                    sourceView.setXLink(targetView)
                    if linkY:
                        sourceView.setYLink(targetView)
                else:
                    sourceView.setXLink(None)
                    if linkY:
                        sourceView.setYLink(None)
            sourceView.rightMouseRange()

    def linkViewsAltAz(self) -> None:
        plots = [
            self.ui.raRawErrors,
            self.ui.raErrors,
            self.ui.decRawErrors,
            self.ui.decErrors,
        ]
        self.linkViews(plots, linkY=True)

    def linkViewsRa(self) -> None:
        self.linkViews([self.ui.raRawErrorsRef, self.ui.raErrorsRef], linkY=False)

    def linkViewsDec(self) -> None:
        self.linkViews([self.ui.decRawErrorsRef, self.ui.decErrorsRef], linkY=False)
