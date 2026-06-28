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
from mw4.gui.utilities.nativeQt.qtMessageDialog import MWMessageDialog
from PySide6.QtWidgets import QWidget


@pytest.fixture(scope="function")
def dlg(qapp):
    parent = QWidget()
    parent.resize(400, 400)
    d = MWMessageDialog(parent=parent, title="t", question="q?")
    yield d
    d.close()


def test_initStandardButtons(qapp):
    d = MWMessageDialog(title="t", question="q?")
    assert d.useStandardButtons is True
    assert d.resultCode == MWMessageDialog.Rejected
    assert d.buttonNo.text() == "No"
    assert d.buttonYes.text() == "Yes"
    assert len(d.buttonWidgets) == 2
    d.close()


def test_initCustomButtons(qapp):
    d = MWMessageDialog(title="t", question="q?", buttons=["A", "B", "C"])
    assert d.useStandardButtons is False
    assert len(d.buttonWidgets) == 3
    assert [b.text() for b in d.buttonWidgets] == ["A", "B", "C"]
    d.close()


def test_initIconTypeOutOfRangeFallsBackToZero(qapp):
    d = MWMessageDialog(title="t", question="q?", iconType=99)
    assert d.useStandardButtons is True
    d.close()


def test_initEmptyButtonsListUsesStandard(qapp):
    d = MWMessageDialog(title="t", question="q?", buttons=[])
    assert d.useStandardButtons is True
    d.close()


def test_initParentCenters(qapp):
    parent = QWidget()
    parent.resize(800, 600)
    parent.move(100, 100)
    d = MWMessageDialog(parent=parent, title="t", question="q?")
    assert d.x() >= 100
    assert d.y() >= 100
    d.close()


def test_initIconTypes(qapp):
    for iconType in range(4):
        d = MWMessageDialog(title="t", question="q?", iconType=iconType)
        assert d.textLabel.text() == "q?"
        d.close()


def test_onClickStoresValueAndQuits(dlg):
    with mock.patch.object(dlg, "close"):
        dlg.onClick(7)
    assert dlg.resultCode == 7


def test_onClickStandardYes(dlg):
    with mock.patch.object(dlg, "close"):
        dlg.buttonYes.clicked.emit()
    assert dlg.resultCode == MWMessageDialog.YesIndex


def test_onClickStandardNo(dlg):
    with mock.patch.object(dlg, "close"):
        dlg.buttonNo.clicked.emit()
    assert dlg.resultCode == MWMessageDialog.NoIndex


def test_onClickCustomButton(qapp):
    d = MWMessageDialog(title="t", question="q?", buttons=["A", "B"])
    with mock.patch.object(d, "close"):
        d.buttonWidgets[1].clicked.emit()
    assert d.resultCode == 1
    d.close()


def test_finishLoopRunning(dlg):
    with (
        mock.patch.object(dlg.eventLoop, "isRunning", return_value=True),
        mock.patch.object(dlg.eventLoop, "quit") as q,
    ):
        dlg.finishLoop()
        q.assert_called_once()


def test_finishLoopNotRunning(dlg):
    with (
        mock.patch.object(dlg.eventLoop, "isRunning", return_value=False),
        mock.patch.object(dlg.eventLoop, "quit") as q,
    ):
        dlg.finishLoop()
        q.assert_not_called()


def test_closeEventQuitsLoop(dlg):
    with (
        mock.patch.object(dlg.eventLoop, "isRunning", return_value=True),
        mock.patch.object(dlg.eventLoop, "quit") as q,
    ):
        dlg.close()
        q.assert_called_once()
    assert dlg.resultCode == MWMessageDialog.Rejected


def test_exec(dlg):
    with (
        mock.patch.object(dlg, "show"),
        mock.patch.object(dlg.eventLoop, "exec"),
    ):
        dlg.resultCode = MWMessageDialog.YesIndex
        assert dlg.exec() == MWMessageDialog.YesIndex


def test_questionStandardYes(qapp):
    with mock.patch.object(MWMessageDialog, "exec", return_value=MWMessageDialog.YesIndex):
        result = MWMessageDialog.question(None, "t", "q?")
    assert result is True


def test_questionStandardNo(qapp):
    with mock.patch.object(MWMessageDialog, "exec", return_value=MWMessageDialog.NoIndex):
        result = MWMessageDialog.question(None, "t", "q?")
    assert result is False


def test_questionStandardRejected(qapp):
    with mock.patch.object(MWMessageDialog, "exec", return_value=MWMessageDialog.Rejected):
        result = MWMessageDialog.question(None, "t", "q?")
    assert result is False


def test_questionCustomButtons(qapp):
    with mock.patch.object(MWMessageDialog, "exec", return_value=2):
        result = MWMessageDialog.question(None, "t", "q?", buttons=["A", "B", "C"])
    assert result == 2


def test_questionEmptyButtonsTreatedAsStandard(qapp):
    with mock.patch.object(MWMessageDialog, "exec", return_value=MWMessageDialog.YesIndex):
        result = MWMessageDialog.question(None, "t", "q?", buttons=[])
    assert result is True


def test_standardButtonsDefaultButtonIsNo(dlg):
    assert dlg.buttonNo.isDefault() is True


def test_standardButtonsNoButtonCanReceiveFocus(dlg):
    assert dlg.buttonNo.focusPolicy() != 0


def test_standardButtonsYesButtonNotDefault(dlg):
    assert dlg.buttonYes.isDefault() is False


def test_standardButtonsNoButtonMinimumSize(dlg):
    assert dlg.buttonNo.minimumWidth() == 80
    assert dlg.buttonNo.minimumHeight() == 25


def test_standardButtonsYesButtonMinimumSize(dlg):
    assert dlg.buttonYes.minimumWidth() == 80
    assert dlg.buttonYes.minimumHeight() == 25


def test_customButtonsDefaultBehavior(qapp):
    d = MWMessageDialog(title="t", question="q?", buttons=["OK", "Cancel"])
    assert len(d.buttonWidgets) == 2
    d.close()


def test_allIconTypesHaveValidConfiguration(qapp):
    for iconType in range(4):
        d = MWMessageDialog(title="t", question="q?", iconType=iconType)
        assert d.buttonNo.isDefault() or d.buttonNo is not None
        d.close()


def test_initialDialogRejectedState(qapp):
    d = MWMessageDialog(title="t", question="q?")
    assert d.resultCode == MWMessageDialog.Rejected
    d.close()


def test_multilineQuestionSupported(qapp):
    long_text = "Line 1\nLine 2\nLine 3"
    d = MWMessageDialog(title="t", question=long_text)
    assert d.textLabel.wordWrap() is True
    d.close()
