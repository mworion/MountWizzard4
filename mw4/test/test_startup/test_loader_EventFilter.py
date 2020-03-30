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
# Python  v3.7.5
#
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest

# external packages
from PyQt5.QtCore import QEvent
from PyQt5.QtWidgets import QWidget

# local import
from mw4.loader import QAwesomeTooltipEventFilter


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown(qtbot):
    global app

    app = QAwesomeTooltipEventFilter()
    yield
    del app


def test_eventFilter_1(qtbot):
    widget = 'test'
    event = QEvent(QEvent.ToolTipChange)
    suc = app.eventFilter(widget=widget, event=event)
    assert not suc


def test_eventFilter_2(qtbot):
    widget = QWidget()
    event = QEvent(QEvent.ToolTipChange)
    app.eventFilter(widget=widget, event=event)


def test_eventFilter_3(qtbot):
    widget = QWidget()
    widget.setToolTip('<html><head/><body><p><br/></p></body></html>')
    event = QEvent(QEvent.ToolTipChange)
    suc = app.eventFilter(widget=widget, event=event)
    assert suc


def test_eventFilter_4(qtbot):
    widget = QWidget()
    widget.setToolTip('test')
    event = QEvent(QEvent.ToolTipChange)
    suc = app.eventFilter(widget=widget, event=event)
    assert suc


def test_eventFilter_5(qtbot):
    widget = 'test'
    event = QEvent(QEvent.ToolTip)
    app.eventFilter(widget=widget, event=event)


def test_eventFilter_6(qtbot):
    widget = QWidget()
    event = QEvent(QEvent.ToolTip)
    app.eventFilter(widget=widget, event=event)


def test_eventFilter_7(qtbot):
    widget = QWidget()
    widget.setToolTip('<html><head/><body><p><br/></p></body></html>')
    event = QEvent(QEvent.ToolTip)
    suc = app.eventFilter(widget=widget, event=event)
    assert suc
