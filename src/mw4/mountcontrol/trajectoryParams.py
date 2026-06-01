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


@dataclass
class TrajectoryParams(JdParamsMixin):
    obsSite: ObsSite
    flip: bool = False
    message: str = ""
    offsetRA: float = 0
    offsetDEC: float = 0
    offsetDECcorr: float = 0
    offsetTime: float = 0
