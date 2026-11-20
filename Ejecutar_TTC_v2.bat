@echo off
title Iniciando TTC v2.0 Next-Gen (GPU WebView2)...
cd /d "%~dp0"
if exist "C:\Users\INFORMES1\AppData\Local\Python\pythoncore-3.14-64\python.exe" (
    "C:\Users\INFORMES1\AppData\Local\Python\pythoncore-3.14-64\python.exe" TTC_v2.py
) else (
    python TTC_v2.py
)
if errorlevel 1 (
    echo.
    echo Hubo un error al iniciar TTC v2.0 Next-Gen.
    pause
)
