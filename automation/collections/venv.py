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
# setting up python virtual environments in all platforms for defined context
#


@task()
def ubuntu(c):
    printMW('generating new venv ubuntu')
    with c.cd('remote_scripts/ubuntu'):
        runMW(c, f'ssh {userUbuntu} < setup_ubuntu.sh')


@task()
def windows(c):
    printMW('generating new venv windows')
    with c.cd('remote_scripts/windows'):
        runMW(c, f'ssh {userWindows} < setup_windows.bat')


@task()
def macMojave(c):
    printMW('generating new venv mac')
    with c.cd('remote_scripts/mac'):
        runMW(c, f'ssh {userMojave} < setup_mac.sh')


@task()
def macCatalina(c):
    printMW('generating new venv mac')
    with c.cd('remote_scripts/mac'):
        runMW(c, f'ssh {userCatalina} < setup_mac.sh')


@task()
def mac_local(c):
    printMW('generating new test venv mac')
    with c.cd('/Users/mw/PycharmProjects'):
        runMW(c, 'rm -rf venv_test')
        runMW(c, 'virtualenv venv_test -p python3.7')
        runMW(c, 'source venv_test/bin/activate; pip install mw4 --no-cache-dir --upgrade')


@task()
def work(c):
    printMW('generating new venv work')
    with c.cd('remote_scripts/work'):
        runMW(c, f'ssh {userWork} < setup_work.sh')
