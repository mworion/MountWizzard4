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
# Licence APL2.0
#
###########################################################
from mw4.gui.styles.styles import Styles


def dataPlots():
    return {
        "No chart": {},
        "Axis Stability": {
            "template": {"legendRef": None, "label": "Delta angle [arcsec]"},
            "lineItems": {
                "mount-deltaRaJNow": {
                    "plotItemRef": None,
                    "name": "RA",
                    "pen": Styles().M_GREEN,
                },
                "mount-deltaDecJNow": {
                    "plotItemRef": None,
                    "name": "DEC",
                    "pen": Styles().M_RED,
                },
            },
        },
        "Angular Tracking": {
            "template": {"legendRef": None, "label": "Angle error [arcsec]"},
            "lineItems": {
                "mount-errorAngularPosRA": {
                    "plotItemRef": None,
                    "name": "RA counter",
                    "pen": Styles().M_GREEN,
                },
                "mount-errorAngularPosDEC": {
                    "plotItemRef": None,
                    "name": "DEC counter",
                    "pen": Styles().M_RED,
                },
            },
        },
        "Temperature": {
            "template": {
                "range": (-20, 40, False),
                "legendRef": None,
                "label": "Temperature [°C]",
            },
            "lineItems": {
                "sensor1Weather-WEATHER_PARAMETERS.WEATHER_TEMPERATURE": {
                    "plotItemRef": None,
                    "name": "Sensor 1",
                    "pen": Styles().M_GREEN,
                },
                "sensor2Weather-WEATHER_PARAMETERS.WEATHER_TEMPERATURE": {
                    "plotItemRef": None,
                    "name": "Sensor 2",
                    "pen": Styles().M_RED,
                },
                "sensor3Weather-WEATHER_PARAMETERS.WEATHER_TEMPERATURE": {
                    "plotItemRef": None,
                    "name": "Sensor 3",
                    "pen": Styles().M_PINK,
                },
                "sensor4Weather-WEATHER_PARAMETERS.WEATHER_TEMPERATURE": {
                    "plotItemRef": None,
                    "name": "Sensor 4",
                    "pen": Styles().M_YELLOW,
                },
                "directWeather-WEATHER_PARAMETERS.WEATHER_TEMPERATURE": {
                    "plotItemRef": None,
                    "name": "Direct",
                    "pen": Styles().M_PRIM,
                },
            },
        },
        "Camera Temperature": {
            "template": {
                "range": (-20, 20, False),
                "legendRef": None,
                "label": "Camera Temperature [°C]",
            },
            "lineItems": {
                "camera-CCD_TEMPERATURE.CCD_TEMPERATURE_VALUE": {
                    "plotItemRef": None,
                    "name": "Camera",
                    "pen": Styles().M_PINK,
                },
            },
        },
        "Camera Cooler Power": {
            "template": {
                "range": (-5, 105, True),
                "legendRef": None,
                "label": "Camera Cooler Power [%]",
            },
            "lineItems": {
                "camera-CCD_COOLER_POWER.CCD_COOLER_VALUE": {
                    "plotItemRef": None,
                    "name": "CoolerPower",
                    "pen": Styles().M_PINK,
                },
            },
        },
        "Dew Temperature": {
            "template": {
                "range": (-20, 40, False),
                "legendRef": None,
                "label": "Dew Temperature [°C]",
            },
            "lineItems": {
                "sensor1Weather-WEATHER_PARAMETERS.WEATHER_DEWPOINT": {
                    "plotItemRef": None,
                    "name": "Sensor 1",
                    "pen": Styles().M_GREEN,
                },
                "sensor2Weather-WEATHER_PARAMETERS.WEATHER_DEWPOINT": {
                    "plotItemRef": None,
                    "name": "Sensor 2",
                    "pen": Styles().M_RED,
                },
                "sensor3Weather-WEATHER_PARAMETERS.WEATHER_DEWPOINT": {
                    "plotItemRef": None,
                    "name": "Sensor 3",
                    "pen": Styles().M_PINK,
                },
                "sensor4Weather-WEATHER_PARAMETERS.WEATHER_DEWPOINT": {
                    "plotItemRef": None,
                    "name": "Sensor 4",
                    "pen": Styles().M_YELLOW,
                },
                "directWeather-WEATHER_PARAMETERS.WEATHER_DEWPOINT": {
                    "plotItemRef": None,
                    "name": "Direct",
                    "pen": Styles().M_PRIM,
                },
            },
        },
        "Pressure": {
            "template": {
                "range": (900, 1050, False),
                "legendRef": None,
                "label": "Pressure [hPa]",
            },
            "lineItems": {
                "sensor1Weather-WEATHER_PARAMETERS.WEATHER_PRESSURE": {
                    "plotItemRef": None,
                    "name": "Sensor 1",
                    "pen": Styles().M_GREEN,
                },
                "sensor2Weather-WEATHER_PARAMETERS.WEATHER_PRESSURE": {
                    "plotItemRef": None,
                    "name": "Sensor 2",
                    "pen": Styles().M_RED,
                },
                "sensor3Weather-WEATHER_PARAMETERS.WEATHER_PRESSURE": {
                    "plotItemRef": None,
                    "name": "Sensor 3",
                    "pen": Styles().M_PINK,
                },
                "sensor4Weather-WEATHER_PARAMETERS.WEATHER_PRESSURE": {
                    "plotItemRef": None,
                    "name": "Sensor 4",
                    "pen": Styles().M_YELLOW,
                },
                "directWeather-WEATHER_PARAMETERS.WEATHER_PRESSURE": {
                    "plotItemRef": None,
                    "name": "Direct",
                    "pen": Styles().M_PRIM,
                },
            },
        },
        "Humidity": {
            "template": {"range": (-5, 105, True), "legendRef": None, "label": "Humidity [%]"},
            "lineItems": {
                "sensor1Weather-WEATHER_PARAMETERS.WEATHER_HUMIDITY": {
                    "plotItemRef": None,
                    "name": "Sensor 1",
                    "pen": Styles().M_GREEN,
                },
                "sensor2Weather-WEATHER_PARAMETERS.WEATHER_HUMIDITY": {
                    "plotItemRef": None,
                    "name": "Sensor 2",
                    "pen": Styles().M_RED,
                },
                "sensor3Weather-WEATHER_PARAMETERS.WEATHER_HUMIDITY": {
                    "plotItemRef": None,
                    "name": "Sensor 3",
                    "pen": Styles().M_PINK,
                },
                "sensor4Weather-WEATHER_PARAMETERS.WEATHER_HUMIDITY": {
                    "plotItemRef": None,
                    "name": "Sensor 4",
                    "pen": Styles().M_YELLOW,
                },
                "directWeather-WEATHER_PARAMETERS.WEATHER_HUMIDITY": {
                    "plotItemRef": None,
                    "name": "Direct",
                    "pen": Styles().M_PRIM,
                },
            },
        },
        "Sky Quality": {
            "template": {
                "range": (10, 22.5, False),
                "legendRef": None,
                "label": "Sky Quality [mpas]",
            },
            "lineItems": {
                "sensor1Weather-SKY_QUALITY.SKY_BRIGHTNESS": {
                    "plotItemRef": None,
                    "name": "Sensor 1",
                    "pen": Styles().M_GREEN,
                },
                "sensor2Weather-SKY_QUALITY.SKY_BRIGHTNESS": {
                    "plotItemRef": None,
                    "name": "Sensor 2",
                    "pen": Styles().M_RED,
                },
                "sensor3Weather-SKY_QUALITY.SKY_BRIGHTNESS": {
                    "plotItemRef": None,
                    "name": "Sensor 3",
                    "pen": Styles().M_PINK,
                },
                "sensor4Weather-SKY_QUALITY.SKY_BRIGHTNESS": {
                    "plotItemRef": None,
                    "name": "Sensor 4",
                    "pen": Styles().M_YELLOW,
                },
            },
        },
        "Voltage": {
            "template": {
                "range": (8, 15, False),
                "legendRef": None,
                "label": "Supply Voltage [V]",
            },
            "lineItems": {
                "power-powVolt": {
                    "plotItemRef": None,
                    "name": "Main Sensor",
                    "pen": Styles().M_YELLOW,
                },
            },
        },
        "Current": {
            "template": {"range": (0, 5, False), "legendRef": None, "label": "Current [A]"},
            "lineItems": {
                "power-powCurr": {"plotItemRef": None, "name": "Sum", "pen": Styles().M_CYAN1},
                "power-powCurr1": {
                    "plotItemRef": None,
                    "name": "Current 1",
                    "pen": Styles().M_GREEN,
                },
                "power-powCurr2": {
                    "plotItemRef": None,
                    "name": "Current 2",
                    "pen": Styles().M_PINK,
                },
                "power-powCurr3": {
                    "plotItemRef": None,
                    "name": "Current 3",
                    "pen": Styles().M_RED,
                },
                "power-powCurr4": {
                    "plotItemRef": None,
                    "name": "Current 4",
                    "pen": Styles().M_YELLOW,
                },
            },
        },
        "Time Diff Comp-Mount": {
            "template": {"legendRef": None, "label": "Time Difference [ms]"},
            "lineItems": {
                "mount-timeDiff": {
                    "plotItemRef": None,
                    "name": "MountControl",
                    "pen": Styles().M_YELLOW,
                },
            },
        },
        "Focus Position": {
            "template": {"legendRef": None, "label": "Focus Position [units]"},
            "lineItems": {
                "focuser-ABS_FOCUS_POSITION.FOCUS_ABSOLUTE_POSITION": {
                    "plotItemRef": None,
                    "name": "MountControl",
                    "pen": Styles().M_YELLOW,
                }
            },
        },
    }
