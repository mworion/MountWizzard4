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
# written in python3, (c) 2019-2022 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
import logging

# local imports
from base.loggerMW import setupLogging

setupLogging()
log = logging.getLogger()


def convertProfileData(data):
    """
    convertDate tries to convert data from an older or newer version of the
    config file to the actual needed one.

    :param      data: config data as dict
    :return:    data: config data as dict
    """
    if data.get('version', '0.0') in ['0.0', '4.1']:
        return data
    if 'mainW' not in data:
        return data

    log.info(f'Conversion from [{data.get("version")}] to [4.1]')
    if 'driversData' in data['mainW']:
        data['driversData'] = data['mainW']['driversData']
        data['version'] = '4.1'
        del data['mainW']['driversData']

    horizonFile = data['mainW'].get('horizonFileName', '')
    if 'hemisphereW' in data:
        data['hemisphereW']['horizonMaskFileName'] = horizonFile
    else:
        data['hemisphereW'] = {'horizonMaskFileName': horizonFile}
    return data
