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
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
import logging
from mw4.mountcontrol.connection import Connection
from packaging.version import Version


class Firmware:
    """ """
    log = logging.getLogger("MW4")

    def __init__(self, parent):
        self.parent = parent
        self.product: str = ""
        self._vString: Version = Version("0.0.0")
        self.hardware: str = ""
        self.date: str = ""
        self.time: str = ""

    @property
    def vString(self):
        return self._vString

    @vString.setter
    def vString(self, value: str):
        self._vString = Version(value)

    def checkNewer(self, compare: str) -> bool:
        """ """
        return self.vString >= Version(compare)

    def isHW2024(self) -> bool:
        """ """
        return self.hardware == "Q-TYPE2024"

    def isHW2012(self) -> bool:
        """ """
        return self.hardware == "Q-TYPE2012"

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
        commandString = ":U2#:GVD#:GVN#:GVP#:GVT#:GVZ#:GCFG#"
        suc, response, chunks = conn.communicate(commandString)
        if not suc:
            return False
        return self.parse(response, chunks)
