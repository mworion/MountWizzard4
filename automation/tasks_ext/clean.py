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
# cleaning the caches before new build
#


@task
def clean_mountwizzard(c):
    printMW('clean mountwizzard')
    runMW(c, 'rm -rf .pytest_cache')
    runMW(c, 'rm -rf mw4.egg-info')
    runMW(c, 'find ./mw4 | grep -E "(__pycache__)" | xargs rm -rf')


@task
def clean_mountcontrol(c):
    printMW('clean mountcontrol')
    with c.cd('../mountcontrol'):
        runMW(c, 'rm -rf .pytest_cache')
        runMW(c, 'rm -rf mountcontrol.egg-info')
        runMW(c, 'rm -rf ./build/*')
        runMW(c, 'find ./mountcontrol | grep -E "(__pycache__)" | xargs rm -rf')


@task
def clean_indibase(c):
    printMW('clean indibase')
    with c.cd('../indibase'):
        runMW(c, 'rm -rf .pytest_cache')
        runMW(c, 'rm -rf indibase.egg-info')
        runMW(c, 'find ./indibase | grep -E "(__pycache__)" | xargs rm -rf')
