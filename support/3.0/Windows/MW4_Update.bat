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
echo update script version 3.0
echo ---------------------------------------------

echo update script version 3.0 > update.log 2>&1

echo.
echo ---------------------------------------------
echo updating MW4 to newest official release
echo ---------------------------------------------

call venv\Scripts\activate >> update.log 2>&1

if not errorlevel 1 goto :proceedRunMW4
echo.
echo ---------------------------------------------
echo no valid virtual environment installed
echo please check the install.log for errors
echo ---------------------------------------------

echo no valid virtual environment installed >> update.log 2>&1
exit

:proceedRunMW4
echo.
echo ---------------------------------------------
echo checking installed python version
echo ---------------------------------------------

echo Checking environment and start script >> update.log 2>&1

for /f "delims=" %%a in ('python --version') do @set T=%%a

echo variable T has value of %T% >> update.log

echo %T% | find "3.10" > nul
if not errorlevel 1 SET P_VER='python3.10'

echo %T% | find "3.9" > nul
if not errorlevel 1 SET P_VER='python3.9'

echo %T% | find "3.8" > nul
if not errorlevel 1 SET P_VER='python3.8'

echo %T% | find "3.7" > nul
if not errorlevel 1 SET P_VER='python3.7'

echo variable P_VER has value of %P_VER% >> update.log 2>&1

echo %P_VER% | find "python" > nul
if not errorlevel 1 goto :proceedOK

echo.
echo ---------------------------------------------
echo no valid python version installed
echo ---------------------------------------------

echo no valid python version installed >> update.log 2>&1
exit

:proceedOK
echo.
echo ---------------------------------------------
echo python version ok: %P_VER%
echo ---------------------------------------------

venv\Scripts\python -m pip install mountwizzard4 --upgrade --no-cache-dir >> update.log 2>&1

echo.
echo ----------------------------------------
echo updated mountwizzard4 successfully
echo for details see update.log
echo ----------------------------------------