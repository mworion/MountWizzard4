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
# external packages
import PyQt5.QtWidgets
# local import
from mw4.relay import kmRelay

test = PyQt5.QtWidgets.QApplication([])


#
#
# testing relay connections
#
#


def test_connect1(qtbot):
    host = ('192.168.2.14', 80)
    relay = kmRelay.KMRelay(host)
    relay.user = 'astro'
    relay.password = 'astro'
    value =relay.geturl('/status.xml')

    assert len(value)


def test_connect2(qtbot):
    host = ('192.168.2.14', 80)
    relay = kmRelay.KMRelay(host)
    relay.user = 'astro'
    relay.password = ''
    value = relay.geturl('/status.xml')

    assert value.startswith('401 Unauthorized:')


def test_connect3(qtbot):
    host = ('192.168.2.14', 80)
    relay = kmRelay.KMRelay(host)
    relay.user = ''
    relay.password = 'astro'
    value = relay.geturl('/status.xml')

    assert value.startswith('401 Unauthorized:')


def test_connect4(qtbot):
    host = ('192.168.2.14', 8)
    relay = kmRelay.KMRelay(host)
    relay.user = ''
    relay.password = ''
    value = relay.geturl('/status.xml')

    assert value is None


def test_connect5(qtbot):
    host = ('192.168.2.255', 80)
    relay = kmRelay.KMRelay(host)
    relay.user = ''
    relay.password = ''
    value = relay.geturl('/status.xml')

    assert value is None


#
#
# testing relay values
#
#

host = ('192.168.2.14', 80)


def test_connect(qtbot):
    relay = kmRelay.KMRelay(host)
    relay.user = 'astro'
    relay.password = 'astro'

    with qtbot.waitSignal(relay.statusReady) as blocker:
        relay.cyclePolling()
    assert [0, 0, 0, 1, 0, 0, 0, 0] == relay.status
