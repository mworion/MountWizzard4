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
import logging
# external packages
import PyQt5
# local imports


class MeasureData(PyQt5.QtCore.QObject):
    """
    the class MeasureData inherits all information and handling of environment devices

        >>> mData = MeasureData(
        >>>                 )
    """

    __all__ = ['MeasureData',
               ]

    version = '0.1'
    logger = logging.getLogger(__name__)

    # update rate to 1 seconds for setting indi server
    CYCLE_UPDATE_TASK = 1000

    def __init__(self,
                 app,
                 ):
        super().__init__()
        self.app = app
        self.mData = {
            'time': list(),
            'y': list(),
        }

        self.timerTask = PyQt5.QtCore.QTimer()
        self.timerTask.setSingleShot(False)
        self.timerTask.timeout.connect(self.measureTask)
        self.timerTask.start(self.CYCLE_UPDATE_TASK)

    def measureTask(self):
        obs = self.app.mount.obsSite
        if obs.raJNow is None:
            return
        self.mData['time'].append(obs.timeJD.utc_strftime('%H:%M:%S'))
        self.mData['y'].append(obs.raJNow.hours)

    def clearData(self):
        self.mData['time'] = list()
        self.mData['y'] = list()
