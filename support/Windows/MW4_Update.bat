@echo off
rem
rem updater for Win10
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
echo update script version 0.2
echo ---------------------------------------------
echo.

venv\Scripts\activate && pip install mountwizzard4 --upgrade --no-cache-dir >> update.log