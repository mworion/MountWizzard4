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
    printMW('uploading dist mountcontrol')
    with c.cd('../dist'):
        runMW(c, 'twine upload mountcontrol.tar.gz -r pypi')


@task(pre=[])
def indibase(c):
    printMW('uploading dist indibase')
    with c.cd('../dist'):
        runMW(c, 'twine upload indibase.tar.gz -r pypi')


@task(pre=[])
def mountwizzard(c):
    printMW('uploading dist mountwizzard4')
    with c.cd('../dist'):
        runMW(c, 'twine upload mountwizzard4.tar.gz -r pypi')
