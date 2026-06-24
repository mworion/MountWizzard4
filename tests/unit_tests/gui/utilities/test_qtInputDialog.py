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
from mw4.gui.utilities.qtInputDialog import MWInputDialog
from PySide6.QtWidgets import QWidget


@pytest.fixture(scope="function")
def dlg(qapp):
    parent = QWidget()
    parent.resize(400, 400)
    d = MWInputDialog(
        parent=parent,
        title="Test Input",
        label="Enter text:",
        actualValue="default",
    )
    yield d
    d.close()


def test_initTextMode(qapp):
    d = MWInputDialog(title="title", label="label", inputMode="text")
    assert d.inputMode == "text"
    assert d.resultCode == MWInputDialog.Rejected
    assert d.btnOk.text() == "OK"
    assert d.btnCancel.text() == "Cancel"
    d.close()


def test_initIntMode(qapp):
    d = MWInputDialog(title="title", label="label", inputMode="int")
    assert d.inputMode == "int"
    d.close()


def test_initDoubleMode(qapp):
    d = MWInputDialog(title="title", label="label", inputMode="double")
    assert d.inputMode == "double"
    d.close()


def test_initWithDefaultValue(qapp):
    d = MWInputDialog(title="title", label="label", actualValue="test value")
    assert d.inputEdit.text() == "test value"
    d.close()


def test_initEmptyDefaultValue(qapp):
    d = MWInputDialog(title="title", label="label")
    assert d.inputEdit.text() == ""
    d.close()


def test_initParentCenters(qapp):
    parent = QWidget()
    parent.resize(800, 600)
    parent.move(100, 100)
    d = MWInputDialog(parent=parent, title="title", label="label")
    assert d.x() >= 100
    assert d.y() >= 100
    d.close()


def test_validateInputText(dlg):
    assert dlg.validateInput("any text") is True
    assert dlg.validateInput("") is False
    assert dlg.validateInput("123") is True


def test_validateInputInt(qapp):
    d = MWInputDialog(
        title="title",
        label="label",
        inputMode="int",
        minValue=-2147483647,
    )
    # QSpinBox enforces validation automatically, so validateInput
    # returns True for non-empty strings
    assert d.validateInput("123") is True
    assert d.validateInput("0") is True
    assert d.validateInput("-456") is True
    assert d.validateInput("") is False
    # Invalid strings are accepted by validateInput (spinbox enforces it)
    assert d.validateInput("abc") is True
    assert d.validateInput("12.34") is True
    d.close()


def test_validateInputIntWithMinMax(qapp):
    d = MWInputDialog(
        title="title",
        label="label",
        inputMode="int",
        minValue=0,
        maxValue=100,
    )
    # QSpinBox enforces validation automatically
    assert d.validateInput("50") is True
    assert d.validateInput("0") is True
    assert d.validateInput("100") is True
    assert d.validateInput("-1") is True
    assert d.validateInput("101") is True
    d.close()


def test_validateInputDouble(qapp):
    d = MWInputDialog(
        title="title",
        label="label",
        inputMode="double",
        minValue=-2147483647.0,
    )
    # QDoubleSpinBox enforces validation automatically
    assert d.validateInput("123.45") is True
    assert d.validateInput("123") is True
    assert d.validateInput("0.0") is True
    assert d.validateInput("-456.789") is True
    assert d.validateInput("") is False
    assert d.validateInput("abc") is True
    d.close()


def test_validateInputDoubleWithMinMax(qapp):
    d = MWInputDialog(
        title="title",
        label="label",
        inputMode="double",
        minValue=0.0,
        maxValue=100.0,
    )
    # QDoubleSpinBox enforces validation automatically
    assert d.validateInput("50.5") is True
    assert d.validateInput("0.0") is True
    assert d.validateInput("100.0") is True
    assert d.validateInput("-0.1") is True
    assert d.validateInput("100.1") is True
    d.close()


def test_onAcceptValidText(dlg):
    dlg.inputEdit.setText("valid input")
    with mock.patch.object(dlg, "close"):
        dlg.onAccept()
    assert dlg.resultCode == MWInputDialog.Accepted
    assert dlg.inputValue == "valid input"


def test_onAcceptEmptyText(dlg):
    dlg.inputEdit.setText("")
    dlg.onAccept()
    assert dlg.resultCode == MWInputDialog.Rejected
    assert dlg.inputValue == ""


def test_onAcceptInvalidInt(qapp):
    d = MWInputDialog(title="title", label="label", inputMode="int")
    d.inputWidget.setValue(999)
    d.onAccept()
    assert d.resultCode == MWInputDialog.Accepted
    d.close()


