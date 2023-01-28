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
# written in python3, (c) 2019-2023 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import logging

# external packages

# local imports
from mountcontrol.connection import Connection
from mountcontrol.convert import valueToInt


class Firmware(object):
    """
    The class Firmware inherits all information and handling of firmware
    attributes of the connected mount and provides the abstracted interface
    to a 10 micron mount.

        >>> fw = Firmware(host='')
    """

    __all__ = ['Firmware']

    log = logging.getLogger(__name__)

    def __init__(self, host=None):
        self.host = host
        self._product = None
        self._vString = None
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
        if not isinstance(value, str):
            self._vString = None
            return
        if not value.count('.') > 0:
            self._vString = None
            return
        if any(valueToInt(x) is None for x in value.split('.')):
            self._vString = None
            return
        self._vString = value

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

    def number(self):
        if not self._vString:
            return None

        parts = self._vString.split('.')
        try:
            if len(parts) == 3:
                value = int(parts[0]) * 10000 + int(parts[1]) * 100 + int(parts[2])

            elif len(parts) == 2:
                value = int(parts[0]) * 10000 + int(parts[1]) * 100

            else:
                value = None

        except Exception as e:
            self.log.warning(f'error: {e}, malformed value: {parts}')
            return None

        else:
            return value

    def checkNewer(self, compare):
        """
        Checks if the provided FW number is newer than the one of the mount

        :param compare:     fw number to test as int
        :return:            True if newer / False
        """
        value = self.number()
        if value:
            return compare < value
        else:
            return None

    def parse(self, response, numberOfChunks):
        """
        Parsing the polling slow command.

        :param response:        data load from mount
        :param numberOfChunks:
        :return: success:       True if ok, False if not
        """

        if len(response) != numberOfChunks:
            self.log.warning('wrong number of chunks')
            return False
        self.date = response[0]
        self.vString = response[1]
        self.product = response[2]
        self.time = response[3]
        self.hardware = response[4]
        return True

    def poll(self):
        """
        Sending the polling slow command. As the mount need polling the data,
        I send a set of commands to get the data back to be able to process
        and store it.

        :return: success:   True if ok, False if not
        """

        conn = Connection(self.host)
        commandString = ':U2#:GVD#:GVN#:GVP#:GVT#:GVZ#'
        suc, response, chunks = conn.communicate(commandString)
        if not suc:
            return False
        suc = self.parse(response, chunks)
        return suc
