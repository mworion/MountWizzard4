@echo off
rem
rem run script for Win10
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
echo ---------------------------------------------
echo run script version 2.2
echo ---------------------------------------------

echo run script version 2.2 > run.log 2>&1

call venv\Scripts\activate venv >> run.log 2>&1

if not errorlevel 1 goto :proceedRunMW4
echo.
echo ---------------------------------------------
echo no valid virtual environment installed
echo please check the install.log for errors
echo ---------------------------------------------

echo no valid virtual environment installed >> run.log 2>&1
exit

:proceedRunMW4
echo.
echo ---------------------------------------------
echo checking installed python version
echo ---------------------------------------------

echo Checking environment and start script >> run.log 2>&1

for /f "delims=" %%a in ('python --version') do @set T=%%a

echo variable T has value of %T% >> run.log

echo %T% | find "3.9" > nul
if not errorlevel 1 SET P_VER='python3.9'

echo %T% | find "3.8" > nul
if not errorlevel 1 SET P_VER='python3.8'

echo %T% | find "3.7" > nul
if not errorlevel 1 SET P_VER='python3.7'

echo variable P_VER has value of %P_VER% >> run.log 2>&1

echo %P_VER% | find "python" > nul
if not errorlevel 1 goto :proceedOK

echo.
echo ---------------------------------------------
echo no valid python version installed
echo ---------------------------------------------

echo no valid python version installed >> run.log 2>&1
exit

:proceedOK
echo.
echo ---------------------------------------------
echo python version ok: %P_VER%
echo ---------------------------------------------

SET QT_SCALE_FACTOR=1 >> run.log 2>&1
SET QT_FONT_DPI=96 >> run.log 2>&1
venv\Scripts\python.exe venv\Lib\site-packages\mw4\loader.py >> run.log 2>&1