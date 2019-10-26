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
# building resource and widgets for qt
#


@task
def resource(c):
    printMW('building resources')
    runMW(c, 'cp ../data/deltat.data ../mw4/resource/deltat.data')
    runMW(c, 'cp ../data/deltat.preds ../mw4/resource/deltat.preds')
    runMW(c, 'cp ../data/Leap_Second.dat ../mw4/resource/Leap_Second.dat')
    resourceDir = '../mw4/resource/'
    runMW(c, f'pyrcc5 -o {resourceDir}resources.py {resourceDir}resources.qrc')


@task
def widgets(c):
    printMW('building widgets')
    widgetDir = '../mw4/gui/widgets/'
    widgets = ['hemisphere', 'image', 'main', 'measure', 'message', 'satellite']
    for widget in widgets:
        name = widgetDir + widget
        runMW(c, f'python -m PyQt5.uic.pyuic -x {name}.ui -o {name}_ui.py')
