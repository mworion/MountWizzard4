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

# external packages

# local import
from logic.profiles.profileConvert import convertProfileData, blendProfile


def test_convertProfileData_1():
    data = {
        'version': '4.1'
    }
    val = convertProfileData(data)
    assert val['version'] == '4.1'


def test_convertProfileData_2():
    data = {
        'version': '4.0'
    }
    val = convertProfileData(data)
    assert val['version'] == '4.0'


def test_convertProfileData_3():
    data = {
        'version': '4.0',
        'mainW': {},
    }
    val = convertProfileData(data)
    assert val['version'] == '4.0'


def test_convertProfileData_4():
    data = {
        'version': '4.0',
        'hemisphereW': {},
        'mainW': {
            'driversData': 'test'
        },
    }
    val = convertProfileData(data)
    assert val['version'] == '4.1'
    assert 'driversData' in val
    assert 'driversData' not in val['mainW']


def test_blendProfile():
    conf = blendProfile({}, {})
    assert conf == {}
