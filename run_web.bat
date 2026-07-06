@echo off
call .\venv\Scripts\activate.bat
echo Starting DeskPilot Web Interface on http://localhost:5000/
python api.py
pause
