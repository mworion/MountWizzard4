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
# building mac dmg
#


@task(pre=[])
def mac(c):
    printMW('build mac dmg')
    with c.cd('images'):
        runMW(c, f'scp drive_mw4.icns {buildMAC}')
        runMW(c, f'scp dmg_background.png {buildMAC}')
    with c.cd('remote_scripts/mac'):
        runMW(c, f'scp dmg_settings.py {buildMAC}')
        runMW(c, f'scp "MW Home.webloc" {buildMAC}')
        runMW(c, f'scp "MW Docu.webloc" {buildMAC}')
        runMW(c, f'ssh {userMAC} < build_mac_dmg.sh')
    with c.cd('..'):
        runMW(c, f'scp {buildMAC}/dist/MountWizzard4.dmg .')
