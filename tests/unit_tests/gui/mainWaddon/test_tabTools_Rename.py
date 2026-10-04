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
import numpy as np
import pytest
from astropy.io import fits
from mw4.gui.mainWaddon.tabTools_Rename import Rename
from mw4.gui.utilities.nativeQt.qtFileDialog import MWFileDialog
from mw4.gui.utilities.qtMain import MWidget
from mw4.gui.widgets.main_ui import Ui_MainWindow
from pathlib import Path
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from unittest import mock


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    mainW = MWidget()
    mainW.app = App()
    mainW.ui = Ui_MainWindow()
    mainW.ui.setupUi(mainW)
    window = Rename(mainW)
    yield window
    mainW.app.threadPool.waitForDone(1000)


@pytest.fixture(autouse=True)
def resetState(function):
    # chooseDir tests leave renameDir as a tuple; reset to a Path before each test.
    function.renameDir = Path("tests/work/image")
    function.workerRenameFiles = None
    yield


def test_initConfig_1(function):
    function.app.config["WindowMain"] = {}
    function.initConfig()


def test_storeConfig_1(function):
    function.storeConfig()


def test_setupIcons_1(function):
    function.setupIcons()


def test_setupGuiTools(function):
    function.setupGuiTools()
    for ui in function.selectorsDropDowns.values():
        assert ui.count() == 7


def test_convertHeaderEntry_1(function):
    chunk = function.convertHeaderEntry(entry="", fitsKey="1")
    assert not chunk


def test_convertHeaderEntry_2(function):
    chunk = function.convertHeaderEntry(entry="1", fitsKey="")
    assert not chunk


def test_convertHeaderEntry_3(function):
    chunk = function.convertHeaderEntry(entry="2019-05-26T17:02:18.843", fitsKey="DATE-OBS")
    assert chunk == "2019-05-26_17-02-18"


def test_convertHeaderEntry_4(function):
    chunk = function.convertHeaderEntry(entry="2019-05-26T17:02:18", fitsKey="DATE-OBS")
    assert chunk == "2019-05-26_17-02-18"


def test_convertHeaderEntry_5(function):
    chunk = function.convertHeaderEntry(entry=1, fitsKey="XBINNING")
    assert chunk == "Bin1"


def test_convertHeaderEntry_6(function):
    chunk = function.convertHeaderEntry(entry=25, fitsKey="CCD-TEMP")
    assert chunk == "Temp025"


def test_convertHeaderEntry_7(function):
    chunk = function.convertHeaderEntry(entry="Light", fitsKey="FRAME")
    assert chunk == "Light"


def test_convertHeaderEntry_8(function):
    chunk = function.convertHeaderEntry(entry="red", fitsKey="FILTER")
    assert chunk == "red"


def test_convertHeaderEntry_9(function):
    chunk = function.convertHeaderEntry(entry=14, fitsKey="EXPTIME")
    assert chunk == "Exp14s"


def test_convertHeaderEntry_imagetyp(function):
    chunk = function.convertHeaderEntry(entry="Light", fitsKey="IMAGETYP")
    assert chunk == "Light"


def test_convertHeaderEntry_11(function):
    chunk = function.convertHeaderEntry(entry="12354", fitsKey="XXX")
    assert not chunk


def test_processSelectors_1(function):
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    header = hdu[0].header
    header.set("DATE-OBS", "2019-05-26T17:02:18.843")
    name = function.processSelectors(header, "Frame")
    assert not name


def test_processSelectors_2(function):
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    header = hdu[0].header
    header.set("DATE-OBS", "2019-05-26T17:02:18.843")
    name = function.processSelectors(header, "Datetime")
    assert name == "2019-05-26_17-02-18"


def test_processSelectors_exptime(function):
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    header = hdu[0].header
    header.set("EXPTIME", 30)
    name = function.processSelectors(header, "Exp Time")
    assert name == "Exp30s"


def test_processSelectors_imagetyp(function):
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    header = hdu[0].header
    header.set("IMAGETYP", "Light Frame")
    name = function.processSelectors(header, "Frame")
    assert name == "Light Frame"


def writeFits(fileName: Path, header: dict) -> Path:
    hdu = fits.PrimaryHDU(np.arange(100.0))
    for key, value in header.items():
        hdu.header[key] = value
    fits.HDUList([hdu]).writeto(fileName, overwrite=True)
    return fileName


def test_renameFile_1(function):
    fileName = writeFits(Path("tests/work/image/m01.fit"), {})
    with mock.patch.object(Path, "rename") as mockRename:
        function.renameFile(fileName, Path("tests/work/image"), "", ["None"])
    mockRename.assert_called_once_with(Path("tests/work/image/UNKNOWN.fits"))


def test_renameFile_2(function):
    fileName = writeFits(Path("tests/work/image/m02.fit"), {"OBJECT": "m51"})
    with mock.patch.object(Path, "rename") as mockRename:
        function.renameFile(fileName, Path("tests/work/image"), "", ["None"])
    mockRename.assert_called_once_with(Path("tests/work/image/M51.fits"))


