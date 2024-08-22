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
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages

# local imports

def checkFormatMAC(value):
    """
    checkFormatMAC makes some checks to ensure that the format of the
    string is ok for WOL package.

    :param      value: string with mac address
    :return:    checked string in upper cases
    """
    if not value:
        return None

    if not isinstance(value, str):
        return None

    value = value.upper()
    value = value.replace('.', ':')
    value = value.split(':')
    if len(value) != 6:
        return None

    for chunk in value:
        if len(chunk) != 2:
            return None

        for char in chunk:
            if char not in ['0', '1', '2', '3', '4',
                            '5', '6', '7', '8', '9',
                            'A', 'B', 'C', 'D', 'E', 'F']:
                return None

    value = '{0:2s}:{1:2s}:{2:2s}:{3:2s}:{4:2s}:{5:2s}'.format(*value)
    return value
