@echo off
rem
rem run script for Win10
rem (c) 2020 mworion
rem

echo.
echo ---------------------------------------------
echo.
echo     M   M  W   W   W    4
echo    MM  MM  W  WW  W    4
echo   M M M M  W W W W    4  4
echo  M  MM  M  WW  WW    444444
echo M   M   M  W   W       4
echo.
echo ---------------------------------------------
echo run script version 0.2
echo ---------------------------------------------
echo.

venv\Scripts\activate && venv\Scripts\python.exe venv\Lib\site-packages\mw4\loader.py test > runTest.log