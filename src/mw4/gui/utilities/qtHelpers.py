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
from importlib.resources import as_file, files
from mw4.mountcontrol.convert import formatDstrToText, formatHstrToText
from PySide6.QtCore import (
    QEvent,
    QObject,
    Qt,
    Signal,
    SignalInstance,
)
from PySide6.QtGui import (
    QColor,
    QIcon,
    QImage,
    QMouseEvent,
    QPainter,
    QPixmap,
)
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QLineEdit,
    QTableWidget,
    QTabWidget,
    QWidget,
)
from qimage2ndarray import array2qimage, rgb_view
from skyfield.api import Angle


def changeStyleDynamic(widget: QWidget, widgetProperty: str, value: str) -> None:
    if widget.property(widgetProperty) == value:
        return
    if widgetProperty == "background":
        print(widget, widget.objectName())

    widget.setProperty(widgetProperty, value)
    widget.style().unpolish(widget)
    widget.style().polish(widget)
    pass


def findIndexValue(ui: QComboBox, searchString: str, relaxed: bool = False) -> int:
    for index in range(ui.model().rowCount()):
        modelIndex = ui.model().index(index, 0)
        indexValue = ui.model().data(modelIndex)

        if not indexValue:
            continue
        if relaxed:
            if searchString in indexValue:
                return index
        else:
            if indexValue.startswith(searchString):
                return index
    return 0


def guiSetText(
    ui: QLineEdit, formatElement: str, value: float | Angle | str | bool | None
) -> None:
    if value is None:
        text = ""
    elif formatElement.startswith("HSTR"):
        text = formatHstrToText(value)
    elif formatElement.startswith("DSTR"):
        text = formatDstrToText(value)
    elif formatElement.startswith("D"):
        formatStr = "{0:" + formatElement.lstrip("D") + "}"
        text = formatStr.format(value.degrees)
    elif formatElement.startswith("H"):
        formatStr = "{0:" + formatElement.lstrip("H") + "}"
        text = formatStr.format(value.hours)
    elif value == "E":
        text = "EAST"
    elif value == "W":
        text = "WEST"
    elif isinstance(value, bool):
        text = "ON" if value else "OFF"
    else:
        formatStr = "{0:" + formatElement + "}"
        text = formatStr.format(value)
    ui.setText(text)


def clickable(widget: QWidget) -> SignalInstance:
    class MouseClickEventFilter(QObject):
        clicked = Signal(object)

        def eventFilter(self, obj: QWidget, event: QMouseEvent):
            if event.type() == QEvent.Type.MouseButtonRelease:
                if obj.rect().contains(event.pos()):
                    self.clicked.emit(widget)
                return True
            else:
                return False

    clickEventFilter = MouseClickEventFilter(widget)
    widget.installEventFilter(clickEventFilter)
    if not hasattr(widget, "clickFilters"):
        widget.clickFilters = []
    widget.clickFilters.append(clickEventFilter)
    return clickEventFilter.clicked


def setPixmapAlpha(pixmap: QPixmap, opacity: float) -> QPixmap:
    """Returns a new QPixmap with the specified opacity (0.0 to 1.0)."""
    # Create a blank pixmap of the same size supporting transparency
    transparent_pixmap = QPixmap(pixmap.size())
    transparent_pixmap.fill(Qt.GlobalColor.transparent)
    # Init painter to draw onto our new transparent pixmap
    painter = QPainter(transparent_pixmap)
    painter.setOpacity(opacity)
    painter.drawPixmap(0, 0, pixmap)
    painter.end()
    return transparent_pixmap


def img2pixmap(imageFilePath: str) -> QPixmap:
    with as_file(files("mw4").joinpath(imageFilePath)) as imageFile:
        image = QImage(str(imageFile))
    image.convertToFormat(QImage.Format.Format_RGB32)
    imgArr = rgb_view(image)
    image = array2qimage(imgArr)
    pixmap = QPixmap().fromImage(image)
    return pixmap


def svg2pixmap(svgFileName: str, color: list[int]) -> QPixmap:
    with as_file(files("mw4").joinpath(svgFileName)) as image:
        img = QPixmap(image)
    qp = QPainter(img)
    qp.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
    color = color[0:3]
    qp.fillRect(img.rect(), QColor(*color))
    qp.end()
    return img


def svg2icon(svgFileName: str, color: list[int]) -> QIcon:
    img = svg2pixmap(svgFileName, color)
    return QIcon(img)


def getTabIndex(tab: QTabWidget, name: str) -> int:
    tabWidget = tab.findChild(QWidget, name)
    tabIndex = tab.indexOf(tabWidget)
    return tabIndex


def getTabAndIndex(tab: QTabWidget, config: dict, name: str) -> None:
    config[name] = {"index": tab.currentIndex()}
    for index in range(tab.count()):
        config[name][f"{index:02d}"] = tab.widget(index).objectName()


def setTabAndIndex(tab: QTabWidget, config: dict, name: str) -> None:
    config = config.get(name, {})
    if not isinstance(config, dict):
        config = {}
    for index in reversed(range(tab.count())):
        nameTab = config.get(f"{index:02d}", "")
        if nameTab is None:
            continue
        tabIndex = getTabIndex(tab, nameTab)
        tab.tabBar().moveTab(tabIndex, index)
    tab.setCurrentIndex(config.get("index", 0))


def positionCursorInTable(table: QTableWidget, searchName: str) -> None:
    result = table.findItems(searchName, Qt.MatchFlag.MatchExactly)
    if len(result) == 0:
        return
    item = result[0]
    index = table.row(item)
    table.selectRow(index)
    table.scrollToItem(item, QAbstractItemView.ScrollHint.EnsureVisible)
