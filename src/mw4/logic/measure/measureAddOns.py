# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion

measure: dict[str, list[str]] = {
    "mount": [
        "deltaRaJNow",
        "deltaDecJNow",
        "errorAngularPosRA",
        "errorAngularPosDEC",
        "status",
        "timeDiff",
        "rtt",
    ],
    "sensor1Weather": [
        "WEATHER_PARAMETERS.WEATHER_TEMPERATURE",
        "WEATHER_PARAMETERS.WEATHER_PRESSURE",
        "WEATHER_PARAMETERS.WEATHER_DEWPOINT",
        "WEATHER_PARAMETERS.WEATHER_HUMIDITY",
        "WEATHER_PARAMETERS.CloudCov",
        "WEATHER_PARAMETERS.RainVol",
        "SKY_QUALITY.SKY_BRIGHTNESS",
    ],
    "sensor2Weather": [
        "WEATHER_PARAMETERS.WEATHER_TEMPERATURE",
        "WEATHER_PARAMETERS.WEATHER_PRESSURE",
        "WEATHER_PARAMETERS.WEATHER_DEWPOINT",
        "WEATHER_PARAMETERS.WEATHER_HUMIDITY",
        "WEATHER_PARAMETERS.CloudCov",
        "WEATHER_PARAMETERS.RainVol",
        "SKY_QUALITY.SKY_BRIGHTNESS",
    ],
    "sensor3Weather": [
        "WEATHER_PARAMETERS.WEATHER_TEMPERATURE",
        "WEATHER_PARAMETERS.WEATHER_PRESSURE",
        "WEATHER_PARAMETERS.WEATHER_DEWPOINT",
        "WEATHER_PARAMETERS.WEATHER_HUMIDITY",
        "WEATHER_PARAMETERS.CloudCov",
        "WEATHER_PARAMETERS.RainVol",
        "SKY_QUALITY.SKY_BRIGHTNESS",
    ],
    "sensor4Weather": [
        "WEATHER_PARAMETERS.WEATHER_TEMPERATURE",
        "WEATHER_PARAMETERS.WEATHER_PRESSURE",
        "WEATHER_PARAMETERS.WEATHER_DEWPOINT",
        "WEATHER_PARAMETERS.WEATHER_HUMIDITY",
        "WEATHER_PARAMETERS.CloudCov",
        "WEATHER_PARAMETERS.RainVol",
        "SKY_QUALITY.SKY_BRIGHTNESS",
    ],
    "directWeather": [
        "WEATHER_PARAMETERS.WEATHER_TEMPERATURE",
        "WEATHER_PARAMETERS.WEATHER_PRESSURE",
        "WEATHER_PARAMETERS.WEATHER_DEWPOINT",
        "WEATHER_PARAMETERS.WEATHER_HUMIDITY",
    ],
    "camera": [
        "CCD_TEMPERATURE.CCD_TEMPERATURE_VALUE",
        "CCD_COOLER_POWER.CCD_COOLER_VALUE",
    ],
    "filter": [
        "FILTER_SLOT.FILTER_SLOT_VALUE",
    ],
    "focuser": [
        "ABS_FOCUS_POSITION.FOCUS_ABSOLUTE_POSITION",
    ],
    "power": [
        "powCurr1",
        "powCurr2",
        "powCurr3",
        "powCurr4",
        "powCurr",
        "powVolt",
    ],
}
