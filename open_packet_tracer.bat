@echo off
setlocal EnableExtensions

set "SCRIPT_DIR=%~dp0"

where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    py "%SCRIPT_DIR%packet_tracer_launcher.py" %*
    exit /b %ERRORLEVEL%
)

where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    python "%SCRIPT_DIR%packet_tracer_launcher.py" %*
    exit /b %ERRORLEVEL%
)

echo Python no esta instalado o no esta en PATH.
exit /b 1
