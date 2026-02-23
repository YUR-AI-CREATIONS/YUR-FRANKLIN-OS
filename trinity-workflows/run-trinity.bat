@echo off
REM Trinity Workflow Executor for Franklin OS
REM Usage: run-trinity.bat [workflow-name] [mode] [MISSION_ID]

setlocal

set TRINITY_PATH=C:\Users\jerem\Trinity
set WORKFLOW_DIR=%~dp0
set WORKFLOW_NAME=%1
set MODE=%2
set MISSION_ID=%3

if "%WORKFLOW_NAME%"=="" (
    echo Usage: run-trinity.bat [workflow-name] [mode] [MISSION_ID]
    echo.
    echo Available workflows:
    dir /b %WORKFLOW_DIR%*.yaml
    echo.
    echo Modes: validate, dry-run, run
    exit /b 1
)

if "%MODE%"=="" set MODE=run

echo.
echo ========================================
echo Trinity Executor for Franklin OS
echo ========================================
echo Workflow: %WORKFLOW_NAME%
echo Mode: %MODE%
echo Mission: %MISSION_ID%
echo ========================================
echo.

set PYTHONPATH=%TRINITY_PATH%\src;%CD%\..\backend;%CD%\..\services

if "%MISSION_ID%"=="" (
    if "%MODE%"=="dry-run" (
        python -m trinity.cli run %WORKFLOW_DIR%\%WORKFLOW_NAME%.yaml --dry-run
    ) else if "%MODE%"=="validate" (
        python -m trinity.cli validate %WORKFLOW_DIR%\%WORKFLOW_NAME%.yaml
    ) else (
        python -m trinity.cli run %WORKFLOW_DIR%\%WORKFLOW_NAME%.yaml
    )
) else (
    set MISSION_ID=%MISSION_ID%
    if "%MODE%"=="dry-run" (
        python -m trinity.cli run %WORKFLOW_DIR%\%WORKFLOW_NAME%.yaml --dry-run
    ) else if "%MODE%"=="validate" (
        python -m trinity.cli validate %WORKFLOW_DIR%\%WORKFLOW_NAME%.yaml
    ) else (
        python -m trinity.cli run %WORKFLOW_DIR%\%WORKFLOW_NAME%.yaml
    )
)

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [SUCCESS] Workflow completed successfully
    exit /b 0
) else (
    echo.
    echo [ERROR] Workflow failed with code %ERRORLEVEL%
    exit /b %ERRORLEVEL%
)
