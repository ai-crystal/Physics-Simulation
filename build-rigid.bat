@echo off
rem Build one volume: rigid
chcp 936 >nul
cd /d "%~dp0"
call build.bat rigid
