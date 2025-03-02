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

# local imports
from mountcontrol.convert import valueToFloat


class TrajectoryParams(object):
    """
    The class TrajectoryParams inherits all information and handling of TLE tracking
    and managing attributes of the connected mount and provides the abstracted
    interface to a 10 micron mount.

        >>> trajectoryParams = TrajectoryParams(host='')
    """

    __all__ = ["TrajectoryParams"]

    log = logging.getLogger("MW4")

    def __init__(self, obsSite=None):
        self._jdStart = None
        self._jdEnd = None
        self._flip = None
        self._message = None
        self.obsSite = obsSite
        self.offsetRA = None
        self.offsetDEC = None
        self.offsetDECcorr = None
        self.offsetTime = None

    @property
    def flip(self):
        return self._flip

    @flip.setter
    def flip(self, value):
        if value is None:
            self._flip = None
            return
        elif isinstance(value, bool):
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
