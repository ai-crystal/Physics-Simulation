@echo off
rem Build one volume: diff
chcp 936 >nul
cd /d "%~dp0"
call build.bat diff
