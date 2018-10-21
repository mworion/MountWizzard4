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
# Python  v3.6.5
#
# Michael Würtenberger
# (c) 2018
#
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock
# external packages
import pytest
import pytestqt
import skyfield
# local import
from base.widget import InputValue


#
#
# testing mainW gui change tracking
#
#

def test_InputValue_ok1(qtbot):
    window = qtbot
    title = 'test'
    message = 'test'
    actValue = 100
    minValue = 0
    maxValue = 200
    stepValue = 1

    window = InputValue(window=window,
                        title=title,
                        message=message,
                        actValue=actValue,
                        minValue=minValue,
                        maxValue=maxValue,
                        stepValue=stepValue,
                        )
    window.show()
    qtbot.add_widget(window)


