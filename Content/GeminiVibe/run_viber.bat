@echo off
title Gemini UE VibeCoder
cd /d "%~dp0"
:: Переконайся, що тут встановлено твій API-ключ, або він є глобально в системі
:: set GEMINI_API_KEY=твій_ключ_тут
python viber.py
pause