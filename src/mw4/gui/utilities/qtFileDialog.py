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
import re
import shlex
from enum import IntEnum
from mw4.gui.utilities.qtMain import MWidget
from pathlib import Path
from PySide6.QtCore import QDir, QEventLoop, QModelIndex, Qt
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFileSystemModel,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QToolButton,
    QTreeView,
    QVBoxLayout,
    QWidget,
)


class MWFileDialog(MWidget):
    """
    Lightweight, themed file/directory chooser built on top of the frameless
    :class:`MWidget`. Provides the small subset of features MW4 actually
    needs: browse the file system, select a single file, multiple files or a
    directory, type a file name, switch between named filters and accept or
    cancel the selection.

    The dialog is not a :class:`QDialog` – :meth:`exec` runs a local
    :class:`QEventLoop` so the call site can stay synchronous, mirroring
    Qt's own ``QDialog.exec()`` semantics.
    """

    class AcceptMode(IntEnum):
        AcceptOpen = 0
        AcceptSave = 1

    class FileMode(IntEnum):
        AnyFile = 0
        ExistingFile = 1
        ExistingFiles = 2
        Directory = 3

    Accepted = 1
    Rejected = 0

    def __init__(
        self,
        parent: QWidget | None = None,
        title: str = "Select",
        folder: Path | str = Path(""),
        filterSet: str = "All files (*)",
        acceptMode: "MWFileDialog.AcceptMode" = AcceptMode.AcceptOpen,
        fileMode: "MWFileDialog.FileMode" = FileMode.ExistingFile,
    ) -> None:
        super().__init__()
        self.acceptMode = acceptMode
        self.fileMode = fileMode
        self.resultCode: int = self.Rejected
        self.selected: list[Path] = []
        self.currentDir: Path = Path(folder)
        self.eventLoop = QEventLoop()
        self.setWindowTitle(title)
        self.resize(self.FULL_WIDTH, self.FULL_HEIGHT)

        self.model = QFileSystemModel(self)
        self.model.setRootPath("")
        if fileMode == self.FileMode.Directory:
            self.model.setFilter(QDir.Filter.AllDirs | QDir.Filter.NoDotAndDotDot)
        else:
            self.model.setFilter(QDir.Filter.AllEntries | QDir.Filter.NoDotAndDotDot)

        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setSelectionMode(
            QAbstractItemView.SelectionMode.ExtendedSelection
            if fileMode == self.FileMode.ExistingFiles
            else QAbstractItemView.SelectionMode.SingleSelection
        )
        self.tree.setSortingEnabled(True)
        self.tree.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tree.doubleClicked.connect(self.onDoubleClicked)

        self.upButton = QToolButton()
        self.upButton.setText("⬆")
        self.upButton.setToolTip("Parent directory")
        self.upButton.clicked.connect(self.onUp)

        self.pathEdit = QLineEdit()
        self.pathEdit.returnPressed.connect(self.onPathEntered)

        self.fileNameEdit = QLineEdit()
        self.fileNameEdit.returnPressed.connect(self.onAccept)

        self.filterCombo = QComboBox()
        for entry in [f.strip() for f in filterSet.split(";;") if f.strip()]:
            self.filterCombo.addItem(entry)
        if self.filterCombo.count() == 0:
            self.filterCombo.addItem("All files (*)")
        self.filterCombo.currentTextChanged.connect(self.onFilterChanged)

        acceptText = "Open" if acceptMode == self.AcceptMode.AcceptOpen else "Save"
        if fileMode == self.FileMode.Directory:
            acceptText = "Choose"
        self.btnAccept = QPushButton(acceptText)
        self.btnAccept.clicked.connect(self.onAccept)
        self.btnCancel = QPushButton("Cancel")
        self.btnCancel.clicked.connect(self.onReject)

        topRow = QHBoxLayout()
        topRow.addWidget(self.upButton)
        topRow.addWidget(self.pathEdit, 1)

        nameRow = QHBoxLayout()
        nameRow.addWidget(QLabel("File name:"))
        nameRow.addWidget(self.fileNameEdit, 1)

        filterRow = QHBoxLayout()
        filterRow.addWidget(QLabel("Files of type:"))
        filterRow.addWidget(self.filterCombo, 1)

        buttonRow = QHBoxLayout()
        buttonRow.addStretch(1)
        buttonRow.addWidget(self.btnAccept)
        buttonRow.addWidget(self.btnCancel)

        contentLayout = QVBoxLayout(self.ws)
        contentLayout.addLayout(topRow)
        contentLayout.addWidget(self.tree, 1)
        contentLayout.addLayout(nameRow)
        contentLayout.addLayout(filterRow)
        contentLayout.addLayout(buttonRow)

        self.setCurrentDir(self.currentDir)
        self.tree.selectionModel().selectionChanged.connect(self.onSelectionChanged)
        self.onFilterChanged(self.filterCombo.currentText())

        if parent is not None:
            self.move(
                parent.x() + max(0, (parent.width() - self.width()) // 2),
                parent.y() + max(0, (parent.height() - self.height()) // 2),
            )

    def setCurrentDir(self, folder: Path) -> None:
        if not folder.exists() or not folder.is_dir():
            folder = Path.home()
        idx = self.model.index(str(folder))
        self.tree.setRootIndex(idx)
        self.pathEdit.setText(str(folder))
        self.currentDir = folder

    def onUp(self) -> None:
        parent = self.currentDir.parent
        if parent != self.currentDir:
            self.setCurrentDir(parent)

    def onPathEntered(self) -> None:
        candidate = Path(self.pathEdit.text()).expanduser()
        if candidate.is_dir():
            self.setCurrentDir(candidate)
        else:
            self.pathEdit.setText(str(self.currentDir))

    def onFilterChanged(self, text: str) -> None:
        match = re.search(r"\((.*?)\)", text)
        patterns = match.group(1).split() if match else ["*"]
        if not patterns:
            patterns = ["*"]
        self.model.setNameFilters(patterns)
        self.model.setNameFilterDisables(False)

    def onSelectionChanged(self, *_: object) -> None:
        indexes = [i for i in self.tree.selectionModel().selectedIndexes() if i.column() == 0]
        names: list[str] = []
        for idx in indexes:
            path = Path(self.model.filePath(idx))
            if self.fileMode == self.FileMode.Directory:
                if path.is_dir():
                    names.append(path.name)
            else:
                if path.is_file():
                    names.append(path.name)
        if len(names) > 1:
            text = " ".join(f'"{n}"' if " " in n else n for n in names)
        else:
            text = names[0] if names else ""
        self.fileNameEdit.setText(text)

    def onDoubleClicked(self, idx: QModelIndex) -> None:
        path = Path(self.model.filePath(idx))
        if path.is_dir():
            self.setCurrentDir(path)
        elif path.is_file() and self.fileMode != self.FileMode.Directory:
            self.fileNameEdit.setText(path.name)
            self.onAccept()

    def parseFileNames(self, text: str) -> list[str]:
        text = text.strip()
        if not text:
            return []
        if self.fileMode == self.FileMode.ExistingFiles:
            try:
                return [n for n in shlex.split(text) if n]
            except ValueError:
                return [text]
        return [text]

    def resolveSelection(self) -> list[Path]:
        text = self.fileNameEdit.text()
        names = self.parseFileNames(text)
        if self.fileMode == self.FileMode.Directory:
            if not names:
                return [self.currentDir]
            return [self.currentDir / names[0]]
        return [self.currentDir / n for n in names]

    def onAccept(self) -> None:
        selection = self.resolveSelection()
        if not selection:
            return
        if self.fileMode == self.FileMode.ExistingFile and not selection[0].is_file():
            return
        if self.fileMode == self.FileMode.ExistingFiles and not all(
            p.is_file() for p in selection
        ):
            return
        if self.fileMode == self.FileMode.Directory and not selection[0].is_dir():
            return
        self.selected = selection
        self.resultCode = self.Accepted
        self.finishLoop()
        self.close()

    def onReject(self) -> None:
        self.selected = []
        self.resultCode = self.Rejected
        self.finishLoop()
        self.close()

    def finishLoop(self) -> None:
        if self.eventLoop.isRunning():
            self.eventLoop.quit()

    def closeEvent(self, event: QCloseEvent) -> None:
        if self.eventLoop.isRunning():
            self.selected = []
            self.resultCode = self.Rejected
            self.eventLoop.quit()
        super().closeEvent(event)

    def exec(self) -> int:
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.show()
        self.eventLoop.exec()
        return self.resultCode

    def selectedFiles(self) -> list[Path]:
        return list(self.selected)

    @classmethod
    def getOpenFileName(
        cls,
        parent: QWidget | None,
        title: str,
        folder: Path,
        filterSet: str,
    ) -> Path:
        dlg = cls(
            parent=parent,
            title=title,
            folder=folder,
            filterSet=filterSet,
            acceptMode=cls.AcceptMode.AcceptOpen,
            fileMode=cls.FileMode.ExistingFile,
        )
        dlg.exec()
        files = dlg.selectedFiles()
        return files[0] if files else Path()

    @classmethod
    def getOpenFileNames(
        cls,
        parent: QWidget | None,
        title: str,
        folder: Path,
        filterSet: str,
    ) -> list[Path]:
        dlg = cls(
            parent=parent,
            title=title,
            folder=folder,
            filterSet=filterSet,
            acceptMode=cls.AcceptMode.AcceptOpen,
            fileMode=cls.FileMode.ExistingFiles,
        )
        dlg.exec()
        return dlg.selectedFiles()

    @classmethod
    def getSaveFileName(
        cls,
        parent: QWidget | None,
        title: str,
        folder: Path,
        filterSet: str,
    ) -> Path:
        dlg = cls(
            parent=parent,
            title=title,
            folder=folder,
            filterSet=filterSet,
            acceptMode=cls.AcceptMode.AcceptSave,
            fileMode=cls.FileMode.AnyFile,
        )
        dlg.exec()
        files = dlg.selectedFiles()
        return files[0] if files else Path()

    @classmethod
    def getExistingDirectory(
        cls,
        parent: QWidget | None,
        title: str,
        folder: Path,
    ) -> Path:
        dlg = cls(
            parent=parent,
            title=title,
            folder=folder,
            acceptMode=cls.AcceptMode.AcceptOpen,
            fileMode=cls.FileMode.Directory,
        )
        dlg.exec()
        files = dlg.selectedFiles()
        return files[0] if files else Path()
