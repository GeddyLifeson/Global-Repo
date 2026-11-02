@echo off
rem Fixes the world-generation crash (stale ore modifiers), restarts the server and sets spawn. Keeps the current world.
python -I "%~dp0live_fix.py" C:\DiaithirServer
pause
