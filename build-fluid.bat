@echo off
rem Build one volume: fluid
chcp 936 >nul
cd /d "%~dp0"
call build.bat fluid
