@echo off
cd /d "%~dp0"
echo Starting Future Abdullah backend...
py -m uvicorn server.main:app --reload --host 127.0.0.1 --port 8000
