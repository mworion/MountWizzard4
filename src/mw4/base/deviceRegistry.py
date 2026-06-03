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
from mw4.logic.camera.camera import Camera
from mw4.logic.cover.cover import Cover
from mw4.logic.dome.dome import Dome
from mw4.logic.environment.directWeather import DirectWeather
from mw4.logic.environment.seeingWeather import SeeingWeather
from mw4.logic.environment.sensorWeather import SensorWeather
from mw4.logic.filter.filter import Filter
from mw4.logic.focuser.focuser import Focuser
from mw4.logic.lightPanel.lightPanel import LightPanel
from mw4.logic.measure.measure import MeasureData
from mw4.logic.plateSolve.plateSolve import PlateSolve
from mw4.logic.powerswitch.kmRelay import KMRelay
from mw4.logic.powerswitch.pegasusUPB import PegasusUPB
from mw4.logic.remote.remote import Remote
from mw4.logic.telescope.telescope import Telescope
from typing import Any


class DeviceRegistry:
    def __init__(self, app: Any) -> None:
        self.drivers: dict[str, dict[str, Any]] = {
            "camera": {
                "class": Camera(app),
                "deviceType": "camera",
                "stat": None,
            },
            "cover": {
                "class": Cover(app),
                "deviceType": "covercalibrator",
                "stat": None,
            },
            "directWeather": {
                "class": DirectWeather(app),
                "deviceType": None,
                "stat": None,
            },
            "dome": {
                "class": Dome(app),
                "deviceType": "dome",
                "stat": None,
            },
            "filter": {
                "class": Filter(app),
                "deviceType": "filterwheel",
                "stat": None,
            },
            "focuser": {
                "class": Focuser(app),
                "deviceType": "focuser",
                "stat": None,
            },
            "lightPanel": {
                "class": LightPanel(app),
                "deviceType": "covercalibrator",
                "stat": None,
            },
            "measure": {
                "class": MeasureData(app),
                "deviceType": None,
                "stat": None,
            },
            "mount": {
                "class": app.mount,
                "deviceType": None,
                "stat": None,
            },
            "plateSolve": {
                "class": PlateSolve(app),
                "deviceType": "plateSolve",
                "stat": None,
            },
            "power": {
                "class": PegasusUPB(app),
                "deviceType": "switch",
                "stat": None,
            },
            "relay": {
                "class": KMRelay(),
                "deviceType": None,
                "stat": None,
            },
            "refraction": {
                "class": None,
                "deviceType": None,
                "stat": None,
            },
            "remote": {
                "class": Remote(app),
                "deviceType": None,
                "stat": None,
            },
            "seeingWeather": {
                "class": SeeingWeather(app),
                "deviceType": "observingconditions",
                "stat": None,
            },
            "sensor1Weather": {
                "class": SensorWeather(app),
                "deviceType": "observingconditions",
                "stat": None,
            },
            "sensor2Weather": {
                "class": SensorWeather(app),
                "deviceType": "observingconditions",
                "stat": None,
            },
            "sensor3Weather": {
                "class": SensorWeather(app),
                "deviceType": "observingconditions",
                "stat": None,
            },
            "sensor4Weather": {
                "class": SensorWeather(app),
                "deviceType": "observingconditions",
                "stat": None,
            },
            "telescope": {
                "class": Telescope(app),
                "deviceType": "telescope",
                "stat": None,
            },
        }