def test_onAcceptValidInt(qapp):
    d = MWInputDialog(title="title", label="label", inputMode="int")
    d.inputWidget.setValue(42)
    with mock.patch.object(d, "close"):
        d.onAccept()
    assert d.resultCode == MWInputDialog.Accepted
    assert d.inputValue == "42"
    d.close()


def test_onAcceptInvalidDouble(qapp):
    d = MWInputDialog(title="title", label="label", inputMode="double")
    d.inputWidget.setValue(999.0)
    d.onAccept()
    assert d.resultCode == MWInputDialog.Accepted
    d.close()


def test_onAcceptValidDouble(qapp):
    d = MWInputDialog(
        title="title",
        label="label",
        inputMode="double",
        decimals=5,
    )
    d.inputWidget.setValue(3.14159)
    with mock.patch.object(d, "close"):
        d.onAccept()
    assert d.resultCode == MWInputDialog.Accepted
    assert d.inputValue == "3.14159"
    d.close()


def test_onReject(dlg):
    dlg.inputEdit.setText("some value")
    with mock.patch.object(dlg, "close"):
        dlg.onReject()
    assert dlg.resultCode == MWInputDialog.Rejected
    assert dlg.inputValue == ""


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
    assert dlg.resultCode == MWInputDialog.Rejected


def test_exec(dlg):
    with (
        mock.patch.object(dlg, "show"),
        mock.patch.object(dlg.eventLoop, "exec"),
    ):
        dlg.resultCode = MWInputDialog.Accepted
        assert dlg.exec() == MWInputDialog.Accepted


def test_getValue(dlg):
    dlg.inputValue = "test value"
    assert dlg.getValue() == "test value"


def test_wasAccepted(dlg):
    dlg.resultCode = MWInputDialog.Accepted
    assert dlg.wasAccepted() is True
    dlg.resultCode = MWInputDialog.Rejected
    assert dlg.wasAccepted() is False


def test_okButtonIsDefault(dlg):
    assert dlg.btnOk.isDefault() is True


def test_okButtonMinimumSize(dlg):
    assert dlg.btnOk.minimumWidth() == 80
    assert dlg.btnOk.minimumHeight() == 25


def test_cancelButtonMinimumSize(dlg):
    assert dlg.btnCancel.minimumWidth() == 80
    assert dlg.btnCancel.minimumHeight() == 25


def test_classMethodGetText(qapp):
    # Test the getText class method behavior
    dlg = MWInputDialog(title="Test", label="Enter:")
    dlg.inputValue = "test input"
    dlg.resultCode = MWInputDialog.Accepted
    assert dlg.wasAccepted() is True
    assert dlg.getValue() == "test input"
    dlg.close()


def test_classMethodGetTextRejected(qapp):
    with (
        mock.patch.object(MWInputDialog, "exec", return_value=MWInputDialog.Rejected),
        mock.patch.object(MWInputDialog, "getValue", return_value=""),
    ):
        text, accepted = MWInputDialog.getText(None, "title", "label")
        assert text == ""
        assert accepted is False


def test_classMethodGetInt(qapp):
    with (
        mock.patch.object(MWInputDialog, "exec", return_value=MWInputDialog.Accepted),
        mock.patch.object(MWInputDialog, "getValue", return_value="42"),
        mock.patch.object(MWInputDialog, "wasAccepted", return_value=True),
    ):
        value, accepted = MWInputDialog.getInt(None, "title", "label")
        assert value == 42
        assert accepted is True


def test_classMethodGetIntInvalid(qapp):
    with (
        mock.patch.object(MWInputDialog, "exec", return_value=MWInputDialog.Rejected),
        mock.patch.object(MWInputDialog, "getValue", return_value=""),
        mock.patch.object(MWInputDialog, "wasAccepted", return_value=False),
    ):
        value, accepted = MWInputDialog.getInt(None, "title", "label")
        assert value == 0
        assert accepted is False


def test_classMethodGetDouble(qapp):
    with (
        mock.patch.object(MWInputDialog, "exec", return_value=MWInputDialog.Accepted),
        mock.patch.object(MWInputDialog, "getValue", return_value="3.14159"),
        mock.patch.object(MWInputDialog, "wasAccepted", return_value=True),
    ):
        value, accepted = MWInputDialog.getDouble(None, "title", "label")
        assert value == pytest.approx(3.14159)
        assert accepted is True


