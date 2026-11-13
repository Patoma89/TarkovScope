@echo off
title Iniciando TTC (Tactical Tarkov Companion)...
cd /d "%~dp0"
if exist "C:\Users\INFORMES1\AppData\Local\Python\pythoncore-3.14-64\python.exe" (
    "C:\Users\INFORMES1\AppData\Local\Python\pythoncore-3.14-64\python.exe" TarkovScope.py
) else (
    python TarkovScope.py
)
if errorlevel 1 (
    echo.
    echo Hubo un error al iniciar TTC (Tactical Tarkov Companion).
    pause
)
