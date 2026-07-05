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
MAC_STYLE = """
    QWidget {
        font-family: Arial;
        font-weight: normal;
        font-size: 13pt;
    }
    QLabel[title=true] {
        font-weight: bold;
        font-size: 18pt;
    }
    QWidget[large] {
        font-family: Arial;
        font-weight: normal;
        font-size: 30pt;
    }
    QGroupBox {
        font-family: Arial;
        font-weight: normal;
        font-size: 11pt;
    }
    QGroupBox[large] {
        font-weight: bold;
        font-size: 13pt;
    }
    QToolTip {
        font-size: 13pt;
    }
    QLineEdit[keypad=true]{
        font-family: Courier New;
        font-weight: bold;
        font-size: 26pt;
    }
    """

NON_MAC_STYLE = """
    QWidget {
        font-family: Arial;
        font-weight: normal;
        font-size: 10pt;
    }
    QLabel[title=true] {
        font-size: 15pt;
        font-weight: bold;
    }
    QWidget[large] {
        font-family: Arial;
        font-weight: bold;
        font-size: 20pt;
    }
    QGroupBox {
        font-family: Arial;
        font-weight: demibold;
        font-size: 8pt;
    }
    QGroupBox[large] {
        font-weight: bold;
        font-size: 10pt;
    }
    QToolTip {
        font-size: 10pt;
    }
    QLineEdit[keypad=true]{
        font-family: Courier New;
        font-weight: bold;
        font-size: 19pt;
    }
    """

