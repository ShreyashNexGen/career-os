@echo off
title CareerOS Server
cd /d "%~dp0"
echo ============================================================
echo   CareerOS - AI Job Search & Application Platform
echo   Local Dashboard: http://localhost:8000
echo   API Docs:        http://localhost:8000/docs
echo ============================================================
echo.
python run.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Server stopped with error.
    pause
)
