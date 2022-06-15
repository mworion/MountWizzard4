@echo off
rem
rem clean script for Win10
rem (c) 2022 mworion
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
echo cleaned python system successfully
echo for details see clean.log
echo ----------------------------------------