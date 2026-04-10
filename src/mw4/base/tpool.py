############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10_micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2026 by mworion
# Licence APL2.0
#
###########################################################
import logging
import os
import sys
from types import TracebackType
from typing import Any, Callable
from PySide6.QtCore import QObject, QRunnable, Signal, Slot


class WorkerSignals(QObject):
    """ """

    finished = Signal()
    error = Signal(object)
    result = Signal(object)


class Worker(QRunnable):
    """ """

    def __init__(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        super().__init__()
        self.setAutoDelete(False)
        self.log = logging.getLogger("MW4")
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    def formatTbFrame(self, tb: TracebackType) -> str:
        """Build a formatted string for a single traceback frame."""
        file = os.path.basename(tb.tb_frame.f_code.co_filename)
        line = tb.tb_lineno
        fnName = getattr(self.fn, "__name__", repr(self.fn))
        eStr = f"fn: [{fnName}], file: [{file}], line: {line} "
        return eStr

    @Slot()
    def run(self) -> None:
        try:
            result = self.fn(*self.args, **self.kwargs)

        except Exception as e:
            # as we want to send a clear message to the log file
            _, _, tb = sys.exc_info()

            # moving toward the end of the trace
            eStr = f"{e} {self.formatTbFrame(tb)}"
            while tb.tb_next is not None:
                tb = tb.tb_next
                eStr += self.formatTbFrame(tb)

            eStr += f" - excType: [{type(e)}], excValue: [{e}]"
            self.log.critical(eStr)
            self.signals.error.emit(eStr)

        else:
            self.signals.result.emit(result)

        finally:
            self.signals.finished.emit()
