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
# running build apps on target systems
#


@task(pre=[])
def windows(c):
    printMW('deploy windows app')
    runMW(c, f'ssh {userWindows} "if exist mountwizzard4 (rmdir /s/q mountwizzard4)"')
    runMW(c, f'ssh {userWindows} "mkdir mountwizzard4"')
    with c.cd('../dist'):
        runMW(c, f'scp MountWizzard4.exe {workWindows}')
    with c.cd('remote_scripts/windows'):
        runMW(c, f'ssh {userWindows} < start_windows_app.bat')


@task(pre=[])
def windowsdbg(c):
    printMW('deploy windows app debug')
    runMW(c, f'ssh {userWindows} "if exist mountwizzard4 (rmdir /s/q mountwizzard4)"')
    runMW(c, f'ssh {userWindows} "mkdir mountwizzard4"')
    with c.cd('../dist'):
        runMW(c, f'scp MountWizzard4-dbg.exe {workWindows}')
    with c.cd('remote_scripts/windows'):
        runMW(c, f'ssh {userWindows} < start_windows_app_dbg.bat')


@task(pre=[])
def mac(c):
    printMW('run mac app')
    runMW(c, f'ssh {userMAC} rm -rf mountwizzard4')
    runMW(c, f'ssh {userMAC} mkdir mountwizzard4')
    # copy necessary files
    with c.cd('../dist'):
        runMW(c, f'scp -r MountWizzard4.app {workMAC}')
    with c.cd('remote_scripts/mac'):
        runMW(c, f'scp -r start_mac_app.sh {workMAC}')
        runMW(c, f'ssh {userMAC} chmod 777 ./mountwizzard4/start_mac_app.sh')
        runMW(c, f'ssh {userMAC} ./mountwizzard4/start_mac_app.sh')
