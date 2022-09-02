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
# written in python3, (c) 2019-2022 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages

# local import


class Relay(object):
    """
    """

    def __init__(self):
        self.app.relay.signals.statusReady.connect(self.updateRelayGui)

    def updateRelayGui(self):
        """
        updateRelayGui changes the style of the button related to the state of the relay

        :return: success for test
        """

        for status, button in zip(self.app.relay.status, self.relayButtons):
            if status:
                self.changeStyleDynamic(button, 'running', True)
            else:
                self.changeStyleDynamic(button, 'running', False)
        return True
