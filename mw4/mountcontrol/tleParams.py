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
from skyfield.units import Angle

# local imports
from mountcontrol.convert import valueToAngle, valueToFloat


class TLEParams(object):
    """
    The class TLEParams inherits all information and handling of TLE tracking
    and managing attributes of the connected mount and provides the abstracted
    interface to a 10 micron mount.
    """

    __all__ = ["TLEParams"]

    log = logging.getLogger("MW4")

    def __init__(self, obsSite=None):
        self.obsSite = obsSite
        self._azimuth = None
        self._altitude = None
        self._ra = None
        self._dec = None
        self._jdStart = None
        self._jdEnd = None
        self._flip = None
        self._message = None
        self._l0 = None
        self._l1 = None
        self._l2 = None
        self._name = None

    @property
    def azimuth(self):
        return self._azimuth

    @azimuth.setter
    def azimuth(self, value):
        if isinstance(value, Angle):
            self._azimuth = value
            return
        self._azimuth = valueToAngle(value, preference="degrees")

    @property
    def altitude(self):
        return self._altitude

    @altitude.setter
    def altitude(self, value):
        if isinstance(value, Angle):
            self._altitude = value
            return
        self._altitude = valueToAngle(value, preference="degrees")

    @property
    def ra(self):
        return self._ra

    @ra.setter
    def ra(self, value):
        if isinstance(value, Angle):
            self._ra = value
            return
        self._ra = valueToAngle(value, preference="hours")

    @property
    def dec(self):
        return self._dec

    @dec.setter
    def dec(self, value):
        if isinstance(value, Angle):
            self._dec = value
            return
        self._dec = valueToAngle(value, preference="degrees")

    @property
    def flip(self):
        return self._flip

    @flip.setter
    def flip(self, value):
        if isinstance(value, bool):
            self._flip = value
            return
        self._flip = bool(value == "F")

    @property
    def jdStart(self):
        return self._jdStart

    @jdStart.setter
    def jdStart(self, value):
        value = valueToFloat(value)
        if value:
            self._jdStart = self.obsSite.ts.tt_jd(value + self.obsSite.UTC2TT)
        else:
            self._jdStart = None

    @property
    def jdEnd(self):
        return self._jdEnd

    @jdEnd.setter
    def jdEnd(self, value):
        value = valueToFloat(value)
        if value:
            self._jdEnd = self.obsSite.ts.tt_jd(value + self.obsSite.UTC2TT)
        else:
            self._jdEnd = None

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, value):
        if value:
            self._message = value
        else:
            self._message = None

    @property
    def l0(self):
        return self._l0

    @l0.setter
    def l0(self, value):
        self._l0 = value

    @property
    def l1(self):
        return self._l1

    @l1.setter
    def l1(self, value):
        self._l1 = value

    @property
    def l2(self):
        return self._l2

    @l2.setter
    def l2(self, value):
        self._l2 = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
