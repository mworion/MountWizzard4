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
# License APL2.0
#
###########################################################
import datetime
import logging
import sys
import time
from collections.abc import Callable
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

if not hasattr(logging.Logger, "_set_defaults"):
    # noinspection PyUnusedLocal
    def _set_defaults(self, *args: Any, **kwargs: Any) -> None:
        return

    logging.Logger._set_defaults = _set_defaults


class LoggerWriter:
    """
    taken from:
    https://stackoverflow.com/questions/19425736/
    how-to-redirect-stdout-and-stderr-to-logger-in-python
    """

    def __init__(self, level: Callable[[str], None], mode: str, std: object) -> None:
        self.level: Callable[[str], None] = level
        self.mode: str = mode
        self.standard: object = std

    def write(self, message: str) -> None:
        first = True
        for line in message.rstrip().splitlines():
            if first:
                self.level(f"[{self.mode}] " + line.strip())
                first = False
            else:
                self.level(" " * 9 + line.strip())

    def flush(self) -> None:
        pass


def redirectSTD() -> None:
    sys.stderr = LoggerWriter(logging.getLogger().error, "STDERR", sys.stderr)
    # sys.stdout = LoggerWriter(logging.getLogger().info, "STDOUT", sys.stdout)


def setupLogging() -> None:
    Path.mkdir(Path("./log"), parents=True, exist_ok=True)
    logging.Formatter.converter = time.gmtime
    timeTag = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d")
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
    logging.getLogger("PySide6").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("astropy").setLevel(logging.WARNING)
    logging.getLogger("keyring").setLevel(logging.WARNING)
    redirectSTD()


def setTrace(app: Any, enable: bool = False) -> None:
    drivers = app.getActiveDrivers()

    for device in drivers:
        for framework in drivers[device]["class"].run:
            if framework in ["ascom", "alpaca"]:
                drivers[device]["class"].run[framework].loggingTrace = enable
            elif framework in ["indi"]:
                drivers[device]["class"].run[framework].setTrace(enable)


def setCustomLoggingLevel(app: Any, level: str = "DEBUG") -> None:
    if level == "TRACE":
        logging.getLogger("MW4").setLevel("DEBUG")
        app.mount.loggingTrace = True
        setTrace(app, enable=True)
    else:
        logging.getLogger("MW4").setLevel(level)
        app.mount.loggingTrace = False
        setTrace(app, enable=False)
