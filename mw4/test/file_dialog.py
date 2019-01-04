import PyQt5.QtWidgets as QtWidgets
import sys
import mw4.gui.widget as widget


class HelloWindow(QtWidgets.QMainWindow, widget.MWidget):
    def __init__(self):
        super().__init__()

        dlg = QtWidgets.QFileDialog()
        dlg.setStyleSheet(self.getStyle())
        options = QtWidgets.QFileDialog.DontUseNativeDialog
        name, _ = dlg.getOpenFileName(dlg,
                                      'test',
                                      '.',
                                      'Config (*.cfg)',
                                      options=options)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWin = HelloWindow()
    mainWin.show()
    sys.exit(app.exec_())
