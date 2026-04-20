@echo off
chcp 65001 > nul
title Install ShallowL Translate AI Standalone / Установка

set "PY_BASE=https://www.python.org/ftp/python/3.12.3/amd64"
set "PY_DIR=%~dp0bin\python"
set "MODEL_PATH=models\dolphin-2.9.3-mistral-nemo-12b.Q4_K_M.gguf"

echo [1/5] Cleaning up... / Очистка старых файлов...
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM koboldcpp.exe /T >nul 2>&1

:: Сносим всё старое под корень
if exist "%PY_DIR%" rmdir /s /q "%PY_DIR%"
if exist "venv" rmdir /s /q "venv"
if exist ".venv" rmdir /s /q ".venv"
if exist "bin\tmp_msi" rmdir /s /q "bin\tmp_msi"
if not exist "bin" mkdir "bin"

echo [2/5] Downloading Official Python Components... / Загрузка компонентов...
mkdir bin\tmp_msi
curl -L -o bin\tmp_msi\core.msi %PY_BASE%/core.msi
if errorlevel 1 goto :ERROR_EXIT
curl -L -o bin\tmp_msi\exe.msi %PY_BASE%/exe.msi
curl -L -o bin\tmp_msi\lib.msi %PY_BASE%/lib.msi
curl -L -o bin\tmp_msi\tcltk.msi %PY_BASE%/tcltk.msi

echo Extracting Components (Portable mode)... / Распаковка (Без реестра)...
:: /a заставляет Windows просто извлечь файлы из MSI, /qn делает это скрыто
msiexec /a "%~dp0bin\tmp_msi\core.msi" /qn TARGETDIR="%PY_DIR%"
msiexec /a "%~dp0bin\tmp_msi\exe.msi" /qn TARGETDIR="%PY_DIR%"
msiexec /a "%~dp0bin\tmp_msi\lib.msi" /qn TARGETDIR="%PY_DIR%"
msiexec /a "%~dp0bin\tmp_msi\tcltk.msi" /qn TARGETDIR="%PY_DIR%"

:: Удаляем технические копии msi и временную папку
del /q "%PY_DIR%\*.msi"
rmdir /s /q bin\tmp_msi

echo [3/5] Installing Pip... / Установка Pip...
curl -L -o bin\get-pip.py https://bootstrap.pypa.io/get-pip.py
"%PY_DIR%\python.exe" bin\get-pip.py --no-warn-script-location
del bin\get-pip.py

echo [4/5] Installing libraries... / Установка библиотек...
"%PY_DIR%\python.exe" -m pip install customtkinter huggingface_hub python-docx PyMuPDF requests openai
if errorlevel 1 goto :ERROR_EXIT

echo [5/5] Checking AI Engine... / Проверка ИИ движка...
if exist "bin\koboldcpp.exe" goto :FINISH
echo Downloading AI Engine...
curl -L -o bin\koboldcpp.exe https://github.com/LostRuins/koboldcpp/releases/latest/download/koboldcpp.exe

:FINISH
if not exist "models" mkdir "models"
echo.
echo Setup completed successfully! / Установка полностью завершена!
pause
exit /b

:ERROR_EXIT
echo [!] Critical error during installation! / Ошибка сети при скачивании!
pause
exit /b