def test_classMethodGetDoubleInvalid(qapp):
    with (
        mock.patch.object(MWInputDialog, "exec", return_value=MWInputDialog.Rejected),
        mock.patch.object(MWInputDialog, "getValue", return_value=""),
        mock.patch.object(MWInputDialog, "wasAccepted", return_value=False),
    ):
        value, accepted = MWInputDialog.getDouble(None, "title", "label")
        assert value == 0.0
        assert accepted is False


def test_directInstantiationText(qapp):
    dlg = MWInputDialog(
        parent=None,
        title="Text Input",
        label="Enter some text:",
        actualValue="initial",
        inputMode="text",
    )
    assert dlg.inputMode == "text"
    assert dlg.inputEdit.text() == "initial"
    dlg.close()


def test_directInstantiationInt(qapp):
    dlg = MWInputDialog(
        parent=None,
        title="Integer Input",
        label="Enter a number:",
        actualValue="100",
        inputMode="int",
    )
    assert dlg.inputMode == "int"
    assert dlg.inputWidget.value() == 100
    dlg.close()


def test_directInstantiationDouble(qapp):
    dlg = MWInputDialog(
        parent=None,
        title="Double Input",
        label="Enter a decimal:",
        actualValue="2.71828",
        inputMode="double",
        decimals=5,
    )
    assert dlg.inputMode == "double"
    assert dlg.inputWidget.value() == pytest.approx(2.71828)
    dlg.close()


def test_intMinMaxValid(qapp):
    d = MWInputDialog(title="title", label="label", inputMode="int", minValue=10, maxValue=50)
    d.inputWidget.setValue(30)
    with mock.patch.object(d, "close"):
        d.onAccept()
    assert d.resultCode == MWInputDialog.Accepted
    d.close()


def test_intMinMaxTooLow(qapp):
    d = MWInputDialog(title="title", label="label", inputMode="int", minValue=10, maxValue=50)
    d.inputWidget.setValue(5)
    assert d.inputWidget.value() == 10
    d.close()


def test_intMinMaxTooHigh(qapp):
    d = MWInputDialog(title="title", label="label", inputMode="int", minValue=10, maxValue=50)
    d.inputWidget.setValue(100)
    assert d.inputWidget.value() == 50
    d.close()


def test_doubleMinMaxValid(qapp):
    d = MWInputDialog(
        title="title",
        label="label",
        inputMode="double",
        minValue=0.0,
        maxValue=100.0,
    )
    d.inputWidget.setValue(50.5)
    with mock.patch.object(d, "close"):
        d.onAccept()
    assert d.resultCode == MWInputDialog.Accepted
    d.close()


def test_doubleMinMaxTooLow(qapp):
    d = MWInputDialog(
        title="title",
        label="label",
        inputMode="double",
        minValue=0.0,
        maxValue=100.0,
    )
    d.inputWidget.setValue(-5.5)
    assert d.inputWidget.value() == pytest.approx(0.0)
    d.close()


def test_doubleMinMaxTooHigh(qapp):
    d = MWInputDialog(
        title="title",
        label="label",
        inputMode="double",
        minValue=0.0,
        maxValue=100.0,
    )
    d.inputWidget.setValue(150.5)
    assert d.inputWidget.value() == pytest.approx(100.0)
    d.close()


def test_classMethodGetTextWithEchoMode(qapp):
    from PySide6.QtWidgets import QLineEdit

    with (
        mock.patch.object(MWInputDialog, "exec"),
        mock.patch.object(MWInputDialog, "getValue", return_value="secret"),
        mock.patch.object(MWInputDialog, "wasAccepted", return_value=True),
    ):
        text, accepted = MWInputDialog.getText(
            None,
            "title",
            "label",
            echoMode=QLineEdit.EchoMode.Password,
        )
        assert text == "secret"
        assert accepted is True


def test_classMethodGetIntWithMinMax(qapp):
    with (
        mock.patch.object(MWInputDialog, "exec"),
        mock.patch.object(MWInputDialog, "getValue", return_value="25"),
        mock.patch.object(MWInputDialog, "wasAccepted", return_value=True),
    ):
        value, accepted = MWInputDialog.getInt(
            None,
            "title",
            "label",
            minValue=10,
            maxValue=50,
        )
        assert value == 25
        assert accepted is True


def test_classMethodGetIntOutOfRange(qapp):
    with (
        mock.patch.object(MWInputDialog, "exec"),
        mock.patch.object(MWInputDialog, "getValue", return_value="5"),
        mock.patch.object(MWInputDialog, "wasAccepted", return_value=False),
    ):
        value, accepted = MWInputDialog.getInt(
            None,
            "title",
            "label",
            minValue=10,
            maxValue=50,
        )
        assert value == 0
        assert accepted is False


