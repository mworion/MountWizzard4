############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10_micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2026 by mworion
# License APL2.0
#
###########################################################

from mw4.logic.measure.measureAddOns import measure

EXPECTED_TOP_LEVEL_KEYS = {
    "mount",
    "sensor1Weather",
    "sensor2Weather",
    "sensor3Weather",
    "sensor4Weather",
    "directWeather",
    "camera",
    "filter",
    "focuser",
    "power",
}

EXPECTED_LENGTHS = {
    "mount": 6,
    "sensor1Weather": 7,
    "sensor2Weather": 7,
    "sensor3Weather": 7,
    "sensor4Weather": 7,
    "directWeather": 4,
    "camera": 2,
    "filter": 1,
    "focuser": 1,
    "power": 6,
}

EXPECTED_MOUNT_FIELDS = [
    "deltaRaJNow",
    "deltaDecJNow",
    "errorAngularPosRA",
    "errorAngularPosDEC",
    "status",
    "timeDiff",
]

WEATHER_SENSOR_FIELDS = [
    "WEATHER_PARAMETERS.WEATHER_TEMPERATURE",
    "WEATHER_PARAMETERS.WEATHER_PRESSURE",
    "WEATHER_PARAMETERS.WEATHER_DEWPOINT",
    "WEATHER_PARAMETERS.WEATHER_HUMIDITY",
    "WEATHER_PARAMETERS.CloudCov",
    "WEATHER_PARAMETERS.RainVol",
    "SKY_QUALITY.SKY_BRIGHTNESS",
]


def test_measureIsDict():
    assert isinstance(measure, dict)


def test_measureTopLevelKeys():
    assert set(measure.keys()) == EXPECTED_TOP_LEVEL_KEYS


def test_measureTopLevelCount():
    assert len(measure) == len(EXPECTED_TOP_LEVEL_KEYS)


def test_allValuesAreLists():
    for key, value in measure.items():
        assert isinstance(value, list), f"measure['{key}'] is not a list"


def test_allListElementsAreStrings():
    for key, value in measure.items():
        for idx, elem in enumerate(value):
            assert isinstance(elem, str), f"measure['{key}'][{idx}] = {elem!r} is not a string"


def test_sectionLengths():
    for key, expectedLen in EXPECTED_LENGTHS.items():
        assert len(measure[key]) == expectedLen, (
            f"measure['{key}'] has {len(measure[key])} items, expected {expectedLen}"
        )


def test_mountFields():
    assert measure["mount"] == EXPECTED_MOUNT_FIELDS


def test_sensor1WeatherFields():
    assert measure["sensor1Weather"] == WEATHER_SENSOR_FIELDS


def test_sensor2WeatherFields():
    assert measure["sensor2Weather"] == WEATHER_SENSOR_FIELDS


def test_sensor3WeatherFields():
    assert measure["sensor3Weather"] == WEATHER_SENSOR_FIELDS


def test_sensor4WeatherFields():
    assert measure["sensor4Weather"] == WEATHER_SENSOR_FIELDS


def test_directWeatherFields():
    assert measure["directWeather"] == [
        "WEATHER_PARAMETERS.WEATHER_TEMPERATURE",
        "WEATHER_PARAMETERS.WEATHER_PRESSURE",
        "WEATHER_PARAMETERS.WEATHER_DEWPOINT",
        "WEATHER_PARAMETERS.WEATHER_HUMIDITY",
    ]


def test_cameraFields():
    assert measure["camera"] == [
        "CCD_TEMPERATURE.CCD_TEMPERATURE_VALUE",
        "CCD_COOLER_POWER.CCD_COOLER_VALUE",
    ]


def test_filterFields():
    assert measure["filter"] == ["FILTER_SLOT.FILTER_SLOT_VALUE"]


def test_focuserFields():
    assert measure["focuser"] == ["ABS_FOCUS_POSITION.FOCUS_ABSOLUTE_POSITION"]


def test_powerFields():
    assert measure["power"] == [
        "powCurr1",
        "powCurr2",
        "powCurr3",
        "powCurr4",
        "powCurr",
        "powVolt",
    ]
