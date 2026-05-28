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
from dataclasses import dataclass
from mw4.mountcontrol.jdParamMixin import JdParamsMixin
from mw4.mountcontrol.obsSite import ObsSite
from skyfield.units import Angle


@dataclass
class TLEParams(JdParamsMixin):
    obsSite: ObsSite
    azimuth: Angle = Angle(degrees=0)
    altitude: Angle = Angle(degrees=0)
    ra: Angle = Angle(hours=0)
    dec: Angle = Angle(degrees=0)
    flip: bool = False
    message: str = ""
    l0: str = ""
    l1: str = ""
    l2: str = ""
    name: str = ""