def test_classMethodGetDoubleWithMinMax(qapp):
    with (
        mock.patch.object(MWInputDialog, "exec"),
        mock.patch.object(MWInputDialog, "getValue", return_value="50.5"),
        mock.patch.object(MWInputDialog, "wasAccepted", return_value=True),
    ):
        value, accepted = MWInputDialog.getDouble(
            None,
            "title",
            "label",
            minValue=0.0,
            maxValue=100.0,
            decimals=2,
        )
        assert value == pytest.approx(50.5)
        assert accepted is True


def test_classMethodGetDoubleOutOfRange(qapp):
    with (
        mock.patch.object(MWInputDialog, "exec"),
        mock.patch.object(MWInputDialog, "getValue", return_value="150.5"),
        mock.patch.object(MWInputDialog, "wasAccepted", return_value=False),
    ):
        value, accepted = MWInputDialog.getDouble(
            None,
            "title",
            "label",
            minValue=0.0,
            maxValue=100.0,
        )
        assert value == 0.0
        assert accepted is False


def test_textModeUsesQLineEdit(qapp):
    from PySide6.QtWidgets import QLineEdit

    d = MWInputDialog(inputMode="text", title="title", label="label")
    assert isinstance(d.inputWidget, QLineEdit)
    d.close()


def test_intModeUsesQSpinBox(qapp):
    from PySide6.QtWidgets import QSpinBox

    d = MWInputDialog(inputMode="int", title="title", label="label")
    assert isinstance(d.inputWidget, QSpinBox)
    d.close()


def test_doubleModeUsesQDoubleSpinBox(qapp):
    from PySide6.QtWidgets import QDoubleSpinBox

    d = MWInputDialog(inputMode="double", title="title", label="label")
    assert isinstance(d.inputWidget, QDoubleSpinBox)
    d.close()


def test_textWidgetMinimumHeight(qapp):
    d = MWInputDialog(inputMode="text", title="title", label="label")
    assert d.inputWidget.minimumHeight() == 25
    d.close()


def test_intWidgetMinimumHeight(qapp):
    d = MWInputDialog(inputMode="int", title="title", label="label")
    assert d.inputWidget.minimumHeight() == 25
    d.close()


def test_doubleWidgetMinimumHeight(qapp):
    d = MWInputDialog(inputMode="double", title="title", label="label")
    assert d.inputWidget.minimumHeight() == 25
    d.close()


def test_initItemMode(qapp):
    items = ["Item 1", "Item 2", "Item 3"]
    d = MWInputDialog(
        title="title",
        label="label",
        inputMode="item",
        items=items,
        currentIndex=1,
    )
    assert d.inputMode == "item"
    assert d.items == items
    assert d.currentIndex == 1
    d.close()


def test_directInstantiationItem(qapp):
    from PySide6.QtWidgets import QComboBox

    items = ["Option A", "Option B", "Option C"]
    dlg = MWInputDialog(
        parent=None,
        title="Item Input",
        label="Choose an item:",
        inputMode="item",
        items=items,
        currentIndex=0,
    )
    assert dlg.inputMode == "item"
    assert isinstance(dlg.inputWidget, QComboBox)
    assert dlg.inputWidget.count() == 3
    assert dlg.inputWidget.currentText() == "Option A"
    dlg.close()


def test_itemModeUsesQComboBox(qapp):
    from PySide6.QtWidgets import QComboBox

    d = MWInputDialog(
        inputMode="item",
        title="title",
        label="label",
        items=["a", "b"],
    )
    assert isinstance(d.inputWidget, QComboBox)
    d.close()


def test_itemWidgetMinimumHeight(qapp):
    d = MWInputDialog(
        inputMode="item",
        title="title",
        label="label",
        items=["a", "b"],
    )
    assert d.inputWidget.minimumHeight() == 25
    d.close()


def test_onAcceptValidItem(qapp):
    items = ["Apple", "Banana", "Cherry"]
    d = MWInputDialog(
        title="title",
        label="label",
        inputMode="item",
        items=items,
        currentIndex=1,
    )
    with mock.patch.object(d, "close"):
        d.onAccept()
    assert d.resultCode == MWInputDialog.Accepted
    assert d.inputValue == "Banana"
    d.close()


