@echo off
chcp 65001 > nul
title Install ShallowL Translate / Установка ShallowL Translate

echo [1/3] Preparing virtual environment... / Подготовка виртуального окружения...
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM koboldcpp.exe /T >nul 2>&1

if exist venv rmdir /s /q venv
python -m venv venv
call venv\Scripts\activate

if "%VIRTUAL_ENV%"=="" (
    echo [ERROR] Virtual environment failed! / [ОШИБКА] Виртуальное окружение не создалось!
    pause
    exit /b
)

echo [2/3] Installing libraries... / Установка библиотек...
python -m pip install --upgrade pip
pip install customtkinter huggingface_hub python-docx PyMuPDF requests openai

echo [3/3] Downloading AI Engine and Model... / Загрузка движка ИИ и Модели...
if not exist bin mkdir bin
curl -L -o bin\koboldcpp.exe https://github.com/LostRuins/koboldcpp/releases/latest/download/koboldcpp.exe

if not exist models mkdir models
hf download dphn/dolphin-2.9.3-mistral-nemo-12b-GGUF dolphin-2.9.3-mistral-nemo-12b.Q4_K_M.gguf --local-dir models

echo.
echo Setup completed successfully! / Установка полностью завершена!
pause