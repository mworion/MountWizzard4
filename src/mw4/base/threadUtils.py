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
import time


def mainThreadSleep(ms: int) -> None:
    """Pause for *ms* milliseconds.

    Thread-safe alternative to ``sleepAndEvents`` for use inside
    ``QThreadPool`` worker functions.  Unlike ``sleepAndEvents`` this
    function does **not** create any Qt objects, so it is safe to call
    from any thread.
    """
    time.sleep(ms / 1000.0)
