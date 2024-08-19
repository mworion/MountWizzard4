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
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages

# local import
from gui.utilities.qCustomTableWidgetItem import QCustomTableWidgetItem


def test_QCustomTableWidgetItem_1():
    i1 = QCustomTableWidgetItem('')
    i2 = QCustomTableWidgetItem('')
    assert not (i1 < i2)


def test_QCustomTableWidgetItem_2():
    i1 = QCustomTableWidgetItem('-2.0')
    i2 = QCustomTableWidgetItem('')
    assert i1 < i2


def test_QCustomTableWidgetItem_3():
    i1 = QCustomTableWidgetItem('-2.0')
    i2 = QCustomTableWidgetItem('5')
    assert i1 < i2
