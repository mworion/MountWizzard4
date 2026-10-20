# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from mw4.gui.styles.styles import Styles
from typing import Any

PlotDef = dict[str, Any]


def lineItem(name: str, pen: str) -> PlotDef:
    return {"plotItemRef": None, "name": name, "pen": pen}


def chart(
    label: str,
    lineItems: dict[str, PlotDef],
    valueRange: tuple[float, float, bool] | None = None,
) -> PlotDef:
    template: PlotDef = {"legendRef": None, "label": label}
    if valueRange is not None:
        template["range"] = valueRange
    return {"template": template, "lineItems": lineItems}


def weatherItems(parameter: str, styles: Styles, withDirect: bool = True) -> dict[str, PlotDef]:
    """Line items of the four sensor weather devices and optionally the direct one."""
    sensorPens = (styles.M_GREEN, styles.M_RED, styles.M_PINK, styles.M_YELLOW)
    items = {
        f"sensor{i}Weather-{parameter}": lineItem(f"Sensor {i}", pen)
        for i, pen in enumerate(sensorPens, start=1)
    }
    if withDirect:
        items[f"directWeather-{parameter}"] = lineItem("Direct", styles.M_PRIM)
    return items


def dataPlots() -> dict[str, PlotDef]:
    styles = Styles()
    weather = "WEATHER_PARAMETERS.WEATHER_"
    return {
        "No chart": {},
        "Axis Stability": chart(
            "Delta angle [arcsec]",
            {
                "mount-deltaRaJNow": lineItem("RA", styles.M_GREEN),
                "mount-deltaDecJNow": lineItem("DEC", styles.M_RED),
            },
        ),
        "Angular Tracking": chart(
            "Angle error [arcsec]",
            {
                "mount-errorAngularPosRA": lineItem("RA counter", styles.M_GREEN),
                "mount-errorAngularPosDEC": lineItem("DEC counter", styles.M_RED),
            },
        ),
        "Temperature": chart(
            "Temperature [°C]",
            weatherItems(f"{weather}TEMPERATURE", styles),
            (-20, 40, False),
        ),
        "Camera Temperature": chart(
            "Camera Temperature [°C]",
            {
                "camera-CCD_TEMPERATURE.CCD_TEMPERATURE_VALUE": lineItem("Camera", styles.M_PINK),
            },
            (-20, 20, False),
        ),
        "Camera Cooler Power": chart(
            "Camera Cooler Power [%]",
            {
                "camera-CCD_COOLER_POWER.CCD_COOLER_VALUE": lineItem("CoolerPower", styles.M_PINK),
            },
            (-5, 105, True),
        ),
        "Dew Temperature": chart(
            "Dew Temperature [°C]",
            weatherItems(f"{weather}DEWPOINT", styles),
            (-20, 40, False),
        ),
        "Pressure": chart(
            "Pressure [hPa]",
            weatherItems(f"{weather}PRESSURE", styles),
            (900, 1050, False),
        ),
        "Humidity": chart(
            "Humidity [%]",
            weatherItems(f"{weather}HUMIDITY", styles),
            (-5, 105, True),
        ),
        "Sky Quality": chart(
            "Sky Quality [mpas]",
            weatherItems("SKY_QUALITY.SKY_BRIGHTNESS", styles, withDirect=False),
            (10, 22.5, False),
        ),
        "Voltage": chart(
            "Supply Voltage [V]",
            {"power-powVolt": lineItem("Main Sensor", styles.M_YELLOW)},
            (8, 15, False),
        ),
        "Current": chart(
            "Current [A]",
            {
                "power-powCurr": lineItem("Sum", styles.M_CYAN1),
                "power-powCurr1": lineItem("Current 1", styles.M_GREEN),
                "power-powCurr2": lineItem("Current 2", styles.M_PINK),
                "power-powCurr3": lineItem("Current 3", styles.M_RED),
                "power-powCurr4": lineItem("Current 4", styles.M_YELLOW),
            },
            (0, 5, False),
        ),
        "Time Diff Comp-Mount": chart(
            "Time Difference [ms]",
            {"mount-timeDiff": lineItem("MountControl", styles.M_YELLOW)},
        ),
        "RTT Comp-Mount": chart(
            "Round Trip Time [ms]",
            {"mount-rtt": lineItem("MountControl", styles.M_YELLOW)},
        ),
        "Focus Position": chart(
            "Focus Position [units]",
            {
                "focuser-ABS_FOCUS_POSITION.FOCUS_ABSOLUTE_POSITION": lineItem(
                    "MountControl", styles.M_YELLOW
                ),
            },
        ),
    }
