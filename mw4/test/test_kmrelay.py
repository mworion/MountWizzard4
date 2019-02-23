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
# Python  v3.6.7
#
# Michael Würtenberger
# (c) 2018
#
# Licence APL2.0
#
###########################################################
# standard libraries
from unittest import mock
# external packages
import PyQt5.QtWidgets
# local import
from mw4.relay import kmRelay
from mw4.test.test_setupQt import setupQt
app, spy, mwGlob, test = setupQt()


host_ip = '192.168.2.14'

#
#
# testing relay connections
#
#


def test_connect1(qtbot):
    host = (host_ip, 80)
    relay = kmRelay.KMRelay(host)
    relay.user = 'astro'
    relay.password = 'astro'
    value = relay.getRelay('/status.xml')

    assert value.reason == 'OK'


def test_connect2(qtbot):
    host = (host_ip, 80)
    relay = kmRelay.KMRelay(host)
    relay.user = 'astro'
    relay.password = ''
    value = relay.getRelay('/status.xml')

    assert value.status_code == 401


def test_connect3(qtbot):
    host = (host_ip, 80)
    relay = kmRelay.KMRelay(host)
    relay.user = ''
    relay.password = 'astro'
    value = relay.getRelay('/status.xml')

    assert value.status_code == 401


def test_connect4(qtbot):
    host = (host_ip, 8)
    relay = kmRelay.KMRelay(host)
    relay.user = ''
    relay.password = ''
    value = relay.getRelay('/status.xml')

    assert value is None


def test_connect5(qtbot):
    host = ('192.168.2.255', 80)
    relay = kmRelay.KMRelay(host)
    relay.user = ''
    relay.password = ''
    value = relay.getRelay('/status.xml')

    assert value is None


def test_connect6(qtbot):
    relay = kmRelay.KMRelay(None)
    relay.user = ''
    relay.password = ''
    value = relay.getRelay('/status.xml')

    assert value is None


#
#
# testing relay values integration
#
#


host = (host_ip, 80)


def test_status1(qtbot):
    relay = kmRelay.KMRelay(host)
    relay.user = 'astro'
    relay.password = 'astro'
    returnValue = """<response>
                     <relay0>0</relay0>
                     <relay1>0</relay1>
                     <relay2>0</relay2>
                     <relay3>0</relay3>
                     <relay4>0</relay4>
                     <relay5>0</relay5>
                     <relay6>0</relay6>
                     <relay7>0</relay7>
                     <relay8>0</relay8>
                     </response>"""

    class Test:
        pass
    ret = Test()
    ret.text = returnValue
    ret.reason = 'OK'
    ret.status_code = 200

    with mock.patch.object(relay,
                           'getRelay',
                           return_value=ret):

        for i in range(0, 9):
            relay.set(i, 0)

        with qtbot.waitSignal(relay.statusReady):
            relay.cyclePolling()
        assert [0, 0, 0, 0, 0, 0, 0, 0] == relay.status


def test_status2(qtbot):
    relay = kmRelay.KMRelay(host)
    relay.user = 'astro'
    relay.password = 'astro'
    returnValue = """<response>
                     <relay0>1</relay0>
                     <relay1>1</relay1>
                     <relay2>1</relay2>
                     <relay3>1</relay3>
                     <relay4>1</relay4>
                     <relay5>1</relay5>
                     <relay6>1</relay6>
                     <relay7>1</relay7>
                     <relay8>1</relay8>
                     </response>"""

    class Test:
        pass
    ret = Test()
    ret.text = returnValue
    ret.reason = 'OK'
    ret.status_code = 200

    with mock.patch.object(relay,
                           'getRelay',
                           return_value=ret):

        for i in range(0, 9):
            relay.set(i, 1)

        with qtbot.waitSignal(relay.statusReady):
            relay.cyclePolling()
        assert [1, 1, 1, 1, 1, 1, 1, 1] == relay.status


def test_status3(qtbot):
    relay = kmRelay.KMRelay(host)
    relay.user = 'astro'
    relay.password = 'astro'
    returnValue = """<response>
                     <relay0>1</relay0>
                     <relay1>1</relay1>
                     <relay2>1</relay2>
                     <relay3>1</relay3>
                     <relay4>1</relay4>
                     <relay5>1</relay5>
                     <relay6>1</relay6>
                     <relay7>1</relay7>
                     <relay8>1</relay8>
                     </response>"""

    class Test:
        pass
    ret = Test()
    ret.text = returnValue
    ret.reason = 'OK'
    ret.status_code = 200

    with mock.patch.object(relay,
                           'getRelay',
                           return_value=ret):

        for i in range(0, 9):
            relay.switch(i)

        with qtbot.waitSignal(relay.statusReady):
            relay.cyclePolling()
        assert [1, 1, 1, 1, 1, 1, 1, 1] == relay.status


def test_status4(qtbot):
    relay = kmRelay.KMRelay(host)
    relay.user = 'astro'
    relay.password = 'astro'
    returnValue = """<response>
                     <relay0>0</relay0>
                     <relay1>0</relay1>
                     <relay2>0</relay2>
                     <relay3>0</relay3>
                     <relay4>0</relay4>
                     <relay5>0</relay5>
                     <relay6>0</relay6>
                     <relay7>0</relay7>
                     <relay8>0</relay8>
                     </response>"""

    class Test:
        pass
    ret = Test()
    ret.text = returnValue
    ret.reason = 'OK'
    ret.status_code = 200

    with mock.patch.object(relay,
                           'getRelay',
                           return_value=ret):

        for i in range(0, 9):
            relay.pulse(i)

        with qtbot.waitSignal(relay.statusReady):
            relay.cyclePolling()
    assert [0, 0, 0, 0, 0, 0, 0, 0] == relay.status
