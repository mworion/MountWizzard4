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


dataPlots = {
    "No chart": {},
    "Axis Stability": {
        "template": {"legendRef": None, "label": "Delta angle [arcsec]"},
        "lineItems": {
            "deltaRaJNow": {"plotItemRef": None, "name": "RA", "pen": Styles().M_GREEN},
            "deltaDecJNow": {"plotItemRef": None, "name": "DEC", "pen": Styles().M_RED},
        }
    },
    "Angular Tracking": {
        "template": {"legendRef": None, "label": "Angle error [arcsec]"},
        "lineItems": {
            "errorAngularPosRA": {
                "plotItemRef": None,
                "name": "RA counter",
                "pen": Styles().M_GREEN,
            },
            "errorAngularPosDEC": {
                "plotItemRef": None,
                "name": "DEC counter",
                "pen": Styles().M_RED,
            },
        }
    },
    "Temperature": {
        "template": {
            "range": (-20, 40, False),
            "legendRef": None,
            "label": "Temperature [°C]",
        },
        "lineItems": {
            "sensor1WeatherTemp": {
                "plotItemRef": None,
                "name": "Sensor 1",
                "pen": Styles().M_GREEN,
            },
            "sensor2WeatherTemp": {
                "plotItemRef": None,
                "name": "Sensor 2",
                "pen": Styles().M_RED,
            },
            "sensor3WeatherTemp": {
                "plotItemRef": None,
                "name": "Sensor 3",
                "pen": Styles().M_PINK,
            },
            "sensor4WeatherTemp": {
                "plotItemRef": None,
                "name": "Sensor 4",
                "pen": Styles().M_YELLOW,
            },
            "directWeatherTemp": {"plotItemRef": None, "name": "Direct", "pen": Styles().M_PRIM},
        }
    },
    "Camera Temperature": {
        "template": {
            "range": (-20, 20, False),
            "legendRef": None,
            "label": "Camera Temperature [°C]",
        },
        "lineItems": {
            "cameraTemp": {"plotItemRef": None, "name": "Camera", "pen": Styles().M_PINK},
        }
    },
    "Camera Cooler Power": {
        "template": {
            "range": (-5, 105, True),
            "legendRef": None,
            "label": "Camera Cooler Power [%]",
        },
        "lineItems": {
            "cameraPower": {"plotItemRef": None, "name": "CoolerPower", "pen": Styles().M_PINK},
        }
    },
    "Dew Temperature": {
        "template": {
            "range": (-20, 40, False),
            "legendRef": None,
            "label": "Dew Temperature [°C]",
        },
        "lineItems": {
            "sensor1WeatherDew": {
                "plotItemRef": None,
                "name": "Sensor 1",
                "pen": Styles().M_GREEN,
            },
            "sensor2WeatherDew": {
                "plotItemRef": None,
                "name": "Sensor 2",
                "pen": Styles().M_RED,
            },
            "sensor3WeatherDew": {
                "plotItemRef": None,
                "name": "Sensor 3",
                "pen": Styles().M_PINK,
            },
            "sensor4WeatherDew": {
                "plotItemRef": None,
                "name": "Sensor 4",
                "pen": Styles().M_YELLOW,
            },
            "directWeatherDew": {"plotItemRef": None, "name": "Direct", "pen": Styles().M_PRIM},
        }
    },
    "Pressure": {
        "template": {
            "range": (900, 1050, False),
            "legendRef": None,
            "label": "Pressure [hPa]",
        },
        "lineItems": {
            "sensor1WeatherPress": {
                "plotItemRef": None,
                "name": "Sensor 1",
                "pen": Styles().M_GREEN,
            },
            "sensor2WeatherPress": {
                "plotItemRef": None,
                "name": "Sensor 2",
                "pen": Styles().M_RED,
            },
            "sensor3WeatherPress": {
                "plotItemRef": None,
                "name": "Sensor 3",
                "pen": Styles().M_PINK,
            },
            "sensor4WeatherPress": {
                "plotItemRef": None,
                "name": "Sensor 4",
                "pen": Styles().M_YELLOW,
            },
            "directWeatherPress": {
                "plotItemRef": None,
                "name": "Direct",
                "pen": Styles().M_PRIM,
            },
        }
    },
    "Humidity": {
        "template": {"range": (-5, 105, True), "legendRef": None, "label": "Humidity [%]"},
        "lineItems": {
            "sensor1WeatherHum": {
                "plotItemRef": None,
                "name": "Sensor 1",
                "pen": Styles().M_GREEN,
            },
            "sensor2WeatherHum": {
                "plotItemRef": None,
                "name": "Sensor 2",
                "pen": Styles().M_RED,
            },
            "sensor3WeatherHum": {
                "plotItemRef": None,
                "name": "Sensor 3",
                "pen": Styles().M_PINK,
            },
            "sensor4WeatherHum": {
                "plotItemRef": None,
                "name": "Sensor 4",
                "pen": Styles().M_YELLOW,
            },
            "directWeatherHum": {"plotItemRef": None, "name": "Direct", "pen": Styles().M_PRIM},
        }
    },
    "Sky Quality": {
        "template": {
            "range": (10, 22.5, False),
            "legendRef": None,
            "label": "Sky Quality [mpas]",
        },
        "lineItems": {
            "sensor1WeatherSky": {
                "plotItemRef": None,
                "name": "Sensor 1",
                "pen": Styles().M_GREEN,
            },
            "sensor2WeatherSky": {
                "plotItemRef": None,
                "name": "Sensor 2",
                "pen": Styles().M_RED,
            },
            "sensor3WeatherSky": {
                "plotItemRef": None,
                "name": "Sensor 3",
                "pen": Styles().M_PINK,
            },
            "sensor4WeatherSky": {
                "plotItemRef": None,
                "name": "Sensor 4",
                "pen": Styles().M_YELLOW,
            },
        }
    },
    "Voltage": {
        "template": {
            "range": (8, 15, False),
            "legendRef": None,
            "label": "Supply Voltage [V]",
        },
        "lineItems": {
            "powVolt": {"plotItemRef": None, "name": "Main Sensor", "pen": Styles().M_YELLOW},
        }
    },
    "Current": {
        "template": {"range": (0, 5, False), "legendRef": None, "label": "Current [A]"},
        "lineItems": {
            "powCurr": {"plotItemRef": None, "name": "Sum", "pen": Styles().M_CYAN1},
            "powCurr1": {"plotItemRef": None, "name": "Current 1", "pen": Styles().M_GREEN},
            "powCurr2": {"plotItemRef": None, "name": "Current 2", "pen": Styles().M_PINK},
            "powCurr3": {"plotItemRef": None, "name": "Current 3", "pen": Styles().M_RED},
            "powCurr4": {"plotItemRef": None, "name": "Current 4", "pen": Styles().M_YELLOW},
        }
    },
    "Time Diff Comp-Mount": {
        "template": {"legendRef": None, "label": "Time Difference [ms]"},
        "lineItems": {
            "timeDiff": {"plotItemRef": None, "name": "MountControl", "pen": Styles().M_YELLOW},
        }
    },
    "Focus Position": {
        "template": {"legendRef": None, "label": "Focus Position [units]"},
        "lineItems": {
            "focusPosition": {
                "plotItemRef": None,
                "name": "MountControl",
                "pen": Styles().M_YELLOW,
            }
        },
    },
}
