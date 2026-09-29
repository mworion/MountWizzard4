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
# written in python3, (c) 2019-2026 by mworion
# License APL2.0
#
###########################################################
import pytest
from mw4.base.appProtocol import AppProtocol
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="module")
def app(qapp):
    testApp = App()
    yield testApp
    testApp.shutdown()


def test_stubSatisfiesProtocol(app):
    assert isinstance(app, AppProtocol)


def test_objectDoesNotSatisfyProtocol():
    assert not isinstance(object(), AppProtocol)


def test_missingMemberFailsProtocol(app):
    class Partial:
        pass

    partial = Partial()
    for name in ("dReg", "config", "timeMgr", "msg", "threadPool"):
        setattr(partial, name, getattr(app, name))
    assert not isinstance(partial, AppProtocol)


def test_protocolMembers():
    members = AppProtocol.__protocol_attrs__
    for name in ("dReg", "config", "msg", "initConfig", "storeConfig", "MAX_THREAD_COUNT"):
        assert name in members
    for name in ("mount", "relay", "measure", "deviceStat", "application"):
        assert name not in members
