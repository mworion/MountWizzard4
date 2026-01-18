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
import numpy
from dataclasses import dataclass
from skyfield.api import Angle, Star


@dataclass
class ModelStar:
    """ """

    coord: Star = Star(ra_hours=0, dec_degrees=0)
    errorRMS: float = 0
    errorAngle: Angle = Angle(degrees=0)
    number: int = 0
    alt: Angle = Angle(degrees=0)
    az: Angle = Angle(degrees=0)

    def errorRA(self):
        return Angle(degrees=self.errorRMS * numpy.sin(self.errorAngle.radians))

    def errorDEC(self):
        return Angle(degrees=self.errorRMS * numpy.cos(self.errorAngle.radians))