def test_validateInputItem(qapp):
    d = MWInputDialog(
        title="title",
        label="label",
        inputMode="item",
        items=["Item 1", "Item 2"],
    )
    assert d.validateInput("Item 1") is True
    assert d.validateInput("Item 2") is True
    assert d.validateInput("") is False
    d.close()


def test_classMethodGetItem(qapp):
    items = ["Red", "Green", "Blue"]
    with (
        mock.patch.object(MWInputDialog, "exec"),
        mock.patch.object(MWInputDialog, "getValue", return_value="Green"),
        mock.patch.object(MWInputDialog, "wasAccepted", return_value=True),
    ):
        item, accepted = MWInputDialog.getItem(
            None,
            "Color",
            "Select a color:",
            items,
            currentIndex=1,
        )
        assert item == "Green"
        assert accepted is True


def test_classMethodGetItemRejected(qapp):
    items = ["Red", "Green", "Blue"]
    with (
        mock.patch.object(MWInputDialog, "exec"),
        mock.patch.object(MWInputDialog, "getValue", return_value=""),
        mock.patch.object(MWInputDialog, "wasAccepted", return_value=False),
    ):
        item, accepted = MWInputDialog.getItem(
            None,
            "Color",
            "Select a color:",
            items,
            currentIndex=0,
        )
        assert item == ""
        assert accepted is False


def test_itemWithDifferentCurrentIndex(qapp):
    items = ["First", "Second", "Third", "Fourth"]
    d = MWInputDialog(
        title="title",
        label="label",
        inputMode="item",
        items=items,
        currentIndex=2,
    )
    assert d.inputWidget.currentIndex() == 2
    assert d.inputWidget.currentText() == "Third"
    d.close()


def test_itemWithEmptyList(qapp):
    d = MWInputDialog(
        title="title",
        label="label",
        inputMode="item",
        items=[],
    )
    assert d.inputWidget.count() == 0
    d.close()


def test_itemMultipleAccepts(qapp):
    items = ["A", "B", "C"]
    d = MWInputDialog(
        title="title",
        label="label",
        inputMode="item",
        items=items,
        currentIndex=0,
    )
    # First accept
    with mock.patch.object(d, "close"):
        d.onAccept()
    assert d.resultCode == MWInputDialog.Accepted
    assert d.inputValue == "A"

    # Change selection and accept again
    d.inputWidget.setCurrentIndex(1)
    d.resultCode = MWInputDialog.Rejected
    d.inputValue = ""
    with mock.patch.object(d, "close"):
        d.onAccept()
    assert d.resultCode == MWInputDialog.Accepted
    assert d.inputValue == "B"
    d.close()


def test_getItemDefaultCurrentIndex(qapp):
    items = ["Option 1", "Option 2", "Option 3"]
    with (
        mock.patch.object(MWInputDialog, "exec"),
        mock.patch.object(MWInputDialog, "getValue", return_value="Option 1"),
        mock.patch.object(MWInputDialog, "wasAccepted", return_value=True),
    ):
        item, accepted = MWInputDialog.getItem(
            None,
            "Choose",
            "Select option:",
            items,
        )
        assert item == "Option 1"
        assert accepted is True


def test_initIntModeWithInvalidValue(qapp):
    d = MWInputDialog(
        title="title",
        label="label",
        inputMode="int",
        actualValue="not_a_number",
    )
    # Should default to 0 due to exception handling
    assert d.inputWidget.value() == 0
    d.close()


def test_initDoubleModeWithInvalidValue(qapp):
    d = MWInputDialog(
        title="title",
        label="label",
        inputMode="double",
        actualValue="not_a_number",
    )
    # Should default to 0.0 due to exception handling
    assert d.inputWidget.value() == 0.0
    d.close()


def test_classMethodGetIntWithInvalidValue(qapp):
    with (
        mock.patch.object(MWInputDialog, "exec"),
        mock.patch.object(MWInputDialog, "getValue", return_value="not_an_int"),
        mock.patch.object(MWInputDialog, "wasAccepted", return_value=True),
    ):
        value, accepted = MWInputDialog.getInt(None, "title", "label")
        assert value == 0
        assert accepted is False


def test_classMethodGetDoubleWithInvalidValue(qapp):
    with (
        mock.patch.object(MWInputDialog, "exec"),
        mock.patch.object(MWInputDialog, "getValue", return_value="not_a_float"),
        mock.patch.object(MWInputDialog, "wasAccepted", return_value=True),
    ):
        value, accepted = MWInputDialog.getDouble(None, "title", "label")
        assert value == 0.0
        assert accepted is False
