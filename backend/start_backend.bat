@echo off
cd /d %~dp0
echo Текущая директория: %cd%
call venv\Scripts\activate
echo Виртуальное окружение активировано
python -m uvicorn app.main:app --reload
pause
