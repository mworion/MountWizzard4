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
import shutil
import sys
import tempfile
from pathlib import Path
from PySide6.QtCore import QCoreApplication, QThreadPool

os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ["QT_DEBUG_PLUGINS"] = "0"

ROOT_DIR = Path(__file__).resolve().parent.parent


def setupWorkerSandbox(workerId: str) -> Path:
    """Build an isolated working directory for one pytest-xdist worker.

    Tests address files relative to the repository root (``tests/work/...``,
    ``tests/testData/...``). Every worker gets a sandbox that mirrors the root
    via symlinks, except for a private copy of ``tests/work``, so parallel
    workers never create or delete each other's files.
    """
    sandbox = Path(tempfile.mkdtemp(prefix=f"mw4-{workerId}-"))
    for entry in ROOT_DIR.iterdir():
        if entry.name != "tests":
            (sandbox / entry.name).symlink_to(entry)
    (sandbox / "tests").mkdir()
    for entry in (ROOT_DIR / "tests").iterdir():
        if entry.name != "work":
            (sandbox / "tests" / entry.name).symlink_to(entry)
    shutil.copytree(ROOT_DIR / "tests" / "work", sandbox / "tests" / "work", symlinks=True)
    return sandbox


def pytest_configure(config):
    """Configure Qt settings before running tests."""
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    os.environ["QT_DEBUG_PLUGINS"] = "0"
    workerId = os.environ.get("PYTEST_XDIST_WORKER")
    if not workerId:
        return
    if str(ROOT_DIR) not in sys.path:
        sys.path.insert(0, str(ROOT_DIR))
    config.workerSandbox = setupWorkerSandbox(workerId)
    os.chdir(config.workerSandbox)


def pytest_unconfigure(config):
    """Leave and remove the pytest-xdist worker sandbox."""
    sandbox = getattr(config, "workerSandbox", None)
    if sandbox is None:
        return
    os.chdir(ROOT_DIR)
    shutil.rmtree(sandbox, ignore_errors=True)


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
    the owning Qt objects are garbage collected. Use aggressive cleanup to
    prevent mutex destruction errors during shutdown.
    """
    try:
        app = QCoreApplication.instance()
        if app is not None:
            for _ in range(5):
                app.processEvents()

        pool = QThreadPool.globalInstance()
        if pool is not None:
            pool.clear()
            pool.waitForDone(1000)
            pool.clear()

        if app is not None:
            for _ in range(5):
                app.processEvents()
            app.quit()
            for _ in range(5):
                app.processEvents()

    finally:
        gc.collect()
        gc.collect()
        gc.collect()
