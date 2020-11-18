@echo off
rem
rem run script for Win10
rem (c) 2020 mworion
rem

echo.
echo ---------------------------------------------
echo Script version 0.2
echo ---------------------------------------------
echo.

venv\Scripts\activate && SET QT_SCALE_FACTOR=1 && SET QT_FONT_DPI=96 && venv\Scripts\python.exe venv\Lib\site-packages\mw4\loader.py >> run.log