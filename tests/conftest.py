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
import gc
import os

os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ["QT_DEBUG_PLUGINS"] = "0"


def pytest_configure(config):
    """Configure Qt settings before running tests."""
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    os.environ["QT_DEBUG_PLUGINS"] = "0"


def pytest_runtest_teardown(item):
    """Clean up Qt resources after each test."""
    gc.collect()
    try:
        from PySide6.QtCore import QCoreApplication, QThreadPool

        pool = QThreadPool.globalInstance()
        if pool is not None:
            pool.waitForDone(100)

        app = QCoreApplication.instance()
        if app is not None:
            app.processEvents()
    except Exception:
        pass


def pytest_sessionfinish(session, exitstatus):
    """Cleanup Qt resources after all tests complete."""
    import sys
    import io

    gc.collect()
    try:
        from PySide6.QtCore import QCoreApplication, QThreadPool

        pool = QThreadPool.globalInstance()
        if pool is not None:
            pool.waitForDone(1000)

        app = QCoreApplication.instance()
        if app is not None:
            app.processEvents()
            app.quit()
            del app

        gc.collect()
    except Exception:
        pass

