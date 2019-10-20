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
from automation.collections.support import *
#
# building the components
#


@task(pre=[])
def mountcontrol(c):
    printMW('building dist mountcontrol')
    with c.cd('../../mountcontrol'):
        runMW(c, 'rm -f dist/*.tar.gz')
        runMW(c, 'python setup.py sdist')
        runMW(c, 'cp dist/mountcontrol*.tar.gz ../MountWizzard4/dist/mountcontrol.tar.gz')


@task(pre=[])
def indibase(c):
    printMW('building dist indibase')
    with c.cd('../../indibase'):
        runMW(c, 'rm -f dist/*.tar.gz')
        runMW(c, 'python setup.py sdist')
        runMW(c, 'cp dist/indibase*.tar.gz ../MountWizzard4/dist/indibase.tar.gz')


@task(pre=[resource, widgets, mountcontrol, indibase])
def mountwizzard(c):
    printMW('building dist mountwizzard4')
    with c.cd('..'):
        runMW(c, 'rm -f dist/mountwizzard4*.tar.gz')
        runMW(c, 'python setup.py sdist')
        runMW(c, 'cp dist/mountwizzard4*.tar.gz ../MountWizzard4/dist/mountwizzard4.tar.gz')
