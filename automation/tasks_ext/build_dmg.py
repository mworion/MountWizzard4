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
# building mac dmg
#


@task(pre=[])
def build_mac_dmg(c):
    printMW('build mac dmg')
    with c.cd('remote_scripts'):
        runMW(c, f'scp dmg_settings.py {buildMAC}')
        runMW(c, f'scp drive_mw4.icns {buildMAC}')
    # doing the build job
    with c.cd('remote_scripts'):
        runMW(c, f'ssh {userMAC} < build_mac_dmg.sh')
    runMW(c, f'scp {buildMAC}/dist/MountWizzard4.dmg ./dist')
