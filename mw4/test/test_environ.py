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
from unittest import mock
# external packages
import PyQt5.QtWidgets
# local import
from mw4.environ import environ

test = PyQt5.QtWidgets.QApplication([])
host_ip = '192.168.2.14'




'''
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

    with mock.patch.object(relay,
                           'getRelay',
                           return_value=returnValue):

        for i in range(0, 9):
            relay.pulse(i)

        with qtbot.waitSignal(relay.statusReady) as blocker:
            relay.cyclePolling()
    assert [0, 0, 0, 0, 0, 0, 0, 0] == relay.status
'''