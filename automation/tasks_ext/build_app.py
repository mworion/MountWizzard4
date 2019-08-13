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
# building the apps based on pyinstaller packages
#


@task(pre=[])
def build_windows_app(c):
    printMW('build windows app and exe')
    # preparing the directories
    runMW(c, 'rm -rf ./dist/*.exe')
    runMW(c, f'ssh {userWindows} "if exist MountWizzard (rmdir /s/q MountWizzard)"')
    runMW(c, f'ssh {userWindows} "mkdir MountWizzard"')
    # copy necessary files
    with c.cd('../mountcontrol'):
        runMW(c, f'scp dist/*.tar.gz {buildWindows}/mc.tar.gz')
    with c.cd('../indibase'):
        runMW(c, f'scp dist/*.tar.gz {buildWindows}/ib.tar.gz')
    runMW(c, f'scp dist/*.tar.gz {buildWindows}/mw4.tar.gz')

    runMW(c, f'scp mw4_windows.spec {buildWindows}')
    runMW(c, f'scp mw4_windows_console.spec {buildWindows}')
    with c.cd('remote_scripts'):
        runMW(c, f'scp mw4.ico {buildWindows}')
    # doing the build job
    print('build windows windowed')
    with c.cd('remote_scripts'):
        runMW(c, f'ssh {userWindows} < build_windows.bat')
    runMW(c, f'scp {buildWindows}/dist/MountWizzard4.exe ./dist/')


@task(pre=[])
def build_mac_app_local(c):
    printMW('building mac app local')
    runMW(c, 'rm -rf ./dist/*.app')
    runMW(c, 'rm -rf ./dist/*.dmg')
    runMW(c, 'pip install ../mountcontrol/dist/mountcontrol-*.tar.gz')
    runMW(c, 'pip install ../indibase/dist/indibase-*.tar.gz')
    runMW(c, 'pyinstaller -y mw4_mac_local.spec')


@task(pre=[])
def build_mac_app_local_work(c):
    printMW('building mac app local work')
    runMW(c, 'rm -rf ./dist/*.app')
    runMW(c, 'rm -rf ./dist/*.dmg')
    runMW(c, 'pip install ../mountcontrol/dist/mountcontrol-*.tar.gz')
    runMW(c, 'pip install ../indibase/dist/indibase-*.tar.gz')
    runMW(c, 'pyinstaller -y mw4_mac_local_work.spec')


@task(pre=[])
def build_mac_app(c):
    printMW('build mac app')
    # preparing the directories
    runMW(c, 'rm -rf ./dist/*.app')
    runMW(c, f'ssh {userMAC} rm -rf MountWizzard')
    runMW(c, f'ssh {userMAC} mkdir MountWizzard')
    # copy necessary files
    with c.cd('../mountcontrol'):
        runMW(c, f'scp dist/*.tar.gz {buildMAC}/mc.tar.gz')
    with c.cd('../indibase'):
        runMW(c, f'scp dist/*.tar.gz {buildMAC}/ib.tar.gz')
    runMW(c, f'scp dist/*.tar.gz {buildMAC}/mw4.tar.gz')
    runMW(c, f'scp mw4_mac.spec {buildMAC}')
    with c.cd('remote_scripts'):
        runMW(c, f'scp mw4.icns {buildMAC}')
        runMW(c, f'scp dmg_settings.py {buildMAC}')
        runMW(c, f'scp set_image.py {buildMAC}')
    # doing the build job
    with c.cd('remote_scripts'):
        runMW(c, f'ssh {userMAC} < build_mac.sh')
    runMW(c, f'scp -r {buildMAC}/dist/MountWizzard4.app ./dist')
