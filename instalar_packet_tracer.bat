@echo off
setlocal EnableExtensions
title Instalador Protocolo Packet Tracer

REM ============================================================
REM  Registra el protocolo ciscopt:// para que el boton de la
REM  web abra Packet Tracer. Necesita permisos de administrador.
REM  Si no ejecutas como admin, se relanza solo con elevacion.
REM ============================================================

set "SCRIPT_DIR=%~dp0"
set "BAT_PATH=%SCRIPT_DIR%open_packet_tracer.bat"

REM --- Relanzar como administrador si no lo somos ---
net session >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Solicitando permisos de administrador...
    powershell -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b 0
)

echo.
echo  ============================================
echo   Instalador del protocolo ciscopt://
echo  ============================================
echo   Carpeta: %SCRIPT_DIR%
echo.

if not exist "%SCRIPT_DIR%packet_tracer_launcher.py" (
    echo  [ERROR] No se encuentra packet_tracer_launcher.py
    pause
    exit /b 1
)

set "REG_FILE=%TEMP%\packet_tracer_protocol_install.reg"

(
echo Windows Registry Editor Version 5.00
echo.
echo [HKEY_CLASSES_ROOT\ciscopt]
echo @="URL:Packet Tracer Protocol"
echo "URL Protocol"=""
echo.
echo [HKEY_CLASSES_ROOT\ciscopt\DefaultIcon]
echo @="\"%SCRIPT_DIR%packet_tracer_launcher.py\",1"
echo.
echo [HKEY_CLASSES_ROOT\ciscopt\shell\open\command]
echo @="\"%BAT_PATH%\" \"%%1\""
) > "%REG_FILE%"

echo  [OK] Registro generado.
echo  Registrando protocolo ciscopt:// ...

regedit /s "%REG_FILE%"
del "%REG_FILE%" >nul 2>nul

REM --- Verificar que realmente quedo registrado ---
reg query "HKCR\ciscopt\shell\open\command" >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo  [OK] Protocolo registrado correctamente.
) else (
    echo  [ERROR] No se pudo registrar el protocolo.
    echo          Acepta la ventana UAC y vuelve a intentar.
    pause
    exit /b 1
)

echo.
echo  ============================================
echo   Listo. Al pulsar el boton en la web, el
echo   navegador mostrara un aviso para abrir la
echo   aplicacion "ciscopt" -> haz clic en Abrir.
echo  ============================================
echo.
pause
