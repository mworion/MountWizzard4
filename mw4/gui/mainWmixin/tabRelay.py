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
# Python  v3.6.7
#
# Michael Würtenberger
# (c) 2018
#
# Licence APL2.0
#
###########################################################
# standard libraries
# external packages
# local import


class Relay(object):
    """
    the main window class handles the main menu as well as the show and no show part of
    any other window. all necessary processing for functions of that gui will be linked
    to this class. therefore window classes will have a threadpool for managing async
    processing if needed.
    """

    def __init__(self):
        self.app.relay.statusReady.connect(self.updateRelayGui)

    def initConfig(self):
        # config = self.app.config['mainW']
        return True

    def storeConfig(self):
        # config = self.app.config['mainW']
        return True

    def setupIcons(self):
        """
        setupIcons add icon from standard library to certain buttons for improving the
        gui of the app.

        :return:    True if success for test
        """
        return True

    def clearGUI(self):
        """
        clearGUI rewrites the gui in case of a special event needed for clearing up

        :return: success for test
        """
        return True

    def updateRelayGui(self):
        """
        updateRelayGui changes the style of the button related to the state of the relay

        :return: success for test
        """

        for status, button in zip(self.app.relay.status, self.relayButtons):
            if status:
                self.changeStyleDynamic(button, 'running', 'true')
            else:
                self.changeStyleDynamic(button, 'running', 'false')
        return True

'''
WEATHER_TEMPERATURE 20.3
WEATHER_HUMIDITY 38.0
WEATHER_DEWPOINT 5.5
DEW_A 0.0
DEW_B 0.0
POWER_CURRENT_1 0.5275
POWER_CURRENT_2 0.0
POWER_CURRENT_3 0.0
POWER_CURRENT_4 0.0
DEW_CURRENT_A 0.0
DEW_CURRENT_B 0.0
CONSUMPTION_AVG_AMPS 0.28
CONSUMPTION_AMP_HOURS 0.0
CONSUMPTION_WATT_HOURS 0.01
FOCUS_ABSOLUTE_POSITION -1.0
CONSUMPTION_AVG_AMPS 0.28
CONSUMPTION_AMP_HOURS 0.0
CONSUMPTION_WATT_HOURS 0.01
CONSUMPTION_AVG_AMPS 0.28
CONSUMPTION_AMP_HOURS 0.0
CONSUMPTION_WATT_HOURS 0.01
'''