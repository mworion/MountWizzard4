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
# start deploying the final apps and distributions for first test run on target
# platform. it starts th app with 'test' parameter -> this end the app after 3 sec
#


@task(pre=[])
def deploy_ubuntu_dist(c):
    printMW('deploy ubuntu dist')
    runMW(c, f'ssh {userUbuntu} rm -rf mountwizzard4')
    runMW(c, f'ssh {userUbuntu} mkdir mountwizzard4')
    # copy necessary files
    with c.cd('../mountcontrol'):
        runMW(c, f'scp dist/*.tar.gz {workUbuntu}/mc.tar.gz')
    with c.cd('../indibase'):
        runMW(c, f'scp dist/*.tar.gz {workUbuntu}/ib.tar.gz')
    runMW(c, f'scp dist/*.tar.gz {workUbuntu}/mw4.tar.gz')
    with c.cd('remote_scripts'):
        runMW(c, f'scp start_ubuntu.sh {workUbuntu}')
        runMW(c, f'ssh {userUbuntu} < install_dist_ubuntu.sh')


@task(pre=[])
def deploy_mate_dist(c):
    printMW('deploy mate dist')
    runMW(c, f'ssh {userMate} rm -rf test')
    runMW(c, f'ssh {userMate} mkdir test')
    # copy necessary files
    with c.cd('../mountcontrol'):
        runMW(c, f'scp dist/*.tar.gz {workMate}/mc.tar.gz')
    with c.cd('../indibase'):
        runMW(c, f'scp dist/*.tar.gz {workMate}/ib.tar.gz')
    runMW(c, f'scp dist/*.tar.gz {workMate}/mw4.tar.gz')

    with c.cd('remote_scripts'):
        runMW(c, f'scp MountWizzard4.desktop {workMate}')
        runMW(c, f'scp mw4.png {workMate}')
        runMW(c, f'ssh {userMate} < install_dist_mate.sh')


@task(pre=[])
def deploy_work_dist(c):
    printMW('deploy work dist')
    # copy necessary files
    with c.cd('../mountcontrol'):
        runMW(c, f'scp dist/*.tar.gz {workWork}/mc.tar.gz')
    with c.cd('../indibase'):
        runMW(c, f'scp dist/*.tar.gz {workWork}/ib.tar.gz')
    runMW(c, f'scp dist/*.tar.gz {workWork}/mw4.tar.gz')

    # run the
    with c.cd('remote_scripts'):
        runMW(c, f'scp MountWizzard4.desktop {userWork}:.local/share/applications')
        runMW(c, f'scp mw4.png {workWork}')
        runMW(c, f'ssh {userWork} < install_dist_work.sh')
        runMW(c, f'scp start_work.sh {userWork}')
    runMW(c, f'ssh {userWork} chmod 777 ./mountwizzard4/start_work.sh')
    runMW(c, f'ssh {userWork} rm -rf ./mountwizzard4/*.tar.gz')


@task(pre=[])
def deploy_windows_dist(c):
    printMW('deploy windows dist')
    runMW(c, f'ssh {userWindows} "if exist mountwizzard4 (rmdir /s/q mountwizzard4)"')
    runMW(c, f'ssh {userWindows} "mkdir mountwizzard4"')
    with c.cd('../mountcontrol'):
        runMW(c, f'scp dist/*.tar.gz {workWindows}/mc.tar.gz')
    with c.cd('../indibase'):
        runMW(c, f'scp dist/*.tar.gz {workWindows}/ib.tar.gz')
    runMW(c, f'scp dist/*.tar.gz {workWindows}/mw4.tar.gz')
    with c.cd('remote_scripts'):
        runMW(c, f'ssh {userWindows} < install_dist_windows.bat')


@task(pre=[venv_mac])
def deploy_mac_dist(c):
    printMW('deploy mac dist')
    runMW(c, f'ssh {userMAC} rm -rf mountwizzard4')
    runMW(c, f'ssh {userMAC} mkdir mountwizzard4')
    # copy necessary files
    with c.cd('../mountcontrol'):
        runMW(c, f'scp dist/*.tar.gz {workMAC}/mc.tar.gz')
    with c.cd('../indibase'):
        runMW(c, f'scp dist/*.tar.gz {workMAC}/ib.tar.gz')
    runMW(c, f'scp dist/*.tar.gz {workMAC}/mw4.tar.gz')

    # run the installation
    with c.cd('remote_scripts'):
        runMW(c, f'ssh {userMAC} < install_dist_mac.sh')
