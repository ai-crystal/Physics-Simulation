@echo off
rem Build one volume: intro
chcp 936 >nul
cd /d "%~dp0"
call build.bat intro
