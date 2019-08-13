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
# building the components
#


@task(pre=[])
def build_mountcontrol(c):
    printMW('building dist mountcontrol')
    with c.cd('../mountcontrol'):
        runMW(c, 'rm -f dist/*.tar.gz')
        runMW(c, 'python setup.py sdist')


@task(pre=[])
def build_indibase(c):
    printMW('building dist indibase')
    with c.cd('../indibase'):
        runMW(c, 'rm -f dist/*.tar.gz')
        runMW(c, 'python setup.py sdist')


@task(pre=[resource, widgets])
def build_mountwizzard(c):
    printMW('building dist mountwizzard4')
    runMW(c, 'rm -f dist/*.tar.gz')
    runMW(c, 'python setup.py sdist')
