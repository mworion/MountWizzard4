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
# written in python3, (c) 2019-2021 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages
from PyQt5.QtGui import QColor

# local imports


class Styles:

    COLOR_ASTRO = QColor(32, 144, 192)
    COLOR_BLUE = QColor(0, 0, 255)
    COLOR_BLUE1 = QColor(96, 176, 224)
    COLOR_BLUE2 = QColor(80, 140, 176)
    COLOR_BLUE3 = QColor(48, 104, 128)
    COLOR_BLUE4 = QColor(44, 80, 112)
    COLOR_YELLOW = QColor(255, 255, 0)
    COLOR_GREEN = QColor(0, 255, 0)
    COLOR_WHITE = QColor(255, 255, 255)
    COLOR_WHITE1 = QColor(224, 224, 224)
    COLOR_RED = QColor(255, 0, 0)
    COLOR_ORANGE = QColor(192, 96, 96)
    COLOR_BLACK = QColor(0, 0, 0)
    COLOR_3D = QColor(60, 60, 60)
    COLOR_BACKGROUND = QColor(32, 32, 32)
    COLOR_FRAME = QColor(192, 192, 192)
    COLOR_PINK = QColor(192, 16, 192)

    TRAFFICLIGHTCOLORS = ['green', 'yellow', 'red', '']

    BACK_BG = 'background-color: transparent;'
    BACK_RED = 'background-color: red;'
    BACK_GREEN = 'background-color: green;'
    BACK_NORM = 'background-color: #202020;'
    BACK_BACK = 'background-color: #181818'
    BACK_BLUE1 = 'background-color: #104860'
    BACK_BLUE2 = 'background-color: #0C3648'
    BACK_BLUE3 = 'background-color: #082430'
    BACK_BLUE4 = 'background-color: #061828'

    M_TRANS = '#20202000'
    M_BACK = '#181818'
    M_BLUE_H = '#30C0FF'
    M_BLUE = '#2090C0'
    M_BLUE1 = '#104860'
    M_BLUE2 = '#0C3648'
    M_BLUE3 = '#082430'
    M_BLUE4 = '#061828'
    M_BLACK = '#000000'
    M_WHITE_H = '#F0F0F0'
    M_WHITE = '#A0A0A0'
    M_WHITE_L = '#808080'
    M_GREY_H = '#606060'
    M_GREY = '#404040'
    M_GREY_MID = '#303030'
    M_GREY_LL = '#282828'
    M_GREY_LIGHT = '#202020'
    M_GREY_DARK = '#101010'
    M_GREEN_H = '#00A000'
    M_GREEN = '#008000'
    M_GREEN_L = '#006000'
    M_GREEN_LL = '#003000'
    M_GREEN_LL_A = '#00100040'
    M_RED = '#B03030'
    M_RED_L = '#802020'
    M_PINK_H = '#FF00FF'
    M_PINK = '#B000B0'
    M_PINK_L = '#800080'
    M_YELLOW_H = '#FFFF00'
    M_YELLOW = '#C0C000'
    M_YELLOW_L = '#808000'

    MAC_STYLE = """
    QWidget {
        background-color: #181818;
        font-family: Arial;
        font-weight: normal;
        font-size: 13pt;
    }
    QWidget [large='true'] {
        font-family: Arial;
        font-weight: normal;
        font-size: 30pt;
    }
    QGroupBox[large='true'] {
        font-family: Arial;
        font-weight: bold;
        font-size: 13pt;
    }
    QGroupBox {
        font-family: Arial;
        font-weight: normal;
        font-size: 11pt;
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
    """

    NON_MAC_STYLE = """
    QWidget {
        background-color: #181818;
        font-family: Arial;
        font-weight: normal;
        font-size: 10pt;
    }
    QWidget [large='true'] {
        font-family: Arial;
        font-weight: bold;
        font-size: 20pt;
    }
    QGroupBox[large='true'] {
        font-family: Arial;
        font-weight: normal;
        font-size: 10pt;
    }
    QGroupBox {
        font-family: Arial;
        font-weight: normal;
        font-size: 8pt;
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
    """

    BASIC_STYLE = """
    QWidget {
        color: rgb(32, 144, 192);
    }
    QTextEdit {
        color: #C0C0C0;
        background-color: #202020;
        border-radius: 0px;
    }
    QToolTip {
        border-width: 2px;
        border-style: outset;
        border-color: #404040;
        background-color: #202020;
        color: rgb(32, 144, 192);
        padding: 5px;
        max-width: 500px;
    }
    QLabel {
        background-color: transparent;
        color: #C0C0C0;
    }
    QLabel:disabled {
        background-color: transparent;
        color: #404040;
    }
    QLabel[color='blue'] {
        border-width: 3px;
        border-color: rgb(16, 72, 96);
        border-style: outset;
        border-radius: 2px;
        background-color: rgb(9, 36, 48);
    }
    QLabel[iconpicture='true'] {
        border-width: 1px;
        border-color: #404040;
        border-style: plain;
        border-radius: 0px;
    }
    /* QLine Edit*/
    QLineEdit {
        background-color: #000000;
        color: rgb(32, 144, 192);
        text-align: right;
        border-width: 1px;
        border-color: #404040;
        border-style: flat;
        border-radius: 2px;
    }
    QLineEdit[input='true']{
        background-color: #000000;
        border-width: 1px;
        border-color: rgb(16, 72, 96);
        border-style: outset;
    }
    QLineEdit:read-only{
        background-color: #202020;
    }
    QLineEdit[color='green'] {
        border-width: 2px;
        border-style: outset;
        border-color: green;
    }
    QLineEdit[color='yellow'] {
        border-width: 2px;
        border-style: outset;
        border-color: yellow;
    }
    QLineEdit[color='red'] {
        border-width: 2px;
        border-style: outset;
        border-color: red;
    }
    QLineEdit[char='green'] {
        color: #00C000;
    }
    QLineEdit[char='yellow'] {
        color: '#C0C000';
    }
    QLineEdit[char='red'] {
        color: #C00000;
    }
    QLineEdit[color='M_RED_L'] {
        border-width: 2px;
        border-style: outset;
        border-color: #802020;
    }
    QLineEdit[color='M_YELLOW_L'] {
        border-width: 2px;
        border-style: outset;
        border-color: #808000;
    }
    QLineEdit[color='M_GREEN_L'] {
        border-width: 2px;
        border-style: outset;
        border-color: #006000;
    }
    QLineEdit[status='on'] {
        color: black;
        border-width: 2px;
        background-color: rgb(32, 144, 192);
    }
    QLabel[color='green'] {
        color: green;
    }
    QLabel[color='yellow'] {
        color: yellow;
    }
    QLabel[color='red'] {
        color: red;
    }

    /* Group Box */
    QGroupBox {
        background-color: #181818;
        border-width: 1px;
        border-style: outset;
        border-radius: 3px;
        border-color: #404040;
        margin-top: 6px;
    }
    QGroupBox::title {
        left: 5px;
        subcontrol-origin: margin;
        subcontrol-position: top left;
        color: #C0C0C0;
        background-color: #181818;
    }
    QGroupBox::title[large='true'] {
        left: 5px;
        subcontrol-origin: margin;
        subcontrol-position: top left;
        color: rgb(32, 144, 196);
        background-color: #181818;
    }
    QGroupBox::title[refraction='true']{
        color: rgb(32, 144, 192);
    }
    QGroupBox[refraction='true'] {
        border-width: 2px;
        border-color: rgb(32, 144, 192);
    }
    QGroupBox:disabled{
        border-width: 2px;
        border-color: red;
    }
    QGroupBox::indicator {
        border-width: 1px;
        border-color: #404040;
        background-color: #101010;
        border-style: outset;
        border-radius: 2px;
        width: 13px;
        height: 13px;
    }
    QGroupBox::indicator:checked {
        background-color: rgb(32, 144, 192);
        image: url(:/icon/checkmark.ico);
    }

    /* Checkboxes */
    QCheckBox {
        color: #C0C0C0;
        spacing: 8px;
        background-color: transparent;
    }
    QCheckBox::indicator {
        border-width: 1px;
        border-color: #404040;
        background-color: #101010;
        border-style: outset;
        border-radius: 2px;
        width: 13px;
        height: 13px;
    }
    QCheckBox::indicator:checked {
        background-color: rgb(32, 144, 192);
        image: url(:/icon/checkmark.ico);
    }
    QCheckBox::indicator:disabled {
        background-color: transparent;
        image: None;
    }
    QCheckBox:disabled {
        color: #404040;
    }
    QRadioButton {
        color: #C0C0C0;
        background-color: transparent;
    }
    QRadioButton:disabled {
        color: #404040;
        background-color: transparent;
    }
    QRadioButton::indicator {
        border-width: 1px;
        border-color: #404040;
        background-color: #101010;
        border-style: outset;
        border-radius: 2px;
        width: 13px;
        height: 13px;
    }
    QRadioButton::indicator:checked {
        background-color: rgb(32, 144, 192);
        image: url(:/icon/checkmark.ico);
    }
    /* Spin Boxes */
    QDoubleSpinBox {
        background-color: #101010;
        color: rgb(32, 144, 192);
        text-align: right;
        border-color: #404040;
        border-width: 1px;
        border-style: outset;
        border-radius: 2px;
        padding-right: 2px;
    }
    QDoubleSpinBox:disabled {
        background-color: #202020;
        color: #404040;
    }
    QDoubleSpinBox::up-button {
        subcontrol-origin: border;
        subcontrol-position: top right;
        width: 12px;
        border-width: 1px;
        border-radius: 2px;
        border-color: #404040;
        border-style: outset;
        background-color: #181818;
    }
    QDoubleSpinBox::up-arrow {
        image: url(:/icon/arrow-up.ico);
        width: 12px;
        height: 16px;
    }
    QDoubleSpinBox::down-button {
        subcontrol-origin: border;
        subcontrol-position: bottom right;
        width: 12px;
        border-width: 1px;
        border-style: outset;
        border-radius: 2px;
        border-color: #404040;
        background-color: #181818;
    }
    QDoubleSpinBox::down-arrow {
        image: url(:/icon/arrow-down.ico);
        width: 12px;
        height: 16px;
    }
    /* Spin Boxes */
    QSpinBox {
        background-color: #101010;
        color: rgb(32, 144, 192);
        text-align: right;
        border-color: #404040;
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
        border-color: #404040;
        border-style: outset;
        background-color: #181818;
    }
    QSpinBox::up-arrow {
        image: url(:/icon/arrow-up.ico);
        width: 16px;
        height: 16px;
    }
    QSpinBox::down-button {
        subcontrol-origin: border;
        subcontrol-position: bottom right;
        width: 16px;
        border-width: 1px;
        border-style: outset;
        border-radius: 2px;
        border-color: #404040;
        background-color: #181818;
    }
    QSpinBox::down-arrow {
        image: url(:/icon/arrow-down.ico);
        width: 16px;
        height: 16px;
    }
    /* Push Buttons */
    QPushButton[alignLeft='true'] {
        text-align: left;
        padding-left: 3px;
        padding-right: 3px;
    }
    QPushButton:focus {
        outline: none;
    }
    QPushButton {
        background-color: #202020;
        color: #C0C0C0;
        border-color: #404040;
        border-width: 1px;
        border-style: outset;
        border-radius: 2px;
        min - width: 10em;
    }
    QMessageBox QPushButton {
        background-color: #202020;
        color: #C0C0C0;
        border-color: #404040;
        border-width: 1px;
        border-style: outset;
        border-radius: 2px;
        min-width: 90px;
        min-height: 25px;
    }
    QMessageBox QPushButton:default {
        border-width: 2px;
        border-color: rgb(32, 144, 192);
    }
    QListWidget {
        border-color: #404040;
        border-width: 1px;
        border-style: outset;
        border-radius: 2px;
        color: #C0C0C0;
        padding-left: 5px;
        padding-top: 5px;
    }
    QPushButton:pressed {
        border-color: #404040;
        border-width: 2px;
        border-style: inset;
        border-radius: 2px;
        /*
        border-image: url(:/icon/check-circle.svg)
        */
    }
    QPushButton[running='false'] {
        background-color: #202020;
        color: #C0C0C0;
    }
    QPushButton[running='true'] {
        background-color: rgb(32, 144, 192);
        color: #000000;
    }
    QPushButton[pause='false'] {
        background-color: #202020;
        color: #C0C0C0;
    }
    QPushButton[pause='true'] {
        background-color: #00C000;
        color: #000000;
    }
    QPushButton[cancel='true'] {
        background-color: rgb(192,0, 0);
        color: #C0C0C0;
    }
    QPushButton[cancel='false'] {
        background-color: #202020;
        color: #C0C0C0;
    }
    QPushButton:disabled {
        background-color: #101010;
        color: #404040;
        border-color: #202020;
        border-width: 1px;
        border-style: outset;
        border-radius: 2px;
    }
    QPushButton[color='gray'] {
        background-color: gray;
        color: #000000;
    }
    QPushButton[color='red'] {
        background-color: red;
        color: #000000;
    }
    QPushButton[color='yellow'] {
        background-color: yellow;
        color: #000000;
    }
    QPushButton[color='green'] {
        background-color: green;
        color: #000000;
    }
    QPushButton[stop='true'] {
        background-color: transparent;
        color: transparent;
        border-color: transparent;
    }
    /* Combo Boxes */
    QComboBox {
        combobox-popup: 0;
        color: #C0C0C0;
        border-color: #404040;
        border-width: 1px;
        border-style: outset;
        border-radius: 2px;
        padding-left: 5px;
        background-color: #202020;
    }
    QComboBox::drop-down {
        subcontrol-origin: border;
        subcontrol-position: right;
        width: 20px;
        border-color: #404040;
        border-width: 1px;
        border-style: outset;
        border-radius: 2px;
        background-color: #202020;
    }
    QComboBox::down-arrow {
        image: url(:/icon/arrow-down.ico);
        width: 20px;
        height: 31px;
    }
    QComboBox QListView {
        border-width: 2px;
        border-style: outset;
        border-color: #404040;
        border-radius: 2px;
        color: #C0C0C0;
        background-color: #101010;
        min-height: 60px;
    }
    QComboBox QListView::item {
        min-height: 28px;
    }
    QComboBox QListView::item:selected {
        border-width: 1px;
        border-style: outset;
        border-color: #404040;
        border-radius: 2px;
        color: #101010;
        background-color: rgb(32, 144, 192);
    }
    QComboBox QListView::item:!selected {
    }

    /* lines */
    QFrame[frameShape="4"] {
        color: rgb(16, 72, 96);
    }
    QFrame[frameShape="5"] {
        color: rgb(16, 72, 96);
    }
    /* tab widget */
    QTabWidget:pane {
        border-width: 2px;
        border-color: #404040;
        border-radius: 2px;
        border-style: outset;
    }
    /* needed for MAC OSX */
    QTabWidget:tab-bar {
        alignment: center;
    }
    QTabBar::tab {
        background-color: #202020;
        color: #C0C0C0;
        border-width: 2px;
        border-color: rgb(16, 72, 96);
        border-radius: 3px;
        border-style: outset;
        padding: 4px;
        padding-left: 4px;
        padding-right: 4px;
    }
    QTabBar::tab:selected {
        color: #000000;
        background: rgb(32, 144, 192);
    }
    QTabBar::tab:!selected {
        margin-top: 2px;
    }
    QTabBar::tab:only-one {
        margin: 1;
    }
    QTabBar::tab:disabled {
        color: #404040;
        border-color: #202020;
        width: 0;
        height: 0;
        padding: 0;
        border: none;
    }
    /* scroll bar */
    QScrollBar:vertical
    {   background-color: #202020;
        width: 20px;
        margin: 20px 3px 20px 3px;
        border-width: 1px;
        border-color: #404040;
        border-style: outset;
        border-radius: 3px;
    }
    QScrollBar::handle:vertical
    {   background-color:  rgb(32, 144, 192);
        min-height: 10px;
        border-radius: 3px;
    }
    QScrollBar::sub-line:vertical
    {   margin: 3px 0px 3px 0px;
        border-image: url(:icon/arrow-up.ico);
        height: 16px;
        width: 16px;
        subcontrol-position: top;
        subcontrol-origin: margin;
    }
    QScrollBar::add-line:vertical
    {   margin: 3px 0px 3px 0px;
        border-image: url(:icon/arrow-down.ico);
        height: 16px;
        width: 16px;
        subcontrol-position: bottom;
        subcontrol-origin: margin;
    }
    QScrollBar::sub-line:vertical:on
    {   border-image: url(:icon/arrow-up.ico);
        height: 16px;
        width: 16px;
        subcontrol-position: top;
        subcontrol-origin: margin;
    }
    QScrollBar::add-line:vertical:on
    {   border-image: url(:icon/arrow-down.ico);
        height: 16px;
        width: 16px;
        subcontrol-position: bottom;
        subcontrol-origin: margin;
    }
    QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical
    {   background: none;
        border-width: 1px;
        border-color: #404040;
        border-style: outset;
        border-radius: 4px;
    }
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical
    {   background: none;
    }

    /* progress bar */
    QProgressBar {
        color: white;
        background-color: #101010;
        border-radius: 3px;
        border-width: 1px;
        border-color: #404040;
        border-style: outset;
    }
    QProgressBar:disabled {
        color: #404040;
        background-color: #101010;
        border-radius: 3px;
        border-width: 1px;
        border-color: #202020;
        border-style: outset;
    }
    QProgressBar::chunk {
        background-color: rgb(32, 144, 192);
        width: 1px;
        margin: 0px;
        border-width: 0px;
        border-color: #404040;
        border-radius: 0px;
        border-style: outset;
    }
    QTextBrowser {
        color: rgb(32, 144, 192);
        background-color: #101010;
        border-radius: 3px;
        border-width: 2px;
        border-color: #404040;
        border-style: outset;
        margin: -5px;
    }
    QFileDialog QListView:enabled {
        background-color: #101010;
        color: rgb(32, 144, 192);
        text-align: right;
        border-width: 1px;
        border-color: #404040;
        border-style: outset;
        border-radius: 2px;
    }
    QFileDialog QListView:disabled {
        background-color: #101010;
        color: #404040;
        text-align: right;
        border-width: 1px;
        border-color: #404040;
        border-style: outset;
        border-radius: 2px;
    }
    QFileDialog QPushButton {
        min-width: 50px;
        min-height: 20px;
    }
    QInputDialog QPushButton {
        background-color: #202020;
        color: #C0C0C0;
        border-color: #404040;
        border-width: 1px;
        border-style: outset;
        border-radius: 2px;
        min-width: 90px;
        min-height: 25px;
    }
    QInputDialog QPushButton:default {
        border-width: 2px;
        border-color: rgb(32, 144, 192);
    }
    """
