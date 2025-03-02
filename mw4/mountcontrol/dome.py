############################################################
# -*- coding: utf-8 -*-
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PySide for python
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import logging

# external packages
from skyfield.api import Angle

# local imports
from mountcontrol.connection import Connection
from mountcontrol.convert import valueToInt, valueToFloat


class Dome(object):
    """ """

    log = logging.getLogger("MW4")

    def __init__(self, parent):
        self.parent = parent
        self._shutterState = 0
        self._flapState = 0
        self._slew = False
        self._azimuth = None

    @property
    def shutterState(self):
        return self._shutterState

    @shutterState.setter
    def shutterState(self, value):
        value = valueToInt(value)
        if value is None:
            self._shutterState = None
        elif value < 0:
            self._shutterState = None
        elif value > 4:
            self._shutterState = None
        else:
            self._shutterState = value

    @property
    def flapState(self):
        return self._flapState

    @flapState.setter
    def flapState(self, value):
        value = valueToInt(value)
        if value is None:
            self._flapState = None
        elif value < 0:
            self._flapState = None
        elif value > 4:
            self._flapState = None
        else:
            self._flapState = value

    @property
    def slew(self):
        return self._slew

    @slew.setter
    def slew(self, value):
        value = valueToInt(value)
        if value is None:
            self._slew = None
        else:
            self._slew = bool(value)

    @property
    def azimuth(self):
        return self._azimuth

    @azimuth.setter
    def azimuth(self, value):
        value = valueToFloat(value)
        if value is None:
            self._azimuth = None
        else:
            self._azimuth = (value / 10) % 360.0

    def parse(self, response: list, numberOfChunks: int) -> bool:
        """ """
        if len(response) != numberOfChunks:
            self.log.warning("wrong number of chunks")
            return False
        self.shutterState = response[0]
        self.flapState = response[1]
        self.slew = response[2]
        self.azimuth = response[3]
        return True

    def poll(self) -> bool:
        """ """
        conn = Connection(self.parent.host)
        commandString = ":GDS#:GDF#:GDW#:GDA#"
        suc, response, chunks = conn.communicate(commandString)
        if not suc:
            return False
        return self.parse(response, chunks)

    def openShutter(self) -> bool:
        """ """
        conn = Connection(self.parent.host)
        commandString = ":SDS2#"
        suc, _, _ = conn.communicate(commandString, responseCheck="1")
        return suc

    def closeShutter(self) -> bool:
        """ """
        conn = Connection(self.parent.host)
        commandString = ":SDS1#"
        suc, _, _ = conn.communicate(commandString, responseCheck="1")
        return suc

    def openFlap(self) -> bool:
        """ """
        conn = Connection(self.parent.host)
        commandString = ":SDF2#"
        suc, _, _ = conn.communicate(commandString, responseCheck="1")
        return suc

    def closeFlap(self) -> bool:
        """ """
        conn = Connection(self.parent.host)
        commandString = ":SDF1#"
        suc, _, _ = conn.communicate(commandString, responseCheck="1")
        return suc

    def slewDome(self, azimuth: Angle) -> bool:
        """ """
        azimuth = azimuth.degrees % 360
        conn = Connection(self.parent.host)
        setAzimuth = f":SDA{azimuth:04.0f}#"
        commandString = setAzimuth
        suc, _, _ = conn.communicate(commandString, responseCheck="1")
        return suc

    def enableInternalDomeControl(self) -> bool:
        """ """
        conn = Connection(self.parent.host)
        commandString = ":SDAr#"
        suc, _, _ = conn.communicate(commandString)
        return suc
