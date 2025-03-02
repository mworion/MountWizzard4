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
import os
import time
import datetime
import logging
from logging.handlers import RotatingFileHandler
from functools import partial, partialmethod


# external packages

# local imports


class LoggerWriter:
    """
    taken from:
    https://stackoverflow.com/questions/19425736/
    how-to-redirect-stdout-and-stderr-to-logger-in-python
    """

    def __init__(self, level, mode, std):
        self.level = level
        self.mode = mode
        self.standard = std

    def write(self, message: str) -> None:
        first = True
        for line in message.rstrip().splitlines():
            if first:
                self.level(f"[{self.mode}] " + line.strip())
                first = False
            else:
                self.level(" " * 9 + line.strip())

    def flush(self) -> None:
        """
        flush has to be present, but is not used
        """
        pass


def redirectSTD() -> None:
    """ """
    # sys.stderr = LoggerWriter(logging.getLogger().error, 'STDERR', sys.stderr)
    # sys.stdout = LoggerWriter(logging.getLogger().info, 'STDOUT', sys.stdout)


def setupLogging() -> None:
    """ """
    if not os.path.isdir("./log"):
        os.mkdir("./log")

    logging.Formatter.converter = time.gmtime
    timeTag = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    logFile = f"./log/mw4-{timeTag}.log"
    logHandler = RotatingFileHandler(
        logFile,
        mode="a",
        maxBytes=100 * 1024 * 1024,
        backupCount=100,
        encoding=None,
        delay=False,
    )
    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(asctime)s.%(msecs)03d]"
        "[%(levelname)1.1s]"
        "[%(filename)15.15s]"
        "[%(lineno)4s]"
        " %(message)s",
        handlers=[logHandler],
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # setting different log level for imported packages to avoid unnecessary data
    # urllib3 is used by requests, so we have to add this as well
    logging.getLogger("PySide6").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("astropy").setLevel(logging.WARNING)
    logging.getLogger("keyring").setLevel(logging.WARNING)

    logging.TRACE = 5
    logging.addLevelName(5, "TRACE")
    logging.Logger.trace = partialmethod(logging.Logger.log, logging.TRACE)
    logging.trace = partial(logging.log, logging.TRACE)

    logging.UI = 35
    logging.addLevelName(logging.UI, "UI")
    logging.Logger.ui = partialmethod(logging.Logger.log, logging.UI)
    logging.ui = partial(logging.log, logging.UI)

    logging.HEADER = 55
    logging.addLevelName(logging.HEADER, "HEADER")
    logging.Logger.header = partialmethod(logging.Logger.log, logging.HEADER)
    logging.header = partial(logging.log, logging.HEADER)

    redirectSTD()


def setCustomLoggingLevel(level: str = "WARN") -> None:
    """ """
    logging.getLogger("MW4").setLevel(level)
