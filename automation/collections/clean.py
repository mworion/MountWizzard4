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
# cleaning the caches before new build
#


@task
def mountwizzard(c):
    printMW('clean mountwizzard')
    runMW(c, 'rm -rf .pytest_cache')
    runMW(c, 'rm -rf mw4.egg-info')
    runMW(c, 'find ./mw4 | grep -E "(__pycache__)" | xargs rm -rf')


@task
def mountcontrol(c):
    printMW('clean mountcontrol')
    with c.cd('../mountcontrol'):
        runMW(c, 'rm -rf .pytest_cache')
        runMW(c, 'rm -rf mountcontrol.egg-info')
        runMW(c, 'rm -rf ./build/*')
        runMW(c, 'find ./mountcontrol | grep -E "(__pycache__)" | xargs rm -rf')


@task
def indibase(c):
    printMW('clean indibase')
    with c.cd('../indibase'):
        runMW(c, 'rm -rf .pytest_cache')
        runMW(c, 'rm -rf indibase.egg-info')
        runMW(c, 'find ./indibase | grep -E "(__pycache__)" | xargs rm -rf')
