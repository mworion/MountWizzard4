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
from packaging.version import Version

# external packages

# local imports
from mountcontrol.connection import Connection


class Firmware(object):
    """ """

    log = logging.getLogger("MW4")

    def __init__(self, parent):
        self.parent = parent
        self._product = None
        self._vString = Version("0.0.0")
        self._hardware = None
        self._date = None
        self._time = None

    @property
    def product(self):
        return self._product

    @product.setter
    def product(self, value):
        self._product = value

    @property
    def vString(self):
        return self._vString

    @vString.setter
    def vString(self, value):
        if isinstance(value, str):
            self._vString = Version(value)
        else:
            self._vString = Version("0.0.0")

    @property
    def hardware(self):
        return self._hardware

    @hardware.setter
    def hardware(self, value):
        self._hardware = value

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, value):
        self._date = value

    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, value):
        self._time = value

    def checkNewer(self, compare: str) -> bool:
        """ """
        return self.vString >= Version(compare)

    def parse(self, response: list, numberOfChunks: int) -> bool:
        """ """
        if len(response) != numberOfChunks:
            self.log.warning("wrong number of chunks")
            return False
        self.date = response[0]
        self.vString = response[1]
        self.product = response[2]
        self.time = response[3]
        self.hardware = response[4]
        return True

    def poll(self) -> bool:
        """ """
        conn = Connection(self.parent.host)
        commandString = ":U2#:GVD#:GVN#:GVP#:GVT#:GVZ#"
        suc, response, chunks = conn.communicate(commandString)
        if not suc:
            return False
        return self.parse(response, chunks)
