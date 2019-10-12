import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import PyQt5
import sys
import mw4.gui.widget as widget
from mw4.gui.media import resources


class HelloWindow(QtWidgets.QMainWindow, widget.MWidget):
    def __init__(self):
        super().__init__()

        dlg = QtWidgets.QInputDialog()
        dlg.setStyleSheet(self.getStyle())
        dlg.setWindowIcon(PyQt5.QtGui.QIcon(':/mw4.ico'))

        dlg.setWindowTitle('WindowText')
        dlg.setInputMode(QtWidgets.QInputDialog.IntInput)
        dlg.setIntRange(0, 100)
        dlg.setIntStep(5)
        dlg.setIntValue(50)
        dlg.setLabelText('LabelText')
        dlg.setOkButtonText('OK Text')
        dlg.setCancelButtonText('CancelText')
        dlg.setComboBoxEditable(False)
        print(dlg.comboBoxItems())

        dlg.setFixedWidth(400)
        dlg.setFixedHeight(400)

        a = dlg.findChildren(QtWidgets.QWidget)[0]
        #print(a)
        #a.setFocusPolicy(QtCore.Qt.NoFocus)

        a = dlg.findChildren(QtWidgets.QWidget)
        for i, widget in enumerate(a):
            print(i, widget.objectName())
            colora = int(i / len(a) * 255)
            colorb = int((len(a) - i) / len(a) * 255)
            # widget.setStyleSheet('background-color: rgb({0},{1},0);'.format(colora, colorb))


        print(dlg.exec_(), dlg.intValue())


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWin = HelloWindow()
    mainWin.show()
    # sys.exit(app.exec_())
