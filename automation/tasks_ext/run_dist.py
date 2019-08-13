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
# run dists on targets for test
#


@task(pre=[])
def run_mac_dist(c):
    printMW('run mac dist')
    with c.cd('remote_scripts'):
        runMW(c, f'scp start_mac.sh {workMAC}')
    runMW(c, f'ssh {userMAC} chmod 777 ./mountwizzard4/start_mac.sh')
    runMW(c, f'ssh {userMAC} ./mountwizzard4/start_mac.sh')


@task(pre=[])
def run_windows_dist(c):
    printMW('run windows app')
    with c.cd('remote_scripts'):
        runMW(c, f'scp start_windows.bat {workWindows}')
    runMW(c, f'ssh {userWindows} "mountwizzard4\\\\start_windows.bat"')


@task(pre=[])
def run_ubuntu_dist(c):
    printMW('un ubuntu dist')
    with c.cd('remote_scripts'):
        runMW(c, f'scp start_ubuntu.sh {workUbuntu}')
    runMW(c, f'ssh {userUbuntu} chmod 777 ./mountwizzard4/start_ubuntu.sh')
    runMW(c, f'ssh {userUbuntu} ./mountwizzard4/start_ubuntu.sh')


@task(pre=[])
def run_mate_dist(c):
    printMW('run work dist')
    with c.cd('remote_scripts'):
        runMW(c, f'scp start_mate.sh {userMate}')
    runMW(c, f'ssh {userMate} chmod 777 ./test/start_mate.sh')
    runMW(c, f'ssh {userMate} ./test/start_mate.sh')
