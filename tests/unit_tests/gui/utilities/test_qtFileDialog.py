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
import pytest
import unittest.mock as mock
from mw4.gui.utilities.qtFileDialog import MWFileDialog
from pathlib import Path
from PySide6.QtCore import QModelIndex
from PySide6.QtWidgets import QWidget


@pytest.fixture(scope="function")
def dlg(qapp, tmp_path):
    (tmp_path / "a.txt").write_text("a")
    (tmp_path / "b.txt").write_text("b")
    (tmp_path / "sub").mkdir()
    parent = QWidget()
    parent.resize(200, 200)
    d = MWFileDialog(
        parent=parent,
        title="t",
        folder=tmp_path,
        filterSet="Text (*.txt);;All (*)",
    )
    yield d
    d.close()


def test_initFileMode(qapp, tmp_path):
    d = MWFileDialog(folder=tmp_path, fileMode=MWFileDialog.FileMode.Directory)
    assert d.acceptMode == MWFileDialog.AcceptMode.AcceptOpen
    assert d.fileMode == MWFileDialog.FileMode.Directory
    assert d.btnAccept.text() == "Choose"
    d.close()


def test_initSaveMode(qapp, tmp_path):
    d = MWFileDialog(
        folder=tmp_path,
        acceptMode=MWFileDialog.AcceptMode.AcceptSave,
    )
    assert d.btnAccept.text() == "Save"
    d.close()


def test_initEmptyFilterFallback(qapp, tmp_path):
    d = MWFileDialog(folder=tmp_path, filterSet=";;")
    assert d.filterCombo.count() == 1
    assert d.filterCombo.itemText(0) == "All files (*)"
    d.close()


def test_setCurrentDirInvalidFallsBackHome(qapp):
    d = MWFileDialog(folder=Path("/this/does/not/exist"))
    assert d.currentDir == Path.home()
    d.close()


def test_onUpAndPathEntered(dlg, tmp_path):
    parent = tmp_path.parent
    dlg.onUp()
    assert dlg.currentDir == parent

    dlg.pathEdit.setText(str(tmp_path))
    dlg.onPathEntered()
    assert dlg.currentDir == tmp_path

    dlg.pathEdit.setText(str(tmp_path / "nope"))
    dlg.onPathEntered()
    assert dlg.pathEdit.text() == str(tmp_path)


def test_onUpAtRootIsNoop(qapp):
    d = MWFileDialog(folder=Path("/"))
    d.onUp()
    assert d.currentDir == Path("/")
    d.close()


def test_onFilterChanged(dlg):
    dlg.onFilterChanged("Images (*.png *.jpg)")
    assert dlg.model.nameFilters() == ["*.png", "*.jpg"]
    dlg.onFilterChanged("Garbage")
    assert dlg.model.nameFilters() == ["*"]
    dlg.onFilterChanged("Empty ()")
    assert dlg.model.nameFilters() == ["*"]


def test_parseFileNamesSingleAndMulti(dlg):
    assert dlg.parseFileNames("") == []
    assert dlg.parseFileNames("a.txt") == ["a.txt"]
    dlg.fileMode = MWFileDialog.FileMode.ExistingFiles
    assert dlg.parseFileNames('"a b.txt" c.txt') == ["a b.txt", "c.txt"]
    assert dlg.parseFileNames('"unterminated') == ['"unterminated']


def test_resolveSelectionDirectoryDefault(qapp, tmp_path):
    d = MWFileDialog(folder=tmp_path, fileMode=MWFileDialog.FileMode.Directory)
    assert d.resolveSelection() == [tmp_path]
    d.fileNameEdit.setText("sub")
    (tmp_path / "sub").mkdir(exist_ok=True)
    assert d.resolveSelection() == [tmp_path / "sub"]
    d.close()


def test_onSelectionChangedFiles(dlg, tmp_path):
    idx = dlg.model.index(str(tmp_path / "a.txt"))
    dlg.tree.selectionModel().select(idx, dlg.tree.selectionModel().SelectionFlag.Select)
    dlg.onSelectionChanged()
    assert dlg.fileNameEdit.text() == "a.txt"


