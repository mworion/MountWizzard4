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
# start deploying the final apps and distributions for first test run on target
# platform. it starts th app with 'test' parameter -> this end the app after 3 sec
#


@task(pre=[])
def ubuntu(c):
    printMW('deploy ubuntu dist')
    runMW(c, f'ssh {userUbuntu} rm -rf mountwizzard4')
    runMW(c, f'ssh {userUbuntu} mkdir mountwizzard4')
    # copy necessary files
    with c.cd('..'):
        runMW(c, f'scp dist/indibase.tar.gz {workUbuntu}/indibase.tar.gz')
        runMW(c, f'scp dist/mountcontrol.tar.gz {workUbuntu}/mountcontrol.tar.gz')
        runMW(c, f'scp dist/mountwizzard4.tar.gz {workUbuntu}/mountwizzard4.tar.gz')
    with c.cd('remote_scripts/ubuntu'):
        runMW(c, f'scp start_ubuntu.sh {workUbuntu}')
        runMW(c, f'ssh {userUbuntu} < install_dist_ubuntu.sh')


@task(pre=[])
def mate(c):
    printMW('deploy mate dist')
    runMW(c, f'ssh {userMate} rm -rf test')
    runMW(c, f'ssh {userMate} mkdir test')
    # copy necessary files
    with c.cd('..'):
        runMW(c, f'scp dist/ib.tar.gz {workWork}/indibase.tar.gz')
        runMW(c, f'scp dist/mountcontrol.tar.gz {workWork}/mountcontrol.tar.gz')
        runMW(c, f'scp dist/mountwizzard4.tar.gz {workWork}/mountwizzard4.tar.gz')
    with c.cd('images'):
        runMW(c, f'scp mw4.png {workWork}')
    with c.cd('remote_scripts/ubuntu'):
        runMW(c, f'scp MountWizzard4.desktop {workMate}')
        runMW(c, f'ssh {userMate} < install_dist_mate.sh')


@task(pre=[])
def work(c):
    printMW('deploy work dist')
    # copy necessary files
    with c.cd('..'):
        runMW(c, f'scp dist/indibase.tar.gz {workWork}/indibase.tar.gz')
        runMW(c, f'scp dist/mountcontrol.tar.gz {workWork}/mountcontrol.tar.gz')
        runMW(c, f'scp dist/mountwizzard4.tar.gz {workWork}/mountwizzard4.tar.gz')
    # run the
    with c.cd('images'):
        runMW(c, f'scp mw4.png {workWork}')
    with c.cd('remote_scripts/work'):
        runMW(c, f'scp MountWizzard4.desktop {userWork}:.local/share/applications')
        runMW(c, f'ssh {userWork} < install_dist_work.sh')
        runMW(c, f'scp start_work.sh {userWork}')
    runMW(c, f'ssh {userWork} chmod 777 ./mountwizzard4/start_work.sh')
    runMW(c, f'ssh {userWork} rm -rf ./mountwizzard4/*.tar.gz')


@task(pre=[])
def windows(c):
    printMW('deploy windows dist')
    runMW(c, f'ssh {userWindows} "if exist mountwizzard4 (rmdir /s/q mountwizzard4)"')
    runMW(c, f'ssh {userWindows} "mkdir mountwizzard4"')
    with c.cd('..'):
        runMW(c, f'scp dist/indibase.tar.gz {userWindows}/indibase.tar.gz')
        runMW(c, f'scp dist/mountcontrol.tar.gz {userWindows}/mountcontrol.tar.gz')
        runMW(c, f'scp dist/mountwizzard4.tar.gz {userWindows}/mountwizzard4.tar.gz')
    with c.cd('remote_scripts/windows'):
        runMW(c, f'ssh {userWindows} < install_dist_windows.bat')


@task(pre=[])
def macMojave(c):
    printMW('deploy mac dist')
    runMW(c, f'ssh {userMojave} rm -rf mountwizzard4')
    runMW(c, f'ssh {userMojave} mkdir mountwizzard4')
    # copy necessary files
    with c.cd('..'):
        runMW(c, f'scp dist/indibase.tar.gz {userMojave}/indibase.tar.gz')
        runMW(c, f'scp dist/mountcontrol.tar.gz {userMojave}/mountcontrol.tar.gz')
        runMW(c, f'scp dist/mountwizzard4.tar.gz {userMojave}/mountwizzard4.tar.gz')

    # run the installation
    with c.cd('remote_scripts/mac'):
        runMW(c, f'ssh {userMojave} < install_dist_mac.sh')


@task(pre=[])
def macCatalina(c):
    printMW('deploy mac dist')
    runMW(c, f'ssh {userCatalina} rm -rf mountwizzard4')
    runMW(c, f'ssh {userCatalina} mkdir mountwizzard4')
    # copy necessary files
    with c.cd('..'):
        runMW(c, f'scp dist/indibase.tar.gz {workCatalina}/indibase.tar.gz')
        runMW(c, f'scp dist/mountcontrol.tar.gz {workCatalina}/mountcontrol.tar.gz')
        runMW(c, f'scp dist/mountwizzard4.tar.gz {workCatalina}/mountwizzard4.tar.gz')

    # run the installation
    with c.cd('remote_scripts/mac'):
        runMW(c, f'ssh {userCatalina} < install_dist_mac.sh')
