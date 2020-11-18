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

venv\Scripts\activate && venv\Scripts\python.exe venv\Lib\site-packages\mw4\loader.py test > runTest.log