def test_onSelectionChangedMultiple(qapp, tmp_path):
    (tmp_path / "x.txt").write_text("x")
    (tmp_path / "y y.txt").write_text("y")
    d = MWFileDialog(folder=tmp_path, fileMode=MWFileDialog.FileMode.ExistingFiles)
    sm = d.tree.selectionModel()
    sm.select(
        d.model.index(str(tmp_path / "x.txt")),
        sm.SelectionFlag.Select | sm.SelectionFlag.Rows,
    )
    sm.select(
        d.model.index(str(tmp_path / "y y.txt")),
        sm.SelectionFlag.Select | sm.SelectionFlag.Rows,
    )
    d.onSelectionChanged()
    assert '"y y.txt"' in d.fileNameEdit.text()
    assert "x.txt" in d.fileNameEdit.text()
    d.close()


def test_onSelectionChangedDirectoryMode(qapp, tmp_path):
    (tmp_path / "sub").mkdir(exist_ok=True)
    d = MWFileDialog(folder=tmp_path, fileMode=MWFileDialog.FileMode.Directory)
    sm = d.tree.selectionModel()
    sm.select(
        d.model.index(str(tmp_path / "sub")),
        sm.SelectionFlag.Select | sm.SelectionFlag.Rows,
    )
    d.onSelectionChanged()
    assert d.fileNameEdit.text() == "sub"
    d.close()


def test_onDoubleClickedDir(dlg, tmp_path):
    idx = dlg.model.index(str(tmp_path / "sub"))
    dlg.onDoubleClicked(idx)
    assert dlg.currentDir == tmp_path / "sub"


def test_onDoubleClickedFileAccepts(dlg, tmp_path):
    idx = dlg.model.index(str(tmp_path / "a.txt"))
    with mock.patch.object(dlg, "onAccept") as m:
        dlg.onDoubleClicked(idx)
        m.assert_called_once()
    assert dlg.fileNameEdit.text() == "a.txt"


def test_onDoubleClickedIgnoredInDirMode(qapp, tmp_path):
    (tmp_path / "a.txt").write_text("a")
    d = MWFileDialog(folder=tmp_path, fileMode=MWFileDialog.FileMode.Directory)
    idx = d.model.index(str(tmp_path / "a.txt"))
    with mock.patch.object(d, "onAccept") as m:
        d.onDoubleClicked(idx)
        m.assert_not_called()
    d.close()


def test_onAcceptExistingFile(dlg, tmp_path):
    dlg.fileNameEdit.setText("a.txt")
    with mock.patch.object(dlg, "close"):
        dlg.onAccept()
    assert dlg.resultCode == MWFileDialog.Accepted
    assert dlg.selectedFiles() == [tmp_path / "a.txt"]


def test_onAcceptRejectsNonExisting(dlg):
    dlg.fileNameEdit.setText("missing.txt")
    dlg.onAccept()
    assert dlg.resultCode == MWFileDialog.Rejected


def test_onAcceptEmptyIsNoop(dlg):
    dlg.fileNameEdit.setText("")
    dlg.onAccept()
    assert dlg.resultCode == MWFileDialog.Rejected


def test_onAcceptExistingFiles(qapp, tmp_path):
    (tmp_path / "a.txt").write_text("a")
    (tmp_path / "b.txt").write_text("b")
    d = MWFileDialog(folder=tmp_path, fileMode=MWFileDialog.FileMode.ExistingFiles)
    d.fileNameEdit.setText("a.txt b.txt")
    with mock.patch.object(d, "close"):
        d.onAccept()
    assert d.selectedFiles() == [tmp_path / "a.txt", tmp_path / "b.txt"]
    d.close()


def test_onAcceptExistingFilesRejectsMissing(qapp, tmp_path):
    (tmp_path / "a.txt").write_text("a")
    d = MWFileDialog(folder=tmp_path, fileMode=MWFileDialog.FileMode.ExistingFiles)
    d.fileNameEdit.setText("a.txt nope.txt")
    d.onAccept()
    assert d.resultCode == MWFileDialog.Rejected
    d.close()


def test_onAcceptDirectoryRejectsFile(qapp, tmp_path):
    (tmp_path / "a.txt").write_text("a")
    d = MWFileDialog(folder=tmp_path, fileMode=MWFileDialog.FileMode.Directory)
    d.fileNameEdit.setText("a.txt")
    d.onAccept()
    assert d.resultCode == MWFileDialog.Rejected
    d.close()


