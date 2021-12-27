@echo off
rem
rem Installer for Win10
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
echo.
echo ##      ## #### ##    ##    ##     #####
echo ##  ##  ##  ##  ###   ##  ####    ##   ##
echo ##  ##  ##  ##  ####  ##    ##   ##     ##
echo ##  ##  ##  ##  ## ## ##    ##   ##     ##
echo ##  ##  ##  ##  ##  ####    ##   ##     ##
echo ##  ##  ##  ##  ##   ###    ##    ##   ##
echo  ###  ###  #### ##    ##  ######   #####
echo.
echo install script version 2.2
echo ---------------------------------------------

echo install script version 2.2 > install.log 2>&1


echo.
echo ---------------------------------------------
echo checking installed python version
echo ---------------------------------------------

echo checking environment and start script >> install.log 2>&1

for /f "delims=" %%a in ('python --version') do @set T=%%a

echo variable T has value of %T% >> install.log 2>&1

echo %T% | find "3.9" > nul
if not errorlevel 1 SET P_VER='python3.9'

echo %T% | find "3.8" > nul
if not errorlevel 1 SET P_VER='python3.8'

echo %T% | find "3.7" > nul
if not errorlevel 1 SET P_VER='python3.7'

echo variable P_VER has value of %P_VER% >> install.log 2>&1

echo %P_VER% | find "python" > nul
if not errorlevel 1 goto :proceed32Bit

echo.
echo ---------------------------------------------
echo no valid python version installed
echo ---------------------------------------------

echo no valid python version installed >> install.log 2>&1
exit

:proceed32Bit
echo import platform > test.py
echo print(platform.architecture()[0]) >> test.py

for /f "delims=" %%a in ('python test.py') do @set OS=%%a
del test.py

echo Checking 32/64 bit OS >> install.log 2>&1
echo variable OS has value of %OS% >> install.log 2>&1
echo %OS% | find "32" > nul
if errorlevel 1 goto :64bit

echo python 32bit installed >> install.log 2>&1
echo.
echo ---------------------------------------------
echo python 32Bit installed
echo ---------------------------------------------

goto :proceedVirtualenv

:64bit
echo python 64bit installed >> install.log 2>&1
echo.
echo ---------------------------------------------
echo python 64Bit installed
echo ---------------------------------------------

:proceedVirtualenv
echo installing wheel >> install.log 2>&1
python -m pip install wheel --disable-pip-version-check >> install.log 2>&1

echo.
echo ---------------------------------------------
echo installing %P_VER% in virtual environ
echo ---------------------------------------------

echo Installing %P_VER% in virtual environ >> install.log 2>&1
python -m venv venv >> install.log 2>&1
if not errorlevel 1 goto :proceedInstallMW4

echo.
echo ---------------------------------------------
echo no valid virtual environment installed
echo please check the install.log for errors
echo ---------------------------------------------

exit

:proceedInstallMW4
echo checking system packages, should be no mw4 in >> install.log  2>&1
python -m pip list >> install.log 2>&1
echo.
echo ---------------------------------------------
echo installing mountwizzard4 - takes some time
echo ---------------------------------------------

call venv\Scripts\activate venv >> install.log 2>&1
python -m pip install pip --upgrade >> install.log 2>&1
python -m pip install setuptools --upgrade >> install.log 2>&1
python -m pip install wheel --upgrade >> install.log 2>&1
python -m pip install mountwizzard4 --upgrade --no-cache-dir >> install.log 2>&1

echo checking venv packages, mw4 should be present >> install.log  2>&1
python -m pip list >> install.log 2>&1
echo.
echo ---------------------------------------------
echo installed mountwizzard4 successfully
echo for details see install.log
echo ---------------------------------------------

echo MountWizzard4 successfully installed >> install.log 2>&1
