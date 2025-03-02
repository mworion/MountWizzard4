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

# external packages

# local imports


def checkFormatMAC(value: str) -> str:
    """ """
    if not value:
        return ""

    if not isinstance(value, str):
        return ""

    value = value.upper()
    value = value.replace(".", ":")
    value = value.split(":")
    if len(value) != 6:
        return ""

    for chunk in value:
        if len(chunk) != 2:
            return ""

        for char in chunk:
            if char not in [
                "0",
                "1",
                "2",
                "3",
                "4",
                "5",
                "6",
                "7",
                "8",
                "9",
                "A",
                "B",
                "C",
                "D",
                "E",
                "F",
            ]:
                return ""

    value = "{0:2s}:{1:2s}:{2:2s}:{3:2s}:{4:2s}:{5:2s}".format(*value)
    return value
