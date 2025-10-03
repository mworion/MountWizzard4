############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages
# local import
from gui.utilities.qMultiWait import QMultiWait
from PySide6.QtCore import QObject, Signal


def test_QMultiWait_1():
    class Test(QObject):
        a = Signal()

    w = QMultiWait()
    A = Test()
    w.addWaitableSignal(A.a)


def test_QMultiWait_2():
    class Test(QObject):
        a = Signal()

    w = QMultiWait()
    A = Test()
    w.addWaitableSignal(A.a)
    w.checkSignal()


def test_QMultiWait_3():
    w = QMultiWait()
    w.resetSignals()


def test_QMultiWait_4():
    class Test(QObject):
        a = Signal()

    w = QMultiWait()
    A = Test()
    w.addWaitableSignal(A.a)
    w.clear()
