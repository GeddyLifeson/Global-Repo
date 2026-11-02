@echo off
rem Reset Diaithir Server: backup, fresh Age I world, spawn at Creag Ruadh (on land), boot, check. One double-click.
rem Needs: stage folder at E:\DiaithirServer\stage (repo.zip, jars, remove.txt). Safe to run again: it resumes where it stopped.
setlocal
set ROOT=E:\DiaithirServer
set REPO=E:\DiaithirRPG-reset
set BRANCH=claude/v1-overnight-reset
title Reset Diaithir Server
rem No GitHub needed: the repo files come zipped in the stage folder.
if not exist "%ROOT%\stage\repo.zip" (echo Missing %ROOT%\stage\repo.zip & pause & exit /b 1)
if exist "%REPO%" rmdir /s /q "%REPO%"
python -m zipfile -e "%ROOT%\stage\repo.zip" "%REPO%"
if not exist "%REPO%\tools\world\regen.cmd" (echo Could not unpack the repo files. & pause & exit /b 1)
rem Client: Untamed Wilds diaithir.2 (whale kick) and diaithir-ages diaithir.2 (key crash) into every Prism instance with the pack.
for /d %%I in ("E:\Prism\instances\*" "%APPDATA%\PrismLauncher\instances\*") do for %%M in ("%%I\.minecraft\mods" "%%I\minecraft\mods") do if exist "%%~M\untamedwilds-*.jar" (
  del /q "%%~M\untamedwilds-26.1.2-3.0.1.jar" "%%~M\untamedwilds-26.1.2-3.0.1-diaithir.1.jar" "%%~M\diaithir-ages-neoforge-26.1.2-0.1.0-diaithir.1.jar" 2>nul
  copy /y "%ROOT%\stage\mods\untamedwilds-26.1.2-3.0.1-diaithir.2.jar" "%%~M\" >nul
  copy /y "%ROOT%\stage\mods\diaithir-ages-neoforge-26.1.2-0.1.0-diaithir.2.jar" "%%~M\" >nul
  echo Client updated: %%~M
)
call "%REPO%\tools\world\regen.cmd" -Root %ROOT% -Force
set RC=%errorlevel%
echo.
if %RC%==0 (echo Server is up, join ssh-elem.tun.ply.gg) else (echo Something stopped it. Re-run this file; it resumes. Log: %ROOT%\regen_state.txt)
pause
exit /b %RC%
