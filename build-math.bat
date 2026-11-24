@echo off
rem Build one volume: math
chcp 936 >nul
cd /d "%~dp0"
call build.bat math
