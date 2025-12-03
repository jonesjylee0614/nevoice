@echo off
chcp 65001 >nul 2>&1
REM High-Performance Async WebSocket Server
REM Uses native websockets library, aligned with FunASR Demo
REM
REM Usage:
REM   start_wss_demo.bat                 # Default mode (wss_demo.py)
REM   start_wss_demo.bat --ssl           # With SSL
REM   start_wss_demo.bat --port 10097    # Custom port
REM   start_wss_demo.bat --compat        # Use FunASR compatible server (wss_funasr_compatible.py)

setlocal enabledelayedexpansion

REM Default config
set PORT=10096
set HOST=0.0.0.0
set USE_SSL=false
set CERTFILE=
set KEYFILE=
set USE_COMPAT=false

REM Parse arguments
:parse_args
if "%~1"=="" goto :done_args
if "%~1"=="--port" (
    set PORT=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--host" (
    set HOST=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--ssl" (
    set USE_SSL=true
    shift
    goto :parse_args
)
if "%~1"=="--certfile" (
    set CERTFILE=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--keyfile" (
    set KEYFILE=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--compat" (
    set USE_COMPAT=true
    shift
    goto :parse_args
)
echo Unknown argument: %~1
exit /b 1
:done_args

REM Change to script directory
cd /d "%~dp0"

REM SSL certificate paths (default to ssl_key in project)
if "%USE_SSL%"=="true" (
    if "%CERTFILE%"=="" set CERTFILE=ssl_key\server.crt
    if "%KEYFILE%"=="" set KEYFILE=ssl_key\server.key
    
    if not exist "!CERTFILE!" (
        echo ERROR: Certificate file not found: !CERTFILE!
        exit /b 1
    )
    if not exist "!KEYFILE!" (
        echo ERROR: Key file not found: !KEYFILE!
        exit /b 1
    )
)

echo.
echo ========================================
echo   Async WebSocket Server (FunASR Style)
echo ========================================
echo   Host: %HOST%
echo   Port: %PORT%
if "%USE_SSL%"=="true" (
    echo   SSL: Enabled
    echo   Cert: %CERTFILE%
    echo   Key: %KEYFILE%
) else (
    echo   SSL: Disabled ^(use --ssl to enable^)
)
if "%USE_COMPAT%"=="true" (
    echo   Mode: FunASR Compatible ^(wss_funasr_compatible.py^)
) else (
    echo   Mode: Default ^(wss_demo.py^)
)
echo.
echo Protocol:
echo   1. Send config JSON on connect
echo   2. Then send binary audio frames ^(PCM 16kHz 16bit^)
echo   3. Send is_speaking=false JSON to stop
echo ========================================
echo.

REM Build command - choose server based on --compat flag
if "%USE_COMPAT%"=="true" (
    set CMD=python server/wss_funasr_compatible.py --host %HOST% --port %PORT%
) else (
    set CMD=python server/wss_demo.py --host %HOST% --port %PORT%
)
if "%USE_SSL%"=="true" (
    set CMD=!CMD! --certfile !CERTFILE! --keyfile !KEYFILE!
)

echo Running: %CMD%
echo.
%CMD%

