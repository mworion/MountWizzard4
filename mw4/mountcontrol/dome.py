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
# written in python3, (c) 2019-2021 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import logging

# external packages

# local imports
from mountcontrol.connection import Connection
from mountcontrol.convert import valueToInt


class Dome(object):
    """
    The class Firmware inherits all information and handling of firmware
    attributes of the connected mount and provides the abstracted interface
    to a 10 micron mount.

        >>> fw = Dome(host='')
    """

    __all__ = ['Dome',
               ]

    log = logging.getLogger(__name__)

    def __init__(self,
                 host=None,
                 ):
        self.host = host
        self.shutterState = 0
        self.flapState = 0
        self.slew = False
        self.azimuth = None

    @property
    def shutterState(self):
        return self._shutterState

    @shutterState.setter
    def shutterState(self, value):
        self._shutterState = value

    @property
    def flapState(self):
        return self._flapState

    @flapState.setter
    def flapState(self, value):
        self._flapState = value

    @property
    def slew(self):
        return self._slew

    @slew.setter
    def slew(self, value):
        self._slew = bool(value)

    @property
    def azimuth(self):
        return self._azimuth

    @azimuth.setter
    def azimuth(self, value):
        self._azimuth = value

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

    def slew(self, azimuth=None):
        """
        :return:
        """
        if azimuth is None:
            return False

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

    def setDomeControlInternal(self):
        """
        :return:
        """
        conn = Connection(self.host)
        commandString = ':SDAr#'
        suc, response, numberOfChunks = conn.communicate(commandString)
        return suc
