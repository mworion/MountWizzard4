############################################################
# -*- coding: utf-8 -*-
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PyQT5 for python
#
# written in python3, (c) 2019-2023 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import platform

# external packages

# local imports


class Styles:
    colorSet = 0

    def __init__(self):
        self.cs = {
            'M_TRANS': ['#00000000', '#00000000', '#00000000', ],
            'M_BLUE': ['#2090C0', '#C05050', '#000000', ],
            'M_BLUE1': ['#186C90', '#903838', '#C0C0C0', ],
            'M_BLUE2': ['#104860', '#602828', '#A0A0A0', ],
            'M_BLUE3': ['#092B39', '#481C1C', '#808080', ],
            'M_BLUE4': ['#04151C', '#241010', '#404040', ],
            'M_WHITE': ['#C0C0C0', '#E00000', '#101010', ],
            'M_WHITE1': ['#A0A0A0', '#A00000', '#404040', ],
            'M_GREY': ['#404040', '#402020', '#A0A0A0', ],
            'M_GREY1': ['#282828', '#201010', '#C0C0C0', ],
            'M_BACK': ['#181818', '#181818', '#E0E0E0', ],
            'M_BLACK': ['#000000', '#000000', '#FFFFFF', ],
            'M_RED': ['#D03030', '#C03030', '#600000', ],
            'M_RED1': ['#902020', '#802020', '#A00000', ],
            'M_RED2': ['#701818', '#802020', '#E00000', ],
            'M_YELLOW': ['#D0D000', '#D0D000', '#606000', ],
            'M_YELLOW1': ['#909000', '#808000', '#909000', ],
            'M_YELLOW2': ['#707000', '#A0A000', '#C0C000', ],
            'M_GREEN': ['#00C000', '#00C000', '#006000', ],
            'M_GREEN1': ['#008000', '#008000', '#009000', ],
            'M_GREEN2': ['#005000', '#00A000', '#00C000', ],
            'M_PINK': ['#FF00FF', '#C000C0', '#E000E0', ],
            'M_PINK1': ['#B000B0', '#900090', '#900090', ],
            'M_CYAN': ['#00FFFF', '#00FFFF', '#00FFFF', ],
            'M_CYAN1': ['#00B0B0', '#00B0B0', '#00B0B0', ],
            'checkmark': ['checkmark0', 'checkmark1', 'checkmark2', ],
            'arrow-up': ['arrow-up0', 'arrow-up1', 'arrow-up2', ],
            'arrow-down': ['arrow-down0', 'arrow-down1', 'arrow-down2', ],
            'radio': ['radio0', 'radio1', 'radio2', ],
        }

        self.MAC_STYLE = """
        QWidget {
            background-color: $M_BACK$;
            font-family: Arial;
            font-weight: normal;
            font-size: 13pt;
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
        QTextBrowser {
            font-family: Courier New;
            font-weight: bold;
            font-size: 13pt;
        }
        QListWidget {
            font-family: Courier New;
            font-weight: bold;
            font-size: 13pt;
        }
        QToolTip {
            font-size: 13pt;
        }
        QLineEdit[keypad]{
            font-family: Courier New;
            font-weight: bold;
            font-size: 26pt;
        }
        """

        self.NON_MAC_STYLE = """
        QWidget {
            background-color: $M_BACK$;
            font-family: Arial;
            font-weight: normal;
            font-size: 10pt;
        }
        QWidget[large] {
            font-family: Arial;
            font-weight: bold;
            font-size: 20pt;
        }
        QGroupBox {
            font-family: Arial;
            font-weight: normal;
            font-size: 8pt;
        }
        QGroupBox[large] {
            font-weight: bold;
            font-size: 10pt;
        }
        QTextBrowser {
            font-family: Courier New;
            font-weight: bold;
            font-size: 9pt;
        }
        QListWidget {
            font-family: Courier New;
            font-weight: bold;
            font-size: 9pt;
        }
        QToolTip {
            font-size: 10pt;
        }
        QLineEdit[keypad]{
            font-family: Courier New;
            font-weight: bold;
            font-size: 19pt;
        }
        """

        self.BASIC_STYLE = """
        QWidget {
            color: $M_BLUE$;
        }
        QLabel[keypad]{
            color: $M_BLUE$;
            background-color: $M_BACK$;
        }
        QTextEdit {
            color: $M_WHITE$;
            background-color: $M_BLACK$;
            border-radius: 0px;
        }
        QToolTip {
            border-width: 2px;
            border-style: outset;
            border-color: $M_GREY$;
            background-color: $M_BACK$;
            color: $M_BLUE$;
            padding: 5px;
            max-width: 500px;
        }
        QLabel {
            background-color: $M_TRANS$;
            color: $M_WHITE$;
        }
        QLabel[keypad] {
            background-color: $M_BLACK$;
            border-radius: 8px;
        }
        QLabel:disabled {
            background-color: $M_TRANS$;
            color: $M_GREY$;
        }
        QLabel[color='blue'] {
            border-width: 3px;
            border-color: $M_BLUE1$;
            border-style: outset;
            border-radius: 2px;
            background-color: $M_BLUE1$;
        }
        QLabel[iconpicture='true'] {
            border-width: 1px;
            border-color: $M_GREY$;
            border-style: plain;
            border-radius: 0px;
        }
        /* QLine Edit*/
        QLineEdit {
            background-color: $M_BLACK$;
            color: $M_BLUE$;
            text-align: right;
            border-width: 1px;
            border-color: $M_GREY$;
            border-style: flat;
            border-radius: 2px;
        }
        QLineEdit::item:active {
            border-color: $M_BLUE$;
        }
        QLineEdit:disabled {
            background-color: $M_GREY1$;
        }
        QLineEdit[keypad] {
            background-color: $M_BACK$;
            color: $M_BLUE$;
            border-width: 0px;
            border-color: $M_BACK$;
        }
        QLineEdit[input='true']{
            border-width: 1px;
            border-color: $M_GREY$;
            border-style: outset;
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
        QLineEdit[status='on'] {
            color: $M_WHITE$;
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
        /* Group Box */
        QGroupBox {
            background-color: $M_BACK$;
            border-width: 1px;
            border-style: outset;
            border-radius: 3px;
            border-color: $M_GREY$;
            margin-top: 6px;
        }
        QGroupBox::title {
            left: 5px;
            subcontrol-origin: margin;
            subcontrol-position: top left;
            color: $M_WHITE$;
            background-color: $M_BACK$;
        }
        QGroupBox::title[large=true] {
            left: 5px;
            subcontrol-origin: margin;
            subcontrol-position: top left;
            color: $M_BLUE$;
            background-color: $M_BACK$;
        }
        QGroupBox::title[refraction=true]{
            color: $M_BLUE$;
        }
        QGroupBox[refraction=true] {
            border-color: $M_BLUE$;
        }
        QGroupBox:disabled{
            border-color: $M_RED$;
        }
        QGroupBox::indicator:disabled {
            border-color: $M_GREY$;
            background-color: $M_BACK$;
        }
        QGroupBox::indicator:unchecked {
            border-color: $M_GREY$;
            background-color: $M_BACK$;
        }
        QGroupBox::title:disabled{
            color: $M_GREY$;
        }
        QGroupBox[frameless=true] {
            border-width: 0px;
        }
        QGroupBox[frameless=true]:disabled {
            border-width: 2px;
            border-color: $M_RED$;
        }
        QGroupBox::indicator {
            border-width: 2px;
            border-color: $M_GREY$;
            background-color: $M_BACK$;
            border-style: outset;
            border-radius: 2px;
            width: 13px;
            height: 13px;
        }
        QGroupBox::indicator:checked {
            border-width: 1px;
            border-color: $M_BLUE$;
            background-color: $M_BLUE2$;
            image: url(:/icon/$checkmark$.svg);
        }
        QGroupBox[running=true] {
            color: $M_WHITE$;
            border-color: $M_YELLOW$;
            background-color: $M_GREY1$;
        }
        QGroupBox:title[running=true] {
            color: $M_WHITE$;
        }
        /* Checkboxes */
        QCheckBox {
            color: $M_WHITE$;
            spacing: 5px;
            background-color: $M_TRANS$;;
        }
        QCheckBox::indicator {
            border-width: 1px;
            border-color: $M_GREY$;
            background-color: $M_BACK$;
            border-style: outset;
            border-radius: 2px;
            width: 13px;
            height: 13px;
        }
        QCheckBox::indicator:checked {
            border-width: 1px;
            border-color: $M_BLUE$;
            background-color: $M_BLUE2$;
            image: url(:/icon/$checkmark$.svg);
        }
        QCheckBox::indicator:disabled {
            background-color: $M_BACK$;
            border-color: $M_GREY$;
        }
        QCheckBox:disabled {
            color: $M_GREY$;
        }
        QRadioButton {
            color: $M_WHITE$;
            spacing: 5px;
            background-color: $M_TRANS$;;
        }
        QRadioButton:disabled {
            color: $M_GREY$;
            background-color: $M_TRANS$;;
        }
        QRadioButton::indicator {
            border-width: 2px;
            border-color: $M_GREY$;
            background-color: $M_BACK$;
            border-style: outset;
            border-radius: 7px;
            width: 13px;
            height: 13px;
        }
        QRadioButton::indicator:checked {
            border-color: $M_BLUE$;
            background-color: $M_BLUE2$;
            image: url(:/icon/$radio$.svg);
        }
        QRadioButton::indicator:disabled {
            background-color: $M_BACK$;
            border-color: $M_GREY$;
        }
        /* Spin Boxes */
        QDoubleSpinBox {
            background-color: $M_BACK$;
            color: $M_BLUE$;
            border-color: $M_GREY$;
            border-width: 1px;
            border-style: outset;
            border-radius: 2px;
            text-align: right;
            padding-right: 2px;
        }
        QDoubleSpinBox:disabled {
            background-color: $M_GREY1$;
            color: $M_GREY$;
        }
        QDoubleSpinBox::up-button {
            subcontrol-origin: border;
            subcontrol-position: top right;
            width: 12px;
            border-width: 1px;
            border-radius: 2px;
            border-color: $M_GREY$;
            border-style: outset;
            background-color: $M_BACK$;
        }
        QDoubleSpinBox::up-arrow {
            image: url(:/icon/$arrow-up$.svg);
            width: 10px;
            height: 10px;
        }
        QDoubleSpinBox::down-button {
            subcontrol-origin: border;
            subcontrol-position: bottom right;
            width: 12px;
            border-width: 1px;
            border-style: outset;
            border-radius: 2px;
            border-color: $M_GREY$;
            background-color: $M_BACK$;
        }
        QDoubleSpinBox::down-arrow {
            image: url(:/icon/$arrow-down$.svg);
            width: 10px;
            height: 10px;
        }
        /* Spin Boxes */
        QSpinBox {
            background-color: $M_BACK$;
            color: $M_BLUE$;
            text-align: right;
            border-color: $M_GREY$;
            border-width: 1px;
            border-style: outset;
            border-radius: 2px;
            padding-right: 2px;
            height: 24px;
        }
        QSpinBox::up-button {
            subcontrol-origin: border;
            subcontrol-position: top right;
            width: 16px;
            border-width: 1px;
            border-radius: 2px;
            border-color: $M_GREY$;
            border-style: outset;
            background-color: $M_BACK$;
        }
        QSpinBox::up-arrow {
            image: url(:/icon/$arrow-up$.svg);
            width: 10px;
            height: 10px;
        }
        QSpinBox::down-button {
            subcontrol-origin: border;
            subcontrol-position: bottom right;
            width: 16px;
            border-width: 1px;
            border-style: outset;
            border-radius: 2px;
            border-color: $M_GREY$;
            background-color: $M_BACK$;
        }
        QSpinBox::down-arrow {
            image: url(:/icon/$arrow-down$.svg);
            width: 10px;
            height: 10px;
        }
        /* Push Buttons */
        QPushButton {
            background-color: $M_GREY1$;
            color: $M_WHITE$;
            border-color: $M_GREY$;
            border-width: 1px;
            border-style: outset;
            border-radius: 2px;
            min - width: 10em;
        }
        QPushButton[keypad] {
            background-color: $M_GREY1$;
            border-color: $M_BLUE$;
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
            background-color: $M_BLUE$;
        }
        QPushButton[running=true] {
            border-color: $M_BLUE$;
            background-color: $M_BLUE2$;
        }
        QPushButton:disabled {
            background-color: $M_BACK$;
            color: $M_GREY$;
            border-color: $M_GREY1$;
            border-width: 1px;
            border-style: outset;
            border-radius: 2px;
        }
        QPushButton[color='gray'] {
            background-color: gray;
            color: $M_BLACK$;
        }
        QPushButton[color='red'] {
            border-color: $M_RED$;
            background-color: $M_RED2$;
            color: $M_WHITE$;
        }
        QPushButton[color='yellow'] {
            background-color: $M_YELLOW2$;
            border-color: $M_YELLOW$;
            color: $M_WHITE$;
        }
        QPushButton[color='green'] {
            background-color: $M_GREEN2$;
            border-color: $M_GREEN$;
            color: $M_WHITE$;
        }
        QPushButton:disabled {
            background-color: $M_BACK$;
            color: $M_GREY$;
            border-color: $M_GREY1$;
            border-width: 1px;
            border-style: outset;
            border-radius: 2px;
        }
        QPushButton[stop=true] {
            color: $M_RED2$;
            border-color: $M_RED$;
        }
        QMessageBox QPushButton {
            background-color: $M_GREY1$;
            color: $M_WHITE$;
            border-color: $M_GREY$;
            border-width: 1px;
            border-style: outset;
            border-radius: 2px;
            min-width: 90px;
            min-height: 25px;
        }
        QMessageBox QPushButton:default {
            border-width: 2px;
            border-color: $M_BLUE$;
        }
        QListView {
            border-color: $M_GREY$;
            border-width: 0px;
            border-style: plain;
            border-radius: 0px;
            color: $M_WHITE$;
            padding: 0px;
            margin: 0px;
            border: 0px;
        }
        QListView::item:selected {
            background-color: $M_BLUE$;
        }
        QTableWidget {
            border-color: $M_GREY$;
            border-width: 0px;
            border-style: plain;
            border-radius: 0px;
            padding: 0px;
            margin: 0px;
            border: 0px;
        }
        QTableWidget QHeaderView:section{
            border-width: 1px;
            border-style: plain;
            border-radius: 2px;
            border-color: $M_BACK$;
            background-color: $M_GREY1$;
            color: $M_WHITE$;
        }
        QTableWidget QHeaderView::down-arrow{
            subcontrol-position: upper;
            subcontrol-origin: padding;
            width: 15px;
            height: 6px;
        }
        QTableView::item:selected {
            background-color: $M_BLUE$;
            color: $M_BACK$;
        }
        /* Combo Boxes */
        QComboBox {
            combobox-popup: 0;
            color: $M_WHITE$;
            border-color: $M_GREY$;
            border-width: 1px;
            border-style: outset;
            border-radius: 2px;
            padding-left: 5px;
            background-color: $M_GREY1$;
        }
        QComboBox:disabled {
            color: $M_GREY$;
        }
        QComboBox[active=true] {
            border-color: $M_GREEN$;
            background-color: $M_GREEN2$;
        }
        QComboBox::drop-down {
            subcontrol-origin: border;
            subcontrol-position: right;
            width: 20px;
            border-color: $M_GREY$;
            border-width: 1px;
            border-style: outset;
            border-radius: 2px;
            background-color: $M_GREY1$;
        }
        QComboBox[active=true]::drop-down {
            border-color: $M_GREEN$;
        }
        QComboBox::down-arrow {
            image: url(:/icon/$arrow-down$.svg);
            width: 16px;
            height: 16px;
        }
        QComboBox QListView {
            border-width: 2px;
            border-style: outset;
            border-color: $M_GREY$;
            border-radius: 2px;
            color: $M_WHITE$;
            background-color: $M_BACK$;
            min-height: 60px;
        }
        QComboBox QListView::item {
            border-width: 1px;
            min-height: 28px;
            border-color: $M_BLUE$;
        }
        QComboBox QListView::item:selected {
            border-style: outset;
            background-color: $M_BLUE2$;
        }
        /* lines */
        QFrame[frameShape="4"] {
            color: $M_BLUE1$;
        }
        QFrame[frameShape="5"] {
            color: $M_BLUE1$;
        }
        /* tab widget */
        QTabWidget:pane {
            border-width: 2px;
            border-color: $M_GREY$;
            border-radius: 5px;
            border-style: outset;
            top: -10px;
            padding-top: 10px;
        }
        /* needed for MAC OSX */
        QTabWidget:tab-bar {
            alignment: center;
        }
        QTabBar::tab {
            background-color: $M_GREY1$;
            color: $M_WHITE$;
            border-width: 1px;
            border-color: $M_BLUE2$;
            border-radius: 3px;
            border-style: outset;
            padding: 4px;
        }
        QTabBar::tab:selected {
            background: $M_BLUE2$;
            border-color: $M_BLUE$;
            border-width: 2px;
        }
        QTabBar::tab:!selected {
            margin-top: 2px;
        }
        QTabBar::tab:only-one {
            margin: 1;
        }
        QTabBar::tab:disabled {
            color: $M_GREY$;
            border-color: $M_GREY1$;
        }
        /* slider */
        QSlider
        {   background-color: $M_GREY1$;
            width: 16px;
            height: 16px;
            margin: 0px 3px 0px 3px;
            border-width: 1px;
            border-color: $M_GREY$;
            border-style: outset;
            border-radius: 2px;
        }
        QSlider::handle
        {   background-color: $M_BLUE$;
            border-radius: 2px;
            border-style: outset;
            border-width: 1px;
        }
        QSlider::add-page
        {   background-color: $M_GREY1$;
            border-color: $M_GREY$;
            border-style: outset;
            border-radius: 2px;
        }
        QSlider::sub-page
        {   background-color: $M_GREY1$;
            border-color: $M_GREY$;
            border-style: outset;
            border-radius: 2px;
        }
        /* scroll bar */
        QScrollBar {
            border-width: 1px;
            border-color: $M_GREY$;
            background-color: $M_GREY1$;
            border-style: outset;
            border-radius: 2px;
        }
        QScrollBar:vertical
        {   width: 16px;
            margin: 4px 4px 4px 4px;
        }
        QScrollBar:horizontal
        {   height: 16px;
            margin: 4px 16px 4px 4px;
        }
        QScrollBar::handle
        {   background-color: $M_BLUE$;
            min-height: 24px;
            min-width: 24px;
            border-radius: 2px;
        }
        QScrollBar::sub-line
        {   margin: 2px 0px 2px 0px;
            height: 0px;
            width: 0px;
            subcontrol-position: top;
            subcontrol-origin: margin;
        }
        QScrollBar::add-line
        {   margin: 2px 0px 2px 0px;
            height: 0px;
            width: 0px;
            subcontrol-position: bottom;
            subcontrol-origin: margin;
        }
        QScrollBar::sub-line:on
        {   height: 16px;
            width: 16px;
            subcontrol-position: top;
            subcontrol-origin: margin;
        }
        QScrollBar::add-line:on
        {   height: 0px;
            width: 0px;
            subcontrol-position: bottom;
            subcontrol-origin: margin;
        }
        QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical
        {   background: none;
            border-width: 0px;
            border-color: $M_GREY$;
            border-style: plain;
            border-radius: 0px;
        }
        QScrollBar::add-page, QScrollBar::sub-page
        {   background: none;
        }
        /* progress bar */
        QProgressBar {
            color: white;
            background-color: $M_BACK$;
            border-radius: 3px;
            border-width: 1px;
            border-color: $M_GREY$;
            border-style: outset;
        }
        QProgressBar:disabled {
            color: $M_GREY$;
            background-color: $M_BACK$;
            border-radius: 3px;
            border-width: 1px;
            border-color: $M_GREY1$;
            border-style: outset;
        }
        QProgressBar::chunk {
            background-color: $M_BLUE$;
            width: 1px;
            margin: 0px;
            border-width: 0px;
            border-color: $M_GREY$;
            border-radius: 0px;
            border-style: outset;
        }
        QTextBrowser {
            color: $M_BLUE$;
            background-color: $M_BLACK$;
            border-radius: 3px;
            border-width: 2px;
            border-color: $M_GREY$;
            border-style: outset;
            margin: -5px;
        }
        QFileDialog QListView:enabled {
            background-color: $M_BACK$;
            color: $M_BLUE$;
            text-align: right;
            border-width: 1px;
            border-color: $M_GREY$;
            border-style: outset;
            border-radius: 2px;
        }
        QFileDialog QListView:disabled {
            background-color: $M_BACK$;
            color: $M_GREY$;
            text-align: right;
            border-width: 1px;
            border-color: $M_GREY$;
            border-style: outset;
            border-radius: 2px;
        }
        QFileDialog QPushButton {
            min-width: 50px;
            min-height: 20px;
        }
        QInputDialog QPushButton {
            background-color: $M_GREY1$;
            color: $M_WHITE$;
            border-color: $M_GREY$;
            border-width: 1px;
            border-style: outset;
            border-radius: 2px;
            min-width: 90px;
            min-height: 25px;
        }
        QInputDialog QPushButton:default {
            border-width: 2px;
            border-color: $M_BLUE$;
        }
        """

    @property
    def M_TRANS(self):
        return self.cs['M_TRANS'][self.colorSet]

    @property
    def M_BLUE(self):
        return self.cs['M_BLUE'][self.colorSet]

    @property
    def M_BLUE1(self):
        return self.cs['M_BLUE1'][self.colorSet]

    @property
    def M_BLUE2(self):
        return self.cs['M_BLUE2'][self.colorSet]

    @property
    def M_BLUE3(self):
        return self.cs['M_BLUE3'][self.colorSet]

    @property
    def M_BLUE4(self):
        return self.cs['M_BLUE4'][self.colorSet]

    @property
    def M_WHITE(self):
        return self.cs['M_WHITE'][self.colorSet]

    @property
    def M_WHITE1(self):
        return self.cs['M_WHITE1'][self.colorSet]

    @property
    def M_GREY(self):
        return self.cs['M_GREY'][self.colorSet]

    @property
    def M_GREY1(self):
        return self.cs['M_GREY1'][self.colorSet]

    @property
    def M_BACK(self):
        return self.cs['M_BACK'][self.colorSet]

    @property
    def M_BLACK(self):
        return self.cs['M_BLACK'][self.colorSet]

    @property
    def M_RED(self):
        return self.cs['M_RED'][self.colorSet]

    @property
    def M_RED1(self):
        return self.cs['M_RED1'][self.colorSet]

    @property
    def M_RED2(self):
        return self.cs['M_RED2'][self.colorSet]

    @property
    def M_YELLOW(self):
        return self.cs['M_YELLOW'][self.colorSet]

    @property
    def M_YELLOW1(self):
        return self.cs['M_YELLOW1'][self.colorSet]

    @property
    def M_YELLOW2(self):
        return self.cs['M_YELLOW2'][self.colorSet]

    @property
    def M_GREEN(self):
        return self.cs['M_GREEN'][self.colorSet]

    @property
    def M_GREEN1(self):
        return self.cs['M_GREEN1'][self.colorSet]

    @property
    def M_GREEN2(self):
        return self.cs['M_GREEN2'][self.colorSet]

    @property
    def M_PINK(self):
        return self.cs['M_PINK'][self.colorSet]

    @property
    def M_PINK1(self):
        return self.cs['M_PINK1'][self.colorSet]

    @property
    def M_CYAN(self):
        return self.cs['M_CYAN'][self.colorSet]

    @property
    def M_CYAN1(self):
        return self.cs['M_CYAN1'][self.colorSet]

    @property
    def mw4Style(self):
        if platform.system() == 'Darwin':
            styleRaw = self.MAC_STYLE + self.BASIC_STYLE
        else:
            styleRaw = self.NON_MAC_STYLE + self.BASIC_STYLE
        return self.renderStyle(styleRaw)

    @staticmethod
    def hex2rgb(val):
        """
        :param val:
        :return:
        """
        val = val.lstrip('#')
        r = int(val[0:2], 16)
        g = int(val[2:4], 16)
        b = int(val[4:6], 16)
        return [r, g, b]

    def calcHexColor(self, val, f):
        """
        :param val:
        :param f:
        :return:
        """
        rgb = self.hex2rgb(val)
        rgb = [int(x * f) for x in rgb]
        return f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'

    def renderStyle(self, styleRaw):
        """
        :param styleRaw:
        :return:
        """
        style = ''
        for line in styleRaw.split('\n'):
            start = line.find('$')
            end = line.find('$', start + 1)
            key = line[start + 1:end]
            if key in self.cs:
                repl = self.cs[key][self.colorSet]
                line = line.replace(f'${key}$', repl)
                if repl:
                    style += (line + '\n')
            else:
                style += (line + '\n')
        return style
