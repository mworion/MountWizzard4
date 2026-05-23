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
def checkFormatMAC(value: str) -> str:
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
            if char.upper() not in "0123456789ABCDEF":
                return ""

    value = "{:2s}:{:2s}:{:2s}:{:2s}:{:2s}:{:2s}".format(*value)
    return value
