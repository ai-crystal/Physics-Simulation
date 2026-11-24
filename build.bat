@echo off
rem Build the Physics Simulation series (eight volumes) or a single volume.
rem Usage:
rem   build.bat              build every volume
rem   build.bat intro        build one volume (intro/math/rigid/deform/fluid/particle/gpu/diff)
rem   build.bat figures      redraw every figure
rem   build.bat covers       regenerate covers
rem   build.bat list         list volumes
rem   build.bat site         regenerate sidebar and README
setlocal enabledelayedexpansion
chcp 936 >nul
cd /d "%~dp0"

set "PYEXE=C:\Users\Administrator\AppData\Local\Programs\Python\Python312\python.exe"
if not exist "%PYEXE%" set "PYEXE=python"

set "VOLS=intro math rigid deform fluid particle gpu diff"

"%PYEXE%" -c "import markdown, pymupdf, playwright, PIL, matplotlib, numpy" 2>nul
if errorlevel 1 (
  echo [*] Installing dependencies...
  "%PYEXE%" -m pip install -r books\build\requirements.txt
  "%PYEXE%" -m playwright install chromium
)

set "TARGET=%~1"
if "%TARGET%"=="" goto all
if /i "%TARGET%"=="all" goto all
if /i "%TARGET%"=="list" goto list
if /i "%TARGET%"=="figures" goto figures
if /i "%TARGET%"=="covers" goto covers
if /i "%TARGET%"=="site" goto site
goto one

:list
"%PYEXE%" books\build\build.py --list
goto end

:figures
for %%B in (%VOLS%) do (
  if exist "books\code\%%B" (
    for /d %%D in (books\code\%%B\ch*) do (
      for %%F in ("%%D\fig_*.py") do (
        echo [*] figures: %%F
        "%PYEXE%" "%%F" || goto err
      )
    )
  )
)
goto end

:covers
"%PYEXE%" books\build\make_covers.py || goto err
goto end

:site
"%PYEXE%" _private\gen_site.py || goto err
goto end

:all
"%PYEXE%" books\build\gen_appendix.py || goto err
"%PYEXE%" books\build\build.py --all || goto err
goto end

:one
"%PYEXE%" books\build\gen_appendix.py --book %TARGET% || goto err
"%PYEXE%" books\build\build.py --book %TARGET% || goto err
goto end

:err
echo.
echo [!] Build failed. See the messages above.
pause
exit /b 1

:end
echo.
echo [OK] PDF files are in output\
pause
