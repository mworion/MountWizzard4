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
from PySide6.QtCore import QCoreApplication, QThreadPool

os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ["QT_DEBUG_PLUGINS"] = "0"


def pytest_configure(config):
    """Configure Qt settings before running tests."""
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    os.environ["QT_DEBUG_PLUGINS"] = "0"


def pytest_runtest_teardown(item):
    """Clean up Qt resources after each test.

    Only the global thread pool is drained (cheap when idle) so workers from
    one test do not leak into the next. No per-test ``gc.collect()`` is done:
    it costs ~10 ms each with many live Qt objects and dominated the runtime.
    Tests are responsible for releasing their own Qt resources (e.g. unlocking
    worker mutexes), so no forced collection is needed to hide leaks.
    """
    pool = QThreadPool.globalInstance()
    if pool is not None:
        pool.waitForDone(100)

    app = QCoreApplication.instance()
    if app is not None:
        app.processEvents()


def pytest_sessionfinish(session, exitstatus):
    """Cleanup Qt resources after all tests complete.

    Drain the thread pool first so no worker still holds a locked mutex when
    the owning Qt objects are garbage collected, then collect once.
    """
    pool = QThreadPool.globalInstance()
    if pool is not None:
        pool.waitForDone(1000)

    app = QCoreApplication.instance()
    if app is not None:
        app.processEvents()
        app.quit()

    gc.collect()
