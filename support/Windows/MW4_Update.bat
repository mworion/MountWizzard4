@echo off
rem
rem updater for Win10
rem (c) 2020 mworion
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
echo ---------------------------------------------
echo update script version 0.2
echo ---------------------------------------------
echo.


echo.
echo ---------------------------------------------
echo updating MW4 to newest official release
echo ---------------------------------------------
echo.

call venv\Scripts\activate > update.log


echo.
echo ---------------------------------------------
echo checking installed python version
echo ---------------------------------------------
echo.

echo Checking environment and start script >> update.log

for /f "delims=" %%a in ('python --version') do @set T=%%a

echo variable T has value of %T% >> update.log

echo %T% | find "3.8" > nul
if not errorlevel 1 SET P_VER='python3.8'

echo %T% | find "3.7" > nul
if not errorlevel 1 SET P_VER='python3.7'

echo %T% | find "3.6" > nul
if not errorlevel 1 SET P_VER='python3.6'

echo variable P_VER has value of %P_VER% >> update.log

echo %P_VER% | find "python" > nul
if not errorlevel 1 goto :proceedOK

echo.
echo ---------------------------------------------
echo no valid python version installed
echo ---------------------------------------------
echo.
exit

:proceedOK
echo.
echo ---------------------------------------------
echo python version ok
echo ---------------------------------------------
echo.

pip install mountwizzard4 --upgrade --no-cache-dir >> update.log

echo.
echo ----------------------------------------
echo updated mountwizzard4 successfully
echo for details see update.log
echo ----------------------------------------
echo.