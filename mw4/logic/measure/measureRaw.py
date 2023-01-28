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
# written in python3, (c) 2019-2023 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import logging

# external packages
import PyQt5

# local imports


class MeasureDataRaw(PyQt5.QtCore.QObject):
    """
    the class MeasureData inherits all information and handling of data management and
    storage

        >>> measure = MeasureDataRaw(
        >>>             app=None,
        >>>             parent=None,
        >>>             data=None,
        >>>                 )
    """

    __all__ = ['MeasureDataRaw',
               ]

    log = logging.getLogger(__name__)

    # update rate to 1 seconds for setting indi server
    CYCLE_UPDATE_TASK = 1000
    # maximum size of measurement task
    MAXSIZE = 24 * 60 * 60

    def __init__(self, app=None, parent=None, data=None):
        super().__init__()

        self.app = app
        self.parent = parent
        self.data = data
        self.deviceName = 'RAW'
        self.defaultConfig = {
            'raw': {
                'deviceName': 'display only',
            }
        }

    # time for measurement
        self.timerTask = PyQt5.QtCore.QTimer()
        self.timerTask.setSingleShot(False)
        self.timerTask.timeout.connect(self.measureTask)

    def startCommunication(self):
        """
        startCommunication starts cycling of the polling.
        :return: True for test purpose
        """

        self.parent.setEmptyData()
        self.timerTask.start(self.CYCLE_UPDATE_TASK)

        return True

    def stopCommunication(self):
        """
        stopCommunication stops the devices

        :return: true for test purpose
        """

        self.timerTask.stop()
        return True

    def measureTask(self):
        """
        measureTask runs all necessary pre processing and collecting task to assemble a
        large dict of lists, where all measurement data is stored. the intention later on
        would be to store and export this data.
        the time object is related to the time held in mount computer and is in utc timezone.

        data sources are:
            environment
            mount pointing position

        :return: success
        """

        suc = self.parent.measureTask()

        return suc
