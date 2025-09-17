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
# GUI with PySide for python
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages

# local imports
MAC_STYLE = """
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
    QTabWidget:tab-bar {
        alignment: center;
    }
    """

NON_MAC_STYLE = """
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

BASIC_STYLE = """
    QWidget {
        color: $M_TER$;
    }
    QToolTip {
        border-width: %WIDTH%;
        border-style: outset;
        border-color: $M_SEC$;
        color: $M_PRIM$;
        padding: 5px;
        max-width: 500px;
    }
    QLabel {
        color: $M_TER$;
        background-color: None;
    }
    QLabel[keypad]{
        color: $M_PRIM$;
        background-color: $M_BACK1$;
        border-radius: 8px;
    }
    QLabel:disabled {
        color: $M_SEC$;
    }
    QLabel[color='blue'] {
        border-width: %WIDTH%;
        border-color: $M_PRIM1$;
        border-style: outset;
        border-radius: %ROUND%;
        background-color: $M_PRIM1$;
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
    
    /* QLine Edit*/
    QLineEdit {
        color: $M_PRIM$;
        text-align: right;
        background-color: $M_BACK1$;
    }
    QLineEdit:disabled {
        color: $M_PRIM3$;
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
            
    /* text browser */
    QTextBrowser {
        color: $M_PRIM$;
        background-color: $M_BACK1$;
        border-radius: %ROUND%;
        border-width: %WIDTH%;
        margin: -5px;
    }
    QTextBrowser:disabled {
        color: $M_PRIM3$;
        background-color: $M_BACK1$;
    }

    /* Group Box */
    QGroupBox {
        border-width: %WIDTH%;
        border-style: outset;
        border-radius: %ROUND%;
        border-color: $M_PRIM3$;
        margin-top: 6px;
        background-color: $M_BACK$;
    }
    QGroupBox QLineEdit:disabled {
        color: $M_PRIM$;
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
        border-width: %WIDTH%;
        border-color: $M_SEC$;
        border-style: outset;
        border-radius: %ROUND%;
        width: 13px;
        height: 13px;
    }
    QGroupBox::indicator:checked {
        border-width: %WIDTH%;
        border-color: $M_PRIM$;
        background-color: $M_PRIM2$;
        image: url(:/icon/$checkmark$.svg);
    }
    QGroupBox[running=true] {
        color: $M_TER$;
        border-color: $M_YELLOW$;
    }
    /* Checkboxes */
    QCheckBox {
        color: $M_TER$;
        spacing: 5px;
        background-color: $M_TRANS$;
    }
    QCheckBox::indicator {
        border-width: %WIDTH%;
        border-color: $M_SEC$;
        background-color: $M_BACK$;
        border-style: outset;
        border-radius: %ROUND%;
        width: 13px;
        height: 13px;
    }
    QCheckBox::indicator:checked {
        border-color: $M_PRIM$;
        background-color: $M_PRIM2$;
        image: url(:/icon/$checkmark$.svg);
    }
    QCheckBox:disabled {
        color: $M_SEC$;
    }
    QRadioButton {
        color: $M_TER$;
        spacing: 5px;
    }
    QRadioButton:disabled {
        color: $M_SEC$;
    }
    QRadioButton::indicator {
        border-width: %WIDTH%;
        border-color: $M_SEC$;
        background-color: $M_BACK$;
        border-style: outset;
        border-radius: %ROUND%;
        width: 13px;
        height: 13px;
    }
    QRadioButton::indicator:checked {
        border-color: $M_PRIM$;
        background-color: $M_PRIM2$;
        image: url(:/icon/$radio$.svg);
    }
    /* Spin Boxes */
    QDoubleSpinBox {
        background-color: $M_BACK1$;
        color: $M_PRIM$;
        border-color: $M_SEC$;
        border-width: %WIDTH%;
        border-style: outset;
        border-radius: %ROUND%;
        padding-left: 2px;
    }
    QDoubleSpinBox::up-button {
        subcontrol-origin: border;
        subcontrol-position: top right;
        width: 12px;
        border-radius: %ROUND%;
        border-width: %WIDTH%;
        border-color: $M_SEC$;
        border-style: outset;
        background-color: $M_BACK1$;
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
        border-style: outset;
        border-radius: %ROUND%;
        border-width: %WIDTH%;
        border-color: $M_SEC$;
        background-color: $M_BACK1$;
   }
    QDoubleSpinBox::down-arrow {
        image: url(:/icon/$arrow-down$.svg);
        width: 10px;
        height: 10px;
    }
    /* Push Buttons */
    QPushButton {
        background-color: #GRAD_1,$M_BACK1$#;
        color: $M_TER$;
        border-color: $M_SEC$;
        border-width: 1px;
        border-style: outset;
        border-radius: %ROUND%;
        min - width: 10em;
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
    QPushButton[running=true] {
        border-color: $M_PRIM$;
        background-color: #GRAD_1,$M_PRIM2$#;
    }
    QPushButton:disabled {
        color: $M_SEC$;
        border-color: $M_SEC1$;
    }
    QPushButton[color='gray'] {
        background-color: #GRAD_1,$M_GRAY$#;
        color: $M_TER$;
    }
    QPushButton[color='red'] {
        background-color: #GRAD_1,$M_RED2$#;
        border-color: $M_RED$;
        color: $M_TER$;
    }
    QPushButton[color='yellow'] {
        background-color: #GRAD_1,$M_YELLOW2$#;
        border-color: $M_YELLOW$;
        color: $M_TER$;
    }
    QPushButton[color='green'] {
        background-color: #GRAD_1,$M_GREEN2$#;
        border-color: $M_GREEN$;
        color: $M_TER$;
    }
    QPushButton[stop=true] {
        color: $M_RED2$;
        border-color: $M_RED$;
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
    QListView {
        border-color: $M_SEC$;
        border-width: 0px;
        border-style: plain;
        border-radius: 0px;
        color: $M_TER$;
        padding: 0px;
        margin: 0px;
        border: 0px;
    }
    QListView::item:selected {
        border-color: $M_PRIM$;
    }
    
    /* Table Widget */
    QTableWidget {
        border-color: $M_SEC$;
        border-width: 0px;
        border-style: plain;
        border-radius: 0px;
        padding: 0px;
        margin: 0px;
        border: 0px;
    }
    QTableWidget QHeaderView:section{
        border-width: %WIDTH%;
        border-style: plain;
        border-radius: %ROUND%;
        border-color: $M_BACK$;
        background-color: $M_SEC1$;
        color: $M_TER$;
    }
    QTableWidget QHeaderView::down-arrow{
        subcontrol-position: upper;
        subcontrol-origin: padding;
        width: 15px;
        height: 6px;
    }
    QTableView::item:selected {
        background-color: $M_PRIM$;
        color: $M_BACK$;
    }
    
    /* Combo Boxes */
    QComboBox {
        combobox-popup: 0;
        color: $M_TER$;
        border-color: $M_SEC$;
        border-width: 1px;
        border-style: outset;
        border-radius: %ROUND%;
        padding-left: 5px;
        background-color: #GRAD_1,$M_BACK1$#;
    }
    QComboBox:disabled {
        color: $M_SEC$;
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
        border-radius: %ROUND%;
        background-color: #GRAD_1,$M_BACK1$#;
    }
    QComboBox[active=true]::drop-down {
            border-color: $M_GREEN$;
        }
    QComboBox::down-arrow {
        image: url(:/icon/$arrow-down$.svg);
        width: 16px;
        height: 16px;
        background-color: #GRAD_1,$M_BACK1$#;
    }
    QComboBox QListView {
        border-width: %WIDTH%;
        border-style: outset;
        border-color: $M_SEC$;
        border-radius: %ROUND%;
        color: $M_TER$;
        min-height: 60px;
    }
    QComboBox QListView::item {
        border-color: $M_SEC$;
        min-height: 28px;
    }
    QComboBox QListView::item:selected {
        background-color: #GRAD_1,$M_PRIM$#;
    }
    
    /* lines */
    QFrame[frameShape="4"] {
        color: $M_PRIM1$;
    }
    QFrame[frameShape="5"] {
        color: $M_PRIM1$;
    }
    
    /* tab widget */
    QTabWidget:pane {
        top: -6px;
        padding-top: 6px;
        border-width: 0px;
        background-color: #GRAD_2,$M_BACK$#;
    }
    QTabWidget:tab-bar {
        alignment: center;
    }
    QTabBar::tab {
        border-radius: %ROUND%;
        border-width: %WIDTH%;
        border-style: outset;
        color: $M_TER2$;
        border-color: $M_TAB1$;
        background-color: #GRAD_1,$M_TAB2$#;
        padding-top: 6px;
        padding-bottom: 4px;
        padding-left: 4px;
        padding-right: 4px;
    }
    QTabBar::tab:selected {
        background-color: #GRAD_1,$M_TAB1$#;
        color: $M_TER$;
        border-color: $M_TAB$;
    }
    QTabBar::tab:only-one {
        margin: 1;
    }
    QTabBar::tab:disabled {
        color: $M_SEC1$;
        border-color: $M_SEC1$;
        background-color: $M_BACK$;
    }
    
    /* slider */
    QSlider {   
        width: 16px;
        height: 16px;
        margin: 0px 3px 0px 3px;
        border-width: %WIDTH%;
        border-radius: %ROUND%;
        border-color: $M_SEC$;
    }
    QSlider::handle {   
        background-color: $M_PRIM$;
    }
    QSlider::add-page {   
        background-color: $M_SEC1$;
    }
    QSlider::sub-page {   
        background-color: $M_SEC1$;
    }

    /* scroll bar */
    QScrollBar {
        border-width: %WIDTH%;
        border-color: $M_SEC$;
        border-style: outset;
        border-radius: %ROUND%;
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
        border-width: %WIDTH%;
        border-radius: %ROUND%;
    }
    QProgressBar:disabled {
        color: $M_SEC$;
    }
    QProgressBar::chunk {
        border-radius: 2px;
        background-color: #GRAD_1,$M_PRIM$#;
    }
    
    /* System Dialogs */
    QFileDialog QListView {
        background-color: $M_BACK$;
        text-align: right;
        border-width: %WIDTH%;
        border-color: $M_SEC$;
        border-style: outset;
        border-radius: %ROUND%;
    }
    QFileDialog QListView:enabled {
        color: $M_PRIM$;
    }
    QFileDialog QListView:disabled {
        color: $M_SEC$;
    }
    
    QFileDialog QPushButton {
        min-width: 50px;
        min-height: 20px;
    }
    QInputDialog QPushButton {
        background-color: $M_SEC1$;
        color: $M_TER$;
        min-width: 90px;
        min-height: 25px;
    }
    QInputDialog QPushButton:default {
        border-width: %WIDTH%;
        border-color: $M_PRIM$;
    }
    """
