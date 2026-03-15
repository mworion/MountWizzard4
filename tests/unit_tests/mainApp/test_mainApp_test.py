import pytest
import shutil
from mw4.assets import assetsData
from mw4.mainApp import MountWizzard4
from pathlib import Path
from unittest import mock
from unittest.mock import MagicMock

assetsData.qInitResources()


@pytest.fixture(autouse=True, scope="module")
def app(qapp):
    mwGlob = {
        "configDir": Path("tests/work/config"),
        "dataDir": Path("tests/work/data"),
        "tempDir": Path("tests/work/temp"),
        "imageDir": Path("tests/work/image"),
        "modelDir": Path("tests/work/model"),
        "workDir": Path("tests/work"),
    }

    shutil.copy("tests/testData/de440_mw4.bsp", Path("./tests/work/data/de440_mw4.bsp"))
    shutil.copy("tests/testData/finals2000A.all", Path("./tests/work/data/finals2000A.all"))
    shutil.copy("tests/testData/test.run", Path("./tests/work/test.run"))

    mock_emit = MagicMock()
    app_instance = MountWizzard4(mwGlob, qapp, 1)
    app_instance.update1s = MagicMock(emit=mock_emit)
    yield app_instance
    app_instance.threadPool.waitForDone(15000)
    app_instance.aboutToQuit()
    app_instance.deleteLater()
    qapp.processEvents()


def test_quit(app):
    pass
