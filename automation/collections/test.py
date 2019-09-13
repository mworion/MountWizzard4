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
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
import sys
sys.path.append('/Users/mw/PycharmProjects/MountWizzard4')
from invoke import task, context
from automation.collections.gui import printMW, runMW
from automation.collections.config_ssh import *
#
# doing all the testing stuff
#


@task()
def mountcontrol(c):
    printMW('testing mountcontrol')
    with c.cd('../../mountcontrol'):
        runMW(c, 'flake8')
        runMW(c, 'pytest mountcontrol/test/test_units --cov-config tox.ini --cov mountcontrol/')


@task()
def indibase(c):
    printMW('testing indibase')
    with c.cd('../../indibase'):
        runMW(c, 'flake8')
        runMW(c, 'pytest indibase/test/test_units --cov-config .coveragerc --cov mw4/')


@task()
def mountwizzard(c):
    printMW('testing mountwizzard')
    with c.cd('..'):
        runMW(c, 'flake8')
        runMW(c, 'pytest mw4/test/test_units --cov-config .coveragerc --cov mw4/')
