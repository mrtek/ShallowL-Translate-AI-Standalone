@echo off
chcp 65001 > nul
title ShallowL Translate (NVIDIA)
call venv\Scripts\activate

echo STARTING PROGRAM... / ЗАПУСК ПРОГРАММЫ...
python main.py --model models/dolphin-2.9.3-mistral-nemo-12b.Q4_K_M.gguf --gpu-layers 99 --engine cuda

echo.
echo PROGRAM CLOSED OR CRASHED. / ПРОГРАММА ЗАВЕРШЕНА ИЛИ ВЫЛЕТЕЛА.
pause