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
# building the apps based on pyinstaller packages
#


@task(pre=[])
def windows(c):
    printMW('build windows app and exe')
    with c.cd('..'):
        runMW(c, 'rm -rf ./dist/MountWizzard4.exe')
    runMW(c, f'ssh {userWindows} "if exist MountWizzard (rmdir /s/q MountWizzard)"')
    runMW(c, f'ssh {userWindows} "mkdir MountWizzard"')
    with c.cd('..'):
        runMW(c, f'scp dist/ib.tar.gz {buildWindows}/ib.tar.gz')
        runMW(c, f'scp dist/mc.tar.gz {buildWindows}/mc.tar.gz')
        runMW(c, f'scp dist/mw4.tar.gz {buildWindows}/mw4.tar.gz')
    with c.cd('remote_scripts/windows'):
        runMW(c, f'scp mw4_windows.spec {buildWindows}')
    with c.cd('images'):
        runMW(c, f'scp mw4.ico {buildWindows}')
    with c.cd('remote_scripts/windows'):
        runMW(c, f'ssh {userWindows} < build_windows.bat')
    with c.cd('../dist'):
        runMW(c, f'scp {buildWindows}/dist/MountWizzard4.exe .')


@task(pre=[])
def windows_dbg(c):
    printMW('build windows app and exe debug')
    with c.cd('..'):
        runMW(c, 'rm -rf ./dist/MountWizzard4-dbg.exe')
    runMW(c, f'ssh {userWindows} "if exist MountWizzard (rmdir /s/q MountWizzard)"')
    runMW(c, f'ssh {userWindows} "mkdir MountWizzard"')
    with c.cd('..'):
        runMW(c, f'scp dist/ib.tar.gz {buildWindows}/ib.tar.gz')
        runMW(c, f'scp dist/mc.tar.gz {buildWindows}/mc.tar.gz')
        runMW(c, f'scp dist/mw4.tar.gz {buildWindows}/mw4.tar.gz')
    with c.cd('remote_scripts/windows'):
        runMW(c, f'scp mw4_windows_dbg.spec {buildWindows}')
    with c.cd('images'):
        runMW(c, f'scp mw4.ico {buildWindows}')
    with c.cd('remote_scripts/windows'):
        runMW(c, f'ssh {userWindows} < build_windows_dbg.bat')
    with c.cd('../dist'):
        runMW(c, f'scp {buildWindows}/dist/MountWizzard4-dbg.exe .')


@task(pre=[])
def mac_local(c):
    printMW('building mac app local')
    with c.cd('..'):
        runMW(c, 'rm -rf dist/*.app')
        runMW(c, 'rm -rf dist/*.dmg')
    with c.cd('../../mountcontrol'):
        runMW(c, 'pip install dist/mountcontrol-*.tar.gz')
    with c.cd('../../indibase'):
        runMW(c, 'pip install dist/indibase-*.tar.gz')
    with c.cd('images'):
        runMW(c, 'scp mw4.icns /Users/mw/PycharmProjects/MountWizzard4')
    with c.cd('remote_scripts/mac'):
        runMW(c, 'cp mw4_mac_local.spec /Users/mw/PycharmProjects/MountWizzard4')
    with c.cd('..'):
        runMW(c, 'pyinstaller -y mw4_mac_local.spec')


@task()
def sign(c):
    with c.cd('../dist'):
        printMW('signing')
        command = "codesign --deep --force --verbose=4"
        command += " --sign 'Mac Developer: Michael Wuertenberger (2M9FQU8X23)'"
        command += " MountWizzard4.app"
        runMW(c, command)

        printMW('make it online')
        command = "xattr -w com.apple.quarantine"
        command += "'0081;5a37dc6a;Google Chrome;F15F7E1C-F894-4B7D-91B4-E110D11C4858"
        command += " MountWizzard4.app"
        printMW('verify')
        command = "codesign --verify --verbose=4 "
        command += "MountWizzard4.app"
        runMW(c, command)


@task(pre=[], post=[sign])
def macMojave(c):
    printMW('build mac app')
    with c.cd('..'):
        runMW(c, 'rm -rf ./dist/*.app')
    runMW(c, f'ssh {userMojave} rm -rf MountWizzard')
    runMW(c, f'ssh {userMojave} mkdir MountWizzard')
    with c.cd('..'):
        runMW(c, f'scp dist/ib.tar.gz {buildMojave}/ib.tar.gz')
        runMW(c, f'scp dist/mc.tar.gz {buildMojave}/mc.tar.gz')
        runMW(c, f'scp dist/mw4.tar.gz {buildMojave}/mw4.tar.gz')
    with c.cd('images'):
        runMW(c, f'scp mw4.icns {buildMojave}')
    with c.cd('remote_scripts/mac'):
        runMW(c, f'scp mw4_mac.spec {buildMojave}')
        runMW(c, f'scp dmg_settings.py {buildMojave}')
        runMW(c, f'scp set_image.py {buildMojave}')
        runMW(c, f'ssh {userMojave} < build_mac.sh')
    with c.cd('../dist'):
        runMW(c, f'scp -r {buildMojave}/dist/MountWizzard4.app .')


@task(pre=[], post=[sign])
def macCatalina(c):
    printMW('build mac app')
    with c.cd('..'):
        runMW(c, 'rm -rf ./dist/*.app')
    runMW(c, f'ssh {userCatalina} rm -rf MountWizzard')
    runMW(c, f'ssh {userCatalina} mkdir MountWizzard')
    with c.cd('..'):
        runMW(c, f'scp dist/ib.tar.gz {buildCatalina}/ib.tar.gz')
        runMW(c, f'scp dist/mc.tar.gz {buildCatalina}/mc.tar.gz')
        runMW(c, f'scp dist/mw4.tar.gz {buildCatalina}/mw4.tar.gz')
    with c.cd('images'):
        runMW(c, f'scp mw4.icns {buildCatalina}')
    with c.cd('remote_scripts/mac'):
        runMW(c, f'scp mw4_mac.spec {buildCatalina}')
        runMW(c, f'scp dmg_settings.py {buildCatalina}')
        runMW(c, f'scp set_image.py {buildCatalina}')
        runMW(c, f'ssh {userCatalina} < build_mac.sh')
    with c.cd('../dist'):
        runMW(c, f'scp -r {buildCatalina}/dist/MountWizzard4.app .')
