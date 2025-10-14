############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages

# local imports
from mw4.base.alpacaClass import AlpacaClass


class TelescopeAlpaca(AlpacaClass):
    """ """

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.signals = parent.signals
        self.data = parent.data

    def workerGetInitialConfig(self):
        """
        :return: true for test purpose
        """
        super().workerGetInitialConfig()
        self.getAndStoreAlpacaProperty("aperturediameter", "TELESCOPE_INFO.TELESCOPE_APERTURE")
        self.getAndStoreAlpacaProperty("focallength", "TELESCOPE_INFO.TELESCOPE_FOCAL_LENGTH")
        return True
