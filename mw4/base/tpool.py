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
# GUI with PySide for python
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
import sys
import os

# external packages
from PySide6.QtCore import QObject, Signal, QRunnable

# local imports


__all__ = ["Worker"]


class WorkerSignals(QObject):
    """
    The WorkerSignals class offers a list of signals to be used and instantiated
    by the Worker class to get signals for error, finished and result to be
    transferred to the caller back
    """

    finished = Signal()
    error = Signal(object)
    result = Signal(object)
    progress = Signal(int)


class Worker(QRunnable):
    """
    The Worker class offers a generic interface to allow any function to be
    executed as a thread in a threadpool
    """

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.log = logging.getLogger("MW4")
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        # self.kwargs['progressCallback'] = self.signals.progress

    def clearPrintErrorStack(self, tb):
        """
        getting data out for processing

        :param tb:
        :return:
        """
        file = os.path.basename(tb.tb_frame.f_code.co_filename)
        line = tb.tb_frame.f_lineno
        fnName = self.fn.__name__
        eStr = f"fn: [{fnName}], file: [{file}], line: {line} "
        return eStr

    def run(self):
        """
        runs an arbitrary methods with its parameters and catches the result

        :return: nothing, but sends results and status as signals
        """

        try:
            result = self.fn(*self.args, **self.kwargs)

        except Exception:
            # as we want to send a clear message to the log file
            exc_type, exc_value, exc_traceback = sys.exc_info()
            tb = exc_traceback

            # moving toward the end of the trace
            eStr = self.clearPrintErrorStack(tb)
            while tb.tb_next is not None:
                tb = tb.tb_next
                eStr += self.clearPrintErrorStack(tb)

            eStr += f" - excType: [{exc_type}], excValue: [{exc_value}]"
            self.log.critical(eStr)
            self.signals.error.emit(eStr)

        else:
            self.signals.result.emit(result)

        finally:
            self.signals.finished.emit()
