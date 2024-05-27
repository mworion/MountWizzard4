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
import pytest
from unittest import mock

# external packages

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.utilities.toolsQtWidget import MWidget
from gui.widgets.main_ui import Ui_MainWindow
from gui.mainWmixin.tabSett_Dome import SettDome
from resource import resources
resources.qInitResources()


@pytest.fixture(autouse=True, scope='function')
def function(qapp):
    class Mixin(MWidget, SettDome):
        def __init__(self):
            super().__init__()
            self.app = App()
            self.msg = self.app.msg
            self.deviceStat = self.app.deviceStat
            self.ui = Ui_MainWindow()
            self.ui.setupUi(self)
            SettDome.__init__(self)

    window = Mixin()
    yield window


def test_tab1(function):
    function.tab1()


def test_tab2(function):
    function.tab2()


def test_tab3(function):
    function.tab3()


def test_tab4(function):
    function.tab4()


def test_tab5(function):
    function.tab5()


def test_tab6(function):
    function.tab6()


def test_tab7(function):
    function.tab7()


def test_tab8(function):
    function.tab8()


def test_tab9(function):
    function.tab9()


def test_initConfig_1(function):
    function.app.config['mainW'] = {}
    with mock.patch.object(function,
                           'setupIconsDome'):
        with mock.patch.object(function,
                               'setUseGeometry'):
            suc = function.initConfig()
            assert suc


def test_initConfig_2(function):
    with mock.patch.object(function,
                           'setupIconsDome'):
        with mock.patch.object(function,
                               'setUseGeometry'):
            suc = function.initConfig()
            assert suc


def test_storeConfig_1(function):
    suc = function.storeConfig()
    assert suc


def test_setupIconsDome_1(function):
    function.ui.use10micronDef.setChecked(True)
    suc = function.setupIconsDome()
    assert suc


def test_setupIconsDome_2(function):
    function.ui.use10micronDef.setChecked(False)
    suc = function.setupIconsDome()
    assert suc


def test_switchGeometryDefinition_1(function):
    function.ui.use10micronDef.setChecked(True)
    suc = function.switchGeometryDefinition()
    assert suc


def test_switchGeometryDefinition_2(function):
    function.ui.use10micronDef.setChecked(False)
    suc = function.switchGeometryDefinition()
    assert suc


def test_setUseGeometry_1(function):
    function.ui.use10micronDef.setChecked(False)
    function.ui.automaticDome.setChecked(False)
    suc = function.setUseGeometry()
    assert suc


def test_setUseGeometry_2(function):
    function.ui.use10micronDef.setChecked(True)
    function.ui.automaticDome.setChecked(True)
    with mock.patch.object(function,
                           'updateDomeGeometryToGui'):
        suc = function.setUseGeometry()
        assert suc


def test_updateDomeGeometry_1(function):
    suc = function.updateDomeGeometryToGui()
    assert suc


def test_setDomeSettlingTime_1(function):
    suc = function.setDomeSettlingTime()
    assert suc
