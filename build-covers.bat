@echo off
rem Regenerate covers only
chcp 936 >nul
cd /d "%~dp0"
call build.bat covers
