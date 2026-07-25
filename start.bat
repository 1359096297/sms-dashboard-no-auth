@echo off
setlocal
cd /d "%~dp0"

"C:\BtSoft\python\python_3.11.15\python.exe" -m uvicorn main:app --host 127.0.0.1 --port 8000 --workers 1
