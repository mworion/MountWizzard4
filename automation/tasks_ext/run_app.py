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
#
# running build apps on target systems
#


@task(pre=[])
def run_windows_app(c):
    printMW('deploy windows app')
    runMW(c, f'ssh {userWindows} "if exist mountwizzard4 (rmdir /s/q mountwizzard4)"')
    runMW(c, f'ssh {userWindows} "mkdir mountwizzard4"')
    with c.cd('./dist'):
        runMW(c, f'scp MountWizzard4.exe {workWindows}')
    with c.cd('remote_scripts'):
        runMW(c, f'ssh {userWindows} < start_windows_app.bat')


@task(pre=[])
def run_mac_app(c):
    printMW('run mac app')
    runMW(c, f'ssh {userMAC} rm -rf mountwizzard4')
    runMW(c, f'ssh {userMAC} mkdir mountwizzard4')
    # copy necessary files
    with c.cd('./dist'):
        runMW(c, f'scp -r MountWizzard4.app {workMAC}')
    with c.cd('remote_scripts'):
        runMW(c, f'scp -r start_mac_app.sh {workMAC}')
        runMW(c, f'ssh {userMAC} chmod 777 ./mountwizzard4/start_mac_app.sh')
        runMW(c, f'ssh {userMAC} ./mountwizzard4/start_mac_app.sh')
