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
def windows_dbg(c):
    printMW('deploy windows app debug')
    runMW(c, f'ssh {userWindows} "if exist mountwizzard4 (rmdir /s/q mountwizzard4)"')
    runMW(c, f'ssh {userWindows} "mkdir mountwizzard4"')
    with c.cd('../dist'):
        runMW(c, f'scp MountWizzard4-dbg.exe {workWindows}')
    with c.cd('remote_scripts/windows'):
        runMW(c, f'ssh {userWindows} < start_windows_app_dbg.bat')


@task(pre=[])
def macMojave(c):
    printMW('run mac app')
    runMW(c, f'ssh {userMojave} rm -rf mountwizzard4')
    runMW(c, f'ssh {userMojave} mkdir mountwizzard4')
    # copy necessary files
    with c.cd('../dist'):
        runMW(c, f'scp -r MountWizzard4.app {workMojave}')
    with c.cd('remote_scripts/mac'):
        runMW(c, f'scp -r start_mac_app.sh {workMojave}')
        runMW(c, f'ssh {userMojave} chmod 777 ./mountwizzard4/start_mac_app.sh')
        runMW(c, f'ssh {userMojave} ./mountwizzard4/start_mac_app.sh')


@task(pre=[])
def macCatalina(c):
    printMW('run mac app')
    runMW(c, f'ssh {userCatalina} rm -rf mountwizzard4')
    runMW(c, f'ssh {userCatalina} mkdir mountwizzard4')
    # copy necessary files
    with c.cd('../dist'):
        runMW(c, f'scp -r MountWizzard4.app {workCatalina}')
    with c.cd('remote_scripts/mac'):
        runMW(c, f'scp -r start_mac_app.sh {workCatalina}')
        runMW(c, f'ssh {userCatalina} chmod 777 ./mountwizzard4/start_mac_app.sh')
        runMW(c, f'ssh {userCatalina} ./mountwizzard4/start_mac_app.sh')