def test_renameFile_3(function):
    fileName = writeFits(Path("tests/work/image/m03.fit"), {"OBJECT": "m51"})
    with mock.patch.object(Path, "rename") as mockRename:
        function.renameFile(fileName, Path("tests/work/image"), "TEST", ["None"])
    mockRename.assert_called_once_with(Path("tests/work/image/TEST.fits"))


def test_renameFile_4(function):
    fileName = writeFits(Path("tests/work/image/m04.fit"), {"FILTER": "red", "EXPTIME": 30})
    with mock.patch.object(Path, "rename") as mockRename:
        function.renameFile(
            fileName, Path("tests/work/image"), "TEST", ["Filter", "None", "Exp Time"]
        )
    mockRename.assert_called_once_with(Path("tests/work/image/TEST_red_Exp30s.fits"))


def test_runnerRenameFiles_1(function):
    files = [Path("a.fit"), Path("b.fit")]
    with (
        mock.patch.object(function, "renameFile") as mockRename,
        mock.patch.object(function.signals, "progress") as mockProgress,
    ):
        number = function.runnerRenameFiles(files, Path("tests/work/image"), "", ["None"])
    assert number == 2
    assert mockRename.call_count == 2
    assert [c.args[0] for c in mockProgress.emit.call_args_list] == [50, 100]


def test_renameFinished_1(function):
    with mock.patch.object(function, "msg") as mockMsg:
        function.renameFinished(3)
    mockMsg.emit.assert_called_once_with(0, "Tools", "Rename", "3 images were renamed")


def test_renameEnableGUI_1(function):
    function.ui.renameStart.setEnabled(False)
    function.renameEnableGUI()
    assert function.ui.renameStart.isEnabled()


def test_renameRunGUI_1(function):
    function.renameDir = Path("tests/work/xxx")
    function.ui.includeSubdirs.setChecked(False)
    with (
        mock.patch.object(function, "msg") as mockMsg,
        mock.patch("mw4.gui.mainWaddon.tabTools_Rename.startWorker") as mockStart,
    ):
        function.renameRunGUI()
    assert mockMsg.emit.call_args.args[3] == "No valid input directory given"
    mockStart.assert_not_called()


def test_renameRunGUI_2(function):
    function.ui.includeSubdirs.setChecked(True)
    with (
        mock.patch.object(Path, "glob", return_value=iter([])),
        mock.patch.object(function, "msg") as mockMsg,
        mock.patch("mw4.gui.mainWaddon.tabTools_Rename.startWorker") as mockStart,
    ):
        function.renameRunGUI()
    assert mockMsg.emit.call_args.args[3] == "No files to rename"
    mockStart.assert_not_called()


def test_renameRunGUI_3(function):
    files = [Path("tests/work/image/m51.fit")]
    function.ui.includeSubdirs.setChecked(False)
    function.ui.newObjectName.setText("test")
    function.ui.rename1.clear()
    function.ui.rename1.addItem("Filter")
    function.ui.renameStart.setEnabled(True)
    with (
        mock.patch.object(Path, "glob", return_value=iter(files)) as mockGlob,
        mock.patch("mw4.gui.mainWaddon.tabTools_Rename.startWorker") as mockStart,
    ):
        function.renameRunGUI()
    mockGlob.assert_called_once_with("*.fit*")
    assert not function.ui.renameStart.isEnabled()
    args = mockStart.call_args.args
    assert args[2] == function.runnerRenameFiles
    assert args[3] == files
    assert args[4] == Path("tests/work/image")
    assert args[5] == "TEST"
    assert args[6][0] == "Filter"
    assert len(args[6]) == 6
    function.ui.renameStart.setEnabled(True)


def test_renameRunGUI_4(function, qtbot):
    fileName = writeFits(Path("tests/work/image/r1.fit"), {"OBJECT": "m51"})
    function.ui.includeSubdirs.setChecked(False)
    function.ui.newObjectName.setText("")
    function.ui.renameProgress.setValue(0)
    with (
        mock.patch.object(Path, "glob", return_value=iter([fileName])),
        mock.patch.object(Path, "rename") as mockRename,
        mock.patch.object(function, "msg") as mockMsg,
    ):
        function.renameRunGUI()
        qtbot.waitUntil(function.ui.renameStart.isEnabled, timeout=5000)
    mockRename.assert_called_once_with(Path("tests/work/image/M51.fits"))
    assert mockMsg.emit.call_args.args[3] == "1 images were renamed"
    assert function.ui.renameProgress.value() == 100


def test_chooseDir_1(function):
    with mock.patch.object(MWFileDialog, "getExistingDirectory", return_value=("", "", "")):
        function.chooseDir()


def test_chooseDir_2(function):
    with mock.patch.object(
        MWFileDialog, "getExistingDirectory", return_value=("test", "", "")
    ):
        function.chooseDir()
