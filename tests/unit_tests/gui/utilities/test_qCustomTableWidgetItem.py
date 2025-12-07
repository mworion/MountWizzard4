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





from mw4.gui.utilities.qCustomTableWidgetItem import QCustomTableWidgetItem


def test_QCustomTableWidgetItem_1():
    i1 = QCustomTableWidgetItem("")
    i2 = QCustomTableWidgetItem("")
    assert not (i1 < i2)


def test_QCustomTableWidgetItem_2():
    i1 = QCustomTableWidgetItem("-2.0")
    i2 = QCustomTableWidgetItem("")
    assert i1 < i2


def test_QCustomTableWidgetItem_3():
    i1 = QCustomTableWidgetItem("-2.0")
    i2 = QCustomTableWidgetItem("5")
    assert i1 < i2
