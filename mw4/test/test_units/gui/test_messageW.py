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
# Python  v3.7.3
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
# local import
from mw4.test.test_units.setupQt import setupQt


@pytest.fixture(autouse=True, scope='module')
def module_setup_teardown():
    global app, spy, mwGlob, test
    app, spy, mwGlob, test = setupQt()
    app.config['showMessageWindow'] = True
    app.toggleMessageWindow()
    yield


def test_resizeEvent(qtbot):
    app.messageW.resizeEvent(None)


def test_writeMessage1(qtbot):
    app.messageW.ui.message.setText('')
    suc = app.messageW.writeMessage('test_mountwizzard', 0)
    assert suc
    val = app.messageW.ui.message.toPlainText()
    assert val.endswith('test_mountwizzard\n')


def test_writeMessage2(qtbot):
    app.messageW.ui.message.setText('')
    suc = app.messageW.writeMessage('test_mountwizzard', 6)
    assert not suc


def test_writeMessage3(qtbot):
    app.messageW.ui.message.setText('')
    suc = app.messageW.writeMessage('', 0)
    assert suc
    val = app.messageW.ui.message.toPlainText()
    assert val.endswith('\n')


def test_writeMessage4(qtbot):
    app.messageW.ui.message.setText('')
    suc = app.messageW.writeMessage('test_mountwizzard', -1)
    assert not suc
