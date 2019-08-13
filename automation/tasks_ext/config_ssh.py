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
# defining all necessary virtual client login for building over all platforms
#

# defining environment for ubuntu
clientUbuntu = 'astro-ubuntu.fritz.box'
userUbuntu = 'mw@' + clientUbuntu
workUbuntu = userUbuntu + ':/home/mw/mountwizzard4'

# defining work environment for mate working
clientWork = 'astro-comp.fritz.box'
userWork = 'mw@' + clientWork
workWork = userWork + ':/home/mw/mountwizzard4'

# defining work environment for mate test
clientMate = 'astro-comp.fritz.box'
userMate = 'mw@' + clientMate
workMate = userMate + ':/home/mw/test'

# same for windows10 with cmd.exe as shell
clientWindows = 'astro-windows.fritz.box'
userWindows = 'mw@' + clientWindows
workWindows = userWindows + ':/Users/mw/mountwizzard4'
buildWindows = userWindows + ':/Users/mw/MountWizzard'

# same for mac
clientMAC = 'astro-mac.fritz.box'
userMAC = 'mw@' + clientMAC
workMAC = userMAC + ':/Users/mw/mountwizzard4'
buildMAC = userMAC + ':/Users/mw/MountWizzard'
