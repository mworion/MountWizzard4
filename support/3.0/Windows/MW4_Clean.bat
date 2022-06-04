@echo off
rem
rem updater for Win10
rem (c) 2021 mworion
rem

echo.
echo ---------------------------------------------
echo.
echo ##     ## ##      ## ##
echo ###   ### ##  ##  ## ##    ##
echo #### #### ##  ##  ## ##    ##
echo ## ### ## ##  ##  ## ##    ##
echo ##     ## ##  ##  ## #########
echo ##     ## ##  ##  ##       ##
echo ##     ##  ###  ###        ##
echo.
echo ##      ## #### ##    ##
echo ##  ##  ##  ##  ###   ##
echo ##  ##  ##  ##  ####  ##
echo ##  ##  ##  ##  ## ## ##
echo ##  ##  ##  ##  ##  ####
echo ##  ##  ##  ##  ##   ###
echo  ###  ###  #### ##    ##
echo.
echo ---------------------------------------------
echo clean script version 3.0
echo ---------------------------------------------

echo clean script version 3.0 > update.log 2>&1

echo.
echo ---------------------------------------------
echo cleaning python system packages
echo ---------------------------------------------

pip freeze > clean.txt & pip uninstall -r clean.txt -y > clean.log 2>&1

echo.
echo ----------------------------------------
echo updated mountwizzard4 successfully
echo for details see update.log
echo ----------------------------------------