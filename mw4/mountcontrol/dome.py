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
# GUI with PyQT5 for python
#
# written in python3, (c) 2019-2022 by mworion
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
    """
        >>> fw = Dome(host='')
    """
    __all__ = ['Dome',
               ]
    log = logging.getLogger(__name__)

    def __init__(self, host=None):
        self.host = host
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

    def parse(self, response, numberOfChunks):
        """
        :param response:        data load from mount
        :param numberOfChunks:
        :return: success:       True if ok, False if not
        """
        if len(response) != numberOfChunks:
            self.log.warning('wrong number of chunks')
            return False
        self.shutterState = response[0]
        self.flapState = response[1]
        self.slew = response[2]
        self.azimuth = response[3]
        return True

    def poll(self):
        """
        :return: success:   True if ok, False if not
        """
        conn = Connection(self.host)
        commandString = ':GDS#:GDF#:GDW#:GDA#'
        suc, response, chunks = conn.communicate(commandString)
        if not suc:
            return False
        suc = self.parse(response, chunks)
        return suc

    def openShutter(self):
        """
        :return:
        """
        conn = Connection(self.host)
        commandString = ':SDS2#'
        suc, response, numberOfChunks = conn.communicate(commandString)

        if not suc:
            return False
        if '0' in response[0]:
            return False

        return True

    def closeShutter(self):
        """
        :return:
        """
        conn = Connection(self.host)
        commandString = ':SDS1#'
        suc, response, numberOfChunks = conn.communicate(commandString)

        if not suc:
            return False
        if '0' in response[0]:
            return False

        return True

    def openFlap(self):
        """
        :return:
        """
        conn = Connection(self.host)
        commandString = ':SDF2#'
        suc, response, numberOfChunks = conn.communicate(commandString)

        if not suc:
            return False
        if '0' in response[0]:
            return False

        return True

    def closeFlap(self):
        """
        :return:
        """
        conn = Connection(self.host)
        commandString = ':SDF1#'
        suc, response, numberOfChunks = conn.communicate(commandString)

        if not suc:
            return False
        if '0' in response[0]:
            return False

        return True

    def slewDome(self, azimuth=None):
        """
        :return:
        """
        if azimuth is None:
            return False
        if type(azimuth) == Angle:
            azimuth = azimuth.degrees

        azimuth = azimuth % 360
        conn = Connection(self.host)
        setAzimuth = f':SDA{azimuth:04.0f}#'
        commandString = setAzimuth
        suc, response, numberOfChunks = conn.communicate(commandString)

        if not suc:
            return False
        if '0' in response[0]:
            return False

        return True

    def enableInternalDomeControl(self):
        """
        :return:
        """
        conn = Connection(self.host)
        commandString = ':SDAr#'
        suc, response, numberOfChunks = conn.communicate(commandString)
        return suc
