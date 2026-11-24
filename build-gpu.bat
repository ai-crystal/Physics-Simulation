@echo off
rem Build one volume: gpu
chcp 936 >nul
cd /d "%~dp0"
call build.bat gpu
