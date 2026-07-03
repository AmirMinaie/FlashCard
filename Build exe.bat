@echo off
setlocal

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

echo.
echo ==========================================
echo Build finished.
echo Executable:
echo %PROJECT_DIR%\output\dist\DuckMemo.exe
echo ==========================================

pause