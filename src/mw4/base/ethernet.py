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
import re


def checkFormatMAC(value: str) -> str:
    if not value or not isinstance(value, str):
        return ""

    value = value.upper()
    value = value.replace(".", ":")
    value = value.split(":")
    if len(value) != 6:
        return ""

    for chunk in value:
        if not re.fullmatch(r"[0-9A-F]{2}", chunk):
            return ""

    return "{:2s}:{:2s}:{:2s}:{:2s}:{:2s}:{:2s}".format(*value)
