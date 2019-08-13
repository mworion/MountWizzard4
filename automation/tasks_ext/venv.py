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
# setting up python virtual environments in all platforms for defined context
#


@task()
def venv_ubuntu(c):
    printMW('preparing ubuntu')
    with c.cd('remote_scripts'):
        runMW(c, f'ssh {userUbuntu} < setup_ubuntu.sh')


@task()
def venv_windows(c):
    printMW('preparing windows')
    with c.cd('remote_scripts'):
        runMW(c, f'ssh {userWindows} < setup_windows.bat')


@task()
def venv_mac(c):
    printMW('preparing mac')
    with c.cd('remote_scripts'):
        runMW(c, f'ssh {userMAC} < setup_mac.sh')


@task()
def venv_work(c):
    printMW('preparing work')
    with c.cd('remote_scripts'):
        runMW(c, f'ssh {userWork} < setup_ubuntu.sh')