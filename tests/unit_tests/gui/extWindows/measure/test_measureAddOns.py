# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import pytest
from mw4.gui.extWindows.measure.measureAddons import chart, dataPlots, lineItem, weatherItems
from mw4.gui.styles.styles import Styles

CHART_NAMES = [
    "No chart",
    "Axis Stability",
    "Angular Tracking",
    "Temperature",
    "Camera Temperature",
    "Camera Cooler Power",
    "Dew Temperature",
    "Pressure",
    "Humidity",
    "Sky Quality",
    "Voltage",
    "Current",
    "Time Diff Comp-Mount",
    "RTT Comp-Mount",
    "Focus Position",
]


@pytest.fixture(scope="module")
def styles(qapp):
    return Styles()


def test_lineItem():
    assert lineItem("RA", "#fff") == {"plotItemRef": None, "name": "RA", "pen": "#fff"}


def test_chart_withoutRange():
    result = chart("label", {"a": lineItem("A", "#fff")})
    assert result["template"] == {"legendRef": None, "label": "label"}
    assert list(result["lineItems"]) == ["a"]


def test_chart_withRange():
    result = chart("label", {}, (0, 1, True))
    assert result["template"]["range"] == (0, 1, True)


def test_weatherItems_withDirect(styles):
    items = weatherItems("PARAM", styles)
    assert list(items) == [
        "sensor1Weather-PARAM",
        "sensor2Weather-PARAM",
        "sensor3Weather-PARAM",
        "sensor4Weather-PARAM",
        "directWeather-PARAM",
    ]
    assert items["sensor3Weather-PARAM"]["name"] == "Sensor 3"
    assert items["sensor3Weather-PARAM"]["pen"] == styles.M_PINK
    assert items["directWeather-PARAM"] == {
        "plotItemRef": None,
        "name": "Direct",
        "pen": styles.M_PRIM,
    }


def test_weatherItems_withoutDirect(styles):
    items = weatherItems("PARAM", styles, withDirect=False)
    assert "directWeather-PARAM" not in items
    assert len(items) == 4


def test_dataPlots_chartNames(styles):
    assert list(dataPlots()) == CHART_NAMES


def test_dataPlots_noChartIsEmpty(styles):
    assert dataPlots()["No chart"] == {}


def test_dataPlots_chartsHaveTemplateAndItems(styles):
    for name, plot in dataPlots().items():
        if name == "No chart":
            continue
        assert plot["template"]["legendRef"] is None
        assert plot["template"]["label"]
        assert plot["lineItems"]
        for item in plot["lineItems"].values():
            assert item["plotItemRef"] is None
            assert item["name"]
            assert item["pen"]


@pytest.mark.parametrize(
    ("name", "label", "valueRange", "keys"),
    [
        (
            "Axis Stability",
            "Delta angle [arcsec]",
            None,
            ["mount-deltaRaJNow", "mount-deltaDecJNow"],
        ),
        ("Temperature", "Temperature [°C]", (-20, 40, False), None),
        ("Pressure", "Pressure [hPa]", (900, 1050, False), None),
        ("Sky Quality", "Sky Quality [mpas]", (10, 22.5, False), None),
        ("Voltage", "Supply Voltage [V]", (8, 15, False), ["power-powVolt"]),
        ("RTT Comp-Mount", "Round Trip Time [ms]", None, ["mount-rtt"]),
    ],
)
def test_dataPlots_templates(styles, name, label, valueRange, keys):
    plot = dataPlots()[name]
    assert plot["template"]["label"] == label
    assert plot["template"].get("range") == valueRange
    if keys is not None:
        assert list(plot["lineItems"]) == keys


def test_dataPlots_weatherCharts(styles):
    plots = dataPlots()
    assert len(plots["Temperature"]["lineItems"]) == 5
    assert (
        "directWeather-WEATHER_PARAMETERS.WEATHER_DEWPOINT" in plots["Dew Temperature"]["lineItems"]
    )
    assert len(plots["Sky Quality"]["lineItems"]) == 4


def test_dataPlots_currentPens(styles):
    items = dataPlots()["Current"]["lineItems"]
    assert items["power-powCurr"]["pen"] == styles.M_CYAN1
    assert items["power-powCurr3"]["pen"] == styles.M_RED
