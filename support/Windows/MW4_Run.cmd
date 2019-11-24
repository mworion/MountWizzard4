::====================================================================
:: Powershell script launcher
::=====================================================================
:MAIN
    @echo off
    for /f "tokens=*" %%p in ("%~p0") do set SCRIPT_PATH=%%p
    pushd "%SCRIPT_PATH%"

    START /MIN powershell.exe -sta -c "& {.\%~n0.ps1 %*}"

    popd
    set SCRIPT_PATH=