BASIC_STYLE = """
    QWidget {
        background-color: $M_BACK$;
    }
    QWidget QGraphicsView{
        background-color: transparent;
    }
    QWidget #ContainerContent {
        border-radius: 3px;
        background-color: transparent;
    }
    QWidget #ContainerCentral {
        border-radius: 3px;
        border-style: solid;
        border-color: $M_PRIM1$;
        border-width: 2px;
    }
    QToolTip {
        border-width: 1px;
        border-style: outset;
        border-color: $M_SEC$;
        background-color: $M_BACK$;
        color: $M_PRIM$;
        padding: 5px;
        max-width: 500px;
    }
    QLabel{
        color: $M_TER$;
        background-color: transparent;
    }
    QLabel[keypad] {
        color: $M_PRIM$;
        border-radius: 8px;
    }
    QLabel:disabled {
        color: $M_SEC$;
    }
    QLabel[iconpicture='true'] {
        border-style: plain;
        border-radius: 0px;
    }
    QLabel[color='green'] {
        color: $M_GREEN$;
    }
    QLabel[color='yellow'] {
        color: $M_YELLOW$;
    }
    QLabel[color='red'] {
        color: $M_RED$;
    }
    QLabel[hid='green'] {
        border-style: solid;
        border-width: 1px;
        border-radius: 1px;
        border-color: $M_GREEN$;
    }
    /* QLine Edit*/
    QLineEdit {
        color: $M_PRIM$;
        background-color: transparent;
        text-align: right;
    }
    QLineEdit[readOnly='false'] {
        border-width: 1px;
        border-style: outset;
        border-color: $M_PRIM2$;
    }
    QLineEdit:disabled {
        color: $M_PRIM2$;
         border-color: $M_SEC$;
    }
    QLineEdit[keypad] {
        color: $M_PRIM$;
        border-width: 0px;
    }
    QLineEdit[color='green'] {
        border-width: 1px;
        border-style: outset;
        border-color: $M_GREEN$;
    }
    QLineEdit[color='yellow'] {
        border-width: 1px;
        border-style: outset;
        border-color: $M_YELLOW$;
    }
    QLineEdit[color='red'] {
        border-width: 1px;
        border-style: outset;
        border-color: $M_RED$;
    }
    /* Group Box */
    QGroupBox {
        border-width: 1px;
        border-style: outset;
        border-radius: 2px;
        border-color: $M_PRIM3$;
        margin-top: 6px;
    }
    QGroupBox::title {
        left: 5px;
        subcontrol-origin: margin;
        subcontrol-position: top left;
        color: $M_PRIM$;
    }
    QGroupBox[refraction=true] {
        border-color: $M_PRIM$;
    }
    QGroupBox::title:disabled{
        color: $M_PRIM3$;
    }
    QGroupBox[frameless=true] {
        border-width: 0px;
    }
    QGroupBox[frameless=true]:disabled {
        border-color: $M_RED$;
    }
    QGroupBox::indicator {
        border-color: $M_SEC$;
        border-width: 1px;
        border-color: $M_SEC$;
        border-style: outset;
        border-radius: 2px;
        width: 13px;
        height: 13px;
    }
    QGroupBox::indicator:checked {
        border-width: 1px;
        border-color: $M_PRIM$;
        background-color: $M_PRIM2$;
        image: url($checkmark$);
    }
    QGroupBox[run=true] {
        color: $M_TER$;
        border-color: $M_YELLOW$;
    }
    /* Checkboxes */
    QCheckBox {
        color: $M_TER$;
        spacing: 5px;
    }
    QCheckBox::indicator {
        border-width: 1px;
        border-color: $M_SEC$;
        background-color: $M_BACK$;
        border-style: outset;
        border-radius: 2px;
        width: 13px;
        height: 13px;
    }
    QCheckBox::indicator:checked {
        border-color: $M_PRIM$;
        background-color: $M_PRIM2$;
        image: url($checkmark$);
    }
    QCheckBox:disabled {
        color: $M_PRIM2$;
    }
    QCheckBox::indicator:checked:disabled {
        background-color: $M_BACK$;
        image: url($checkmark$);
    }
    QRadioButton {
        color: $M_TER$;
        spacing: 5px;
    }
    QRadioButton:disabled {
        color: $M_PRIM2$;
    }
    QRadioButton::indicator {
        border-width: 1px;
        border-color: $M_SEC$;
        background-color: $M_BACK$;
        border-style: outset;
        border-radius: 2px;
        width: 13px;
        height: 13px;
    }
    QRadioButton::indicator:checked {
        border-color: $M_PRIM$;
        background-color: $M_PRIM2$;
        image: url($radio$);
    }
    QRadioButton::indicator:checked:disabled {
        border-color: $M_PRIM2$;
        background-color: $M_PRIM4$;
        image: url($radio$);
    }
    /* Spin Boxes */
    QDoubleSpinBox {
        color: $M_PRIM$;
        border-color: $M_SEC$;
        border-width: 1px;
        border-style: outset;
        border-radius: 2px;
        padding-left: 2px;
    }
    QDoubleSpinBox:disabled {
        color: $M_PRIM2$;
    }
    QDoubleSpinBox::up-button {
        subcontrol-origin: border;
        subcontrol-position: top right;
        width: 12px;
        border-radius: 2px;
        border-width: 1px;
        border-color: $M_SEC$;
        border-style: outset;
    }
    QDoubleSpinBox::up-arrow {
        image: url($arrow-up$);
        width: 10px;
        height: 10px;
    }
    QDoubleSpinBox::down-button {
        subcontrol-origin: border;
        subcontrol-position: bottom right;
        width: 12px;
        border-style: outset;
        border-radius: 2px;
        border-width: 1px;
        border-color: $M_SEC$;
   }
    QDoubleSpinBox::down-arrow {
        image: url($arrow-down$);
        width: 10px;
        height: 10px;
    }
    QSpinBox {
        color: $M_PRIM$;
        border-color: $M_SEC$;
        border-width: 1px;
        border-style: outset;
        border-radius: 2px;
        padding-left: 2px;
        selection-background-color: $M_BACK$;
        selection-color: $M_PRIM$;
    }
    QSpinBox:disabled {
        color: $M_PRIM2$;
    }
    QSpinBox::up-button {
        subcontrol-origin: border;
        subcontrol-position: top right;
        width: 12px;
        border-radius: 2px;
        border-width: 1px;
        border-color: $M_SEC$;
        border-style: outset;
    }
    QSpinBox::up-arrow {
        image: url($arrow-up$);
        width: 10px;
        height: 10px;
    }
    QSpinBox::down-button {
        subcontrol-origin: border;
        subcontrol-position: bottom right;
        width: 12px;
        border-style: outset;
        border-radius: 2px;
        border-width: 1px;
        border-color: $M_SEC$;
   }
    QSpinBox::down-arrow {
        image: url($arrow-down$);
        width: 10px;
        height: 10px;
    }
    /* Push Buttons */
    QPushButton {
        color: $M_TER$;
        border-color: $M_SEC$;
        border-width: 1px;
        border-style: outset;
        border-radius: 2px;
        min - width: 10em;
    }
    QPushButton:default {
        border-color: $M_PRIM$;
        border-width: 2px;
        border-style: outset;
    }
    QPushButton[keypad] {
        border-color: $M_PRIM$;
        border-radius: 8px;
        border-width: 2px;
        border-style: outset;
        font-weight: bold;
        font-size: 12px;
    }
    QPushButton[alignLeft=true] {
        text-align: left;
        padding-left: 3px;
        padding-right: 3px;
    }
    QPushButton:pressed {
        background-color: $M_PRIM$;
    }
    QPushButton[color='gray'] {
        background-color: $M_GRAY$;
        color: $M_TER$;
    }
    QPushButton[color='green'] {
        background-color: $M_GREEN2$;
        border-color: $M_GREEN$;
        color: $M_TER$;
    }
    QPushButton[color='yellow'] {
        background-color: $M_YELLOW2$;
        border-color: $M_YELLOW$;
        color: $M_TER$;
    }
    QPushButton[color='red'] {
        background-color: $M_RED2$;
        border-color: $M_RED$;
        color: $M_TER$;
    }
    QPushButton[run=true] {
        background-color: $M_GREEN2$;
        border-color: $M_GREEN$;
        color: $M_TER$;
    }
    QPushButton[stop=true] {
        background-color: $M_RED2$;
        border-color: $M_RED$;
        color: $M_TER$;
    }
    QPushButton[pause=true] {
        background-color: $M_YELLOW2$;
        border-color: $M_YELLOW$;
        color: $M_TER$;
    }
    QPushButton:disabled {
        color: $M_PRIM2$;
        border-color: $M_SEC1$;
    }
    /* Message Boxes */
    QMessageBox QPushButton {
        min-width: 90px;
        min-height: 25px;
    }
    QMessageBox QPushButton:default {
        border-color: $M_PRIM$;
    }
    /* ListView */
    QListWidget {
        background-color: transparent;
    }
    QListWidget:item {
        color: $M_PRIM$;
        background-color: transparent;
    }
    QListWidget:item:selected {
        color: $M_TER$;
        background-color: $M_PRIM2$;
    }
    QListView {
        border-color: $M_SEC$;
        border-width: 0px;
        border-style: plain;
        border-radius: 0px;
        color: $M_TER$;
        padding: 0px;
        margin: 0px;
        border: 0px;
        color: $M_PRIM$;
        background-color: $M_BACK$;
    }
    /* Table Widget */
    QTableWidget {
        border-width: 0px;
        border-style: plain;
        border-radius: 0px;
        padding: 0px;
        margin: 0px;
        border: 0px;
        selection-background-color: $M_PRIM2$;
        selection-color: $M_TER$;
    }
    QTableWidget QHeaderView:section{
        border-width: 1px;
        border-style: plain;
        border-radius: 2px;
        background-color: $M_BACK1$;
        color: $M_TER$;
    }
    QTableWidget QHeaderView::down-arrow{
        subcontrol-position: upper;
        subcontrol-origin: padding;
        width: 15px;
        height: 6px;
    }
    QTableView::item {
        color: $M_PRIM$;
    }
    QTextBrowser {
        border-width: 0px;
        border-style: plain;
        border-radius: 0px;
        padding: 0px;
        margin: 0px;
        border: 0px;
        color: $M_PRIM$;
        font-family: Arial;
        font-weight: normal;
        font-size: 15pt;
    }
    /* Combo Boxes */
    QComboBox {
        combobox-popup: 0;
        color: $M_TER$;
        border-color: $M_SEC$;
        border-width: 1px;
        border-style: outset;
        border-radius: 2px;
        padding-left: 5px;
    }
    QComboBox:disabled {
        color: $M_PRIM2$;
    }
    QComboBox[active=true] {
        border-color: $M_GREEN$;
        background-color: $M_GREEN2$;
    }
    QComboBox::drop-down {
        subcontrol-origin: border;
        subcontrol-position: right;
        width: 24px;
        border-color: $M_SEC$;
        border-style: outset;
        border-width: 1px;
        border-radius: 2px;
        color: green;
    }
    QComboBox::down-arrow {
        image: url($arrow-down$);
        width: 16px;
        height: 16px;
    }
    QComboBox QListView {
        border-width: 1px;
        border-style: outset;
        border-color: $M_SEC$;
        border-radius: 2px;
        color: $M_TER$;
        min-height: 60px;
    }
    QComboBox QListView::item {
        border-color: $M_SEC$;
        min-height: 28px;
        background-color: $M_BACK1$;
    }
    QComboBox QListView::item:selected {
        background-color: $M_PRIM$;
    }
    /* lines */
    QFrame[frameShape="4"] {
        color: $M_PRIM1$;
    }
    QFrame[frameShape="5"] {
        color: $M_PRIM1$;
    }
    QFrame[title='true'] {
        color: $M_TER$;
        background: $M_PRIM2$;
        border-radius: 3px;
    }
    /* tab widget */
    QTabWidget:pane {
        top: -6px;
        padding-top: 6px;
        border-width: 0px;
    }
    QTabBar::tab {
        border-radius: 2px;
        border-width: 1px;
        border-style: outset;
        color: $M_TER2$;
        border-color: $M_TAB2$;
        padding-top: 6px;
        padding-bottom: 4px;
        padding-left: 4px;
        padding-right: 4px;
    }
    QTabBar::tab:selected {
        color: $M_TER$;
        border-color: $M_TAB$;
    }
    QTabBar::tab:only-one {
        margin: 1;
    }
    QTabBar::tab:disabled {
        color: $M_SEC1$;
        border-color: $M_SEC1$;
    }
    /* slider */
    QSlider {
        width: 16px;
        height: 16px;
        margin: 0px 3px 0px 3px;
        border-width: 1px;
        border-radius: 2px;
        border-color: $M_SEC$;
    }
    QSlider::add-page {
        background-color: $M_SEC1$;
    }
    QSlider::sub-page {
        background-color: $M_SEC1$;
    }

    /* scroll bar */
    QScrollBar {
        border-width: 1px;
        border-color: $M_SEC$;
        border-style: outset;
        border-radius: 2px;
    }
    QScrollBar:vertical {
        width: 16px;
        margin: 4px 4px 4px 4px;
    }
    QScrollBar:horizontal {
        height: 16px;
        margin: 4px 16px 4px 4px;
    }
    QScrollBar::handle {
        background-color: $M_PRIM$;
        min-height: 24px;
        min-width: 24px;
    }
    QScrollBar::sub-line {
        margin: 2px 0px 2px 0px;
        height: 0px;
        width: 0px;
        subcontrol-position: top;
        subcontrol-origin: margin;
    }
    QScrollBar::add-line {
        margin: 2px 0px 2px 0px;
        height: 0px;
        width: 0px;
        subcontrol-position: bottom;
        subcontrol-origin: margin;
    }
    QScrollBar::sub-line:on {
        height: 16px;
        width: 16px;
        subcontrol-position: top;
        subcontrol-origin: margin;
    }
    QScrollBar::add-line:on {
        height: 0px;
        width: 0px;
        subcontrol-position: bottom;
        subcontrol-origin: margin;
    }
    QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
        border-width: 0px;
        border-style: plain;
        border-radius: 0px;
    }
    /* progress bar */
    QProgressBar {
        color: white;
        text-align: center;
        border-style: outset;
        border-color: $M_PRIM2$;
        border-width: 1px;
        border-radius: 2px;
    }
    QProgressBar:disabled {
        color: $M_SEC$;
        border-color: $M_SEC$;
    }
    QProgressBar::chunk {
        border-radius: 2px;
        background-color: $M_PRIM$;
    }
    /* system replacements */
    QTreeView{
        color: $M_PRIM$;
        background-color: $M_BACK$;
    }
    QTreeView QHeaderView:section{
        border-width: 1px;
        border-style: plain;
        border-radius: 2px;
        color: $M_PRIM$;
        background-color: $M_BACK$;
    }

    """
