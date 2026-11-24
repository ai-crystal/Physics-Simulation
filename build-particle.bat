@echo off
rem Build one volume: particle
chcp 936 >nul
cd /d "%~dp0"
call build.bat particle
