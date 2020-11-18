@echo off
rem
rem updater for Win10
rem (c) 2020 mworion
rem

echo.
echo ---------------------------------------------
echo Script version 0.2
echo ---------------------------------------------
echo.

venv\Scripts\activate && pip install mountwizzard4 --upgrade --no-cache-dir >> update.log