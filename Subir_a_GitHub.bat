@echo off
title Subiendo cambios de TTC a GitHub...
cd /d "%~dp0"
echo ========================================================
echo   SUBIENDO CAMBIOS DE TTC A GITHUB
echo ========================================================
echo.

echo [1/3] Configurando identidad en Git...
git config user.name "Patoma89"
git config user.email "patoma89@users.noreply.github.com"

echo.
echo [2/3] Creando commit con los cambios...
git add .
git commit -m "feat: Renombrar a TTC y anadir sitio web interactivo para GitHub Pages"

echo.
echo [3/3] Subiendo a GitHub (git push origin main)...
git push origin main

echo.
if %errorlevel% neq 0 (
    echo ========================================================
    echo [ERROR / AVISO] No se pudo completar el push automaticamente.
    echo Revisa el mensaje de arriba.
    echo Si te pide autenticacion en GitHub, autorizala en la ventana que se abra.
    echo ========================================================
) else (
    echo ========================================================
    echo [EXITO] Los cambios ya estan subidos a GitHub correctamente.
    echo Puedes entrar a: https://github.com/Patoma89/TarkovScope
    echo ========================================================
)
echo.
pause
