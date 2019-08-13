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
# doing all the testing stuff
#


@task()
def test_mountcontrol(c):
    printMW('testing mountcontrol')
    with c.cd('../mountcontrol'):
        runMW(c, 'flake8')
        runMW(c, 'pytest mountcontrol/test/test_units --cov-config tox.ini --cov mountcontrol/')


@task()
def test_indibase(c):
    printMW('testing indibase')
    with c.cd('../indibase'):
        runMW(c, 'flake8')
        runMW(c, 'pytest indibase/test/test_units --cov-config .coveragerc --cov mw4/')


@task(pre=[resource, widgets])
def test_mountwizzard(c):
    printMW('testing mountwizzard')
    runMW(c, 'flake8')
    runMW(c, 'pytest mw4/test/test_units --cov-config .coveragerc --cov mw4/')
