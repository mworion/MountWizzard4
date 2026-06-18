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
"""Session-wide pytest configuration for unit tests.

Sets up the MW4 logging infrastructure once for the entire test session so
that individual test files do not need to call setupLogging() at module level.
"""

import logging
import pytest
import sys
import warnings
from mw4.base.loggerMW import setupLogging


class FilteredStderr:
    """Wrapper for stderr that filters PyQtGraph cleanup errors."""

    def __init__(self, original_stderr):
        self._stderr = original_stderr

    def write(self, message):
        """Write to stderr, filtering PyQtGraph errors."""
        if "Exception ignored in atexit" in message and any(
            keyword in message
            for keyword in [
                "pyqtgraph",
                "sizeHint",
                "resizeEvent",
                "boundingRect",
                "itemChange",
                "already deleted",
            ]
        ):
            return len(message)
        return self._stderr.write(message)

    def flush(self):
        """Flush stderr."""
        self._stderr.flush()

    def isatty(self):
        """Check if stderr is a tty."""
        return getattr(self._stderr, "isatty", lambda: False)()

    def __getattr__(self, name):
        """Delegate all other attributes to the real stderr."""
        return getattr(self._stderr, name)


@pytest.fixture(scope="session", autouse=True)
def setupTestLogging():
    """Initialise the rotating-file log handler once per test session."""
    # Suppress ResourceWarning for logging handlers as they are properly
    # cleaned up at the end of the session
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore", category=ResourceWarning, message="unclosed file.*mw4.*\\.log"
        )
        setupLogging()
    yield
    # Close all logging handlers to prevent ResourceWarning
    for handler in logging.root.handlers[:]:
        handler.close()
        logging.root.removeHandler(handler)


def pytest_configure(config):
    """Install stderr wrapper before tests start."""
    sys.stderr = FilteredStderr(sys.stderr)









