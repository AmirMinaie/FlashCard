@echo off
setlocal EnableDelayedExpansion

:: Record build start time
set "START=%TIME%"

call venv\Scripts\activate

echo ==========================================
echo Cleaning previous build files...
echo ==========================================

if exist "output\dist" rmdir /s /q "output\dist"
if exist "output\build" rmdir /s /q "output\build"
if exist "output\DuckMemo.spec" del /q "output\DuckMemo.spec"

for /d /r . %%d in (__pycache__) do (
    if exist "%%d" rmdir /s /q "%%d"
)

echo.
echo ==========================================
echo Building DuckMemo...
echo ==========================================

set "PROJECT_DIR=%CD%"

pyinstaller ^
    "%PROJECT_DIR%\app\Main.py" ^
    --name DuckMemo ^
    --onefile ^
    --noconsole ^
    --clean ^
    --icon "%PROJECT_DIR%\app\assets\images\icon.ico" ^
    --distpath "%PROJECT_DIR%\output\dist" ^
    --workpath "%PROJECT_DIR%\output\build" ^
    --specpath "%PROJECT_DIR%\output" ^
    --add-data "%PROJECT_DIR%\app\Kv;Kv" ^
    --add-data "%PROJECT_DIR%\app\assets;assets" ^
    --add-data "%PROJECT_DIR%\app\widgets;widgets" ^
    --collect-all kivymd ^
    --hidden-import kivymd.icon_definitions ^
    --hidden-import kivymd.uix.progressbar ^
    --hidden-import kivymd.uix.slider

:: Record build end time
set "END=%TIME%"

:: Convert start time to seconds
for /f "tokens=1-4 delims=:., " %%a in ("%START%") do (
    set /a START_SEC=%%a*3600 + %%b*60 + %%c
)

:: Convert end time to seconds
for /f "tokens=1-4 delims=:., " %%a in ("%END%") do (
    set /a END_SEC=%%a*3600 + %%b*60 + %%c
)

:: Handle midnight rollover
if !END_SEC! LSS !START_SEC! set /a END_SEC+=86400

:: Calculate elapsed time
set /a ELAPSED=END_SEC-START_SEC
set /a HH=ELAPSED/3600
set /a MM=(ELAPSED%%3600)/60
set /a SS=ELAPSED%%60

echo.
echo ==========================================
echo Build finished.
echo Executable:
echo %PROJECT_DIR%\output\dist\DuckMemo.exe
echo.
echo Build Time: !HH!h !MM!m !SS!s
echo ==========================================

pause