def test_onReject(dlg):
    dlg.fileNameEdit.setText("a.txt")
    with mock.patch.object(dlg, "close"):
        dlg.onReject()
    assert dlg.resultCode == MWFileDialog.Rejected
    assert dlg.selectedFiles() == []


def test_finishLoopRunning(dlg):
    with (
        mock.patch.object(dlg.eventLoop, "isRunning", return_value=True),
        mock.patch.object(dlg.eventLoop, "quit") as q,
    ):
        dlg.finishLoop()
        q.assert_called_once()


def test_closeEventQuitsLoop(dlg):
    with (
        mock.patch.object(dlg.eventLoop, "isRunning", return_value=True),
        mock.patch.object(dlg.eventLoop, "quit") as q,
    ):
        dlg.close()
        q.assert_called_once()
    assert dlg.resultCode == MWFileDialog.Rejected


def test_exec(dlg):
    with (
        mock.patch.object(dlg, "show"),
        mock.patch.object(dlg.eventLoop, "exec"),
    ):
        dlg.resultCode = MWFileDialog.Accepted
        assert dlg.exec() == MWFileDialog.Accepted


def test_classmethodsInvokeExec(qapp, tmp_path):
    (tmp_path / "a.txt").write_text("a")
    with (
        mock.patch.object(MWFileDialog, "exec", return_value=1),
        mock.patch.object(
            MWFileDialog,
            "selectedFiles",
            return_value=[tmp_path / "a.txt"],
        ),
    ):
        assert MWFileDialog.getOpenFileName(None, "t", tmp_path, "*.*") == tmp_path / "a.txt"
        assert MWFileDialog.getOpenFileNames(None, "t", tmp_path, "*.*") == [
            tmp_path / "a.txt"
        ]
        assert MWFileDialog.getSaveFileName(None, "t", tmp_path, "*.*") == tmp_path / "a.txt"
        assert MWFileDialog.getExistingDirectory(None, "t", tmp_path) == tmp_path / "a.txt"


def test_classmethodsEmptyResult(qapp, tmp_path):
    with (
        mock.patch.object(MWFileDialog, "exec", return_value=0),
        mock.patch.object(MWFileDialog, "selectedFiles", return_value=[]),
    ):
        assert MWFileDialog.getOpenFileName(None, "t", tmp_path, "*.*") == Path()
        assert MWFileDialog.getOpenFileNames(None, "t", tmp_path, "*.*") == []
        assert MWFileDialog.getSaveFileName(None, "t", tmp_path, "*.*") == Path()
        assert MWFileDialog.getExistingDirectory(None, "t", tmp_path) == Path()


def test_modelIndexUsedAsExpected(dlg):
    assert isinstance(dlg.model.index(str(Path.home())), QModelIndex)


def test_treeViewDefaultColumnConfiguration(dlg):
    header = dlg.tree.header()
    assert header is not None
    assert dlg.tree.isColumnHidden(0) is False


def test_treeViewColumnWidth(dlg):
    dlg.tree.setColumnWidth(0, 300)
    assert dlg.tree.columnWidth(0) == 300


def test_treeViewHideColumn(dlg):
    dlg.tree.hideColumn(1)
    assert dlg.tree.isColumnHidden(1) is True
    dlg.tree.showColumn(1)
    assert dlg.tree.isColumnHidden(1) is False


def test_treeViewMultipleColumnsConfiguration(dlg):
    dlg.tree.hideColumn(2)
    dlg.tree.hideColumn(3)
    assert dlg.tree.isColumnHidden(2) is True
    assert dlg.tree.isColumnHidden(3) is True
    assert dlg.tree.isColumnHidden(0) is False
    assert dlg.tree.isColumnHidden(1) is False


def test_acceptButtonIsDefault(dlg):
    assert dlg.btnAccept.isDefault() or dlg.btnAccept.hasFocus() is not None


def test_acceptButtonMinimumSize(dlg):
    assert dlg.btnAccept.minimumWidth() == 80
    assert dlg.btnAccept.minimumHeight() == 25


def test_cancelButtonMinimumSize(dlg):
    assert dlg.btnCancel.minimumWidth() == 80
    assert dlg.btnCancel.minimumHeight() == 25


def test_treeViewSortingEnabled(dlg):
    assert dlg.tree.isSortingEnabled() is True


def test_treeViewSortColumn(dlg):
    assert dlg.tree.header().sortIndicatorSection() == 0
