import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import PyQt5
import sys
import mw4.gui.widget as widget
from mw4.gui.media import resources


class HelloWindow(QtWidgets.QMainWindow, widget.MWidget):
    def __init__(self):
        super().__init__()

        dlg = QtWidgets.QFileDialog()
        dlg.setStyleSheet(self.getStyle())
        options = QtWidgets.QFileDialog.DontUseNativeDialog
        dlg.setOption(options)
        dlg.setNameFilter('Config files (*.cfg)')
        dlg.setWindowTitle('Test')
        dlg.setFilter(QtCore.QDir.Files)
        dlg.setWindowIcon(PyQt5.QtGui.QIcon(':/mw4.ico'))
        dlg.setDirectory('./config')
        dlg.setFixedWidth(400)
        dlg.setFixedHeight(400)

        dlg.findChildren(QtWidgets.QListView, 'sidebar')[0].setVisible(False)
        dlg.findChildren(QtWidgets.QComboBox, 'lookInCombo')[0].setVisible(False)
        dlg.findChildren(QtWidgets.QLabel, 'lookInLabel')[0].setVisible(False)
        dlg.findChildren(QtWidgets.QWidget, 'backButton')[0].setVisible(False)
        dlg.findChildren(QtWidgets.QWidget, 'forwardButton')[0].setVisible(False)
        dlg.findChildren(QtWidgets.QWidget, 'toParentButton')[0].setVisible(False)
        dlg.findChildren(QtWidgets.QWidget, 'newFolderButton')[0].setVisible(False)
        dlg.findChildren(QtWidgets.QWidget, 'listModeButton')[0].setVisible(False)
        dlg.findChildren(QtWidgets.QWidget, 'detailModeButton')[0].setVisible(False)

        dlg.setAcceptMode(QtWidgets.QFileDialog.AcceptOpen)

        # dlg.findChildren(QtWidgets.QGridLayout, 'gridLayout')[0].setEnabled(False)

        a = dlg.findChildren(QtWidgets.QWidget)
        for i, widget in enumerate(a):
            # print(i, widget.objectName())
            colora = int(i / len(a) * 255)
            colorb = int((len(a) - i) / len(a) * 255)
            # widget.setStyleSheet('background-color: rgb({0},{1},0);'.format(colora, colorb))
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            print(dlg.selectedFiles())


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWin = HelloWindow()
    mainWin.show()
    # sys.exit(app.exec_())
