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
import unittest.mock as mock
import sys
import pytest
import astropy
import platform

# external packages
from PySide6.QtWidgets import QWidget

# local import
from mw4.update import UpdateGUI, Update
from base.loggerMW import setupLogging

setupLogging()


@pytest.fixture(autouse=True, scope='module')
def app():
    with mock.patch.object(QWidget,
                           'show'):
        with mock.patch.object(sys,
                               'exit'):
            update = UpdateGUI(runnable='python', version='1.2.3')
            with mock.patch.object(update.app,
                                   'exec'):
                yield update
                update.app.shutdown()
                del update.app


def test_updateGUI_1(app):
    with mock.patch.object(platform,
                           'system',
                           return_value='Windows'):
        app.run()


def test_updateGUI_2(app):
    with mock.patch.object(platform,
                           'system',
                           return_value='Darwin'):
        app.writeText('test', 0)


def test_updateGUI_3(app):
    with mock.patch.object(platform,
                           'system',
                           return_value='Darwin'):
        with mock.patch.object(Update,
                               'restart'):
            app.runCancel()


def test_updateGUI_4(app):
    with mock.patch.object(platform,
                           'system',
                           return_value='Darwin'):
        with mock.patch.object(Update,
                               'restart'):
            with mock.patch.object(Update,
                                   'runInstall',
                                   return_value=False):
                app.runUpdate()


def test_updateGUI_5(app):
    with mock.patch.object(platform,
                           'system',
                           return_value='Darwin'):
        with mock.patch.object(Update,
                               'restart'):
            with mock.patch.object(Update,
                                   'runInstall',
                                   return_value=True):
                app.runUpdate()
