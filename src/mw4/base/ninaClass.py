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
from mw4.base.sgproNinaClass import SgproNinaCommon


class NINAClass(SgproNinaCommon):
    PROTOCOL_NAME: str = "NINA"

    def isConnectedState(self, response: dict) -> bool:
        state = response.get("State", -1)
        return state != 5
