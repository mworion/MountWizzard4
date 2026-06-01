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

import pytest
from mw4.base.loggerMW import setupLogging


@pytest.fixture(scope="session", autouse=True)
def setupTestLogging():
    """Initialise the rotating-file log handler once per test session."""
    setupLogging()
